"""Fill saved reactions and compare frozen views, without rerunning an analyst."""
from __future__ import annotations

import argparse
from datetime import datetime, time, timedelta
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo('America/New_York')
WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_FOLDER = WORKSPACE / 'runs/live'
DIRECTIONS = {'up':'up','down':'down','flat':'flat','more than the price':'up',
              'less than the price':'down','equal to the price':'flat',
              'not computed':'not computed','not known':'not computed'}


def read(path):
    data=json.loads(path.read_text())
    if not isinstance(data,dict):raise ValueError(path.name+' must contain a JSON object')
    return data


def timestamp(value):
    if not isinstance(value,str) or not value.strip():raise ValueError('timestamp is missing')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:
        # Use the reader's strict Eastern parser, including DST ambiguity checks.
        from closes_reader import filing_time
        result=filing_time(result.strftime('%Y-%m-%dT%H:%M:%S'))
    return result.astimezone(EASTERN)


def discover(folder):
    """One directory per run; do not mistake nested node/fetch caches for runs."""
    paths=[]
    for current,dirs,files in os.walk(folder,followlinks=False):
        dirs[:]=sorted(d for d in dirs if not d.startswith('.') and not (Path(current)/d).is_symlink())
        if {'facts.json','view.json','run_identity.json'} & set(files):
            paths.append(Path(current));dirs[:]=[]
    return sorted(paths)


def load_view(run,old):
    frozen=old.get('view_source') if old else None
    if frozen:
        path=(run/frozen['path']).resolve()
        if not path.is_relative_to(run.resolve()):raise ValueError('saved view path leaves run')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=frozen['sha256']:
            raise ValueError('the saved view changed; reaction refresh will not replace it')
        return frozen
    direct=run/'view.json'
    candidates=[]
    if direct.exists():
        data=read(direct)
        nested=data.get('view') if isinstance(data.get('view'),dict) else {}
        candidates=[(direct,data.get('view_time') or data.get('time') or data.get('worksheet_time') or nested.get('time'),data.get('direction') or nested.get('direction'))]
    else:
        for path in run.glob('Spinoff worksheet*.json'):
            if ', model ' in path.name:continue
            data=read(path)
            if isinstance(data.get('view'),dict) and data.get('worksheet_time'):
                candidates.append((path,data['worksheet_time'],data['view'].get('direction')))
    if not candidates:return None
    # Keep the earliest view, including an early "not computed". Never select
    # a later successful view because the reaction is now visible.
    candidates.sort(key=lambda x:(timestamp(x[1]),x[0].name))
    path,when,direction=candidates[0]
    normalized=DIRECTIONS.get(str(direction).strip().lower(),'not computed')
    same_time=[x for x in candidates if timestamp(x[1])==timestamp(when)]
    if any(DIRECTIONS.get(str(x[2]).strip().lower(),'not computed')!=normalized for x in same_time):
        raise ValueError('conflicting views have the same earliest timestamp')
    data=read(path)
    practice=data.get('artifact_type') in ('seeded_test','practice','practice_run') or bool(data.get('seeded_test'))
    return {'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'time':timestamp(when).isoformat(),'direction':normalized,'practice':practice}


def load_identity(run):
    facts=read(run/'facts.json') if (run/'facts.json').exists() else {}
    view=read(run/'view.json') if (run/'view.json').exists() else {}
    ticker=facts.get('ticker') or view.get('ticker')
    if not isinstance(ticker,str) or not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,15}',ticker):
        raise ValueError('saved ticker is missing or invalid')
    evidence=read(run/'filing_time.json') if (run/'filing_time.json').exists() else facts.get('market_price',{})
    filed=evidence.get('effective_filed_eastern') or evidence.get('edgar_accepted') or view.get('filing_time')
    # Never substitute the run start, file mtime or report-period date.
    return ticker,timestamp(filed)


def close_rows(rows,ticker,now):
    if not isinstance(rows,list):raise ValueError('reader did not return daily observations')
    result={}
    for row in rows:
        if not isinstance(row,dict):raise ValueError('reader observation is not an object')
        day=datetime.fromisoformat(row['date']).date()
        close=Decimal(str(row['close']))
        when=timestamp(row['close_time']) if row.get('close_time') else datetime.combine(day,time(16),EASTERN)
        if when.date()!=day:raise ValueError('reader date and close timestamp disagree')
        if row.get('ticker',ticker)!=ticker:raise ValueError('reader ticker does not match run')
        if not close.is_finite() or close<=0:raise ValueError('reader close must be positive and finite')
        if not row.get('source'):raise ValueError('reader close has no source')
        if when>now:continue
        item={'date':day.isoformat(),'close':str(close),'close_time':when.isoformat(),
              'source':row['source'],'currency':row.get('currency')}
        if when in result:raise ValueError('duplicate reader close timestamp')
        result[when]=item
    return [result[key] for key in sorted(result)]


def compute(rows,filed):
    before=[r for r in rows if timestamp(r['close_time'])<filed]
    after=[r for r in rows if timestamp(r['close_time'])>filed]
    if not before or not after:return None
    a,b=before[-1],after[0]
    if a.get('currency') and b.get('currency') and a['currency']!=b['currency']:
        raise ValueError('before/after close currencies differ')
    change=(Decimal(b['close'])/Decimal(a['close'])-1)*100
    return {'before':a,'after':b,'percent':str(change),
            'direction':'up' if change>0 else 'down' if change<0 else 'flat'}


