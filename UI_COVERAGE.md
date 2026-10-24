# UI coverage

The `ui-coverage-tool` configuration is tracked in `ui_coverage_config.yaml`.
It is shared by local runs and GitHub Actions; no additional GitHub secrets are
required. The existing application URL and test-user settings are still needed.

## Local run

Use Python 3.11 or 3.12 with the pinned dependencies (GitHub Actions uses 3.11).
From the repository root, with that virtual environment activated:

```shell
python -m pip install -r requirements.txt
python -m playwright install chromium
ui-coverage-tool clear-results
python -m pytest -m regression --numprocesses 2
ui-coverage-tool save-report
```

Run the last command even when pytest reports a failure. Open `coverage.html`
to inspect the result. Keep `coverage-history.json` between runs: generating the
next report appends a history entry. `clear-results` removes raw action files,
not the accumulated history.

The test application already embeds the coverage agent needed for iframe
highlighting. In the report, navigate to the page to inspect and refresh the
overlay. This measures recorded UI actions and assertions, not application code
coverage or completeness of business requirements.

## GitHub Actions

The `UI tests` workflow runs regression tests, restores the previous coverage
history, generates the report even if tests fail, and uploads `coverage-report`:

- `coverage.html`: interactive report;
- `coverage-report.json`: collected selectors, action statistics, and history;
- `coverage-history.json`: history used by the next run.

Only runs on `main` save history to the shared cache. Cache keys include the run
ID and attempt number, so rerunning a workflow can save updated history too.
Workflow concurrency serializes runs for the same ref to reduce lost history
updates. GitHub caches can be evicted, so download the history artifact if you
need a permanent copy.

Run the workflow twice on `main`, download the second `coverage-report` artifact,
and check the History section. Both runs should be present. The existing Allure
report remains available through its own artifact and Pages publishing job.

## Element integration checks

```shell
python -m pytest tests/coverage --quiet
```

These checks use local HTML to verify button states, input and textarea actions,
indexed selectors, and the absence of coverage records for a failed action.
