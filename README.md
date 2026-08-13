# Trackr Watcher

Checks the Germany Finance, Hong Kong Finance, and UK Finance summer
internship boards on [the-trackr.com](https://the-trackr.com) every 15
minutes, and sends you a Telegram message whenever a programme's Opening
Date or Closing Date changes.

Runs entirely on GitHub Actions — no computer needs to stay on.

## One-time setup

1. **Create a GitHub repo.** Go to github.com, click "New repository", give
   it any name (e.g. `trackr-watcher`), keep it **private**, and create it
   with no README/gitignore (we already have our own files).

2. **Upload these files.** Easiest way: on the new repo's page, click
   "uploading an existing file" and drag in this whole `trackr-watcher`
   folder's contents (`check_trackr.py`, `state.json`, `README.md`, and the
   `.github/workflows/watch.yml` file — make sure the `.github/workflows`
   folder structure is preserved). Commit directly to `main`.

   Alternatively, from a terminal in this folder:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/trackr-watcher.git
   git push -u origin main
   ```

3. **Add your Telegram secrets.** In the repo, go to
   Settings -> Secrets and variables -> Actions -> "New repository secret",
   and add two secrets:
   - `TELEGRAM_BOT_TOKEN` — your bot token from @BotFather
   - `TELEGRAM_CHAT_ID` — your Telegram chat ID

4. **Enable Actions.** Go to the "Actions" tab of the repo and enable
   workflows if prompted. You should see "Watch Trackr boards" listed.

5. **First run.** The workflow runs automatically every 15 minutes, or you
   can trigger it immediately: Actions tab -> "Watch Trackr boards" ->
   "Run workflow".

   Heads up: the very first run just records the current state of every
   programme as the baseline — it won't message you about programmes that
   already have opening dates. From then on, you'll get a Telegram message
   any time an Opening Date or Closing Date changes on any of the three
   boards.

## Adding more boards later

Edit the `BOARDS` list at the top of `check_trackr.py`. Each entry needs a
`label`, `region`, and `industry` matching what the-trackr.com's API
expects — you can find these by opening the board's page, opening browser
dev tools -> Network tab, and looking at the request to
`api.the-trackr.com/programmes?...`.

## Adjusting the check frequency

Edit the `cron` line in `.github/workflows/watch.yml`. GitHub's minimum
granularity is 1 minute but scheduled runs can be delayed under load,
especially at very short intervals — 15 minutes is a reliable default.
