# Import formats

The Import screen reads one file at a time and shows a preview before saving anything.
Duplicates (same prompt *and* answer, ignoring case and spacing) are flagged and, by default,
skipped.

## 1. JSON — best when a tool generates the cards

```json
{
  "deck": "Biology — membranes",
  "items": [
    {
      "prompt": "What drives osmosis?",
      "answer": "A water concentration gradient across a semi-permeable membrane.",
      "explanation": "Water moves toward the higher solute concentration.",
      "source": "Lecture 3, slide 12",
      "tags": ["membranes", "transport"]
    }
  ]
}
```

Keys `question`/`front` and `answer`/`back` also work. `explanation`, `source` and `tags` are
optional. A bare list `[{...}, {...}]` without the wrapper is fine too — the deck is then taken
from the file name.

## 2. Markdown or plain text — best for notes

```
# Deck name

Q: What is the minimum information principle?
A: One fact per card. If the answer contains "and", split it.
E: Wozniak's rule 4 — a card that bundles facts is a card you will keep failing.
Tags: card-writing, rules

## Optional section heading becomes a tag for the cards below it

Osmosis :: movement of water across a semi-permeable membrane
```

- `Q:` / `A:` / `E:` (also `Question:`, `Answer:`, `Explanation:`) start the fields.
- `Tags:` and `Source:` apply to the current card.
- One-liners with `::` or `;;` are `prompt :: answer` (optionally `prompt :: answer :: explanation`).
- Lines after `A:` that do not start with a known prefix continue the answer, so multi-line
  answers are fine.

## 3. CSV / TSV — best out of spreadsheets

```csv
prompt,answer,explanation,source,tags
What is homeostasis?,Maintaining a stable internal environment.,,Lecture 1,core
```

A header row is optional. Column order without a header: prompt, answer, explanation, source, tags.
`,` `;` and tabs are all detected.

## What makes a good card

1. One fact per card.
2. Your own words.
3. Short answer — something you could say in one breath.
4. Ask why/how where possible.
5. Keep the source so you can check it again.
