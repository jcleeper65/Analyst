"""Daily closes, with strict pre-filing selection at 16:00 America/New_York.

LSEG field reference:
https://developers.lseg.com/en/article-catalog/article/the-data-library-for-python-quick-reference-guide-access-layer
Desktop session reference:
https://cdn.refinitiv.com/public/lseg-lib-python-doc/2.0.0.2/book/en/sections/session-layer/session/session-desktop-definition-object.html
No session or file is opened at import time.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo('America/New_York')
NOT_AVAILABLE = 'not available'
ENV_FILE = Path(__file__).with_name('.env')


def filing_time(value: str) -> datetime:
    """A naive command-line timestamp is always Eastern, never machine local."""
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
        raise ValueError('Use YYYY-MM-DDTHH:MM:SS in Eastern time.')
    naive = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    aware = naive.replace(tzinfo=EASTERN)
    if aware.utcoffset() != naive.replace(tzinfo=EASTERN, fold=1).utcoffset():
        raise ValueError('Filing time is ambiguous or nonexistent at the Eastern daylight-saving transition.')
    return aware


def _settings():
    # dotenv is deliberately optional in the isolated LSEG worker.
    from dotenv import dotenv_values
    return {**dotenv_values(ENV_FILE), **os.environ}


def _normalize(rows, ticker, start, end, source):
    result = {}
    for row in rows:
        try:
            day = date.fromisoformat(str(row['date'])[:10])
            price = float(row['close'])
            if start <= day <= end and math.isfinite(price) and price > 0:
                if day in result and result[day]['close'] != price:
                    return NOT_AVAILABLE
                result[day] = {'ticker': ticker, 'date': day.isoformat(), 'close': price,
                               'close_time': datetime.combine(day, time(16), EASTERN).isoformat(),
                               'source': source}
        except (KeyError, TypeError, ValueError):
            continue
    return [result[day] for day in sorted(result)] or NOT_AVAILABLE


def _lseg_rows(instrument, start, end, app_key):
    import lseg.data as ld
    session = ld.session.desktop.Definition(app_key=app_key).get_session()
    try:
        session.open()
        ld.session.set_default(session)
        frame = ld.get_data(universe=[instrument], fields=['TR.PriceClose.date', 'TR.PriceClose'],
                            parameters={'SDate': start, 'EDate': end, 'Frq': 'D'}, use_field_names_in_headers=True)
        fields = {str(c).lower(): c for c in frame.columns}
        date_field, close_field = fields['tr.priceclose.date'], fields['tr.priceclose']
        rows = []
        for _, row in frame.iterrows():
            try:
                close = float(row[close_field])
                if math.isfinite(close) and close > 0:
                    rows.append({'date': str(row[date_field])[:10], 'close': close})
            except (TypeError, ValueError):
                continue
        return rows
    finally:
        session.close()


def daily_closes(ticker: str, start_date: str, end_date: str):
    """Inclusive dates; list of dated closes or the literal 'not available'."""
    start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    if start > end:
        raise ValueError('Start date must not follow end date.')
    ticker = ticker.strip().upper()
    config = _settings()
    try:
        filename = config.get('LSEG_CLOSES_FILE', '').strip()
        if filename:
            path = Path(filename).expanduser()
            if not path.is_absolute():
                path = ENV_FILE.parent / path
            with path.open(newline='', encoding='utf-8-sig') as stream:
                rows = [row for row in csv.DictReader(stream) if row.get('ticker', '').strip().upper() == ticker]
            return _normalize(rows, ticker, start, end, f'file:{path.resolve()}')
        key = config.get('LSEG_APP_KEY', '').strip()
        if not key:
            return NOT_AVAILABLE
        # Map plain tickers to explicit vendor instrument identifiers when required.
        instrument = json.loads(config.get('LSEG_RIC_MAP', '{}')).get(ticker, ticker)
        python = config.get('LSEG_PYTHON') or str(Path(__file__).resolve().parents[2] / '.venv-lseg/bin/python')
        # The App Key stays in the environment, never in argv or returned errors.
        worker = subprocess.run([python, str(Path(__file__).resolve()), '--worker', instrument,
                                 start.isoformat(), end.isoformat()],
                                env={**os.environ, 'LSEG_APP_KEY': key}, capture_output=True, text=True, timeout=180)
        if worker.returncode:
            return NOT_AVAILABLE
        rows = json.loads(worker.stdout.strip().splitlines()[-1])
        return _normalize(rows, ticker, start, end, f'LSEG TR.PriceClose ({instrument})')
    except Exception:
        # Missing coverage, entitlement, configuration or connection must not stop the desk.
        return NOT_AVAILABLE


def last_close_before(ticker: str, filed: str):
    """Return the most recent available dated close strictly before filing time."""
    cutoff = filing_time(filed)
    end = cutoff.date() if cutoff.time() > time(16) else cutoff.date() - timedelta(days=1)
    rows = daily_closes(ticker, '1900-01-01', end.isoformat())
    if rows == NOT_AVAILABLE:
        return NOT_AVAILABLE
    eligible = [row for row in rows if datetime.fromisoformat(row['close_time']) < cutoff]
    return eligible[-1] if eligible else NOT_AVAILABLE


def main():
    if len(sys.argv) == 5 and sys.argv[1] == '--worker':
        try:
            print(json.dumps(_lseg_rows(sys.argv[2], sys.argv[3], sys.argv[4], os.environ['LSEG_APP_KEY'])))
        except Exception:
            print(json.dumps([]))
        return
    parser = argparse.ArgumentParser(description='Print official closes or the last close before filing time.')
    parser.add_argument('ticker')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filed', help='YYYY-MM-DDTHH:MM:SS, Eastern; strict before')
    group.add_argument('--start', help='Inclusive YYYY-MM-DD')
    parser.add_argument('--end', help='Inclusive YYYY-MM-DD, required with --start')
    args = parser.parse_args()
    if args.start and not args.end:
        parser.error('--end is required with --start')
    print(json.dumps(last_close_before(args.ticker, args.filed) if args.filed else daily_closes(args.ticker, args.start, args.end), indent=2))


if __name__ == '__main__':
    main()
