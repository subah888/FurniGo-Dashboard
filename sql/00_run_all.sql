-- Runs every file in order. From the furnigo_db folder:
--   psql -d furnigo -f sql/00_run_all.sql
\ir 01_schema.sql
\ir 02_survey_data.sql
\ir 03_sample_marketplace_data.sql
