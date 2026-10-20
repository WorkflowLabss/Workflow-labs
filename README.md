# Workflow Lab — narrated Shorts

Existing Python/Pillow/FFmpeg project upgraded with offline espeak-ng narration, eight original evergreen scripts, vertical 720×1280 video, captions, and a private-only YouTube uploader. No paid model, voice, stock-media, or music API is used.

## Current release gate

Public publishing is deliberately unavailable. Repository write permission for the upload ledger also requires approval before uploads can run. Scheduled builds run Monday and Thursday at 14:17 UTC, but scheduled uploads are disabled until a private end-to-end test succeeds. Manual runs default to generate-only; `upload_private` explicitly requests one private upload.

`YOUTUBE_CREDENTIALS` must be a GitHub Actions secret containing client_id, client_secret, and refresh_token. Never put credential JSON into the repository, logs, or artifacts. The Google OAuth app should leave Testing before issuing the long-lived authorization; Testing refresh tokens for youtube.upload expire after seven days. Production does not make tokens permanent: revocation and other expiry rules still apply.

## Reliability

Topics are fingerprinted and tracked in `publish_state.json`. A reservation is committed before upload. Uncertain uploads block the queue rather than retrying and risking duplicates; reconcile against YouTube Studio before repairing a reservation. Upload receipts record the video ID and privacy. Workflow concurrency prevents overlapping jobs. Checkout uses main so a rerun sees the latest ledger. An exhausted queue stops rather than repeating videos.

The queue is finite, original, AI-assisted, and does not research changing tool claims. Add and review new scripts before exhaustion. This is not unlimited autonomous editorial production. Captions are per scene and narration is synthetic. Watch/listen to the first output before enabling routine publishing.

Jobs have a 15-minute timeout, use standard Linux runners, and retain only final review artifacts for three days. GitHub account spending controls and free-minute/storage allowances must be checked separately; a workflow timeout alone does not guarantee zero charges. Do not enable Google Cloud billing. No guarantee of revenue or monetization eligibility is implied.

## Local commands

Install FFmpeg, espeak-ng, and requirements.txt; then run `python generate.py generate`. The reserve and upload commands are intended for the gated Actions workflow. Do not automatically retry an uncertain upload. Keep credentials outside the checkout.
