#!/usr/bin/env python3
"""CRSP close-to-close reactions for supplied release Accepted times. No models."""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import io
import json
import os
from pathlib import Path
import re
from statistics import median
import sys
from unittest.mock import patch
from zoneinfo import ZoneInfo

import exchange_calendars

ROOT=Path(__file__).resolve().parent
EASTERN=ZoneInfo('America/New_York')


class DatabaseFailure(RuntimeError):
    """A fixed public error message, never a raw database exception."""


def accepted(value):
    if not isinstance(value,str) or not re.search(r'[ T]\d{2}:\d{2}:\d{2}',value):
        raise ValueError('Accepted times must include hours, minutes and seconds')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:
        a=result.replace(tzinfo=EASTERN,fold=0);b=result.replace(tzinfo=EASTERN,fold=1)
        if a.utcoffset()!=b.utcoffset():raise ValueError('Ambiguous or nonexistent Eastern Accepted time')
        result=a
    return result.astimezone(EASTERN)


def release_times(values):
    result=[accepted(value) for value in values]
    if not result or len(set(result))!=len(result):raise ValueError('Supply distinct release Accepted times')
    return result


def close_window(filed):
    calendar=exchange_calendars.get_calendar('XNYS',start=(filed-timedelta(days=30)).date().isoformat(),
                                              end=(filed+timedelta(days=30)).date().isoformat())
    closes=[x.to_pydatetime() for x in calendar.schedule['close']]
    return max(x for x in closes if x<filed),min(x for x in closes if x>filed)


def fetch(db,ticker,dates,schema):
    if not re.fullmatch(r'[a-z][a-z0-9_]*',schema):raise ValueError('Invalid CRSP schema name')
    # CIZ supports post-2024 data. Do not silently fall back to the discontinued
    # legacy daily file or select a current ticker mapping for historical dates.
    query=f'''SELECT DISTINCT d.permno, d.dlycaldt AS date,
                     d.dlyprc AS close, d.dlyprcflg AS price_flag
              FROM {schema}.dsf_v2 d
              JOIN {schema}.stksecurityinfohist n ON n.permno=d.permno
               AND d.dlycaldt BETWEEN n.secinfostartdt AND n.secinfoenddt
              WHERE UPPER(n.ticker)=%(ticker)s
               AND d.dlycaldt=ANY(%(dates)s)
              ORDER BY date, permno'''
    try:
        frame=db.raw_sql(query,params={'ticker':ticker,'dates':sorted(set(dates))},date_cols=['date'])
    except Exception as error:
        code=getattr(getattr(error,'orig',None),'pgcode',None)
        message={'42501':'CRSP schema permission denied; request access from your WRDS institution',
                 '42P01':'Requested CRSP CIZ tables are not available in that schema',
                 '42703':'Requested CRSP CIZ columns do not match the subscribed table schema'}.get(code,
                 'WRDS query failed; check subscription access and CIZ schema locally')
        raise DatabaseFailure(message) from None
    return frame.to_dict('records')


def calculate(ticker,filings,rows,now=None):
    now=now or datetime.now(timezone.utc)
    by_day={}
    for row in rows:
        day=row['date'].date() if isinstance(row['date'],datetime) else row['date']
        if isinstance(day,str):day=datetime.fromisoformat(day).date()
        by_day.setdefault(day,[]).append(row)
    results=[]
    for filed in filings:
        before,after=close_window(filed)
        item={'ticker':ticker,'accepted':filed.isoformat(),'before_time':before.isoformat(),
              'after_time':after.isoformat(),'before_price':None,'after_price':None,
              'reaction':None,'reason':None}
        try:
            if after>now:raise ValueError('post-filing session has not closed')
            first,last=by_day.get(before.date(),[]),by_day.get(after.date(),[])
            if len(first)!=1 or len(last)!=1:raise ValueError('exact session close is missing or security is ambiguous')
            first,last=first[0],last[0]
            if first['permno']!=last['permno']:raise ValueError('security identifier changes between session closes')
            if any(str(r['price_flag']).strip()!='TR' for r in (first,last)):
                raise ValueError('CRSP price is not flagged as a closing trade')
            a,b=Decimal(str(first['close'])),Decimal(str(last['close']))
            if any(not p.is_finite() or p<=0 for p in (a,b)):raise ValueError('closing price is not positive and finite')
            item.update(before_price=a,after_price=b,reaction=(b/a-1)*100)
        except (ValueError,TypeError,KeyError,InvalidOperation) as error:
            # Reasons contain only fixed messages, never prices or database errors.
            item['reason']=str(error) if isinstance(error,ValueError) else 'invalid CRSP session observation'
        results.append(item)
    return results


