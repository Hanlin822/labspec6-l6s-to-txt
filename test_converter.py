import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest

from l6s_to_txt import SENTINEL, collect, convert, main, parse_l6s


def fixture(legacy=False):
    x = [200 + i * 1.5 for i in range(60)]
    y = [80 + i / 8 for i in range(60)]
    header = (b'tam\x00' + bytes(11) if legacy else
              SENTINEL + bytes(4) + b'\xe3tam' + b'\xf6\x7f\x00\x00' + bytes(8))
    raw = b'LabSpec6' + header + struct.pack('<60f', *y) + SENTINEL
    raw += b'1/cm' + struct.pack('<60f', *x) + SENTINEL
    return raw, x, y


class ConverterTests(unittest.TestCase):
    def test_both_layouts_and_export_roundtrip(self):
        for legacy in [False, True]:
            raw, x, y = fixture(legacy)
            self.assertEqual(parse_l6s(raw)[:2], (x, y))
            with tempfile.TemporaryDirectory() as folder:
                source = Path(folder) / '中文 1% 样本.l6s'
                source.write_bytes(raw)
                output, metadata, count = convert(source)
                rows = [tuple(map(float, line.split())) for line in output.read_text().splitlines()[1:]]
                self.assertEqual(rows, list(zip(x, y)))
                self.assertEqual(count, 60)
                self.assertIn('source_sha256:', metadata.read_text(encoding='utf-8'))
                self.assertEqual(source.read_bytes(), raw)

    def test_does_not_overwrite_existing_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 's.l6s'
            source.write_bytes(fixture()[0])
            first, meta, _ = convert(source)
            first.write_text('keep me')
            second, _, _ = convert(source)
            self.assertEqual(first.read_text(), 'keep me')
            self.assertNotEqual(first, second)
            self.assertTrue(meta.exists())

    def test_truncation_nonfinite_and_ambiguity(self):
        raw, _, y = fixture()
        for bad in (raw[:-5], b'bad', raw.replace(struct.pack('<60f', *y), struct.pack('<60f', *([float('nan')] * 60)))):
            with self.assertRaises(ValueError):
                parse_l6s(bad)
        with self.assertRaises(ValueError):
            parse_l6s(raw + raw)

    def test_batch_continues_after_failure_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'valid.L6S'
            source.write_bytes(fixture()[0])
            bad = Path(folder) / 'bad.l6s'
            bad.write_bytes(b'bad')
            files, _ = collect([folder, str(source)])
            self.assertEqual(len(files), 2)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(bad), str(source)]), 1)
            self.assertTrue((Path(folder) / 'txt_export' / 'valid.txt').exists())
            self.assertFalse((Path(folder) / 'txt_export' / 'bad.txt').exists())


if __name__ == '__main__':
    unittest.main()
