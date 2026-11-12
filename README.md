# Analyst

Weak human + machine + better process

## Saved views and filing reactions

From the workspace root, run `./aa runs/live` to fill available market reactions
and print one comparison row per saved run. Use `./aa runs/practice --offline`
for practice runs using saved reader data. Live runs belong in `runs/live`;
practice and seeded runs belong elsewhere. The command preserves the saved view
and its timestamp, marks late views `after`, and excludes late/uncomputed views
from the final agreement count. See [the run format and commands](../../runs/README.md).

## Equity research agent team

CrewAI currently supports Python 3.10 through 3.13. This computer has Python 3.14 as `python3`, so use `python3.13` for install and run.

Install the packages:

```bash
python3.13 -m pip install -r requirements.txt
```

Run the fixed-order team with a ticker, peers, and a price:

```bash
python3.13 equity_research_desk.py COST --peers WMT,TGT,BJ --price 992.13
```

Verify a saved run without rerunning its data steps or analyst roles:

```bash
python3.13 equity_research_desk.py --verify-only "equity_research_output/<run-folder>"
```

Put `API_KEY` and `SEC_USER_AGENT` in `.env`. The default model is `gemini/gemini-3.5-flash-lite`. Set `MODEL` to another CrewAI model name if needed, such as `openai/gpt-5.6-terra`. The value in `API_KEY` is passed to that provider. For an OpenAI-compatible gateway, set `LLM_BASE_URL` and `MODEL` in `.env`.

## Local web page

From the workspace directory, start the page with:

```bash
python3.13 Repos/Analyst/web_app.py
```

The page opens at http://127.0.0.1:8501. Enter a ticker, optional peers, and an optional Eastern filing-time override, then select Run research. The team selects the last official close strictly before the effective filing time. Node starts appear during execution. The completed Markdown report and marks render below, with a download link. Review wrong and unsupported marks before using the report. Existing CLI commands are unchanged. Configuration uses the same `.env` file. Keep the server running while using the page. Runs continue if you refresh the page; restarting the server clears its in-memory run list. Saved reports remain in `equity_research_output`. Only one run can be started at a time through the page.

Use `--port 8502` for another port or `--no-browser` to skip automatic browser opening.

See [CLOSES_READER.md](CLOSES_READER.md) for the isolated LSEG install, CSV source, timestamp override, reader commands, and price provenance. `--price` is now ignored for compatibility; new runs use the pre-filing official close.
