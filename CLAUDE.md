# CLAUDE.md — Sys-Monitor engineering guide

Guide for AI coding agents and developers working in this repository. `AGENTS.md` points here;
keep this file as the single source of truth.

## Architecture

Three parts, one repo:

1. **Collectors** — `scripts/monitor_{cpu,memory,disk,network,processes}.py`. Thin wrappers
   over `psutil`. Disk and network keep the previous counter sample in module globals guarded
   by a `threading.Lock` to compute MB/s deltas.
2. **API** — `app.py` (Flask). Keeps the last `HISTORY_LIMIT` snapshots in a
   `deque(maxlen=...)` guarded by `_history_lock`. All writes go through `record_snapshot()`,
   which calls `normalize_payload()` so every stored entry has the same shape.
3. **Agent** — `agent.py`. Loop: collect → `POST /api/metrics` with `X-API-Key` → sleep
   `POLL_INTERVAL`. Never exits on errors.
4. **Dashboard** — `frontend/` (React 19, Vite, Tailwind, Recharts, Framer Motion). Polls
   `GET /api/metrics` every 2 s. Vite proxies `/api` → `http://127.0.0.1:5002` in dev.

`/` (and any non-`/api` path) serves `frontend/dist` when a build exists, otherwise redirects
to `FRONTEND_DEV_URL`. Unknown `/api/*` paths return JSON 404.

## Commands

```sh
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
cd frontend && npm ci

# Run (three terminals)
python app.py                     # API on :5002
python agent.py                   # pushes metrics every POLL_INTERVAL s
cd frontend && npm run dev        # dashboard on :3000

# Verify — run all of these before committing
ruff check . && ruff format --check .
pytest
cd frontend && npm run lint && npm run build

# Production
API_KEY=... docker compose up --build   # http://localhost:5002
```

## Configuration

`config.py` loads `.env` by hand (no `python-dotenv`) and parses ints with `safe_int()`, which
falls back to the default on invalid values. See `.env.example` for every variable. Defaults:
`PORT=5002`, `DEBUG=False`, `POLL_INTERVAL=5`, `HISTORY_LIMIT=20`, `CPU_THRESHOLD=80`,
`MEMORY_THRESHOLD=85`, `DISK_THRESHOLD=90`, `LOG_FILE=logs/app.log`.
`config.py` prints a warning when `API_KEY` is left at the default.

## Code conventions

- **Collectors never raise.** `get_*_usage()` return a dict that always contains an `"error"`
  key (`None` on success). `get_top_processes()` returns `[]` on failure. The API turns sensor
  errors into alerts instead of 500s. Keep this contract when adding collectors.
- **New collector checklist:** add `scripts/monitor_<x>.py` → call it in both `agent.py` and
  the `GET` branch of `api_metrics` → give it a default in `normalize_payload()` → add tests in
  `tests/test_collectors.py` → render it in `frontend/src/App.jsx`.
- **Auth:** compare secrets with `is_authorized()` (`hmac.compare_digest`), never `==`.
- **Validation:** `is_valid_metrics_payload()` returns an error string or `None`. `cpu`,
  `memory`, `disk` require numeric `percent` in `[0, 100]`; booleans are rejected.
- **Errors to clients:** never echo exception text in responses; log it with `exc_info=True`.
- **Logging:** per-request logs at `DEBUG`; `INFO`/`WARNING` only for lifecycle and security
  events. The file handler rotates at 5 MB × 3.
- **Time:** `datetime.now(UTC)`, formatted `%Y-%m-%dT%H:%M:%SZ`. Never `utcnow()`.
- **Header comment:** `app.py`, `agent.py` and test files start with
  `# pyrefly: ignore [missing-import]`.
- **Style:** ruff (config in `pyproject.toml`, line length 100); prettier for JS/CSS/MD/YAML
  (`.prettierrc`: single quotes, width 100); oxlint for the frontend.

## Testing

- `tests/test_api.py` uses the Flask test client. The `client` fixture clears
  `metrics_history`; patch collectors with `patch.object(app_module, "get_cpu_usage", ...)`
  because `app.py` imports them by name.
- `tests/test_collectors.py` and `tests/test_monitor.py` mock `psutil`; network tests reset
  `monitor_network.last_net_io` / `last_net_time` before running.
- No frontend test runner is configured; `npm run lint` and `npm run build` are the gate.

## Git workflow

- Branch from `main`: `feat/…`, `fix/…`, `docs/…`, `chore/…`.
- [Conventional Commits](https://www.conventionalcommits.org/): `feat`, `fix`, `refactor`,
  `perf`, `test`, `docs`, `build`, `ci`, `chore`, optional scope (`feat(api): …`).
- One logical change per commit. pre-commit hooks may reformat staged files; re-stage and
  commit again.
- Commits are authored by the repository owner. Do not add `Co-Authored-By` or AI attribution
  trailers.
- CI (`.github/workflows/ci.yml`) must pass: ruff, pytest on 3.11/3.12, oxlint, frontend build,
  Docker build.

## Deployment notes

- Docker image: Node stage builds `frontend/dist`; Python stage runs
  `gunicorn --workers 1 --threads 4 app:app` as uid 10001 with a `HEALTHCHECK` on
  `/api/health`.
- **Keep one worker.** History is process memory; multiple workers would each hold a different
  history. Scale with threads, or move history to a shared store first.
- Inside a container, psutil reports container metrics, not the host's.

## Known gaps

- No persistent storage; history is lost on restart.
- Dashboard charts the server's live sampling; agent-posted snapshots only appear in
  `/api/metrics/history`. No `host_id` yet for multi-host views.
- Frontend card thresholds are hardcoded in `App.jsx` and can drift from `config.py`.
- `GET /api/metrics` blocks ~100 ms on `cpu_percent(interval=0.1)`.
- `axios` is listed in `frontend/package.json` but unused.
