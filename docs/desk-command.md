# Joined desk command

Run these commands from `Repos/Analyst`. Use Python 3.13 and the existing
Analyst `.env`. The command does not copy credentials into a run.

Run a ticker (replace `TICKER` with the ticker):

```bash
python3.13 desk.py TICKER
```

Use the top ranked company in the latest saved seeker report:

```bash
python3.13 desk.py screen
```

To run the seeker first, supply a distribution start date:

```bash
python3.13 desk.py screen --refresh-screen 2026-01-01
```

The latest report is selected by its saved run time. The command checks its
ranking against its saved factors. Pending issuers are excluded. A partial
screen keeps its coverage disclosure. Use `--screen-folder PATH` to select
another report folder, or `--screen-report PATH` to select one saved JSON report.

New runs go into `runs/practice/TICKER_YYYY-MM-DD_HH-MM-SS.microseconds`.
Add `--live` to save a live run into `runs/live`. The folder time is the command
start time. For `screen`, the temporary folder is renamed after ticker selection;
its start time does not change.

Replay a completed run (replace the path with the saved run folder):

```bash
python3.13 desk.py --replay 'runs/practice/TICKER_YYYY-MM-DD_HH-MM-SS.microseconds'
```

Replay checks saved sources, output hashes, the screen selection, and numerical
claims. It does not fetch data or call a model. It displays the existing final
report path. It keeps the saved view and its time. Missing or changed evidence
stops replay. Hook records are appended to the run.

The same command accepts a failed run. It checks the completed stages and partial
outputs, lists missing outputs, then exits with the original failed part and
error. It does not resume execution or mark the run complete. New failed runs
also retain an artifact manifest; older failed runs use their saved hook hashes.

Start the Lab 05 page:

```bash
python3.13 web_app.py
```

Open <http://127.0.0.1:8501>. Enter a ticker or `screen`. The page starts the same
command in a subprocess. It shows progress, elapsed times, and the final report.
It reports completion only when the command succeeds and saves the final file.

The code fixes this order: input snapshots, seeker when requested, ticker pick,
team, worksheet, final report. A hook checks each part's saved outputs. Team role
outputs are also checked when saved. The final report starts with the filing
inventory, then contains the verified team report and the worksheet view with its
printed evidence. The final report receives the same numerical checks.

All mutable part outputs, reader results, source text, framework storage, and
hook records belong to the run folder. Saved SEC responses are reused by URL.
Saved filing text is checked for changes. Role input packets contain assigned
file paths, hashes, and quote-only permissions. A read-only file tool returns the
actual file's numbered lines. It rejects other files, path escapes, and changed
files. Each role must read its assigned files before returning an answer. Access
records are saved beside the role output. The role instructions prohibit
recalculation of those values. The hook checks the claims; it does not trust a model's assertion
that a value is correct.

The numeric checks reuse the existing worksheet checker. Team claims must have
exact fact citations, saved-file line citations, or supported arithmetic. Screen
scores are checked against the copied factor file. Unmatched financial numbers
and wrong or unsupported verification marks stop the command. Raw source files,
input snapshots, and metadata receive source-integrity or format checks rather
than treatment as new report claims.

If the registry has no matching ticker, the spinoff status is `not applicable`.
The team and the financial worksheet still run. A missing registry or a failed
part stops the command, prints the part name and error, and keeps the folder.
Each part prints its elapsed seconds on its last line. Data steps, role calls,
and reader calls also print times and save records under `timings/`, including on
failure. Hook calls also print and save their elapsed times. Missing requested output files or
an empty output list fail the hook. Reader exceptions stop the worksheet; they
cannot become successful unavailable results. A price-reader failure prevents
the judgment call, and a judgment-call exception prevents the later liquidity request.

Offline tests use seeded data and stub model responses. They cover the real
worksheet renderer and checker, shared sources, failure handling, page command,
and replay. They do not establish that a live provider or reader is available.
