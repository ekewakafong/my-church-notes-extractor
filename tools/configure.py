"""Configure a Church Notes Extractor repository from GitHub Actions inputs."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
PROMPTS_DIR = ROOT / "prompts"
NOTES_DIR = ROOT / "notes"

BIBLE_IDS = {
    "NKJV": "114",
    "KJV": "1",
    "NIV": "111",
    "ESV": "59",
    "NLT": "116",
    "NASB": "2692",
    "CSB": "1713",
}


def clean(value: str | None) -> str:
    return (value or "").strip()


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "author"


def unique_slug(name: str, used: set[str]) -> str:
    base = slugify(name)
    slug = base
    number = 2
    while slug in used:
        slug = f"{base}-{number}"
        number += 1
    used.add(slug)
    return slug


def parse_names(primary: str, additional: str) -> list[dict]:
    raw = [primary]
    raw.extend(part.strip() for part in additional.split(",") if part.strip())
    seen_names: set[str] = set()
    used_slugs: set[str] = set()
    authors = []
    for index, name in enumerate(raw):
        key = name.casefold()
        if key in seen_names:
            continue
        seen_names.add(key)
        authors.append(
            {
                "name": name,
                "short_name": name.split()[0],
                "slug": unique_slug(name, used_slugs),
                "primary": index == 0,
            }
        )
    return authors


def write_note_folders(authors: list[dict]) -> None:
    for author in authors:
        base = NOTES_DIR / author["slug"]
        for entry_type in ("service", "devotional", "personal"):
            folder = base / entry_type
            folder.mkdir(parents=True, exist_ok=True)
            (folder / ".gitkeep").write_text("", encoding="utf-8")


def author_question(authors: list[dict]) -> str:
    if len(authors) == 1:
        return f"These notes belong to {authors[0]['short_name']}."
    names = [a["short_name"] for a in authors]
    if len(names) == 2:
        joined = f"{names[0]}'s or {names[1]}'s"
    else:
        joined = ", ".join(f"{n}'s" for n in names[:-1]) + f", or {names[-1]}'s"
    return f"Before processing an uploaded photo, ask: \"Are these {joined} notes?\" Do not continue until the author is confirmed."


def welcome_message(config: dict) -> str:
    authors = config["authors"]
    church = config["church_name"]
    title = config["system_title"]
    short_names = [a["short_name"] for a in authors]

    if len(short_names) == 1:
        author_line = f"- 👤 Keep {short_names[0]}'s notes organized automatically"
        first_step = f"I'll use {short_names[0]} as the note author, determine the note type, format it, check the repository, and guide you through saving it."
    elif len(short_names) == 2:
        author_line = f"- 👤 Keep {short_names[0]}'s and {short_names[1]}'s notes organized separately"
        first_step = f"I'll first ask whether the notes are {short_names[0]}'s or {short_names[1]}'s, then determine the note type, format it, check the repository, and guide you through saving it."
    else:
        names = ", ".join(short_names[:-1]) + f", and {short_names[-1]}"
        author_line = f"- 👤 Keep notes for {names} organized separately"
        first_step = "I'll first ask whose notes they are, then determine the note type, format it, check the repository, and guide you through saving it."

    church_line = f" for **{church}**" if church else ""

    return f'''---
👋 Welcome to the **{title} Notes Extractor!**

I'm here to help you turn handwritten or typed church notes into organized Markdown files and save them directly to your GitHub notes repository{church_line}.

Here's what I can do:
- 📸 Read a photo of handwritten or typed notes
- 📝 Format service, devotional, or personal ministry notes
- 📖 Format Scripture references and Bible links automatically
{author_line}
- 🔍 Check whether a note for that date already exists
- ➕ Append additional notes when they belong with an existing entry
- 📂 Save each note to the correct folder automatically
- 🔗 Give you the direct GitHub link after it is saved
- 🗂️ Let GitHub automatically rebuild your notes index after each push

**To get started, just upload a photo of your notes.**

{first_step}

No technical knowledge is required for normal use.
---'''


def generate_prompt(config: dict) -> str:
    authors = config["authors"]
    author_rows = "\n".join(
        f"- {a['short_name']} → metadata author: {a['name']} → folder slug: `{a['slug']}`"
        for a in authors
    )
    bible_id = config["bible_id"]
    translation = config["bible_translation"]
    welcome = welcome_message(config)

    return f'''# Church Notes Extractor — Project Instructions

You are a Markdown formatter for **{config['system_title']}**.
Repository: `{config['repository']}`

## Project welcome
When the user opens this project, greet them with the following message before anything else:

{welcome}

After the welcome has been shown, follow the instructions below for all note-processing work.

## Authors
{author_rows}

## Author confirmation
{author_question(authors)}

## Workflow
When the user uploads a photo of handwritten or typed church notes:
1. Confirm whose notes they are as required above.
2. Extract all visible note content.
3. Identify the entry type: `service`, `devotional`, or `personal`. If uncertain, ask.
4. Preserve the user's wording and phrasing. Do not add theology or conclusions that are not in the notes.
5. Format a complete Markdown note using the templates below.
6. Check the target file in GitHub before writing.
7. If no file exists, ask: "Shall I push this to your repo?"
8. If the file already exists and is substantially the same, ask whether to overwrite or skip.
9. If the file already exists but the new material is additional, ask whether to append it. If approved, merge the material before the Summary and update metadata.
10. After a successful push, give the repository path and direct GitHub file link. The repository's GitHub Action rebuilds `INDEX.md` automatically.

## Entry types
- `service`: church service notes with a pastor, guest speaker, or other speaker.
- `devotional`: personal Scripture reading, morning/evening devotional, or daily Scriptures.
- `personal`: ministry research, topic studies, planning notes, or other personal ministry material.

## Metadata
Every file starts with exactly one HTML comment:
`<!-- date: YYYY-MM-DD | author: [full author name] | title: [title] | type: [service|devotional|personal] | speaker: [speaker or Holy Spirit for devotionals] | scripture: [primary references] | tags: [comma separated] | summary: [one sentence] -->`

## Service template
<!-- date: YYYY-MM-DD | author: [Author] | title: [Title] | type: service | speaker: [Speaker] | scripture: [refs] | tags: [tags] | summary: [summary] -->

# [Day], [Month] [Day] Service, [Speaker] — [Message Title]

## Offering Scripture
> [scripture text]
[Book Chapter:Verse](https://bible.com/bible/{bible_id}/ref.{translation})

## Message

### [Point heading]
[notes]

> [scripture quote]
[Book Chapter:Verse](https://bible.com/bible/{bible_id}/ref.{translation})

## Summary
- [key takeaway]
- [key takeaway]
- [key takeaway]

## Devotional template
<!-- date: YYYY-MM-DD | author: [Author] | title: [Title] | type: devotional | speaker: Holy Spirit | scripture: [refs] | tags: [tags] | summary: [summary] -->

# [Title]

## Morning 🌄

### [Section heading]
[reflection]

> [scripture quote]
[Book Chapter:Verse](https://bible.com/bible/{bible_id}/ref.{translation})

## Summary
- [key takeaway]
- [key takeaway]
- [key takeaway]

## Personal template
<!-- date: YYYY-MM-DD | author: [Author] | title: [Title] | type: personal | speaker: | scripture: [refs if any] | tags: [tags] | summary: [summary] -->

# [Title]

## Purpose
[purpose]

## Context
[context]

## Notes
[notes]

## Action Items
- [ ] [action]

## Summary
- [key takeaway]
- [key takeaway]
- [key takeaway]

## Formatting rules
- Put Scripture quotations in Markdown blockquotes using `>`.
- Put a bible.com link immediately after every Scripture quotation.
- Default translation: {translation}.
- If a translation is visible in the notes, use that translation instead.
- If the date is visible, use it; otherwise use today's date.
- If a speaker is visible, preserve the speaker name exactly as written.
- For devotionals, always set `speaker: Holy Spirit`.
- Morning notes use `## Morning 🌄`; evening notes use `## Evening 🌄`.
- Keep personal commentary clearly separated from Scripture quotations.
- Include a Summary section with 3–5 bullets.
- Preserve the user's words and phrasing.
- Do not invent missing theology, facts, Scripture quotations, titles, or speaker names.

## File routing
For author folder slug `[author-slug]`:
- service → `notes/[author-slug]/service/[Month]/YYYY-MM-DD.md`
- devotional → `notes/[author-slug]/devotional/[Month]/YYYY-MM-DD.md`
- personal → `notes/[author-slug]/personal/YYYY-MM-DD.md`

`[Month]` is the full English month name, such as `August`.

## Service title rule
When the speaker is known, the visible service title must include the service context and speaker:
`# [Day], [Month] [Day] Service, [Speaker] — [Message Title]`
If there is no separate message title:
`# [Day], [Month] [Day] Service, [Speaker]`
'''


def update_readme(config: dict) -> None:
    readme = ROOT / "README.md"
    title = config["system_title"]
    church = config["church_name"] or "Not specified"
    author_names = ", ".join(a["name"] for a in config["authors"])
    text = f'''# {title}

Your Church Notes Extractor repository is configured and ready for the final ChatGPT connection.

## Configuration

- **Church:** {church}
- **Authors:** {author_names}
- **Default Bible translation:** {config['bible_translation']}

## Start here

Open **`START-HERE.md`** and follow the short final setup checklist.

After that, normal use is simple: open your ChatGPT Project and upload a photo of your notes.

When notes are committed, GitHub Actions automatically regenerates `INDEX.md`.
'''
    readme.write_text(text, encoding="utf-8")


def write_start_here(config: dict) -> None:
    authors = ", ".join(a["name"] for a in config["authors"])
    church = config["church_name"] or "Not specified"
    text = f'''# Start Here — Your Church Notes System Is Ready

Your repository has been personalized successfully.

## Your setup

- **Notes system:** {config['system_title']}
- **Church:** {church}
- **Authors:** {authors}
- **Default Bible translation:** {config['bible_translation']}

## Final ChatGPT setup

- [ ] Open `prompts/chatgpt-project-instructions.md` in this repository.
- [ ] Copy the entire contents of that file.
- [ ] Create a new ChatGPT Project for your church notes.
- [ ] Paste the copied text into the Project instructions.
- [ ] Connect GitHub to ChatGPT and grant access to this repository.
- [ ] Open the Project. You should see your personalized welcome message.
- [ ] Upload a photo of your first church note.

## What happens after setup

For normal use, you do not need to run Python, edit YAML, or manage folders manually.

You upload a note photo in ChatGPT, review the formatted note, approve the GitHub save, and the repository automatically rebuilds `INDEX.md` after the note is pushed.

## Need the full setup details?

See `SETUP.md` for troubleshooting and technical setup information.
'''
    (ROOT / "START-HERE.md").write_text(text, encoding="utf-8")


def main() -> None:
    primary = clean(os.getenv("PRIMARY_NAME"))
    if not primary:
        raise SystemExit("PRIMARY_NAME is required")

    additional = clean(os.getenv("ADDITIONAL_NAMES"))
    church = clean(os.getenv("CHURCH_NAME"))
    translation = clean(os.getenv("BIBLE_TRANSLATION")).upper() or "NKJV"
    title = clean(os.getenv("SYSTEM_TITLE")) or f"{primary.split()[0]}'s Church Notes"
    repository = clean(os.getenv("REPOSITORY")) or "owner/repository"

    authors = parse_names(primary, additional)
    config = {
        "system_title": title,
        "church_name": church,
        "bible_translation": translation,
        "bible_id": BIBLE_IDS.get(translation, BIBLE_IDS["NKJV"]),
        "repository": repository,
        "authors": authors,
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    (CONFIG_DIR / "church-notes.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_note_folders(authors)
    (PROMPTS_DIR / "chatgpt-project-instructions.md").write_text(
        generate_prompt(config), encoding="utf-8"
    )
    update_readme(config)
    write_start_here(config)

    setup_complete = f'''# Setup Complete

Your Church Notes Extractor repository has been personalized.

## What was configured

- System: **{title}**
- Authors: **{', '.join(a['name'] for a in authors)}**
- Church: **{church or 'Not specified'}**
- Default Bible translation: **{translation}**

## Next step

Open **`START-HERE.md`** and complete the short ChatGPT connection checklist.

Your generated ChatGPT instructions already include a personalized welcome message explaining what the system does and how to begin.
'''
    (ROOT / "SETUP-COMPLETE.md").write_text(setup_complete, encoding="utf-8")
    print(f"Configured {title} for {len(authors)} author(s).")


if __name__ == "__main__":
    main()
