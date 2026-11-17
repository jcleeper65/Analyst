"""Saved screens remain readable after lossless gzip compression."""
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desk_parts import copy_saved_json,latest_screen,read_saved_json


class CompressedScreenTests(unittest.TestCase):
    def test_old_json_path_resolves_compressed_registry_and_copies_plain_json(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);original=root/'registry.json';data={'candidates':{'123':{'name':'Example'}}}
            with gzip.open(str(original)+'.gz','wt',encoding='utf-8') as output:json.dump(data,output)
            self.assertEqual(read_saved_json(original),data)
            copied=root/'copied.json';copy_saved_json(original,copied)
            self.assertEqual(json.loads(copied.read_text()),data)

    def test_latest_screen_compares_plain_and_compressed_run_times(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'Spinoffs, older.json').write_text(json.dumps({'run_time':'2026-11-11T09:00:00-05:00','registry':{}}))
            latest=root/'Spinoffs, newer.json.gz'
            with gzip.open(latest,'wt',encoding='utf-8') as output:
                json.dump({'run_time':'2026-11-12T09:00:00-05:00','registry':{}},output)
            self.assertEqual(latest_screen(root),latest)

    def test_plain_registry_takes_precedence_when_both_exist(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'registry.json';path.write_text('{"version":2}')
            with gzip.open(str(path)+'.gz','wt') as output:output.write('{"version":1}')
            self.assertEqual(read_saved_json(path),{'version':2})
