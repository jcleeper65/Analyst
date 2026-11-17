# Analyst

Weak human + machine + better process

## Saved views and filing reactions

From the workspace root, run `./aa runs/live` to fill available market reactions
and print one comparison row per saved run. Use `./aa runs/practice --offline`
for practice runs using saved reader data. Live runs belong in `runs/live`;
practice and seeded runs belong elsewhere. The command preserves the saved view
and its timestamp, marks late views `after`, and excludes late/uncomputed views
from the final agreement count. See [the run format and commands](../../runs/README.md).

### Historical reaction base rate — WRDS/CRSP

The historical median absolute release reaction belongs below the hit-rate table
in the product manual. The command and verified eight-release input are ready;
see [WRDS release reactions](docs/wrds-reactions.md). CRSP values stay in a private
file outside the repo and do not enter model prompts or this page.

The November 16 check authenticated to WRDS and found six of the eight required
close pairs in the accessible annual schema. Monthly and quarterly schemas denied
access. The median remains **not computed** until all eight pairs are available.

## Equity research agent team

CrewAI currently supports Python 3.10 through 3.13. This computer has Python 3.14 as `python3`, so use `python3.13` for install and run.

Install the packages:

```bash
python3.13 -m pip install -r requirements.txt
```

Run the joined desk from this repo. Replace `TICKER` with the ticker:

```bash
python3.13 desk.py TICKER
```

Select the top company from the latest saved seeker report:

```bash
python3.13 desk.py screen
```

Replay a completed run with saved data and no model calls:

```bash
python3.13 desk.py --replay 'runs/practice/<saved-run-folder>'
```

The code fixes the order: seeker when requested, pick, team, worksheet, and
final report. The hook checks saved outputs and blocks completion on failure.
All parts share one run folder. Practice is the default; add `--live` for
`runs/live`. See [all commands and run behavior](docs/desk-command.md).

Put `API_KEY` and `SEC_USER_AGENT` in `.env`. The default model is `gemini/gemini-3.5-flash-lite`. Set `MODEL` to another CrewAI model name if needed, such as `openai/gpt-5.6-terra`. The value in `API_KEY` is passed to that provider. For an OpenAI-compatible gateway, set `LLM_BASE_URL` and `MODEL` in `.env`.

## Local web page

From the workspace directory, start the page with:

```bash
python3.13 Repos/Analyst/web_app.py
```

The page opens at http://127.0.0.1:8501. Enter a ticker or `screen`, optional peers,
and an optional Eastern filing-time override. Select Run desk. The page runs
`desk.py` and displays the verified team report with the worksheet below it.
Progress and elapsed times appear during execution. Failed checks stop the run.
Configuration uses the Analyst `.env`. Keep the server running while using the
page. Refreshing the page does not stop a run. Restarting the server clears its
in-memory run list. Saved reports remain in `runs/practice` or `runs/live`.
The page allows one active run.

Use `--port 8502` for another port or `--no-browser` to skip automatic browser opening.

See [CLOSES_READER.md](CLOSES_READER.md) for the isolated LSEG install, CSV source, timestamp override, reader commands, and price provenance. `--price` is now ignored for compatibility; new runs use the pre-filing official close.
