import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('web_app', Path(__file__).resolve().parents[1] / 'web_app.py')
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)


class WebAppTests(unittest.TestCase):
    def test_peer_input_and_price(self):
        args = web.validate_inputs({'ticker': 'abc', 'peers': 'def, ghi', 'price': '10.25'})
        self.assertEqual(args, ['ABC', '--peers', 'DEF', 'GHI', '--price', '10.25'])

    def test_invalid_inputs(self):
        for values in ({'ticker': '; exit', 'price': 10}, {'ticker': 'ABC', 'price': 'nan'}, {'ticker': 'ABC', 'price': -1}):
            with self.assertRaises(ValueError):
                web.validate_inputs(values)

    def test_progress_report_and_marks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / 'verified_report.md'
            report.write_text('| Claim | Mark |\n|---|---|\n| EPS | wrong |\n\n<script>bad()</script>')
            marks = root / 'nodes/Verifier/output.json'
            marks.parent.mkdir(parents=True)
            marks.write_text(json.dumps({'model_checks': {'checks': [{'status': 'wrong'}]}}))
            web.JOBS['test'] = {'status': 'running', 'nodes': [], 'error': ''}
            process = type('Process', (), {'stdout': io.StringIO(f'Node starting: Research Analyst 1\nNode starting: Verifier 1\nVerified report: {report}\n'), 'wait': lambda self: 0})()
            with patch.object(web, 'OUTPUT', root), patch.object(web.subprocess, 'Popen', return_value=process):
                web.run_job('test', ['ABC'])
            job = web.JOBS['test']
            self.assertEqual(job['status'], 'complete')
            self.assertEqual(job['nodes'], ['Research Analyst 1', 'Verifier 1'])
            self.assertEqual(job['marks']['wrong'], 1)
            self.assertIn('<table>', job['report_html'])
            self.assertNotIn('<script>', job['report_html'])

    def test_failed_run_is_not_complete(self):
        web.JOBS['fail'] = {'status': 'running', 'nodes': [], 'error': ''}
        process = type('Process', (), {'stdout': io.StringIO('Error: Provider unavailable\n'), 'wait': lambda self: 1})()
        with patch.object(web.subprocess, 'Popen', return_value=process):
            web.run_job('fail', ['ABC'])
        self.assertEqual(web.JOBS['fail']['status'], 'failed')
        self.assertIn('Provider unavailable', web.JOBS['fail']['error'])
