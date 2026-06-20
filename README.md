# game1

A small Flask app for tracking plants and fetching plant information/images.

## Quick Start

Start the local dev server:

```bash
g-dev start
```

Open <http://127.0.0.1:5000>.

Useful commands:

```bash
g-dev logs
g-dev status
g-dev stop
```

`g-dev start` initializes the local database if needed and starts the server in the background.

## Setup

Nix flakes and direnv are supported. With direnv enabled, `scripts/` is added to `PATH` automatically.

Without direnv, install dependencies and run scripts from the project root:

```bash
pip install -r requirements.txt
scripts/g-dev start
```

## Local Data

Runtime files are stored under `instance/`:

```text
instance/plants.db
instance/logs/web.log
instance/run/g-dev.json
```

## Configuration

Optional secrets can be stored in `.env` or `~/.env.game1`.

`TREFLE_API_KEY` enables plant data lookups from [Trefle](https://trefle.io/):

```bash
export TREFLE_API_KEY=your_trefle_api_key_here
```
