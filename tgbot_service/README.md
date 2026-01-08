# Telegram Bot - TimeInData

---
## Requirements

---
- Docker
- UV for Python package management and virtual environment.



## Installation

---
From `./tgbot_service/` install dependencies via `uv`:
```bash
  uv sync
```
Then activate virtual environment:
```bash
  source .venv/bin/activate
```


## How to run service?

---
- **Develop** mode (with `export DEBUG=1`)
    ```bash
    uv run -m main.py
    ```