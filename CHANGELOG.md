# v0.3.0

- Remove python 3.9 and 3.10 support
  - The older versions were giving errors with `typing`.
- Major refactor of how statements are managed.
  - Added `statements.py`.
  - Added support for multiple statement directories.
  - Backwards INCOMPATIBLE change: removed default statement directory.
    - This means every account that relied on that default had to be updated.
- Start using `dataclasses` more.
  - Biggest place is reading the various `index.yaml` files.
- Add `isort`
- Add `CHANGELOG.md`
  - Did NOT add changes from older versions.
- Add minimum coverage number (39%).
  - This reflects the current number. (Don't want to "fall backwards".)


# Older Versions

For older versions, refer to the `tag` annotations.

(I can add those older annotations to this file, if someone asks.)
