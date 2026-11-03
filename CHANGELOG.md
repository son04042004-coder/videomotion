# Snapshot 2026-11-03

This is a focused extraction of the current `/videomotion` workflow, not a release of all projects in the original workspace.

Current capabilities retained:
- Two channel styles: k1 yellow/black stickers and k2 white outlined orange/blue stickers, with matching thumbnails.
- Expressive Adam/Vibi voice settings added on 02/11; emotion tags are retained in the API text and removed only for displayed/aligned words.
- Screen captures with text/price boxes, privacy blur regions, cursor clicks, camera zoom, beat cuts, punch effects and scene transitions.
- Motion graphics anchored to spoken words; repeated MG IDs are rejected before rendering.
- 1080×1920/30fps output, subtitles in the TikTok safe area, intentional SFX, thumbnail generation and audio/content/shared-shot QA.
- Skills reflect the owner's 02–03/11 content workflow changes, including four video formats and the separate content checker. These are channel preferences, not a guarantee of platform acceptance.

Packaging changes:
- Included only the required tools, their imported helper modules, font/cursor assets and the two skills.
- Relocated the mask font and default shared-audio paths to the cloned repository.
- Added minimal dependency manifests, setup documentation, original-provider SFX downloading and two reproducible local diagnostic projects.
- Original workspace files were not modified. Excluded private keys, account/browser state, unrelated projects and campaign media.
