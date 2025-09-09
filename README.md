# Expense Tracker (CLI)

A simple, zero-dependency Python CLI to track recurring expenses, subscriptions, and bills using SQLite.

- **Tech**: Python 3.10+, SQLite (standard library)
- **Features**: recurring schedules, payments history, upcoming view, monthly summaries, CSV export

## Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Initialize](#initialize)
  - [Add expenses](#add-expenses)
  - [List expenses](#list-expenses)
  - [Upcoming due](#upcoming-due)
  - [Record payments](#record-payments)
  - [Monthly summary](#monthly-summary)
  - [List payments](#list-payments)
  - [Export CSV](#export-csv)
- [Data Model](#data-model)
- [Recurrence Rules](#recurrence-rules)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```powershell
# Windows PowerShell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize the database (creates expenses.db)
python -m expense_tracker init

# Add examples
python -m expense_tracker add "Netflix" 15.99 --category Entertainment --recurrence monthly --start 2025-01-01
python -m expense_tracker add "Rent" 1200 --category Housing --recurrence monthly --start 2025-01-01

# See data
python -m expense_tracker list
python -m expense_tracker upcoming --days 30
python -m expense_tracker pay Netflix --method Visa --date 2025-01-01
python -m expense_tracker month --month 2025-01
```

## Installation

This project uses only the Python standard library. A virtual environment is recommended.

- Windows (PowerShell):
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- macOS/Linux (bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

You can run the CLI with:
```bash
python -m expense_tracker <command> [options]
```

### Initialize
```bash
python -m expense_tracker init
```
Creates the SQLite database file (default: `expenses.db`).

### Add expenses
```bash
python -m expense_tracker add "<name>" <amount> [--currency USD] [--category <label>] \
  [--recurrence none|daily|weekly|biweekly|monthly|quarterly|yearly] [--start YYYY-MM-DD] [--next YYYY-MM-DD] [--notes TEXT]
```
- Amount can be `12.34` (stored as integer cents internally)
- If `--next` is not given, recurring items default next due to `--start` or today

### List expenses
```bash
python -m expense_tracker list [--all] [--inactive]
```
- `--all` includes inactive items; `--inactive` shows only inactive

### Upcoming due
```bash
python -m expense_tracker upcoming [--days 30]
```
Shows active expenses with `next_due_date` within the window.

### Record payments
```bash
python -m expense_tracker pay <id|name> [--amount 12.34] [--date YYYY-MM-DD] [--method TEXT] [--notes TEXT]
```
- If `--amount` is omitted, uses the expense's configured amount
- For recurring items, advances `next_due_date`; one-off items are deactivated

### Monthly summary
```bash
python -m expense_tracker month [--month YYYY-MM]
```
Displays total payments and count for the specified month (defaults to current month).

### List payments
```bash
python -m expense_tracker payments [--month YYYY-MM] [--id <expense_id>] [--name <expense_name>]
```

### Export CSV
```bash
python -m expense_tracker export <output.csv> [--table expenses|payments|all]
```
Exports one or both tables to CSV.

## Data Model

- `expenses`
  - `id` INTEGER PRIMARY KEY
  - `name` TEXT
  - `amount_cents` INTEGER, `currency` TEXT
  - `category` TEXT
  - `recurrence` TEXT
  - `start_date` TEXT (YYYY-MM-DD)
  - `next_due_date` TEXT (YYYY-MM-DD)
  - `notes` TEXT
  - `active` INTEGER (1/0)
  - timestamps: `created_at`, `updated_at`

- `payments`
  - `id` INTEGER PRIMARY KEY
  - `expense_id` INTEGER (FK → expenses.id)
  - `amount_cents` INTEGER
  - `paid_date` TEXT (YYYY-MM-DD)
  - `method`, `notes` TEXT
  - `created_at` TEXT

## Recurrence Rules

Supported: `none`, `daily`, `weekly`, `biweekly`, `monthly`, `quarterly`, `yearly`.
- `monthly` uses calendar-aware month addition (e.g., Jan 31 → Feb 28/29)
- `yearly` handles leap years (Feb 29 → Feb 28 on non-leap years)

## Configuration

- Database file: `--db <path>` (default `expenses.db` in CWD)
- Currency is a free-form 3–5 character code; default `USD`.

## Development

- Python 3.10+ recommended
- No external dependencies
- Run CLI locally:
```bash
python -m expense_tracker --help
```

Run tests (if/when added) under `.venv`.

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the terms of the [MIT license](LICENSE).
