# Manual Minute motion drafts

Six source-reviewed vehicle explainers with original animated illustrations, neural narration, active-word captions and 1080x1920 exports.

Install FFmpeg, DejaVu fonts and Python 3.12, then `pip install -r manual-minute-v2/requirements.txt`. Run `python manual-minute-v2/build.py --topic all` followed by `python manual-minute-v2/quality-check.py --topic all`.

The Manual Minute Motion Drafts GitHub workflow supports manual topic selection. Update-branch pushes render and verify a wiper-service sample. Artifacts expire after seven days. Voice caches and validated renders are reused; partial audio and failed renders are rejected. Online Edge TTS availability is not guaranteed. There is no paid API integration.

Official sources were reviewed October 20, 2026; generation stops when review dates expire. Illustrations are simplified, not exact vehicle screen recordings. Content is source-reviewed, not vehicle-tested. Each new topic needs editorial research and review.

The ready queue records verified render candidates only. This workflow does not upload or schedule YouTube posts. YouTube authorization and a confirmed private upload remain required before automatic publishing.
