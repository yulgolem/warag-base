# Agent guidelines

This repository hosts the **WriterAgents** project.

## Environment setup
- Python 3.10 or newer is required.
- Install dependencies using `pip install -r requirements.txt`.
- Run tests with `PYTHONPATH=. pytest`.

## Coding conventions
- Use four spaces for indentation.
- Keep line length under 88 characters.
- Provide docstrings for all public functions and classes.

## Contribution workflow
- Commit directly to the default branch; do not create new branches.
- After modifying files, run the test suite and ensure it passes.
- Summaries of pull requests must cite relevant file lines using
  `F:path#Lstart(-Lend)?` notation and mention test results.
 
## Limitations
You cannot edit any document in docs/wba_samples/ , they are plain samples
and must stay intact.