# agent-workspace

This repository is the AI assistant's **only writable place on GitHub**.
Everything that has to be uploaded to GitHub from the assistant's sandbox goes here,
because the access token behind the sandbox is scoped to this one repository.

Think of it as **repos inside a repo**: one folder per project, each folder shaped like
its own little repository.

Last updated: 2026-11-06

---

## 1. What this repo is for

- A single home for every GitHub project we build together.
- A place where the assistant can actually write: create files, commit, push.
- One predictable structure, so it stays readable when there are 5, 20 or 50 projects.

## 2. What the assistant learned about its permissions

The sandbox reaches GitHub through a token that is wired in outside the sandbox. Its
permissions were probed endpoint by endpoint on 2026-11-06:

| Area | Result |
| --- | --- |
| `agent-workspace` contents (read + write) | **allowed** — API upload (201) and real `git push` both work |
| `agent-workspace` repo settings, branches | **allowed** (admin/maintain/push/triage/pull all true) |
| Reading other repos (e.g. `Scratchpad`) | allowed (repo info, contents, branches, commits, issues, PRs) |
| Writing to any **other** repo | **denied** (403) |
| Creating a new repository | **denied** (403) |
| Creating issues / pull requests | **denied** (403) |
| Creating gists | **denied** (403) |
| Reading `/user/emails`, `/notifications`, repo `/collaborators` | denied (403) |

**Consequences:**

1. There is exactly one place to upload to, and this is it. No new repos can be created.
2. No issues, no pull requests, no gists — files and commits only.
3. Anything that would normally be "one repo per project" becomes **one folder per project**
   in this repo. Hence the structure below.
4. This repo is **public**, so everything uploaded here is visible to anyone. No secrets,
   no keys, no private data — ever.

## 3. Structure

```
agent-workspace/
├── README.md              <- this file: rules + index of projects
├── hello-world/           <- one folder per project
│   ├── README.md          <- what the project is, how to run it
│   └── hello.py
└── <next-project>/
    ├── README.md
    └── ...
```

Rules for the layout:

- **One folder per project**, at the root. The folder name is the project name.
- Folder names: lowercase, words separated by `-` (e.g. `scraper-tools`, `ml-notes`).
- Every project folder gets its own `README.md`: what it is, how to run it, state.
- Keep a project's files inside its folder. No loose files at the root except `README.md`.
- A project that outgrows a folder can be split out into its own repository later — by the
  user, since the assistant cannot create repositories. The folder then gets a pointer line
  to the new location.

## 4. Index of projects

| Project | What it is | Path |
| --- | --- | --- |
| hello-world | The first test upload: a minimal Python hello world script | [`hello-world/`](hello-world/) |

Keep this table up to date whenever a project is added.

## 5. How uploads happen

Two ways, both from inside the sandbox:

- **git** (preferred for several files):
  `git clone https://github.com/Heuristic-Analyst/agent-workspace && ... && git push`
- **Contents API** (fine for one file):
  `PUT http://127.0.0.1:8484/api/repos/Heuristic-Analyst/agent-workspace/contents/<path>`

Commit messages: short, imperative, one line ("Add hello world script").

## 6. Rules

- Never upload secrets, keys, passwords or `.env` files.
- Ask the user before uploading anything that should not be public.
- Keep this README's project index in sync with the folders that actually exist.
