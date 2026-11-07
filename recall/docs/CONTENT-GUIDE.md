# Turning your material into cards

This is the workflow for the part that is not software: taking notes, lecture material or
revision material and producing cards worth reviewing.

## What to send

Anything readable as text or PDF works:

- lecture notes, summaries, your own writing
- slide decks (PDF/PPT), presentation handouts
- revision sheets, past papers, mark schemes
- textbook chapters (or the specific pages)
- a syllabus plus a list of topics you keep getting wrong

If you can, add: **the exam date**, **how much time you have per day**, and **which parts you already
know**. Those three change what is worth making cards for.

## What comes back

One `.json` file per deck, ready for the Import screen:

```json
{
  "deck": "Pharmacology — antibiotics",
  "items": [
    {
      "prompt": "Which antibiotic class blocks bacterial cell-wall synthesis?",
      "answer": "Beta-lactams (penicillins, cephalosporins, carbapenems).",
      "explanation": "They inhibit transpeptidase, so peptidoglycan cannot cross-link.",
      "source": "Lecture 7, slide 22",
      "tags": ["antibiotics", "mechanism"]
    }
  ]
}
```

## Rules the cards follow

1. **One fact per card.** If the answer contains "and", the card gets split.
2. **Your own words**, not the slide's wording, wherever the meaning survives the change.
3. **Understanding first.** Definitions are fine, but "why does this happen?" and "what happens if
   this fails?" cards are the ones that transfer to exam questions.
4. **Atomic answers** — answerable in one breath, out loud.
5. **Cloze for lists**: instead of one card with five items, five cards each hiding one item, or an
   ordered enumeration card.
6. **Discrimination built in**: for things that are easy to confuse (two drugs, two eras, two
   formulas), each card carries the detail that separates it from its neighbour.
7. **Nothing trivial.** If you would never need it outside the exam, and the exam is tomorrow,
   it does not get a card.
8. **Source on every card** (slide number, page) so a wrong card can be traced and fixed.

## How the material is organised

- One deck per subject or exam (e.g. "Biology — membranes", "Statistics — exam 2").
- Tags carry the finer structure: chapter, lecture, or question type.
- The most examinable material gets the *most* cards — coverage follows expected marks, not page
  count.
- Cards you already know from elsewhere are flagged as duplicates and skipped.

## In the app

1. **Import** → *Choose file* → pick the JSON.
2. Check the preview: it shows how many are new and how many already exist.
3. Pick the deck (or type a new name), press **Import cards**.
4. **Study** daily. Sessions of 10–20 minutes are enough; the schedule does the rest.
5. **Stats** after a week: retention between 85% and 90% is the target band. Lower means intervals
   are too long or cards are too big — tell me and the cards get rewritten.

## Sending corrections

If a card is wrong or useless, say which ones (prompt text is enough). They get rewritten or
deleted and re-imported; review history for unchanged cards is preserved.