def median_absolute(results):
    if not results or any(row['reaction'] is None for row in results):return None
    return median(abs(row['reaction']) for row in results)


def render(results):
    """Private numeric output: exactly one row per release, then the median."""
    lines=[]
    for row in results:
        price=lambda key:'not available' if row[key] is None else format(row[key],'.8f')
        reaction='not computed' if row['reaction'] is None else f"{row['reaction']:+.8f}%"
        lines.append(' | '.join([row['ticker'],row['accepted'],row['before_time'],price('before_price'),
                                 row['after_time'],price('after_price'),reaction]))
    value=median_absolute(results)
    lines.append('Median absolute reaction | '+('not computed (incomplete release set)' if value is None else f'{value:.8f}%'))
    return '\n'.join(lines)+'\n'


def status(results):
    count=sum(row['reaction'] is not None for row in results)
    return f'rows={len(results)} complete={count} median={"PASS" if median_absolute(results) is not None else "NOT COMPUTED"}'


def private_output(path,text):
    path=path.expanduser().resolve()
    if path.is_relative_to(ROOT):raise ValueError('Licensed output must be outside the repository')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as handle:handle.write(text)


def connect(env_file):
    # Use the same dotenv parser as the desk, without adding secrets to argv or
    # a subprocess environment. Never fall back to an interactive password prompt.
    from dotenv import dotenv_values
    config={**dotenv_values(env_file),**os.environ}
    username=config.get('WRDS_USERNAME','').strip();password=config.get('WRDS_PASSWORD','')
    if not username or not password:raise ValueError('Add WRDS_USERNAME and WRDS_PASSWORD to the selected .env file')
    import wrds
    def no_prompt(*args,**kwargs):raise RuntimeError('Interactive WRDS login is disabled')
    with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()),patch('builtins.input',no_prompt),patch('getpass.getpass',no_prompt):
        try:
            return wrds.Connection(wrds_username=username,wrds_password=password,verbose=False,
                                   wrds_connect_args={'sslmode':'require','connect_timeout':20,'application_name':'analyst-reactions'})
        except Exception:
            raise RuntimeError('WRDS connection failed; check credentials, network and Duo approval locally') from None


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker',help='Historical trading ticker at the release dates')
    parser.add_argument('times',nargs='*',help='Accepted times; naive values mean Eastern')
    parser.add_argument('--releases',type=Path,help='Public JSON manifest with ticker and releases[].accepted_eastern')
    parser.add_argument('--env',type=Path,default=ROOT/'.env')
    parser.add_argument('--schema',default='crsp',help='CRSP CIZ schema; e.g. crsp or crsp_m_stock')
    parser.add_argument('--output',type=Path,help='Private output file outside the repo; otherwise prints licensed results')
    parser.add_argument('--check',action='store_true',help='Print counts and PASS/FAIL only; use this in an AI session')
    args=parser.parse_args(argv)
    try:
        ticker=args.ticker.upper()
        if not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,15}',ticker):raise ValueError('Invalid ticker')
        times=args.times
        if args.releases:
            if times:raise ValueError('Use either Accepted-time arguments or --releases')
            data=json.loads(args.releases.read_text())
            if data['ticker']!=ticker:raise ValueError('Manifest ticker does not match command')
            times=[row['accepted_eastern'] for row in data['releases']]
        filings=release_times(times)
        dates=[t.date() for filed in filings for t in close_window(filed)]
        if args.output and args.output.expanduser().resolve().is_relative_to(ROOT):
            raise ValueError('Licensed output must be outside the repository')
        if args.output and args.output.expanduser().exists():raise ValueError('Output already exists; choose a new private file')
        db=connect(args.env)
        try:
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                rows=fetch(db,ticker,dates,args.schema)
            results=calculate(ticker,filings,rows)
        finally:
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):db.close()
        if args.output:private_output(args.output,render(results))
        if args.check:print(status(results))
        elif not args.output:print(render(results),end='')
        else:print('Private output saved. '+status(results))
        return 0 if median_absolute(results) is not None else 1
    except DatabaseFailure as error:
        print('FAIL: '+str(error),file=sys.stderr);return 2
    except (ValueError,OSError,KeyError) as error:
        # These are local input/credential errors, not raw database diagnostics.
        print('FAIL: '+str(error),file=sys.stderr);return 2
    except Exception as error:
        # Database exceptions can embed SQL and licensed observations. Do not
        # include exception text, a dataframe, or a traceback in the session.
        print('FAIL: '+type(error).__name__+' during WRDS connection/query; check access and CIZ schema locally',file=sys.stderr)
        return 2


if __name__=='__main__':raise SystemExit(main())
