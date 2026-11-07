"""The scheduler: FSRS-4.5 with Anki-style learning steps for brand-new cards.

FSRS models every card with three numbers
    D  difficulty   (1..10)
    S  stability    in days: the delay at which recall probability is 90 %
    R  retrievability: probability you would recall it right now
and a power forgetting curve  R(t,S) = (1 + FACTOR * t / S) ^ DECAY.

The maths is taken from the published FSRS-4.5 specification; the constants below
are the published default parameters.  They can be replaced per deck by fitted
values later without touching the rest of the program.
"""
import json
import math
import random
import time

DECAY = -0.5
FACTOR = 19.0 / 81.0          # 0.9 ** (1/DECAY) - 1, so that R(S,S) = 0.9

RATING_AGAIN, RATING_HARD, RATING_GOOD, RATING_EASY = 1, 2, 3, 4
RATING_NAMES = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}

DEFAULT_W = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
             1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]


# ------------------------------------------------------------------ helpers
def human_delay(seconds):
    """'45s', '12m', '3h', '8d', '4.2mo', '1.4y'."""
    if seconds is None:
        return ""
    minutes = seconds / 60.0
    if minutes < 1:
        return f"{max(1, int(round(seconds)))}s"
    if minutes < 60:
        return f"{int(round(minutes))}m"
    hours = minutes / 60.0
    if hours < 24:
        return f"{int(round(hours))}h"
    days = hours / 24.0
    if days < 30:
        return f"{int(round(days))}d"
    if days < 365:
        return f"{days / 30.0:.1f}mo"
    return f"{days / 365.0:.1f}y"


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


