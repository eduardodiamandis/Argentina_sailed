# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the pipeline

```bash
python main.py
```

There is no test suite. To test individual modules, import them directly in a Python shell or a scratch script.

## Environment setup

All configuration is loaded from `.env` at the repository root via `Config.py`. Every variable is required; the app raises `EnvironmentError` on startup if any is missing. Copy `.env.example` to `.env` and fill in:

- `URL_SAILED`, `URL_LINEUP` — NABSA download URLs
- `DIR_SAILED_BACKUP`, `DIR_LINEUP_BACKUP` — local backup directories
- `PATH_DATABASE`, `PATH_DATABASE_OUTPUT` — main and output Excel paths
- `DIR_ONEDRIVE`, `FILENAME_ONEDRIVE` — OneDrive target directory and filename
- `SQL_SERVER`, `SQL_DATABASE`, `SQL_TABLE`, `SQL_TABLE_LINEUP` — SQL Server connection
- `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `EMAIL_DESTINATARIO`, `EMAIL_CC` — Gmail SMTP credentials

## Architecture

`main.py` is the sole entry point and orchestrates 8 numbered stages in sequence. Never route logic through `concater.py` or `sailde.py` — those are superseded legacy files kept for reference.

### Module responsibilities

| File | Purpose |
|---|---|
| `Config.py` | Loads `.env`, exposes all settings as typed constants. No other module hardcodes paths/URLs. |
| `Donloader.py` | Opens a URL in the system browser, waits for the file to appear in `~/Downloads`, then moves it to the backup directory. |
| `Database.py` | All data transformation and persistence: `ler_arquivo_novo` (reads raw Excel, trims footer), `merge_com_banco` (period-aware merge), `salvar_local`, `salvar_onedrive`, `salvar_sql_server`, `criar_pivot_tables`. |
| `lineup_processor.py` | Reads the Lineup Excel snapshot, parses ETA/ETB/ETF strings, classifies vessel status, and inserts daily snapshots into `Arg_Lineup` (append-only, never deletes history). |
| `validacao.py` | Post-merge gap detection (`detectar_gaps`) and footer-cut sanity check (`validar_corte_rodape`). |
| `reporter.py` | Builds an HTML report dict and sends it via Gmail SMTP (`gerar_relatorio`, `enviar_email`). |
| `latest_module.py` | Single utility: `get_latest_file(directory)` returns the most recently created file in a folder. |
| `logger_config.py` | Creates the shared `logger` (name `argentina_logger`) with console + rotating file handler. Every module imports `logger` from here. |

### Data flow (Sailed)

```
Donloader.download_file()          # opens browser → ~/Downloads → backup dir
  → Database.ler_arquivo_novo()    # read Excel (header=7), strip footer, coerce dates
  → Database.merge_com_banco()     # period-by-period comparison; rejects periods with fewer rows
  → validacao.detectar_gaps()      # warns if days disappeared from updated periods
  → salvar_local() + salvar_onedrive() + salvar_sql_server()
  → criar_pivot_tables()           # win32com Excel COM: Pivot_2025, Pivot_2026 sheets
  → reporter.enviar_email()        # Gmail SMTP HTML report
```

### Sailed vs Lineup persistence difference

- **Arg_Sailed** (SQL table): full `DELETE` + `INSERT` on every run — always reflects the latest complete state.
- **Arg_Lineup** (SQL table): append-only `INSERT` per snapshot date; use `force=True` in `salvar_lineup_sql` to overwrite today's snapshot. Vessels with `Status=SAILED` are filtered out before insert to avoid duplicating Sailed data.

### Merge safety rule

`merge_com_banco` compares the incoming file against the existing database **period by period** (month/year). A period from the new file is accepted only if it has ≥ as many rows as the database already holds for that period. This prevents a mid-month partial file from overwriting a complete month. Rejected periods are logged as warnings.

### OneDrive sync guard

`salvar_onedrive` calls `_aguardar_arquivo_liberado` before writing, polling with `PermissionError` retries for up to 120 s. This handles OneDrive or Excel locking the file.

## Code style conventions

- Docstrings and log messages are written in **Portuguese** throughout — follow this in all new code.
- All modules use `from __future__ import annotations` for forward-compatible type hints.
- SQL Server connections use Windows Authentication (`Trusted_Connection=yes`); no passwords in code.
- `cursor.fast_executemany = True` is set for Sailed inserts but **must be `False`** for Lineup (the legacy `SQL Server` ODBC driver rejects `None` values with fast mode enabled).
