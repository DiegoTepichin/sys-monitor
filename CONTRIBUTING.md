# Contributing

Thanks for your interest in Sys-Monitor. This guide covers setup, workflow and quality checks.
For internals (architecture, conventions, testing patterns) see
[docs/ENGINEERING.md](docs/ENGINEERING.md).

## 1. Set up

Requirements: Python 3.11+, Node 22+, Docker (optional).

```sh
git clone https://github.com/DiegoTepichin/sys-monitor.git
cd sys-monitor

python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install

cp .env.example .env    # then set API_KEY, e.g. with: openssl rand -hex 32

cd frontend && npm ci && cd ..
```

## 2. Run locally

| Terminal | Command                      | Result                                 |
| -------- | ---------------------------- | -------------------------------------- |
| 1        | `python app.py`              | API on `http://127.0.0.1:5002`         |
| 2        | `python agent.py`            | Pushes metrics every `POLL_INTERVAL` s |
| 3        | `cd frontend && npm run dev` | Dashboard with hot reload on `:3000`   |

## 3. Git workflow

1. Branch from `main`: `feat/short-description`, `fix/…`, `docs/…`.
2. Make atomic commits using [Conventional Commits](https://www.conventionalcommits.org/):

   | Type       | Use for                                  |
   | ---------- | ---------------------------------------- |
   | `feat`     | New functionality                        |
   | `fix`      | Bug fixes                                |
   | `refactor` | Internal changes with no behavior change |
   | `perf`     | Performance improvements                 |
   | `test`     | New or fixed tests                       |
   | `docs`     | Documentation only                       |
   | `build`    | Dependencies, Docker, packaging          |
   | `ci`       | GitHub Actions                           |
   | `chore`    | Maintenance that doesn't touch app code  |

   Example: `fix(api): reject out-of-range percent values`

3. If a pre-commit hook reformats files, `git add` them again and repeat the commit.
4. Open a pull request against `main`. CI must be green.

## 4. Before opening a PR

```sh
ruff check . && ruff format --check .
pytest
cd frontend && npm run lint && npm run build
```

Checklist:

- [ ] Tests cover the new or fixed behavior.
- [ ] New collectors always return a dict with an `error` key and never raise.
- [ ] No secrets in code (use `.env`, which is git-ignored).
- [ ] README and docs/ENGINEERING.md updated if commands, variables or endpoints change.

## 5. Reporting bugs

Open an issue with steps to reproduce, expected vs. actual behavior, OS, Python version and the
relevant lines from `logs/app.log`.
