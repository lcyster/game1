# game1

A small Flask app for tracking plants and fetching plant information/images.

## Requirements

Recommended local setup:

- Nix with flakes enabled
- direnv

Fallback local setup:

- Python 3
- `pip`

## Quick Start With Nix

Enter the development shell:

```bash
nix develop
```

Initialize the database:

```bash
flask --app app.main init-db
```

Start the app:

```bash
flask --app app.main run --debug --host 0.0.0.0
```

Open the app at:

```text
http://127.0.0.1:5000
```

Stop the app with `Ctrl+C` in the terminal where it is running.

## Quick Start With direnv

This repo includes a `.envrc` that loads the Nix development shell and then sources secrets from:

- `~/.env.game1`
- `.env`

Allow direnv for this project:

```bash
direnv allow
```

After that, entering this directory automatically loads the dev environment, adds `scripts/` to `PATH`, and loads environment variables.

## Scripts

Utility scripts live in `scripts/`. The Nix and direnv development environments add this directory to `PATH`, so scripts can be run directly from the project root:

```bash
backfill_images.py
har_analyzer.py <path_to_har_file>
```

## Configuration

Secrets should be stored in `.env` or `~/.env.game1`, not committed to git. The local `.env` file is ignored by `.gitignore`.

### Trefle API Key

The app can use the Trefle API to fetch plant data. This is configured with the `TREFLE_API_KEY` environment variable.

Sign up or get an API key from [Trefle](https://trefle.io/).

Create a local `.env` file:

```bash
export TREFLE_API_KEY=your_trefle_api_key_here
```

With direnv enabled, the variable is loaded automatically. Without direnv, source it manually before starting the app:

```bash
set -a
source .env
set +a
```

## Manual Python Setup

If you are not using Nix, create a virtual environment and install the pinned Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app.main init-db
flask --app app.main run --debug --host 0.0.0.0
```

Stop the app with `Ctrl+C`.
