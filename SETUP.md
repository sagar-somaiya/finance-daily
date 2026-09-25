# Finance Daily V4 — Python data pipeline setup

This replaces the Cloudflare Worker entirely. No API keys to manage, no
per-day quotas to worry about — a free scheduled job does all the fetching.

## What goes where

Put all of these in the SAME GitHub repository, at the top level (the same
place your `index.html` / `finance-daily-v4.html` lives):

```
your-repo/
├── finance-daily-v4.html      (rename to index.html if it's your homepage)
├── data.json                  (placeholder — gets overwritten automatically)
├── fetch_data.py
├── requirements.txt
└── .github/
    └── workflows/
        └── update-data.yml
```

The `.github/workflows/` folder path matters — GitHub only looks there for
automated jobs. Keep that exact folder structure.

## 1. Create (or use) a GitHub repository
If you don't already have one for this project, go to github.com → New
repository → give it a name → Create. Enable GitHub Pages for it under
Settings → Pages → set source to your main branch.

## 2. Upload the files
Easiest way if you're not comfortable with git commands yet: on your repo's
GitHub page, click "Add file" → "Upload files", drag in all 5 items above
(keeping the `.github/workflows/update-data.yml` path), and commit.

## 3. Test the script once, locally (optional but recommended)
In Command Prompt, inside the folder with these files:
```
pip install -r requirements.txt
python fetch_data.py
```
This should print `Wrote data.json at ...` and update the file. Open
`data.json` in a text editor to sanity-check it has real numbers in it.

## 4. Let GitHub Actions take over
Once the files are in your repo, go to the repo's **Actions** tab on
GitHub. You should see "Update Finance Daily Data" listed. Click it, then
click **"Run workflow"** to trigger it manually the first time (don't wait
30 minutes). After ~30–60 seconds, refresh the tab — you should see a
green checkmark, and `data.json` in your repo will now have real data.

From here on, it re-runs automatically every 30 minutes, forever, for free.

## 5. Open your page
Visit your GitHub Pages URL (something like
`https://yourusername.github.io/your-repo/finance-daily-v4.html`). It reads
`data.json` from the same site — no setup needed on the page's side.

## Troubleshooting
- **Actions tab shows a red X**: click into the failed run to see the error
  log. Most common cause: `requirements.txt` or `fetch_data.py` isn't at the
  repo's top level.
- **Page shows "No data.json yet"**: the workflow hasn't run successfully
  yet, or `data.json` isn't in the same folder as the HTML file.
- **Page shows a stale-data warning**: the scheduled job stopped running —
  check the Actions tab for recent failures. GitHub Actions on free/public
  repos are very reliable, but do occasionally get disabled after long
  periods of repo inactivity — just click "Run workflow" once to reactivate.
