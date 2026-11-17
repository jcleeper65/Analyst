"""Synthetic data only. Never connect to WRDS or print licensed values."""
import io
import tempfile
import unittest
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import wrds_reactions as w


class WrdsReactionTests(unittest.TestCase):
    def test_strict_window_and_exact_close_boundary(self):
        before,after=w.close_window(w.accepted('2025-03-06T16:00:00-05:00'))
        self.assertEqual(before.date(),date(2025,3,5))
        self.assertEqual(after.date(),date(2025,3,7))

    def test_holiday_and_early_close(self):
        before,after=w.close_window(w.accepted('2025-11-26T17:00:00-05:00'))
        self.assertEqual(before.date(),date(2025,11,26))
        self.assertEqual(after.isoformat(),'2025-11-28T18:00:00+00:00')

    def test_edgar_naive_time_is_eastern_not_machine_local(self):
        self.assertEqual(w.accepted('2025-03-06T16:22:00').utcoffset().total_seconds(),-18000)
        with self.assertRaises(ValueError):w.accepted('2025-11-02T01:30:00')
        with self.assertRaises(ValueError):w.accepted('2025-03-09T02:30:00')

    def rows(self):
        return [{'date':date(2025,3,6),'permno':12345,'close':100,'price_flag':'TR'},
                {'date':date(2025,3,7),'permno':12345,'close':104,'price_flag':'TR'},
                {'date':date(2025,3,10),'permno':12345,'close':200,'price_flag':'TR'}]

    def evaluate(self,rows=None):
        return w.calculate('ZZZZ',[w.accepted('2025-03-06T16:22:00')],self.rows() if rows is None else rows,
                           now=datetime(2026,1,1,tzinfo=timezone.utc))

    def test_exact_pair_not_later_available_price(self):
        result=self.evaluate();self.assertEqual(result[0]['reaction'],Decimal(4))

    def test_missing_exact_close_does_not_substitute_another_day(self):
        result=self.evaluate([self.rows()[0],self.rows()[2]])
        self.assertIsNone(result[0]['reaction'])

    def test_bid_ask_flags_negative_nonfinite_and_zero_prices_rejected(self):
        for change in [{'price_flag':'BA'},{'close':-100},{'close':0},{'close':float('nan')}]:
            rows=self.rows();rows[0].update(change)
            with self.subTest(change=change):self.assertIsNone(self.evaluate(rows)[0]['reaction'])

    def test_ambiguous_security_and_identifier_change_rejected(self):
        rows=self.rows();rows[1]['permno']=99999
        self.assertIsNone(self.evaluate(rows)[0]['reaction'])
        rows=self.rows()+[dict(self.rows()[0],permno=99999)]
        self.assertIsNone(self.evaluate(rows)[0]['reaction'])

    def test_median_is_absolute_and_requires_all_releases(self):
        self.assertEqual(w.median_absolute([{'reaction':Decimal(-2)},{'reaction':Decimal(8)}]),Decimal(5))
        self.assertIsNone(w.median_absolute([{'reaction':None},{'reaction':Decimal(8)}]))

    def test_output_shape_one_row_each_then_median(self):
        result=self.evaluate()*8
        lines=w.render(result).splitlines()
        self.assertEqual(len(lines),9)
        self.assertTrue(lines[-1].startswith('Median absolute reaction'))

    def test_status_mode_prints_counts_not_values(self):
        text=w.status(self.evaluate())
        self.assertIn('rows=1',text);self.assertIn('complete=1',text)
        self.assertNotIn('100',text);self.assertNotIn('104',text)
        self.assertNotIn('4.000',text)

    def test_query_is_parameterized_and_uses_historical_ticker_dates(self):
        db=Mock();db.raw_sql.return_value.to_dict.return_value=self.rows()
        w.fetch(db,'ZZZZ',[date(2025,3,6),date(2025,3,7)],'crsp')
        query=db.raw_sql.call_args.args[0];params=db.raw_sql.call_args.kwargs['params']
        self.assertNotIn('ZZZZ',query);self.assertEqual(params['ticker'],'ZZZZ')
        self.assertIn('secinfostartdt',query);self.assertIn('secinfoenddt',query)
        self.assertIn('dlyprcflg',query);self.assertIn('ANY',query)
        with self.assertRaises(ValueError):w.fetch(db,'ZZZZ',[],'crsp; drop table x')

    def test_private_output_cannot_be_written_into_repository(self):
        with self.assertRaises(ValueError):w.private_output(w.ROOT/'exports/test.txt','synthetic')

    def test_private_output_permissions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'result.txt';w.private_output(path,'synthetic')
            self.assertEqual(path.stat().st_mode&0o777,0o600)
            with self.assertRaises(FileExistsError):w.private_output(path,'changed')

    def test_duplicate_release_timestamps_rejected(self):
        with self.assertRaises(ValueError):w.release_times(['2025-03-06T16:22:00']*2)

    def test_database_permission_error_is_clear_without_query_or_values(self):
        class Denied(Exception):
            orig=type('DatabaseError',(),{'pgcode':'42501'})()
        db=Mock();db.raw_sql.side_effect=Denied('SECRET_QUERY_AND_LICENSED_VALUES')
        with self.assertRaises(w.DatabaseFailure) as error:
            w.fetch(db,'ZZZZ',[date(2025,3,6)],'crsp_m_stock')
        self.assertIn('permission denied',str(error.exception))
        self.assertNotIn('SECRET_QUERY',str(error.exception))

    def test_unknown_database_error_does_not_expose_its_message(self):
        db=Mock();db.raw_sql.side_effect=RuntimeError('SECRET_QUERY_AND_LICENSED_VALUES')
        with self.assertRaises(w.DatabaseFailure) as error:
            w.fetch(db,'ZZZZ',[date(2025,3,6)],'crsp')
        self.assertNotIn('SECRET_QUERY',str(error.exception))


if __name__=='__main__':unittest.main()
