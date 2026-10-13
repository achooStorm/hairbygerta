# Licensing check

Result: **PASS** (exit code 0)

- Checked: the files in the site folder
- When: 2026-10-13 07:40:16
- Script: qa/licensing_check.py, data: qa/reports/licensing.json

## Files hashed (SHA-256)

| Side | Files | Archive members | Also |
|---|---|---|---|
| Site | 314 | 0 | 0 embedded pictures, 0 git objects |
| Restricted folder | 85 | 103 | 14 text members of old archives left out, 90 Wix reference screenshots |

Different restricted hashes a site file was compared with: 150

## Images by class

| Class | Files |
|---|---|
| allowed | 3 |
| allowed-derivative | 9 |
| placeholder | 52 |
| owner-photo | 0 |
| site screenshot | 178 |
| svg for review | 0 |
| placeholder that fails the test | 0 |
| owner-photo that is not accepted | 0 |
| UNKNOWN | 0 |

## Matches (zero expected)

None.

## Failures

None.

## All checks of this run

| Page | Check | Result | Found |
|---|---|---|---|
| site | manifest | ok | 64 files recorded |
| site | restricted_folder | ok | 85 files and 103 archive members hashed, 14 text members of old archives left out, 150 different hashes to compare |
| site | gitignore_rules | ok | all 10 sample paths are ignored |
| site | screenshots_ignored | ok | 178 image files under qa/, 0 would not be ignored |
| site | git_tracked_paths | ok | not applicable: the site folder is not a git repository yet |
| site | git_tracked_images | ok | not applicable: the site folder is not a git repository yet |
| site | git_history | ok | not applicable: the site folder is not a git repository yet |
| site | hash_match | ok | 0 matches |
| site | archives_readable | ok | 0 archives opened |
| site | archive_pictures | ok | 0 pictures in archives, 0 of them neither allowed nor a placeholder |
| site | allowed_images | ok | 3 of 3 verified |
| site | allowed_sources | ok | all verified allowed images are identical to their source |
| site | allowed_derivatives | ok | 9 derivatives, 0 not proven |
| site | placeholders | ok | 52 of 52 pass |
| site | owner_photos | ok | no image is recorded as owner-photo |
| site | unknown_images | ok | 0 UNKNOWN images |
| site | embedded_pictures | ok | 0 embedded pictures |
| site | svg_files | ok | 0 svg files flagged for review, 0 with a picture inside |
| site | manifest_files_present | ok | 64 of 64 there |
| site | site_screenshots | ok | 178 image files under qa/, not for publishing |
| home | page_images | ok | 17 image addresses, 0 not acceptable |
| gallery | page_images | ok | 50 image addresses, 0 not acceptable |
| book-online | page_images | ok | 15 image addresses, 0 not acceptable |
| about | page_images | ok | 13 image addresses, 0 not acceptable |
| contact | page_images | ok | 5 image addresses, 0 not acceptable |
| english-refund-policy | page_images | ok | 5 image addresses, 0 not acceptable |
| accessibility-statement | page_images | ok | 5 image addresses, 0 not acceptable |
| english-privacy-policy | page_images | ok | 5 image addresses, 0 not acceptable |
| terms-conditions | page_images | ok | 5 image addresses, 0 not acceptable |
| 404 | page_images | ok | 4 image addresses, 0 not acceptable |
| site | stylesheet_images | ok | 0 image addresses, 0 not acceptable |
| site | published_forbidden_addresses | ok | not applicable: this run checked the site folder |
| site | published_screenshots | ok | not applicable: this run checked the site folder |

Exit codes: 0 pass, 1 failure, 2 a file identical to a restricted file was found.
