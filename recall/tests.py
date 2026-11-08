"""Non-GUI tests: scheduler maths, storage, import/export.  Run: python3 tests.py"""
import json
import os
import tempfile
import time

import importer
from db import DB
from sched import Scheduler, human_delay


def fresh():
    path = os.path.join(tempfile.mkdtemp(), "t.db")
    db = DB(path)
    return db, Scheduler(db)


def add(db, deck_id, prompt="q", answer="a"):
    iid = db.add_item(deck_id, prompt, answer)
    return db.card(db.card_ids_for_item(iid)[0])


def test_new_card_steps():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    assert card["state"] == "new"
    fields, delay, _ = s.grade(card, 3)
    assert fields["state"] == "learning", fields
    assert abs(delay - 10 * 60) < 1, delay          # learning steps are 1m, 10m
    card = db.card(card["id"])
    fields, delay, _ = s.grade(card, 3)
    assert fields["state"] == "review", fields
    assert 3 <= delay / 86400 <= 5, delay / 86400    # S0(Good) = 3.71 d
    print("  new card steps ok")


def test_intervals_grow():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    for _ in range(2):
        _, _, _ = s.grade(db.card(card["id"]), 3)
    seen = []
    for _ in range(6):
        c = db.card(card["id"])
        fields, delay, _ = s.grade(c, 3)
        seen.append(round(delay / 86400))
        # pretend the next review happens exactly when the card comes due
        db.save_card(c["id"], last_review=time.time() - delay)
    assert seen == sorted(seen) and len(set(seen)) == len(seen), seen
    assert seen[-1] > seen[0] * 5, seen
    print("  intervals grow with each Good:", seen)


def test_lapse_reduces_stability():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    for _ in range(2):
        s.grade(db.card(card["id"]), 3)
    before = db.card(card["id"])["stability"]
    fields, delay, _ = s.grade(db.card(card["id"]), 1)
    after = db.card(card["id"])["stability"]
    assert fields["state"] == "relearning"
    assert after < before, (before, after)
    assert abs(delay - 600) < 1, delay
    print(f"  lapse: stability {before:.2f} -> {after:.2f} d, back in 10 min")


def test_easy_graduates_at_once():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    fields, delay, _ = s.grade(card, 4)
    assert fields["state"] == "review"
    assert 11 <= delay / 86400 <= 16, delay / 86400   # S0(Easy) = 13.8 d
    print("  Easy on a new card -> review in", round(delay / 86400), "d")


def test_retention_setting_changes_intervals():
    db, s = fresh()
    deck = db.decks()[0]
    out = {}
    for retention in (0.8, 0.9, 0.95):
        db.update_deck(deck["id"], desired_retention=retention)
        card = add(db, deck["id"], f"q{retention}", "a")
        s.grade(card, 4)
        c = db.card(card["id"])
        out[retention] = s.interval_days(c["stability"], retention)
    assert out[0.8] > out[0.9] > out[0.95], out
    print("  retention 80/90/95% ->", {k: round(v) for k, v in out.items()}, "days")


def test_max_interval_clamped():
    db, s = fresh()
    deck = db.decks()[0]
    db.update_deck(deck["id"], max_interval=30)
    card = add(db, deck["id"])
    s.grade(card, 4)
    for _ in range(8):
        _, delay, _ = s.grade(db.card(card["id"]), 4)
        assert delay / 86400 <= 30.001, delay / 86400
    print("  max interval respected (30 d)")


def test_preview_matches_grade():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    pre = s.preview(card)
    assert set(pre) == {1, 2, 3, 4}
    assert pre[3] == human_delay(10 * 60), pre
    print("  preview labels:", pre)


def test_undo():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    before = dict(db.card(card["id"]))
    s.grade(db.card(card["id"]), 3)
    assert db.card(card["id"])["state"] == "learning"
    cid = db.undo_last_review()
    after = db.card(card["id"])
    assert cid == card["id"]
    assert after["state"] == before["state"] and after["due"] == before["due"]
    assert db.reviews_today()[0] == 0
    print("  undo restores the card exactly")


def test_counts_and_limits():
    db, s = fresh()
    deck = db.decks()[0]
    db.update_deck(deck["id"], new_per_day=2)
    for i in range(5):
        add(db, deck["id"], f"q{i}", "a")
    assert db.counts()["new"] == 5
    shown = 0
    while True:
        c = db.next_card()
        if not c:
            break
        s.grade(c, 3)
        shown += 1
        if shown > 12:
            break
    states = db.state_counts()
    assert states.get("review", 0) <= 2, states   # only 2 new cards allowed today
    print("  daily new-card limit works:", states)


