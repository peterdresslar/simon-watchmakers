# my-marimo-app

A [marimo](https://marimo.io) notebook project, managed with [uv](https://docs.astral.sh/uv/).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.13+

## Setup

Create a new repo from this template (click **"Use this template"** on GitHub), then clone and install:

```bash
git clone <your-new-repo-url>
cd <your-new-repo-name>
uv sync
```

Or clone the template directly:

```bash
git clone <template-repo-url>
cd my-marimo-app
uv sync
```

## Run

Edit the notebook interactively:

```bash
uv run marimo edit notebooks/my-notebook.py
```

Run as a read-only app (code hidden, UI elements still interactive):

```bash
uv run marimo run notebooks/my-notebook.py
```

Run as a plain Python script:

```bash
uv run python notebooks/my-notebook.py
```
