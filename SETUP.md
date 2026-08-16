# Setup Guide

This guide is written for people who do not normally work with GitHub.

## Step 1 — Create your repository

1. On the template repository page, click **Use this template**.
2. Choose **Create a new repository**.
3. Give the repository a name, such as `my-church-notes`.
4. Choose **Private** if you do not want your notes publicly visible.
5. Click **Create repository**.

## Step 2 — Allow the automation to update files

In your new repository:

1. Click **Settings**.
2. Click **Actions**, then **General**.
3. Scroll to **Workflow permissions**.
4. Select **Read and write permissions**.
5. Click **Save**.

## Step 3 — Run the one-time setup

1. Click the **Actions** tab.
2. Click **Configure Church Notes System**.
3. Click **Run workflow**.
4. Fill in:
   - Your name.
   - Other people who will have their own notes, separated by commas. Leave blank if none.
   - Church name, if desired.
   - Default Bible translation.
   - Optional title for the notes system.
5. Click **Run workflow**.
6. Wait for the run to show a green check mark.

The workflow creates personalized author folders, writes `config/church-notes.json`, generates ChatGPT instructions, and updates the repository README.

## Step 4 — Connect ChatGPT

1. Open `prompts/chatgpt-project-instructions.md` in your repository.
2. Copy the entire file.
3. Create a new ChatGPT Project for your church notes.
4. Paste the copied text into the Project instructions.
5. Connect your GitHub account to ChatGPT.
6. Grant ChatGPT access to this repository.

GitHub authorization must be performed by the repository owner; the setup workflow cannot authorize another service on the user's behalf.

## Step 5 — Test the system

1. Open the ChatGPT Project.
2. Upload a photo of a devotional, service, or personal ministry note.
3. Confirm the author and entry type when asked.
4. Review the generated Markdown.
5. Approve the GitHub push.

The note will be saved under the appropriate personalized `notes/` folder.

## Step 6 — Automatic indexing

Whenever a note is committed under `notes/`, the **Rebuild Notes Index** workflow runs automatically. It executes:

`python tools/build-index.py`

If `INDEX.md` changes, the workflow commits the new index back to the repository.

## Need to change names later?

Run **Configure Church Notes System** again with the new values. Existing note files are not deleted. New personalized folders and instructions are generated from the latest setup values.
