"""Storage: one SQLite file next to the program.

Three tables matter:
  item   - what you are learning (prompt/answer/source ...), written once
  card   - a question generated from an item (forward, or forward+reverse)
  review - every answer you have ever given; the scheduler's training data
"""
import json
import os
import sqlite3
import time
from datetime import date, datetime, timedelta

SCHEMA_VERSION = 1
LEARN_AHEAD = 600          # seconds: pull a learning card early - only when nothing else is left



def now():
    return time.time()


def day_start(ts=None):
    d = datetime.fromtimestamp(ts if ts is not None else time.time())
    return datetime(d.year, d.month, d.day).timestamp()


def fmt_duration(seconds):
    seconds = int(seconds or 0)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    h, m = divmod(seconds // 60, 60)
    return f"{h}h {m:02d}m"


DEFAULT_PARAMS = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
                  1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]


class DB:
    def __init__(self, path):
        self.path = path
        first_time = not os.path.exists(path)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create()
        if first_time or not self.conn.execute("SELECT 1 FROM deck").fetchone():
            self.add_deck("Default")

    # ------------------------------------------------------------- schema
    def _create(self):
        c = self.conn
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                k TEXT PRIMARY KEY, v TEXT);

            CREATE TABLE IF NOT EXISTS deck (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                desired_retention REAL DEFAULT 0.90,
                new_per_day INTEGER DEFAULT 20,
                reviews_per_day INTEGER DEFAULT 200,
                max_interval INTEGER DEFAULT 730,
                learn_steps TEXT DEFAULT '[1, 10]',
                relearn_steps TEXT DEFAULT '[10]',
                params TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at REAL);

            CREATE TABLE IF NOT EXISTS item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL REFERENCES deck(id) ON DELETE CASCADE,
                prompt TEXT NOT NULL,
                answer TEXT NOT NULL,
                explanation TEXT DEFAULT '',
                source TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                created_at REAL,
                suspended INTEGER DEFAULT 0);

            CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES item(id) ON DELETE CASCADE,
                ordinal INTEGER DEFAULT 0,
                state TEXT DEFAULT 'new',
                due REAL,
                stability REAL,
                difficulty REAL,
                last_review REAL,
                lapses INTEGER DEFAULT 0,
                reps INTEGER DEFAULT 0,
                step INTEGER DEFAULT 0,
                introduced_at REAL,
                suspended INTEGER DEFAULT 0);

            CREATE TABLE IF NOT EXISTS review (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL REFERENCES card(id) ON DELETE CASCADE,
                ts REAL,
                grade INTEGER,
                elapsed_days REAL,
                scheduled_days REAL,
                took_ms INTEGER DEFAULT 0,
                prev_state TEXT,
                prev_due REAL,
                prev_stability REAL,
                prev_difficulty REAL,
                prev_step INTEGER,
                prev_lapses INTEGER,
                prev_reps INTEGER,
                prev_introduced_at REAL);

            CREATE INDEX IF NOT EXISTS idx_card_due ON card(due);
            CREATE INDEX IF NOT EXISTS idx_card_state ON card(state);
            CREATE INDEX IF NOT EXISTS idx_review_ts ON review(ts);
            CREATE INDEX IF NOT EXISTS idx_review_card ON review(card_id);
            CREATE INDEX IF NOT EXISTS idx_item_deck ON item(deck_id);
            """
        )
        c.execute("INSERT OR IGNORE INTO meta(k,v) VALUES('schema',?)", (str(SCHEMA_VERSION),))
        c.execute("INSERT OR IGNORE INTO meta(k,v) VALUES('created',?)", (str(now()),))
        c.execute("INSERT OR IGNORE INTO meta(k,v) VALUES('theme','light')")
        c.commit()

    # ---------------------------------------------------------------- meta
    def get_meta(self, key, default=None):
        row = self.conn.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
        return row["v"] if row else default

    def set_meta(self, key, value):
        self.conn.execute("INSERT INTO meta(k,v) VALUES(?,?) "
                          "ON CONFLICT(k) DO UPDATE SET v=excluded.v", (key, str(value)))
        self.conn.commit()

    # --------------------------------------------------------------- decks
    def add_deck(self, name):
        cur = self.conn.execute(
            "INSERT INTO deck(name, params, created_at, sort_order) VALUES(?,?,?,?)",
            (name.strip(), json.dumps(DEFAULT_PARAMS), now(),
             self.conn.execute("SELECT COUNT(*) FROM deck").fetchone()[0]))
        self.conn.commit()
        return cur.lastrowid

    def decks(self):
        return self.conn.execute("SELECT * FROM deck ORDER BY sort_order, name").fetchall()

    def deck(self, deck_id):
        return self.conn.execute("SELECT * FROM deck WHERE id=?", (deck_id,)).fetchone()

    def deck_by_name(self, name):
        return self.conn.execute("SELECT * FROM deck WHERE name=?", (name,)).fetchone()

    def update_deck(self, deck_id, **fields):
        if not fields:
            return
        keys = ", ".join(f"{k}=?" for k in fields)
        self.conn.execute(f"UPDATE deck SET {keys} WHERE id=?",
                          (*fields.values(), deck_id))
        self.conn.commit()

    def update_all_decks(self, **fields):
        """The same scheduling values for every deck at once. Returns how many decks."""
        if not fields:
            return 0
        keys = ", ".join(f"{k}=?" for k in fields)
        cur = self.conn.execute(f"UPDATE deck SET {keys}", tuple(fields.values()))
        self.conn.commit()
        return cur.rowcount

    def delete_deck(self, deck_id):
        self.conn.execute("DELETE FROM deck WHERE id=?", (deck_id,))
        self.conn.commit()

    def deck_params(self, deck_row):
        raw = deck_row["params"] if deck_row else None
        try:
            p = json.loads(raw) if raw else list(DEFAULT_PARAMS)
            if len(p) < 17:
                p = list(DEFAULT_PARAMS)
            return [float(x) for x in p[:17]]
        except Exception:
            return list(DEFAULT_PARAMS)

    # --------------------------------------------------------------- items
    def add_item(self, deck_id, prompt, answer, explanation="", source="",
                 tags="", reverse=False):
        cur = self.conn.execute(
            "INSERT INTO item(deck_id,prompt,answer,explanation,source,tags,created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (deck_id, prompt.strip(), answer.strip(), explanation.strip(),
             source.strip(), tags.strip(), now()))
        item_id = cur.lastrowid
        self.conn.execute("INSERT INTO card(item_id,ordinal,state,due) VALUES(?,0,'new',0)",
                          (item_id,))
        if reverse:
            self.conn.execute("INSERT INTO card(item_id,ordinal,state,due) VALUES(?,1,'new',0)",
                              (item_id,))
        self.conn.commit()
        return item_id

    def update_item(self, item_id, **fields):
        allowed = {k: v for k, v in fields.items()
                   if k in ("prompt", "answer", "explanation", "source", "tags",
                            "deck_id", "suspended")}
        if not allowed:
            return
        keys = ", ".join(f"{k}=?" for k in allowed)
        self.conn.execute(f"UPDATE item SET {keys} WHERE id=?",
                          (*allowed.values(), item_id))
        self.conn.commit()

    def delete_item(self, item_id):
        self.conn.execute("DELETE FROM item WHERE id=?", (item_id,))
        self.conn.commit()

    def item(self, item_id):
        return self.conn.execute("SELECT * FROM item WHERE id=?", (item_id,)).fetchone()

    def items(self, deck_id=None, search=""):
        sql = ("SELECT i.*, c.id AS card_id, c.state, c.due, c.lapses, c.stability, "
               "d.name AS deck_name FROM item i "
               "JOIN card c ON c.item_id=i.id AND c.ordinal=0 "
               "JOIN deck d ON d.id=i.deck_id WHERE 1=1 ")
        args = []
        if deck_id:
            sql += "AND i.deck_id=? "
            args.append(deck_id)
        if search:
            sql += ("AND (i.prompt LIKE ? OR i.answer LIKE ? OR i.tags LIKE ? "
                    "OR i.source LIKE ?) ")
            like = f"%{search}%"
            args += [like, like, like, like]
        sql += "ORDER BY i.id DESC"
        return self.conn.execute(sql, args).fetchall()

    def item_exists(self, prompt, answer):
        row = self.conn.execute(
            "SELECT 1 FROM item WHERE lower(trim(prompt))=lower(trim(?)) "
            "AND lower(trim(answer))=lower(trim(?)) LIMIT 1",
            (prompt, answer)).fetchone()
        return row is not None

    # --------------------------------------------------------------- cards
    def card(self, card_id):
        return self.conn.execute(
            "SELECT c.*, i.prompt, i.answer, i.explanation, i.source, i.tags, "
            "i.deck_id, i.suspended AS item_suspended, d.name AS deck_name "
            "FROM card c JOIN item i ON i.id=c.item_id JOIN deck d ON d.id=i.deck_id "
            "WHERE c.id=?", (card_id,)).fetchone()

    def card_ids_for_item(self, item_id):
        return [r["id"] for r in self.conn.execute(
            "SELECT id FROM card WHERE item_id=? ORDER BY ordinal", (item_id,))]

    def counts(self, deck_id=None):
        """Queue counts for the study screen."""
        t = now()
        args = []
        where = ""
        if deck_id:
            where = " AND i.deck_id=? "
            args = [deck_id]
        q = lambda sql, a: self.conn.execute(sql, a).fetchone()[0]
        due = q("SELECT COUNT(*) FROM card c JOIN item i ON i.id=c.item_id "
                "WHERE c.suspended=0 AND i.suspended=0 AND c.state IN ('review','relearning') "
                "AND c.due<=?" + where, [t] + args)
        learning = q("SELECT COUNT(*) FROM card c JOIN item i ON i.id=c.item_id "
                     "WHERE c.suspended=0 AND i.suspended=0 AND c.state IN "
                     "('learning','relearning') AND c.due<=?" + where,
                     [t] + args)
        new_left = q("SELECT COUNT(*) FROM card c JOIN item i ON i.id=c.item_id "
                     "WHERE c.suspended=0 AND i.suspended=0 AND c.state='new'" + where, args)
        return {"due": due, "learning": learning, "new": new_left}

    def next_card(self, deck_id=None):
        """The card to show now.

        Order, like Anki: learning cards that are really due, then the most
        overdue review card, then a new card. A card that is still inside its
        learning step is only pulled early (LEARN_AHEAD) when nothing else is
        waiting - otherwise the card you just graded would come straight back.
        """
        t = now()
        where, args = "", []
        if deck_id:
            where = " AND i.deck_id=? "
            args = [deck_id]
        base = ("SELECT c.id FROM card c JOIN item i ON i.id=c.item_id "
                "WHERE c.suspended=0 AND i.suspended=0 ")

        def pick(cond, params):
            row = self.conn.execute(
                base + cond + where + " ORDER BY c.due LIMIT 1",
                list(params) + args).fetchone()
            return self.card(row["id"]) if row else None

        LEARN = "AND c.state IN ('learning','relearning') AND c.due<=?"

        card = pick(LEARN, [t])
        if card:
            return card

        card = pick("AND c.state='review' AND c.due<=?", [t])
        if card:
            return card

        # a new card, only if today's allowance is not used up
        if deck_id:
            deck = self.deck(deck_id)
        else:
            row = self.conn.execute(
                "SELECT id FROM deck ORDER BY sort_order LIMIT 1").fetchone()
            deck = self.deck(row["id"]) if row else None
        if deck and self.new_remaining(deck) > 0:
            row = self.conn.execute(
                base + "AND c.state='new'" + where + " ORDER BY c.id LIMIT 1",
                args).fetchone()
            if row:
                return self.card(row["id"])

        # nothing else left: show a learning card that is due within LEARN_AHEAD
        return pick(LEARN, [t + LEARN_AHEAD])

    def next_due(self, deck_id=None):
        """When is the next card due (seconds from now)? None if nothing is scheduled."""
        sql = ("SELECT MIN(c.due) d FROM card c JOIN item i ON i.id=c.item_id "
               "WHERE c.suspended=0 AND i.suspended=0 AND c.state!='new'")
        args = []
        if deck_id:
            sql += " AND i.deck_id=?"
            args.append(deck_id)
        row = self.conn.execute(sql, args).fetchone()
        if not row or row["d"] is None:
            return None
        return max(0.0, row["d"] - now())

    def new_remaining(self, deck_row):
        if not deck_row:
            return 0
        start = day_start()
        used = self.conn.execute(
            "SELECT COUNT(*) FROM card WHERE introduced_at>=?", (start,)).fetchone()[0]
        return max(0, (deck_row["new_per_day"] or 0) - used)

    def reviews_done_today(self):
        return self.conn.execute(
            "SELECT COUNT(*) FROM review WHERE ts>=?", (day_start(),)).fetchone()[0]

    def save_card(self, card_id, **fields):
        keys = ", ".join(f"{k}=?" for k in fields)
        self.conn.execute(f"UPDATE card SET {keys} WHERE id=?",
                          (*fields.values(), card_id))
        self.conn.commit()

    def log_review(self, before, grade, elapsed_days, scheduled_days, took_ms):
        cur = self.conn.execute(
            "INSERT INTO review(card_id,ts,grade,elapsed_days,scheduled_days,took_ms,"
            "prev_state,prev_due,prev_stability,prev_difficulty,prev_step,prev_lapses,"
            "prev_reps,prev_introduced_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (before["id"], now(), grade, elapsed_days, scheduled_days, took_ms,
             before["state"], before["due"], before["stability"], before["difficulty"],
             before["step"], before["lapses"], before["reps"],
             before.get("introduced_at")))
        self.conn.commit()
        return cur.lastrowid

    def undo_last_review(self):
        row = self.conn.execute(
            "SELECT * FROM review ORDER BY id DESC LIMIT 1").fetchone()
        if not row:
            return None
        self.conn.execute(
            "UPDATE card SET state=?, due=?, stability=?, difficulty=?, step=?, lapses=?, "
            "reps=?, introduced_at=? WHERE id=?",
            (row["prev_state"], row["prev_due"], row["prev_stability"],
             row["prev_difficulty"], row["prev_step"], row["prev_lapses"],
             max(0, (row["prev_reps"] or 0)), row["prev_introduced_at"], row["card_id"]))
        self.conn.execute("DELETE FROM review WHERE id=?", (row["id"],))
        self.conn.commit()
        return row["card_id"]

    # --------------------------------------------------------------- reset
    def _reset_cards(self, where, args=(), forget_history=True):
        """Back to brand new: no schedule, no history. Returns how many cards."""
        ids = [r["id"] for r in self.conn.execute(
            "SELECT c.id FROM card c JOIN item i ON i.id=c.item_id WHERE " + where, args)]
        if not ids:
            return 0
        marks = ",".join("?" * len(ids))
        if forget_history:
            self.conn.execute(f"DELETE FROM review WHERE card_id IN ({marks})", ids)
        self.conn.execute(
            "UPDATE card SET state='new', due=0, stability=NULL, difficulty=NULL, "
            "last_review=NULL, lapses=0, reps=0, step=0, introduced_at=NULL "
            f"WHERE id IN ({marks})", ids)
        self.conn.commit()
        return len(ids)

    def reset_card(self, card_id, forget_history=True):
        return self._reset_cards("c.id=?", (card_id,), forget_history)

    def reset_item(self, item_id, forget_history=True):
        """Both directions of one item (forward and reverse) go back to new."""
        return self._reset_cards("i.id=?", (item_id,), forget_history)

    def reset_deck(self, deck_id, forget_history=True):
        return self._reset_cards("i.deck_id=?", (deck_id,), forget_history)

    def reset_all(self, forget_history=True):
        return self._reset_cards("1=1", (), forget_history)

    def review_count(self, deck_id=None):
        sql = "SELECT COUNT(*) FROM review r JOIN card c ON c.id=r.card_id "
        sql += "JOIN item i ON i.id=c.item_id WHERE 1=1"
        args = []
        if deck_id:
            sql += " AND i.deck_id=?"
            args.append(deck_id)
        return self.conn.execute(sql, args).fetchone()[0]

    # --------------------------------------------------------------- stats
    def state_counts(self, deck_id=None):
        sql = ("SELECT c.state, COUNT(*) n FROM card c JOIN item i ON i.id=c.item_id "
               "WHERE c.suspended=0 AND i.suspended=0 ")
        args = []
        if deck_id:
            sql += "AND i.deck_id=? "
            args.append(deck_id)
        sql += "GROUP BY c.state"
        return {r["state"]: r["n"] for r in self.conn.execute(sql, args)}

    def total_cards(self, deck_id=None):
        sql = "SELECT COUNT(*) FROM card c JOIN item i ON i.id=c.item_id WHERE 1=1 "
        args = []
        if deck_id:
            sql += "AND i.deck_id=? "
            args.append(deck_id)
        return self.conn.execute(sql, args).fetchone()[0]

    def mature_cards(self, deck_id=None):
        sql = ("SELECT COUNT(*) FROM card c JOIN item i ON i.id=c.item_id "
               "WHERE c.state='review' AND c.stability>=21 ")
        args = []
        if deck_id:
            sql += "AND i.deck_id=? "
            args.append(deck_id)
        return self.conn.execute(sql, args).fetchone()[0]

    def retention(self, days=30, mature_only=False):
        since = now() - days * 86400
        sql = ("SELECT COUNT(*) n, SUM(CASE WHEN grade>1 THEN 1 ELSE 0 END) ok "
               "FROM review r JOIN card c ON c.id=r.card_id WHERE r.ts>=?")
        if mature_only:
            sql += " AND c.stability>=21"
        row = self.conn.execute(sql, (since,)).fetchone()
        if not row or not row["n"]:
            return None
        return (row["ok"] or 0) / row["n"]

    def reviews_today(self):
        row = self.conn.execute(
            "SELECT COUNT(*) n, COALESCE(SUM(took_ms),0) ms FROM review WHERE ts>=?",
            (day_start(),)).fetchone()
        return row["n"], (row["ms"] or 0) / 1000.0

    def streak_days(self):
        rows = self.conn.execute(
            "SELECT DISTINCT date(ts,'unixepoch','localtime') d FROM review ORDER BY d DESC"
        ).fetchall()
        if not rows:
            return 0
        streak, cursor = 0, date.today()
        days = {r["d"] for r in rows}
        while cursor.isoformat() in days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def forecast(self, days=30, deck_id=None):
        start = day_start()
        out = [0] * days
        sql = ("SELECT c.due FROM card c JOIN item i ON i.id=c.item_id "
               "WHERE c.suspended=0 AND i.suspended=0 AND c.state IN ('review','relearning')")
        args = []
        if deck_id:
            sql += " AND i.deck_id=?"
            args.append(deck_id)
        for r in self.conn.execute(sql, args):
            d = int(((r["due"] or 0) - start) // 86400)
            if d < 0:
                d = 0
            if d < days:
                out[d] += 1
        return out

    def heatmap(self, weeks=17):
        """Review counts per day for the last `weeks` weeks (columns = weeks)."""
        today = date.today()
        start = today - timedelta(days=today.weekday() + 7 * (weeks - 1))
        rows = self.conn.execute(
            "SELECT date(ts,'unixepoch','localtime') d, COUNT(*) n FROM review "
            "WHERE ts>=? GROUP BY d", (datetime.combine(start, datetime.min.time()).timestamp(),)
        ).fetchall()
        counts = {r["d"]: r["n"] for r in rows}
        grid = []
        for w in range(weeks):
            col = []
            for dow in range(7):
                day = start + timedelta(days=w * 7 + dow)
                if day > today:
                    col.append(None)
                else:
                    col.append(counts.get(day.isoformat(), 0))
            grid.append(col)
        return grid, start

    def backup(self, target_path):
        dest = sqlite3.connect(target_path)
        with dest:
            self.conn.backup(dest)
        dest.close()

    def close(self):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception:
            pass