def test_importer_formats():
    md = """# Biology
Q: What is osmosis?
A: Movement of water across a semi-permeable membrane.
E: From low solute to high solute concentration.
Tags: membranes, transport

Q: Which organelle makes ATP?
A: The mitochondrion.

## Genetics

DNA :: deoxyribonucleic acid
"""
    deck, items = importer.parse_md(md)
    assert deck == "Biology", deck
    assert len(items) == 3, items
    assert items[0]["explanation"].startswith("From low")
    assert "membranes" in items[0]["tags"]
    assert items[1]["answer"] == "The mitochondrion."
    assert items[2]["tags"] == "Genetics"

    js = json.dumps({"deck": "Chem", "items": [
        {"prompt": "p1", "answer": "a1"},
        {"question": "p2", "back": "a2", "tags": ["x", "y"]}]})
    deck, items = importer.parse_json(js)
    assert deck == "Chem" and len(items) == 2
    assert items[1]["tags"] == "x, y"

    csv_text = "prompt,answer,explanation\nWhat is 2+2?,4,basic\nCapital of France?,Paris,\n"
    deck, items = importer.parse_csv(csv_text)
    assert len(items) == 2 and items[1]["answer"] == "Paris"
    print("  importer: md, json and csv all parse")


def test_import_dedup_and_roundtrip():
    db, s = fresh()
    deck = db.decks()[0]
    items = [{"prompt": "q1", "answer": "a1", "explanation": "", "source": "", "tags": ""},
             {"prompt": "q2", "answer": "a2", "explanation": "", "source": "", "tags": ""}]
    importer.mark_duplicates(db, items)
    r = importer.import_into(db, deck["id"], items)
    assert r == {"added": 2, "skipped": 0}, r
    items2 = [dict(i) for i in items]
    importer.mark_duplicates(db, items2)
    assert all(i["duplicate"] for i in items2)
    r = importer.import_into(db, deck["id"], items2)
    assert r == {"added": 0, "skipped": 2}, r
    assert db.total_cards() == 2
    print("  duplicates detected, nothing double-added")


def test_review_states():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    s.grade(card, 3); s.grade(db.card(card["id"]), 3)          # graduate
    f, d, _ = s.grade(db.card(card["id"]), 1)                  # lapse
    assert f["state"] == "relearning"
    f, d, _ = s.grade(db.card(card["id"]), 3)                  # pass relearning
    assert f["state"] == "review", f
    print("  review -> lapse -> relearn -> review ok")


def test_reverse_cards():
    db, s = fresh()
    deck = db.decks()[0]
    iid = db.add_item(deck["id"], "front", "back", reverse=True)
    ids = db.card_ids_for_item(iid)
    assert len(ids) == 2
    c0, c1 = db.card(ids[0]), db.card(ids[1])
    assert c0["ordinal"] == 0 and c1["ordinal"] == 1
    print("  reverse cards created")


def test_forecast_and_heatmap():
    db, s = fresh()
    deck = db.decks()[0]
    card = add(db, deck["id"])
    s.grade(card, 4)
    fc = db.forecast(30)
    assert len(fc) == 30 and sum(fc) == 1, fc
    grid, start = db.heatmap()
    assert len(grid) == 17 and all(len(c) == 7 for c in grid)
    print("  forecast + heatmap ok")


def test_graded_card_does_not_come_back_immediately():
    """A card in its learning step must not be shown again before it is due."""
    db, s = fresh()
    deck = db.decks()[0]
    first = add(db, deck["id"], "first", "A")
    add(db, deck["id"], "second", "B")
    for rating in (1, 2, 3):                       # Again, Hard, Good on a new card
        card = db.card(first["id"])
        s.grade(card, rating)
        nxt = db.next_card()
        assert nxt is not None and nxt["id"] != first["id"], (
            f"rating {rating}: the card just graded came straight back")
    # once the step is over it is due again and jumps the queue
    db.conn.execute("UPDATE card SET due=? WHERE id=?", (time.time() - 1, first["id"]))
    db.conn.commit()
    assert db.next_card()["id"] == first["id"]
    print("  a graded learning card stays out until its step is over")


def test_reset_card_deck_and_everything():
    """Reset means: as fresh as imported - no schedule, no history, cards kept."""
    db, s = fresh()
    d1 = db.decks()[0]
    db.add_deck("Second")
    d2 = db.deck_by_name("Second")
    a = add(db, d1["id"], "a", "A")
    b = add(db, d1["id"], "b", "B")
    c = add(db, d2["id"], "c", "C")
    for card in (a, b, c):
        s.grade(db.card(card["id"]), 4)
    assert db.review_count() == 3

    # one card
    assert db.reset_card(a["id"]) == 1
    ca = db.card(a["id"])
    assert ca["state"] == "new" and ca["due"] == 0 and ca["stability"] is None
    assert ca["reps"] == 0 and ca["lapses"] == 0 and ca["introduced_at"] is None
    assert db.review_count() == 2 and db.card(b["id"])["state"] == "review"

    # one deck: its cards only, and the cards themselves stay
    assert db.reset_deck(d1["id"]) == 2
    assert db.card(b["id"])["state"] == "new"
    assert db.card(c["id"])["state"] == "review"
    assert db.review_count() == 1
    assert len(db.items(d1["id"])) == 2 and db.total_cards(d1["id"]) == 2

    # everything: also frees today's new-card allowance
    assert db.reset_all() == 3
    assert db.review_count() == 0
    assert set(db.state_counts()) == {"new"}
    assert db.new_remaining(db.deck(d1["id"])) == 20
    assert db.next_card() is not None
    print("  reset: one card, one deck, everything; history gone, cards kept")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"running {len(tests)} tests")
    for t in tests:
        t()
    print("all tests passed")
