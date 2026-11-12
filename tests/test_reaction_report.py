import hashlib,json,sys,tempfile,unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock,patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import reaction_report as r


class ReactionReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.now=r.timestamp('2026-11-12T17:00:00-05:00')
        self.fetch=Mock(return_value=[
            {'date':'2026-11-10','close':100,'source':'invented reader','currency':'USD'},
            {'date':'2026-11-11','close':110,'source':'invented reader','currency':'USD'},
            {'date':'2026-11-12','close':120,'source':'invented reader','currency':'USD'}])

    def run_dir(self,name='run',filed='2026-11-10T17:00:00-05:00',view='2026-11-11T09:00:00-05:00',direction='up'):
        p=self.root/name;p.mkdir(parents=True)
        (p/'facts.json').write_text(json.dumps({'ticker':'TEST'}))
        (p/'filing_time.json').write_text(json.dumps({'effective_filed_eastern':filed}))
        (p/'view.json').write_text(json.dumps({'view_time':view,'direction':direction}))
        return p

    def refresh(self,p,**kwargs):return r.refresh(p,self.now,self.fetch,**kwargs)

    def test_reaction_is_first_close_after_not_latest(self):
        p=self.run_dir();row=self.refresh(p)
        self.assertEqual(row['reaction']['percent'],'10.0')
        self.assertEqual(row['reaction']['after']['date'],'2026-11-11')
        self.assertEqual(row['agreement'],'agree');self.assertTrue(row['eligible'])

    def test_view_bytes_and_modification_time_never_change(self):
        p=self.run_dir();paths=[p/'view.json',p/'facts.json',p/'filing_time.json']
        before={str(x):(x.read_bytes(),x.stat().st_mtime_ns) for x in paths}
        self.refresh(p)
        for x in paths:self.assertEqual(before[str(x)],(x.read_bytes(),x.stat().st_mtime_ns))

    def test_pending_is_filled_when_new_close_arrives(self):
        p=self.run_dir();self.fetch.return_value=self.fetch.return_value[:1]
        self.assertIsNone(self.refresh(p)['reaction'])
        self.assertEqual(json.loads((p/'reaction.json').read_text())['status'],'pending')
        self.fetch.return_value+=[{'date':'2026-11-11','close':110,'source':'invented reader'}]
        self.assertEqual(self.refresh(p)['agreement'],'agree')
        self.assertEqual(json.loads((p/'reaction.json').read_text())['status'],'available')

    def test_complete_reaction_is_not_fetched_or_rewritten(self):
        p=self.run_dir();self.refresh(p);path=p/'reaction.json'
        before=(path.read_bytes(),path.stat().st_mtime_ns)
        self.fetch.reset_mock();self.refresh(p)
        self.fetch.assert_not_called();self.assertEqual(before,(path.read_bytes(),path.stat().st_mtime_ns))

    def test_after_view_is_labeled_and_excluded(self):
        row=self.refresh(self.run_dir(view='2026-11-11T16:00:01-05:00'))
        self.assertEqual(row['timing'],'after');self.assertEqual(row['agreement'],'agree')
        self.assertFalse(row['eligible']);self.assertIn('Agreements: 0/0',r.render([row]))

    def test_view_exactly_at_close_is_not_after(self):
        row=self.refresh(self.run_dir(view='2026-11-11T16:00:00-05:00'))
        self.assertEqual(row['timing'],'');self.assertTrue(row['eligible'])

    def test_not_computed_view_does_not_enter_denominator(self):
        row=self.refresh(self.run_dir(direction='not computed'))
        self.assertIsNotNone(row['reaction']);self.assertFalse(row['eligible'])
        self.assertEqual(row['agreement'],'not computed')

    def test_agreement_count_excludes_after_missing_and_not_computed(self):
        self.run_dir('agree');self.run_dir('disagree',direction='down')
        self.run_dir('after',view='2026-11-12T12:00:00-05:00')
        self.run_dir('unknown',direction='not computed')
        p=self.run_dir('missing');(p/'filing_time.json').unlink()
        rows=r.report(self.root,self.now,self.fetch)
        self.assertEqual(len(rows),5)
        self.assertEqual(r.render(rows).splitlines()[-1],'Agreements: 1/2 (50.0%)')

    def test_flat_only_agrees_with_flat(self):
        self.fetch.return_value[1]['close']=100
        self.assertEqual(self.refresh(self.run_dir('flat',direction='flat'))['agreement'],'agree')
        self.assertEqual(self.refresh(self.run_dir('up',direction='up'))['agreement'],'disagree')

    def test_no_completed_post_close_does_not_use_future_observation(self):
        self.now=r.timestamp('2026-11-11T15:59:59-05:00')
        self.assertIsNone(self.refresh(self.run_dir())['reaction'])

    def test_premarket_uses_same_day_close(self):
        row=self.refresh(self.run_dir(filed='2026-11-11T08:00:00-05:00'))
        self.assertEqual(row['reaction']['after']['date'],'2026-11-11')

    def test_weekend_uses_actual_next_reader_close(self):
        self.now=r.timestamp('2026-11-17T17:00:00-05:00')
        self.fetch.return_value=[{'date':'2026-11-13','close':100,'source':'invented'},
                                 {'date':'2026-11-16','close':101,'source':'invented'}]
        row=self.refresh(self.run_dir(filed='2026-11-14T10:00:00-05:00',view='2026-11-16T09:00:00-05:00'))
        self.assertEqual(row['reaction']['after']['date'],'2026-11-16')

    def test_timezone_equivalent_view_is_not_after(self):
        row=self.refresh(self.run_dir(view='2026-11-11T21:00:00Z'))
        self.assertTrue(row['eligible'])

    def test_explicit_early_close_time_is_respected(self):
        self.fetch.return_value[1]['close_time']='2026-11-11T13:00:00-05:00'
        row=self.refresh(self.run_dir(view='2026-11-11T14:00:00-05:00'))
        self.assertEqual(row['timing'],'after')

    def test_missing_filing_time_is_not_inferred_from_run_time(self):
        p=self.run_dir();(p/'filing_time.json').unlink()
        (p/'run_identity.json').write_text(json.dumps({'run_time':'2026-11-10T17:00:00-05:00'}))
        row=self.refresh(p);self.assertIsNone(row['filed']);self.fetch.assert_not_called()

    def test_earliest_worksheet_is_used_including_not_computed(self):
        p=self.run_dir();(p/'view.json').unlink()
        for name,when,direction in [('first','2026-11-11T08:00:00-05:00','not computed'),('later','2026-11-11T09:00:00-05:00','more than the price')]:
            (p/f'Spinoff worksheet, {name}.json').write_text(json.dumps({'worksheet_time':when,'view':{'direction':direction}}))
        self.assertEqual(self.refresh(p)['direction'],'not computed')

    def test_frozen_view_is_not_replaced_by_new_worksheet(self):
        p=self.run_dir();self.refresh(p)
        (p/'Spinoff worksheet, later.json').write_text(json.dumps({'worksheet_time':'2026-11-11T08:00:00-05:00','view':{'direction':'down'}}))
        self.assertEqual(self.refresh(p)['direction'],'up')

    def test_changed_view_is_rejected_without_rewriting_reaction(self):
        p=self.run_dir();self.refresh(p);before=(p/'reaction.json').read_bytes()
        (p/'view.json').write_text(json.dumps({'view_time':'2026-11-11T08:00:00-05:00','direction':'down'}))
        row=self.refresh(p);self.assertIn('saved view changed',row['reason']);self.assertFalse(row['eligible'])
        self.assertEqual((p/'reaction.json').read_bytes(),before)

    def test_changed_filing_is_not_silently_associated_with_old_reaction(self):
        p=self.run_dir();self.refresh(p)
        (p/'filing_time.json').write_text(json.dumps({'effective_filed_eastern':'2026-11-10T18:00:00-05:00'}))
        row=self.refresh(p);self.assertIn('different issuer or filing',row['reason'])

    def test_duplicate_dates_or_currency_mismatch_do_not_produce_reaction(self):
        p=self.run_dir();self.fetch.return_value*=2
        self.assertIsNone(self.refresh(p)['reaction'])
        self.fetch.return_value=self.fetch.return_value[:3];self.fetch.return_value[1]['currency']='EUR'
        self.assertIsNone(self.refresh(p)['reaction'])

    def test_offline_snapshot_fills_without_reader_call(self):
        p=self.run_dir()
        (p/'market_closes.json').write_text(json.dumps({'ticker':'TEST','start':'2026-10-01','end':'2026-11-30','rows':self.fetch.return_value}))
        self.assertEqual(self.refresh(p,offline=True)['agreement'],'agree');self.fetch.assert_not_called()

    def test_discovery_stops_at_run_and_does_not_count_node_facts(self):
        p=self.run_dir('nested/run');child=p/'nodes';child.mkdir();(child/'facts.json').write_text('{}')
        self.assertEqual(r.discover(self.root),[p])

    def test_no_view_still_fills_reaction_without_scoring(self):
        p=self.run_dir();(p/'view.json').unlink()
        row=self.refresh(p);self.assertIsNotNone(row['reaction']);self.assertFalse(row['eligible'])

    def test_seeded_output_is_excluded_if_put_in_live(self):
        p=self.run_dir('live/seeded')
        data=json.loads((p/'view.json').read_text());data['artifact_type']='seeded_test'
        (p/'view.json').write_text(json.dumps(data))
        with patch.object(r,'DEFAULT_FOLDER',self.root/'live'):
            row=self.refresh(p)
        self.assertFalse(row['eligible']);self.assertIn('seeded/practice',row['reason'])
        self.fetch.assert_not_called()

    def test_reader_failure_keeps_one_row_and_can_retry(self):
        p=self.run_dir();self.fetch.side_effect=RuntimeError('offline reader')
        rows=r.report(self.root,self.now,self.fetch)
        self.assertEqual(len(rows),1);self.assertIn('reader request failed',rows[0]['reason'])
        self.fetch.side_effect=None
        self.assertEqual(self.refresh(p)['agreement'],'agree')

    def test_delayed_first_reaction_is_not_cut_off_after_two_weeks(self):
        self.now=r.timestamp('2026-12-02T17:00:00-05:00')
        self.fetch.return_value=[{'date':'2026-11-10','close':100,'source':'invented'},
                                 {'date':'2026-12-01','close':101,'source':'invented'}]
        row=self.refresh(self.run_dir())
        self.assertEqual(row['reaction']['after']['date'],'2026-12-01')
        self.assertEqual(self.fetch.call_args.args[2],'2026-12-02')

    def test_malformed_run_is_not_omitted(self):
        p=self.run_dir();(p/'facts.json').write_text('[]')
        rows=r.report(self.root,self.now,self.fetch)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['direction'],'not computed')

    def test_cli_offline_prints_one_row_per_run_and_final_count(self):
        p=self.run_dir()
        (p/'market_closes.json').write_text(json.dumps({'ticker':'TEST','start':'2026-10-01','end':'2026-11-30','rows':self.fetch.return_value}))
        from io import StringIO
        output=StringIO()
        with patch.object(r,'datetime',wraps=datetime) as clock,patch('sys.stdout',output):
            clock.now.return_value=self.now
            self.assertEqual(r.main([str(self.root),'--offline']),0)
        lines=output.getvalue().splitlines()
        self.assertEqual(len(lines),3);self.assertIn('TEST |',lines[1])
        self.assertEqual(lines[-1],'Agreements: 1/1 (100.0%)')


if __name__=='__main__':unittest.main()
