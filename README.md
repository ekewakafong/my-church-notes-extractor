# Church Notes Extractor Template

A GitHub + ChatGPT framework for turning handwritten or typed church notes into organized Markdown files with an automatically generated index.

## Designed for nontechnical users

You do **not** need Python, Git, VS Code, or command-line experience to use the finished system.

### Setup overview

1. Click **Use this template** on GitHub and create your own repository.
2. Open the new repository's **Actions** tab.
3. Run **Configure Church Notes System**.
4. Enter your name, optional additional note authors, church name, and Bible translation.
5. The workflow creates your personalized folders, configuration, and ChatGPT instructions.
6. Copy `prompts/chatgpt-project-instructions.md` into a ChatGPT Project.
7. Connect GitHub to ChatGPT and grant access to your new repository.
8. Upload a photo of your notes.

After notes are pushed, GitHub Actions automatically rebuilds `INDEX.md`.

## What the template contains

- `tools/configure.py` — personalizes the repository from the setup form.
- `tools/build-index.py` — generates the searchable Markdown index.
- `.github/workflows/setup.yml` — first-run configuration form and automation.
- `.github/workflows/build-index.yml` — automatic index rebuilding after notes are committed.
- `samples/` — example service, devotional, and personal notes.
- `prompts/` — generated ChatGPT Project instructions.
- `notes/` — personalized note folders created during setup.

## Important GitHub setting

The workflows need permission to commit generated files. If a workflow reports a permissions error, go to:

**Settings → Actions → General → Workflow permissions → Read and write permissions → Save**

Then run the workflow again.

See [SETUP.md](SETUP.md) for the full walkthrough.