class Scheduler:
    def __init__(self, db, rng=None):
        self.db = db
        self.rng = rng or random.Random()

    # -------------------------------------------------------------- deck
    def settings(self, deck_row):
        w = self.db.deck_params(deck_row)
        def _steps(raw, default):
            try:
                s = json.loads(raw)
                return [float(x) for x in s] if s else default
            except Exception:
                return default
        return {
            "w": w,
            "retention": float(deck_row["desired_retention"] or 0.9),
            "max_interval": int(deck_row["max_interval"] or 730),
            "learn": _steps(deck_row["learn_steps"], [1.0, 10.0]),
            "relearn": _steps(deck_row["relearn_steps"], [10.0]),
        }

    # -------------------------------------------------------- FSRS pieces
    @staticmethod
    def retrievability(elapsed_days, stability):
        if not stability or stability <= 0:
            return 0.0
        return (1 + FACTOR * max(0.0, elapsed_days) / stability) ** DECAY

    @staticmethod
    def interval_days(stability, retention=0.9):
        r = _clamp(retention, 0.70, 0.99)
        return stability / FACTOR * (r ** (1.0 / DECAY) - 1.0)

    @staticmethod
    def initial_stability(w, grade):
        return max(0.1, w[grade - 1])

    @staticmethod
    def initial_difficulty(w, grade):
        return _clamp(w[4] - (grade - 3) * w[5], 1.0, 10.0)

    def next_difficulty(self, w, difficulty, grade):
        d0_3 = w[4]                      # D0(Good)
        d = difficulty - w[6] * (grade - 3)
        d = w[7] * d0_3 + (1 - w[7]) * d   # mean reversion, fights "ease hell"
        return _clamp(d, 1.0, 10.0)

    def stability_after_recall(self, w, difficulty, stability, retrievability, grade):
        sinc = (math.exp(w[8]) * (11 - difficulty)
                * stability ** (-w[9])
                * (math.exp(w[10] * (1 - retrievability)) - 1)
                * (w[15] if grade == RATING_HARD else 1.0)
                * (w[16] if grade == RATING_EASY else 1.0))
        return stability * (1 + sinc)

    def stability_after_forget(self, w, difficulty, stability, retrievability):
        return (w[11] * difficulty ** (-w[12])
                * ((stability + 1) ** w[13] - 1)
                * math.exp(w[14] * (1 - retrievability)))

    # ------------------------------------------------------------ interval
    def _fuzz(self, days):
        if days <= 2:
            return max(1, int(round(days)))
        span = max(1, int(round(days * 0.05)))
        return max(1, int(round(days + self.rng.randint(-span, span))))

    def _finish(self, days, settings):
        return self._fuzz(_clamp(days, 1, settings["max_interval"]))

    # -------------------------------------------------------------- grade
    def grade(self, card, rating, took_ms=0):
        """Apply an answer. Returns (updated_fields, delay_seconds, review_id)."""
        deck = self.db.deck(card["deck_id"])
        st = self.settings(deck)
        w = st["w"]
        now = time.time()
        state = card["state"]
        fields = {"reps": (card["reps"] or 0) + 1}
        delay_seconds = 0.0

        if state in ("new", "learning"):
            steps = st["learn"]
            step = card["step"] or 0
            if state == "new":
                step = 0
            if rating == RATING_AGAIN:
                fields.update(state="learning", step=0)
                delay_seconds = max(1.0, steps[0]) * 60
            elif rating == RATING_HARD:
                if step == 0:
                    wait = (steps[0] + steps[1]) / 2 if len(steps) > 1 else steps[0] * 1.5
                else:
                    wait = steps[step]
                fields.update(state="learning", step=step)
                delay_seconds = max(1.0, wait) * 60
            elif rating == RATING_GOOD:
                if step + 1 >= len(steps):
                    s0 = self.initial_stability(w, RATING_GOOD)
                    d0 = self.initial_difficulty(w, RATING_GOOD)
                    days = self._finish(self.interval_days(s0, st["retention"]), st)
                    fields.update(state="review", step=0, stability=s0, difficulty=d0,
                                  lapses=card["lapses"] or 0,
                                  introduced_at=card["introduced_at"] or now)
                    delay_seconds = days * 86400
                else:
                    fields.update(state="learning", step=step + 1,
                                  introduced_at=card["introduced_at"] or now)
                    delay_seconds = max(1.0, steps[step + 1]) * 60
            else:  # EASY graduates straight away
                s0 = self.initial_stability(w, RATING_EASY)
                d0 = self.initial_difficulty(w, RATING_EASY)
                days = self._finish(self.interval_days(s0, st["retention"]), st)
                fields.update(state="review", step=0, stability=s0, difficulty=d0,
                              lapses=card["lapses"] or 0,
                              introduced_at=card["introduced_at"] or now)
                delay_seconds = days * 86400
            elapsed_days = 0.0
            scheduled_days = delay_seconds / 86400.0

        elif state == "review":
            elapsed_days = max(0.0, (now - (card["last_review"] or now)) / 86400.0)
            r = self.retrievability(elapsed_days, card["stability"])
            if rating == RATING_AGAIN:
                s = self.stability_after_forget(w, card["difficulty"], card["stability"], r)
                d = self.next_difficulty(w, card["difficulty"], rating)
                steps = st["relearn"]
                fields.update(state="relearning", step=0, stability=max(0.1, s),
                              difficulty=d, lapses=(card["lapses"] or 0) + 1)
                delay_seconds = max(1.0, steps[0]) * 60
            else:
                s = self.stability_after_recall(w, card["difficulty"], card["stability"],
                                                r, rating)
                d = self.next_difficulty(w, card["difficulty"], rating)
                days = self._finish(self.interval_days(s, st["retention"]), st)
                fields.update(state="review", step=0, stability=max(s, card["stability"]),
                              difficulty=d)
                delay_seconds = days * 86400
            scheduled_days = delay_seconds / 86400.0

        else:  # relearning
            steps = st["relearn"]
            step = card["step"] or 0
            elapsed_days = max(0.0, (now - (card["last_review"] or now)) / 86400.0)
            if rating == RATING_AGAIN:
                fields.update(state="relearning", step=0)
                delay_seconds = max(1.0, steps[0]) * 60
            elif rating == RATING_HARD:
                fields.update(state="relearning", step=step)
                delay_seconds = max(1.0, steps[min(step, len(steps) - 1)]) * 60
            else:
                if step + 1 < len(steps) and rating == RATING_GOOD and len(steps) > 1:
                    fields.update(state="relearning", step=step + 1)
                    delay_seconds = max(1.0, steps[step + 1]) * 60
                else:
                    days = self._finish(
                        self.interval_days(card["stability"] or 1.0, st["retention"]), st)
                    fields.update(state="review", step=0)
                    delay_seconds = days * 86400
            scheduled_days = delay_seconds / 86400.0

        before = {
            "id": card["id"], "state": card["state"], "due": card["due"],
            "stability": card["stability"], "difficulty": card["difficulty"],
            "step": card["step"], "lapses": card["lapses"], "reps": card["reps"],
            "introduced_at": card["introduced_at"],
        }
        review_id = self.db.log_review(before, rating, elapsed_days, scheduled_days, took_ms)
        fields["due"] = now + delay_seconds
        fields["last_review"] = now
        self.db.save_card(card["id"], **fields)
        return fields, delay_seconds, review_id

    # ------------------------------------------------------------ preview
    def preview(self, card):
        """What each button would do right now: {rating: 'text'}."""
        deck = self.db.deck(card["deck_id"])
        st = self.settings(deck)
        w = st["w"]
        out = {}
        state = card["state"]

        if state in ("new", "learning"):
            steps = st["learn"]
            step = 0 if state == "new" else (card["step"] or 0)
            out[1] = steps[0] * 60
            out[2] = ((steps[0] + steps[1]) / 2 if step == 0 and len(steps) > 1
                      else steps[min(step, len(steps) - 1)]) * 60
            if step + 1 >= len(steps):
                out[3] = self._finish(
                    self.interval_days(self.initial_stability(w, 3), st["retention"]),
                    st) * 86400
            else:
                out[3] = steps[step + 1] * 60
            out[4] = self._finish(
                self.interval_days(self.initial_stability(w, 4), st["retention"]),
                st) * 86400

        elif state == "review":
            elapsed = max(0.0, (time.time() - (card["last_review"] or time.time())) / 86400.0)
            r = self.retrievability(elapsed, card["stability"] or 1.0)
            out[1] = st["relearn"][0] * 60
            for g in (2, 3, 4):
                s = self.stability_after_recall(w, card["difficulty"] or 5.0,
                                                card["stability"] or 1.0, r, g)
                out[g] = self._finish(self.interval_days(s, st["retention"]), st) * 86400

        else:  # relearning
            steps = st["relearn"]
            step = card["step"] or 0
            out[1] = steps[0] * 60
            out[2] = steps[min(step, len(steps) - 1)] * 60
            out[3] = self._finish(
                self.interval_days(card["stability"] or 1.0, st["retention"]), st) * 86400
            out[4] = out[3]

        return {k: human_delay(v) for k, v in out.items()}
