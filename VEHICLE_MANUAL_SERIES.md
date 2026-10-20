# Manual Minute — vehicle owner-manual video series

Working series name; no new YouTube channel has been created or selected. This is an isolated draft pipeline in the existing repository. The AI/productivity queue and publishing settings remain separate.

## Current deliverables

Three original, AI-assisted scripts paraphrase official manufacturer instructions: 2020–2024 North America Tesla Model Y USB capabilities; the same Model Y family's Screen Clean Mode; and US 2024 Ford F-150 Global Opening, when supported and enabled. Sources were reviewed October 20, 2026. These are source-reviewed summaries, not demonstrations tested in the vehicles.

Each video description and source-review file records vehicle, model-year range, market, equipment qualifiers, official source URL, manual edition, and review date. Original text layouts and offline synthetic narration avoid copying manufacturer manual pages, illustrations, logos, or footage. Narration uses espeak-ng; output is 720×1280 H.264/AAC.

## Run and review

Actions → Vehicle Manual Shorts - Drafts → Run workflow. The default renders all three examples. Each output contains the video, scene script, YouTube metadata, and source-review record. The wrapper cannot upload videos and receives no OAuth secrets. A separate vehicle upload ledger is reserved for a later private-upload integration.

Review the spoken instructions, caption timing, and vehicle applicability before approving any upload. Sources expire after no more than 30 days and require genuine rechecking; never merely update dates. The gate checks source host, metadata, review dates, and declared editorial category; it cannot fact-check a script or prove a vehicle feature is present. Do not automatically generate unreviewed facts from arbitrary manual pages.

## Cadence and publication

Tuesday/Friday recurring draft builds are prepared but disabled unless VEHICLE_DRAFT_SCHEDULE_ENABLED is explicitly set to true. An approved finite queue is a starting library, not unlimited content production. No upload or public schedule is enabled. A destination channel, owner authorization, private upload test, and launch approval are still required. Do not reuse the Workflow Lab YouTube token for a different channel without verifying the destination.

## Editorial boundaries

Focus on stationary convenience features, infotainment, storage, personalization, and non-invasive owner checks. Exclude safety-system bypasses, driver-assistance hacks, high-voltage work, repairs, jacking, emergency procedures, towing limits, brake work, and diagnosing warning lights from unattended publication. Keep material cautions and equipment qualifiers. Do not imply manufacturer endorsement or monetization guarantees. More distinct scripts and better custom explanatory visuals should be developed before a channel launch.
