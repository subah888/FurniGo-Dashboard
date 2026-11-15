# FurniGo BI Dashboard (Streamlit + PostgreSQL)

Eleven use cases from `sql/04_use_case_queries.sql`: A1 to A5 (daily operations, sample data)
and B1 to B6 (survey insights, real data). Each page shows its SQL, a chart, and a table.

## 1. Load the database (once)

```
createdb -U postgres furnigo
cd sql
psql -U postgres -d furnigo -f 00_run_all.sql
```

`00_run_all.sql` uses `\ir`, so run it from inside the `sql` folder (or use `psql -f sql/00_run_all.sql`
from the project root, which also works because `\ir` is relative to the script).
Expected rows: users 12, listings 16, buyer_requests 10, matches 6, transactions 8,
survey_responses 20, survey_answers 526.

## 2. Run the dashboard

```
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501. If your PostgreSQL user or password differs from the defaults,
type them into the sidebar, or set environment variables first:

- macOS/Linux: `export PGUSER=postgres PGPASSWORD=yourpassword`
- Windows (PowerShell): `$env:PGUSER="postgres"; $env:PGPASSWORD="yourpassword"`

## 3. Optional: cloud version

1. Create a free PostgreSQL database (Neon, Supabase, or Render) and run the four SQL files against it.
2. Push this folder to GitHub (never commit passwords).
3. On share.streamlit.io deploy `app.py` and add under Settings > Secrets:

```
DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DBNAME"
```

## Presenting (one use case per member)

| Page | Question it answers |
|---|---|
| A1 | Which listings match a buyer's request? (pick a request) |
| A2 | Which sellers leave soon? (change date and window) |
| A3 | Which sellers do buyers trust? |
| A4 | How much does FurniGo earn? |
| A5 | Where is demand not met? |
| B1 | Which items would students buy used? |
| B2 | How much would they pay, by item? |
| B3 | What frustrates them today? |
| B4 | Interest by university |
| B5 | Delivery fee willingness |
| B6 | What builds trust? |

Part A data is made up. Part B is the real survey (20 responses, 13 from TIU).