def atomic_write(path,data):
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,indent=2)+'\n')
    os.replace(temp,path)


def refresh(run,now,fetch,offline=False):
    row={'ticker':'not known','filed':None,'view_time':None,'direction':'not computed',
         'reaction':None,'agreement':'not computed','timing':'','eligible':False,'reason':None}
    # A lock serializes reaction writes only; view and worksheet files are read-only.
    with (run/'.reaction.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path=run/'reaction.json';old=read(path) if path.exists() else {}
        try:
            # Resolve issuer separately so a missing filing time still prints it.
            facts=read(run/'facts.json') if (run/'facts.json').exists() else read(run/'view.json') if (run/'view.json').exists() else {}
            row['ticker']=str(facts.get('ticker') or 'not known')
            view=load_view(run,old)
            if view:
                row.update(view_time=view['time'],direction=view['direction'])
                if view.get('practice') and run.resolve().is_relative_to(DEFAULT_FOLDER.resolve()):
                    row['direction']='not computed'
                    raise ValueError('seeded/practice run is in runs/live; move it to runs/practice')
            ticker,filed=load_identity(run)
            row.update(ticker=ticker,filed=filed.isoformat())
            if filed>now:raise ValueError('filing time is in the future')
            if old and (old.get('ticker')!=ticker or old.get('filing_time')!=filed.isoformat()):
                raise ValueError('reaction belongs to a different issuer or filing; it was not overwritten')
            start=(filed.date()-timedelta(days=10)).isoformat()
            end=now.date().isoformat()
            stored=old.get('reader_rows',[])
            if old.get('status')=='available':
                # Recompute from saved reader evidence; do not rewrite an outcome.
                rows=close_rows(stored,ticker,now)
            else:
                snapshot=run/'market_closes.json'
                rows=[]
                if snapshot.exists():
                    data=read(snapshot)
                    if data.get('ticker')!=ticker or data.get('start','9999')>start or data.get('end','')<end:
                        raise ValueError('saved market_closes.json does not cover the requested reaction window')
                    rows=data.get('rows',[])
                elif not offline:
                    try:rows=fetch(ticker,start,end)
                    except Exception as error:raise ValueError('reader request failed: '+type(error).__name__) from error
                elif stored:
                    rows=stored
                rows=close_rows(rows,ticker,now)
            reaction=compute(rows,filed)
            if old.get('status')=='available' and reaction is None:
                raise ValueError('saved available reaction has incomplete reader evidence')
            if old.get('status')!='available':
                record={'schema_version':1,'ticker':ticker,'filing_time':filed.isoformat(),
                        'view_source':view,'status':'available' if reaction else 'pending',
                        'reader_window':{'start':start,'end':end},'reader_rows':rows,
                        'reaction':reaction,'checked_at':now.isoformat()}
                atomic_write(path,record)
            row['reaction']=reaction
            if not reaction:
                row['reason']='first post-filing close or pre-filing close is not available'
                return row
            if not view:
                row['reason']='no saved, timestamped directional view'
                return row
            after=timestamp(view['time'])>timestamp(reaction['after']['close_time'])
            row['timing']='after' if after else ''
            if view['direction']=='not computed':return row
            row['agreement']='agree' if view['direction']==reaction['direction'] else 'disagree'
            row['eligible']=not after
            return row
        except (OSError,ValueError,KeyError,TypeError,ArithmeticError) as error:
            row['reason']=str(error)
            return row


def report(folder,now,fetch,offline=False):
    rows=[]
    for run in discover(folder):
        try:row=refresh(run,now,fetch,offline)
        except (OSError,ValueError) as error:
            row={'ticker':'not known','filed':None,'view_time':None,'direction':'not computed',
                 'reaction':None,'agreement':'not computed','timing':'','eligible':False,'reason':str(error)}
        row['run']=str(run);rows.append(row)
    return rows


def render(rows):
    lines=['ticker | filing time | view time | direction | reaction | agree/disagree | timing']
    for row in rows:
        reaction=row['reaction']
        label=f"{reaction['direction']} ({Decimal(reaction['percent']):+.4f}%)" if reaction else 'not available'
        lines.append(' | '.join([row['ticker'],row['filed'] or 'not known',row['view_time'] or 'not known',row['direction'],label,row['agreement'],row['timing']]))
    eligible=[r for r in rows if r['eligible']]
    agreements=sum(r['agreement']=='agree' for r in eligible)
    lines.append(f'Agreements: {agreements}/{len(eligible)}'+(f' ({agreements/len(eligible):.1%})' if eligible else ' (no eligible reactions)'))
    return '\n'.join(lines)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',nargs='?',type=Path,default=DEFAULT_FOLDER,help='Run folder tree; default: runs/live')
    parser.add_argument('--offline',action='store_true',help='Use saved reader evidence only; make no reader requests')
    args=parser.parse_args(argv)
    if not args.folder.is_dir():parser.error('folder does not exist: '+str(args.folder))
    from closes_reader import daily_closes
    rows=report(args.folder.resolve(),datetime.now(EASTERN),daily_closes,args.offline)
    print(render(rows))
    for row in rows:
        if row['reason']:print(row['run']+': '+row['reason'],file=sys.stderr)
    return 0


if __name__=='__main__':sys.exit(main())
