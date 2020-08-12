# Contributing

## Pre-Commit

This repository uses [pre-commit](https://pre-commit.com/).
To install pre-commit,
follow the instructions [here](https://pre-commit.com/#installation),
then run `pre-commit install` in your local repository root.

The pre-commit checks will run automatically before you commit.
You can also run them manually with the command `pre-commit run -a`.


## GitHub Actions

This repository uses GitHub Actions to run CI workflows.
Right now there are two workflows, `pre-commit` and `tests`,
by `.github/workflows/{pre-commit,tests}.yml`.

Each workflow has a `name`,
a set of triggers described by the `on:` section,
and a description of the actual work to do, described by the `jobs:` section.

For the triggers, we use
```yaml
on:
  push:
    branches:
    - master
  pull_request:
```
which says "trigger for pushes to master, and for pull requests".
The "pull request" trigger fires whenever a commit is created on a PR, so
if we did not restrict which branches the "push" trigger fired on,
we would get two triggers per PR commit (and things would get very messy!).

This is the (at one point in time) work description for the `tests` workflow:
```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        platform: [ubuntu-20.04, ubuntu-18.04]
        python-version: [3.5, 3.6, 3.7, 3.8]

    runs-on: ${{ matrix.platform }}

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: python -m pip install htcondor pytest>=6 pytest-cov
    - name: Run tests
      run: pytest --cov --durations=20
    - name: Upload coverage
      uses: codecov/codecov-action@v1

```

`test:` (the second line) is the "job id" and has no actual semantic meaning.
The `strategy` sets up parametric runs of the entire workflow; in this case
we use it to test on multiple platforms, but the syntax is free-form and the
keys/values have no particular meaning (the `platform` values just get fed
into `runs-on`, for example).

The `steps` are the execution steps, in order. Each can have an optional `name`,
and can either run a shell command or use a pre-built "action".
We use a mix; pre-built actions to checkout the git repository itself
and to set up Python, and shell commands to install dependencies and (finally)
run the actual tests.

Full documentation for the syntax of the workflow description file is
[here](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions).
