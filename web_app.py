"""Local browser interface; runs the existing command unchanged in a subprocess."""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'equity_research_output'
JOBS = {}
LOCK = threading.Lock()
MARKDOWN = MarkdownIt('commonmark', {'html': False}).enable('table')


def run_job(job_id, arguments):
    report_path = None
    try:
        process = subprocess.Popen([sys.executable, '-u', str(ROOT / 'equity_research_desk.py'), *arguments],
                                   cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, env={**os.environ, 'NO_COLOR': '1'})
        for raw in process.stdout:
            line = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', raw).strip()
            with LOCK:
                job = JOBS[job_id]
                if line.startswith('Node starting:'):
                    job['nodes'].append(line.removeprefix('Node starting:').strip())
                if line.startswith('Error:'):
                    job['error'] = line.removeprefix('Error:').strip()
                if line.startswith('Verified report:'):
                    report_path = Path(line.removeprefix('Verified report:').strip()).resolve()
        result = process.wait()
        if result != 0:
            raise RuntimeError(JOBS[job_id]['error'] or 'The run stopped before verification completed.')
        if not report_path or not report_path.is_relative_to(OUTPUT.resolve()) or not report_path.is_file():
            raise RuntimeError('The process finished without a saved verified report.')
        report = report_path.read_text(encoding='utf-8')
        marks_path = report_path.parent / 'nodes/Verifier/output.json'
        marks = json.loads(marks_path.read_text()) if marks_path.exists() else {}
        model_checks = marks.get('model_checks', {}).get('checks', [])
        summary = {status: sum(c.get('status') == status for c in model_checks)
                   for status in ('correct', 'wrong', 'unsupported')}
        with LOCK:
            JOBS[job_id].update(status='complete', report=report,
                                report_html=MARKDOWN.render(report), marks=summary,
                                report_name=report_path.parent.name)
    except Exception as error:
        with LOCK:
            JOBS[job_id].update(status='failed', error=str(error))


def validate_inputs(data):
    ticker = str(data.get('ticker', '')).strip().upper()
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9.\-]{0,19}', ticker):
        raise ValueError('Enter a valid ticker symbol.')
    peers = re.split(r'[,\s]+', str(data.get('peers', '')).strip().upper())
    peers = [p for p in peers if p]
    if len(peers) > 20 or any(not re.fullmatch(r'[A-Z0-9][A-Z0-9.\-]{0,19}', p) for p in peers):
        raise ValueError('Enter up to 20 peer tickers, separated by spaces or commas.')
    filed = str(data.get('filed', '')).strip()
    if filed:
        from closes_reader import filing_time
        filing_time(filed)
    return [ticker, '--peers', *peers] + (['--filed', filed] if filed else [])



class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type='application/json'):
        payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == '/':
            return self.respond(200, (ROOT / 'web/index.html').read_text(), 'text/html')
        if self.path.startswith('/api/runs/'):
            job_id = self.path.removeprefix('/api/runs/')
            with LOCK:
                job = JOBS.get(job_id)
                return self.respond(200, job) if job else self.respond(404, {'error': 'Run not found.'})
        self.respond(404, {'error': 'Not found.'})

    def do_POST(self):
        if self.path != '/api/runs':
            return self.respond(404, {'error': 'Not found.'})
        # Only the same-origin local page can start a run.
        if self.headers.get('Origin') != 'http://' + self.headers.get('Host', ''):
            return self.respond(403, {'error': 'Open the local page to start a run.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192:
                raise ValueError('Invalid request size.')
            args = validate_inputs(json.loads(self.rfile.read(length)))
            with LOCK:
                if any(job['status'] == 'running' for job in JOBS.values()):
                    return self.respond(409, {'error': 'A run is already active. Wait for it to finish.'})
                job_id = uuid.uuid4().hex
                JOBS[job_id] = {'status': 'running', 'nodes': [], 'error': ''}
            threading.Thread(target=run_job, args=(job_id, args), daemon=True).start()
            self.respond(202, {'id': job_id})
        except (ValueError, TypeError, AttributeError) as error:
            self.respond(400, {'error': str(error)})


def main():
    parser = argparse.ArgumentParser(description='Start the local equity research page.')
    parser.add_argument('--port', type=int, default=8501)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Equity research page: {url}', flush=True)
    if not args.no_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
