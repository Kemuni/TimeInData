# API service - TimeInData

---
## Requirements

---
- Docker
- UV for Python package management and virtual environment.



## Installation

---
From `./api_service/` install dependencies via `uv`:
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
    uv run -m app.main
    ```

## How to run tests?

---
We use `pytest` + `coverage` + `Docker`(creating temp database in container) for testing. So you need next steps:
1. Run Docker driver. *Our scripts automatically create a temporary database in a container and delete it.*
2. Run tests: 
    ```bash
    pytest
    ```
   Run tests with `coverage`:
    ```bash
    coverage run -m pytest tests/
    ```
   After all you can run `coverage report` to see the coverage report. 
   Or `coverage html` and open `htmlcov/index.html` in your browser.
