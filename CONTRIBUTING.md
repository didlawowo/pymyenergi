# Development and CI

The fork uses `didlawowo/workflow-ci` **v1.18.3**. Runtime changes and fixes to
myenergi commands are reviewed separately from this CI integration.

## Local checks

Use Python 3.12 for development. The library's existing published Python
requirement is preserved; this does not add a claim that older interpreters
have been tested. The CI matrix remains Python 3.9, 3.12 and 3.13.

```sh
uv sync --group dev
uv run pre-commit install --hook-type pre-commit --hook-type pre-push --install-hooks
uv run pre-commit run --all-files --show-diff-on-failure
uv run pytest tests -q --timeout=9
uv run python -m build
uv run twine check --strict dist/*
```

Commit-time checks cover YAML, Python syntax, Ruff lint/format and MyPy on the
library. Pre-push runs the full test suite. Tests prohibit network sockets
except Unix sockets used by the asynchronous event loop. Do not use real hub
credentials or issue physical device commands in CI.

The old `requirements_dev.txt` and `requirements_test.txt` files remain as
upstream history; the fork's primary developer environment is the `dev` group
in `pyproject.toml`. Compatibility jobs resolve tools for their interpreter.
A `uv.lock` must be generated from the configured package proxy, not fabricated.
The shared workflow supports the initial unlocked project and uses frozen
synchronization once a real lockfile is committed.

## CI configuration

`tests.yaml` calls the shared CI workflow for tests, coverage, quality/security,
mutation policy and trusted evidence. It also checks the local pre-commit
contract, the two other interpreters and wheel/source-distribution builds.
Docker and deployment are not enabled.

Configure the repository variable `RUNNER` to an available runner label, or
provision the standard `arc-runner-pymyenergi` pool. The central mutation runner
uses `UNTRUSTED_RUNNER`, then `RUNNER`, then that same repository-specific pool.
Runner package indexes come from infrastructure; no registry endpoint or
production credential is embedded in this repository.

SonarQube is activated centrally only when `SONAR_ENABLED=true` and the
repository's `SONAR_PROJECT_KEY` and Sonar secrets have been provisioned. Only
those two optional Sonar secrets are passed to the shared workflow; there is
no blanket `secrets: inherit`.

The central Python coverage threshold is retained. Its first successful push
to `main` records `.ci/coverage-main.json`; subsequent PRs compare with the base
branch baseline. Do not invent baseline values or lower gates to hide findings.
Mutation policy uses the normal complexity labels and central defaults.

`trusted-policy-integrity.yml` is verification-only and never executes PR code
under `pull_request_target`. GitHub starts that workflow after it exists on the
base branch; it cannot validate its own bootstrap PR from the new head file.

No domain-specific hidden evaluator is claimed for pymyenergi. Such an evaluator
must be implemented and qualified against the myenergi API contract before it
can supply meaningful evidence.
