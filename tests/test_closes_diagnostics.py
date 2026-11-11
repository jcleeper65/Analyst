"""Reader diagnostics use fake subprocesses and keys, with no LSEG requests."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('reader_diagnostics',Path(__file__).resolve().parents[1]/'closes_reader.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)


class DiagnosticsTests(TestCase):
    def test_lseg_211_uses_supported_header_type_argument(self):
        import sys
        from types import ModuleType
        from unittest.mock import Mock
        package=ModuleType('lseg');sdk=ModuleType('lseg.data');package.data=sdk
        session=Mock()
        sdk.session=SimpleNamespace(desktop=SimpleNamespace(Definition=lambda **kwargs:SimpleNamespace(get_session=lambda:session)),set_default=Mock())
        sdk.HeaderType=SimpleNamespace(NAME='field_names')
        calls=[]
        def get_data(universe,fields,parameters,header_type):
            calls.append(header_type)
            return SimpleNamespace(empty=False,columns=['TR.PRICECLOSE.DATE','TR.PRICECLOSE'],iterrows=lambda:iter([(0,{'TR.PRICECLOSE.DATE':'2026-01-02','TR.PRICECLOSE':12})]))
        sdk.get_data=get_data
        with patch.dict(sys.modules,{'lseg':package,'lseg.data':sdk}):
            rows=reader._lseg_rows('ZZZ','2026-01-01','2026-01-02','fake-key')
        self.assertEqual(calls,['field_names']);self.assertEqual(rows['rows'],[{'date':'2026-01-02','close':12}]);self.assertEqual(rows['instrument'],'ZZZ')
        session.close.assert_called_once()

    def test_ticker_resolution_uses_unique_vendor_ric(self):
        from unittest.mock import Mock
        converter=SimpleNamespace(SymbolTypes=SimpleNamespace(TICKER_SYMBOL='ticker',RIC='ric'),AssetClass=SimpleNamespace(EQUITIES='equities'),Definition=Mock())
        frame=SimpleNamespace(columns=['RIC'],__unused__=None)
        class Frame:
            columns=['RIC']
            def __getitem__(self,key):return ['ZZZ.N','ZZZ.N']
        converter.Definition.return_value.get_data.return_value=SimpleNamespace(data=SimpleNamespace(df=Frame()))
        sdk=SimpleNamespace(content=SimpleNamespace(symbol_conversion=converter))
        self.assertEqual(reader._resolve_ticker(sdk,'ZZZ'),'ZZZ.N')
        self.assertEqual(converter.Definition.call_args.kwargs['preferred_country_code'],'USA')

    def test_ambiguous_symbol_resolution_is_logged_as_failure(self):
        from unittest.mock import Mock
        class Frame:
            columns=['RIC']
            def __getitem__(self,key):return ['ZZZ.N','ZZZ.O']
        converter=SimpleNamespace(SymbolTypes=SimpleNamespace(TICKER_SYMBOL='ticker',RIC='ric'),AssetClass=SimpleNamespace(EQUITIES='equities'),Definition=Mock())
        converter.Definition.return_value.get_data.return_value=SimpleNamespace(data=SimpleNamespace(df=Frame()))
        with self.assertRaises(ValueError):reader._resolve_ticker(SimpleNamespace(content=SimpleNamespace(symbol_conversion=converter)),'ZZZ')

    def test_resolved_instrument_is_preserved_in_price_source(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'errors.jsonl'
            worker=SimpleNamespace(returncode=0,stdout=json.dumps({'rows':[{'date':'2026-01-02','close':12}],'instrument':'ZZZ.N'}),stderr='')
            with patch.object(reader,'_settings',return_value={'LSEG_APP_KEY':'fake-key-123','LSEG_DIAGNOSTICS_FILE':str(path)}),patch.object(reader.subprocess,'run',return_value=worker):
                result=reader.daily_closes('ZZZ','2026-01-01','2026-01-02')
            self.assertIn('ZZZ.N',result[0]['source'])

    def test_worker_session_error_is_logged_and_key_is_redacted(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'diagnostics.jsonl'
            config={'LSEG_APP_KEY':'fake-private-key-123','LSEG_DIAGNOSTICS_FILE':str(path)}
            worker=SimpleNamespace(returncode=0,stdout=json.dumps({'rows':[], 'error':{'stage':'session_open','type':'RuntimeError','message':'Rejected fake-private-key-123'}}),stderr='')
            with patch.object(reader,'_settings',return_value=config),patch.object(reader.subprocess,'run',return_value=worker):
                self.assertEqual(reader.daily_closes('ZZZ','2026-01-01','2026-01-02'),'not available')
            event=json.loads(path.read_text())
            self.assertEqual(event['stage'],'session_open')
            self.assertNotIn('fake-private-key-123',path.read_text())
            self.assertEqual(event['ticker'],'ZZZ')

    def test_empty_response_is_distinct_from_sdk_failure(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'diagnostics.jsonl'
            worker=SimpleNamespace(returncode=0,stdout=json.dumps({'rows':[]}),stderr='')
            with patch.object(reader,'_settings',return_value={'LSEG_APP_KEY':'fake-key-123','LSEG_DIAGNOSTICS_FILE':str(path)}),patch.object(reader.subprocess,'run',return_value=worker):
                self.assertEqual(reader.daily_closes('ZZZ','2026-01-01','2026-01-02'),'not available')
            self.assertEqual(json.loads(path.read_text())['stage'],'empty_response')

    def test_success_returns_dated_rows_and_does_not_log_an_error(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'diagnostics.jsonl'
            worker=SimpleNamespace(returncode=0,stdout=json.dumps({'rows':[{'date':'2026-01-02','close':12}]}),stderr='')
            with patch.object(reader,'_settings',return_value={'LSEG_APP_KEY':'fake-key-123','LSEG_DIAGNOSTICS_FILE':str(path)}),patch.object(reader.subprocess,'run',return_value=worker):
                result=reader.daily_closes('ZZZ','2026-01-01','2026-01-02')
            self.assertEqual(result[0]['close'],12)
            self.assertFalse(path.exists())

    def test_worker_stderr_is_sanitized(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'diagnostics.jsonl'
            worker=SimpleNamespace(returncode=1,stdout='',stderr='Authorization: Bearer pretendtoken\nAPI key fake-key-123 invalid')
            with patch.object(reader,'_settings',return_value={'LSEG_APP_KEY':'fake-key-123','LSEG_DIAGNOSTICS_FILE':str(path)}),patch.object(reader.subprocess,'run',return_value=worker):
                reader.daily_closes('ZZZ','2026-01-01','2026-01-02')
            text=path.read_text();self.assertNotIn('pretendtoken',text);self.assertNotIn('fake-key-123',text)
            self.assertEqual(json.loads(text)['stage'],'worker_exit')
