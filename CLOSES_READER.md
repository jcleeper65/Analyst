# Official pre-filing close

The reader is `closes_reader.py`. No source is accessed at import. `daily_closes(ticker, start_date, end_date)` returns dated close records for inclusive ISO dates, or `"not available"`. `last_close_before(ticker, filed)` returns one record or `"not available"`.

Each record has `ticker`, `date`, `close`, `close_time` and `source`. The close timestamp is always 16:00 America/New_York, including daylight saving. At exactly 16:00 the same day's close is excluded; after 16:00 it is eligible. Holidays and weekends use only rows actually present in the source. Last-close lookup requests history from 1900-01-01 through the eligible date; it does not assume the previous weekday traded.

## Install from the workspace directory

```bash
python3.13 -m venv .venv-lseg
.venv-lseg/bin/python -m pip install -r Repos/Analyst/requirements-lseg.txt
```

The separate environment is required because LSEG and CrewAI require incompatible httpx versions. The agent team's Python starts an isolated LSEG worker automatically; it does not import LSEG into CrewAI. Set `LSEG_PYTHON` in the repository `.env` if that environment lives elsewhere.

## Choose a source in Repos/Analyst/.env

For Workspace desktop access:

```dotenv
LSEG_APP_KEY=your_app_key
```

Workspace must be running and signed in with the necessary entitlements. The reader opens `ld.session.desktop.Definition(app_key=...).get_session()`, then uses `ld.get_data` with `TR.PriceClose.date`, `TR.PriceClose`, `SDate`, `EDate`, and `Frq=D`. It closes its session afterwards.

For file access instead:

```dotenv
LSEG_CLOSES_FILE=closes.csv
```

The CSV path is relative to the repository's `.env` directory, unless absolute. It takes precedence over the App Key. Supply `ticker,date,close` columns, with dates as YYYY-MM-DD and unadjusted official closing prices in the instrument's quote currency. Do not include filled-forward rows for non-trading days. Conflicting duplicate prices for a date return not available. File prices are taken as supplied; the reader cannot certify their provenance.

Plain ticker symbols can be ambiguous in vendor data. Optional `LSEG_RIC_MAP` is a JSON object mapping your tickers to explicit LSEG RICs. No exchange suffix is guessed. A plain ticker that LSEG cannot resolve is submitted to its documented U.S. equity symbol-conversion service. Exactly one regular RIC is required. Ambiguous or unresolved conversions return not available with a diagnostic. An explicit LSEG_RIC_MAP entry selects the instrument directly. Prices and filing EPS must use compatible currencies and per-share units; the reader performs no currency or share-unit conversion.

## Commands

Print one close (replace the shell variables with your ticker and filing timestamp):

```bash
python3.13 Repos/Analyst/closes_reader.py "$TICKER" --filed "$FILED"
```

`FILED` must be YYYY-MM-DDTHH:MM:SS in Eastern time. Ambiguous or nonexistent daylight-saving transition times are rejected.

Read a date range:

```bash
python3.13 Repos/Analyst/closes_reader.py "$TICKER" --start "$START_DATE" --end "$END_DATE"
```

Run the team using the EDGAR Accepted timestamp:

```bash
python3.13 Repos/Analyst/equity_research_desk.py "$TICKER" --peers "$PEER_1" "$PEER_2"
```

Use `--filed "$FILED"` to override the cutoff. The raw EDGAR Accepted timestamp, accession, index URL, override, and effective Eastern timestamp are saved in `filing_time.json`. The selected single close and provenance are saved in `market_price.json` and in `facts.json`. Roles receive only the selected close through the computed P/E and its source metadata, not the series or other reader outputs. The verifier receives the selected evidence to check it.

`--price` remains accepted for old commands but is ignored. Valuation always uses the pre-filing close. Missing data, desktop/session failures, or missing configuration produce not available and leave P/E unavailable; they do not stop the rest of the desk. The same filing override is available on the local web page. Restart the page server after this update.

## Documentation

- [LSEG daily TR.PriceClose examples](https://developers.lseg.com/en/article-catalog/article/the-data-library-for-python-quick-reference-guide-access-layer)
- [Desktop session Definition](https://cdn.refinitiv.com/public/lseg-lib-python-doc/2.0.0.2/book/en/sections/session-layer/session/session-desktop-definition-object.html)
- [get_data parameters](https://cdn.refinitiv.com/public/lseg-lib-python-doc/2.0.0.2/book/en/sections/access-layer/access/get-data-function.html)

Implementation was reviewed statically; the reader was not executed during this change.

## Error diagnostics

Unavailable results retain their existing return value. The reader records a sanitized JSON-lines diagnostic with ticker, requested dates, failure stage, error type and message. Stages distinguish session opening, data requests, response parsing, worker timeouts and genuinely empty responses. Configured key/token/password values and bearer tokens are redacted.

The seeker creates a separate `closes_errors_<run timestamp>.jsonl` for each run, records its path/count in the run snapshot, and includes errors in candidate limitations and the report. Standalone reader calls default to `Repos/Analyst/closes_diagnostics.jsonl`. `LSEG_DIAGNOSTICS_FILE` selects another path.

The installed lseg-data 2.1.1 call uses `header_type=ld.HeaderType.NAME`. Earlier failures caused by `use_field_names_in_headers` are retained in their original diagnostic logs. New successful prices identify the resolved vendor instrument in their source.
