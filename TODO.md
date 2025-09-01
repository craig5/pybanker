## Random Todo Items

Infra:

- Convert to pyproject.toml.
- Check for any left over `breakpoints`.
- Add git pre-commit check.
- Auto publish new versions.
- Move away from UserDict/OrderedDict/... and use dataclasses.
- Create test data with new and legacy formats.
- Move to poetry


Data Support:

- Add ability to look at 1 account at a time.
  - E.g. `pybanker show --account foo`
- Add check for up to date "data" dirs.
- Verify "shared accounts" actually exist.
- Add color.
  - Accounts with no errors/warns, show as green.
  - Add "status" to summary output.


Tansactions:

- Validate transactions against data.
- Create summaries of transactions that can compare against data.


Tests:

- Get coverage up to 50%
