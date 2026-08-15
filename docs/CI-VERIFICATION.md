# CI Verification

This file exists to verify the `pull_request` trigger for the Nova AJ test workflow.

The workflow is configured to run against pull requests targeting `main` and executes:

```text
python -m pytest -q
```

No application behavior is changed by this verification commit.
