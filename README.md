# Workflow Lab — $0 Video Draft Builder

This starter generates a **silent, captioned storyboard video**, not a finished narrated video. It uses Python, Pillow and FFmpeg (preinstalled on GitHub-hosted Ubuntu runners). No paid APIs, subscriptions, or account credentials required.

## Install in GitHub
1. Create a **private** repository called `workflow-lab`.
2. Upload `generate.py`, `topics.json`, `requirements.txt`, and the `.github/workflows/build.yml` file, preserving directories.
3. In GitHub, select **Actions → Build video draft → Run workflow**.
4. After completion, open the run and download `workflow-lab-video-draft` under Artifacts.
5. Inspect the video and metadata before publishing. Do not publish as a finished video until you add narration and verify claims.

The workflow also runs every Monday at 15:00 UTC, subject to GitHub Actions scheduling delays and free-tier limits. It rebuilds the **same first topic** each time; it does not independently research or create new topics. To change the video, edit the first entry in `topics.json`.

## Run locally
`pip install -r requirements.txt` then `python generate.py` (requires FFmpeg on PATH).

## Future upgrades
Add original narration, audio/caption timing, topic queue management, automated claim checks, and YouTube OAuth upload integration. Never place credentials in the repository. Keep publishing approval manual until the pipeline is tested. GitHub Actions free usage and policies can change.
