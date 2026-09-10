"""Standalone LabSpec6 single-spectrum converter. Python 3.9+, standard library only."""
# Adapted from RamanLab utils/labspec6_parser.py (MIT).
# Copyright (c) 2025 Aaron Celestian. See LICENSE for the retained notice.
import argparse
from datetime import datetime
import hashlib
import math
from pathlib import Path
import re
import struct
import sys

SENTINEL = b'\x09\x10\x00\x00'


def parse_l6s(raw):
    """Read the layouts validated in this project; reject ambiguous intensity blocks."""
    if raw[:8] != b'LabSpec6':
        raise ValueError('Not a LabSpec6 file')
    unit = raw.find(b'1/cm')
    if unit < 0:
        raise ValueError('Raman-shift unit label not found')
    x = []
    pos = unit + 4
    while pos + 4 <= len(raw):
        value = struct.unpack_from('<f', raw, pos)[0]
        if not 40 < value < 5000:
            if x:
                break
            pos += 4
            continue
        if x and not 0.3 < value - x[-1] < 20:
            break
        x.append(value)
        pos += 4
    if len(x) < 50:
        raise ValueError('Unsupported or incomplete Raman-shift axis (minimum 50 points)')
    # A partial monotonic run must not silently become a truncated spectrum.
    if raw[pos:pos + 4] != SENTINEL:
        raise ValueError('Axis end does not match a block boundary; unsupported or truncated file')
    candidates = set()
    for match in re.finditer(re.escape(b'tam\x00'), raw):
        start = match.start() + 15
        end = start + len(x) * 4
        if raw[end:end + 4] == SENTINEL:
            candidates.add(start)
    pattern = re.escape(SENTINEL) + b'.{4}' + re.escape(b'\xe3tam')
    for match in re.finditer(pattern, raw, re.DOTALL):
        start = match.start() + 24
        end = start + len(x) * 4
        if raw[end:end + 4] == SENTINEL:
            candidates.add(start)
    if len(candidates) != 1:
        raise ValueError('Cannot identify one complete intensity block matching the axis')
    start = candidates.pop()
    y = [v[0] for v in struct.iter_unpack('<f', raw[start:start + len(x) * 4])]
    if not all(math.isfinite(v) for v in y):
        raise ValueError('Non-finite intensity values')
    sample = ''
    film = raw.find(b'film')
    if film >= 0:
        p = film + 16
        # Only decode the name layout actually supported by the parent reader.
        if raw[p:p + 8] == b'Spectrum':
            p = raw.find(b'\x00', p) + 1
            name = bytearray()
            while p + 2 <= len(raw) and raw[p:p + 2] != b'\x00\x00':
                name.extend(raw[p:p + 2])
                p += 2
            try:
                sample = name.decode('utf-16-le')
            except UnicodeDecodeError:
                pass
    return x, y, sample


def convert(source, output=None):
    source = Path(source).resolve()
    if source.suffix.lower() != '.l6s':
        raise ValueError('Only single-spectrum .l6s files are supported')
    raw = source.read_bytes()
    x, y, sample = parse_l6s(raw)
    folder = Path(output).resolve() if output else source.parent / 'txt_export'
    folder.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing exports, including simultaneous runs.
    number = 0
    while True:
        suffix = '' if number == 0 else f'_{number:03d}'
        target = folder / f'{source.stem}{suffix}.txt'
        meta = folder / f'{source.stem}{suffix}.metadata.txt'
        number += 1
        if meta.exists():
            continue
        try:
            stream = target.open('x', encoding='utf-8', newline='\n')
        except FileExistsError:
            continue
        try:
            metadata_stream = meta.open('x', encoding='utf-8', newline='\n')
        except FileExistsError:
            stream.close()
            target.unlink()
            continue
        except Exception:
            stream.close()
            target.unlink()
            raise
        break
    details = {
        'source_file': str(source),
        'source_bytes': len(raw),
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'sample_name': sample or '(not decoded)',
        'data_points': len(x),
        'wavenumber_unit': 'cm^-1',
        'wavenumber_min': x[0],
        'wavenumber_max': x[-1],
        'mean_wavenumber_step': (x[-1] - x[0]) / (len(x) - 1),
        'intensity_min': min(y),
        'intensity_max': max(y),
        'negative_intensity_points': sum(v < 0 for v in y),
        'processing': 'None; decoded float32 values exported with 9 significant digits',
        'converted_at': datetime.now().astimezone().isoformat(),
        'parser': 'Standalone L6S converter 1.0; validated block boundaries',
        'validation': 'Not yet crosschecked against LabSpec6 official TXT export',
        'metadata_scope': 'Basic decoded name and derived statistics only; laser wavelength, power, exposure and acquisition time are NOT decoded',
    }
    try:
        with stream, metadata_stream:
            stream.write('# Wavenumber\tIntensity\n')
            for a, b in zip(x, y):
                stream.write(f'{a:.9g}\t{b:.9g}\n')
            for key, value in details.items():
                metadata_stream.write(f'{key}: {value}\n')
    except Exception:
        stream.close()
        metadata_stream.close()
        target.unlink(missing_ok=True)
        meta.unlink(missing_ok=True)
        raise
    return target, meta, len(x)


def collect(paths, recursive=False):
    files, errors, seen = [], [], set()
    for entry in paths:
        p = Path(entry).expanduser().resolve()
        if p.is_dir():
            try:
                found = sorted((q for q in (p.rglob('*') if recursive else p.iterdir())
                                if q.is_file() and q.suffix.lower() == '.l6s'), key=str)
                if not found:
                    errors.append(f'{p}: no .l6s files found')
            except OSError as exc:
                errors.append(f'{p}: {exc}')
                continue
        else:
            found = [p]
        for q in found:
            if q not in seen:
                seen.add(q)
                files.append(q)
    return files, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', help='One or more .l6s files or folders')
    parser.add_argument('-o', '--output', type=Path, help='Output folder; default: each source folder/txt_export')
    parser.add_argument('-r', '--recursive', action='store_true', help='Include subfolders')
    pick = parser.add_mutually_exclusive_group()
    pick.add_argument('--pick-files', action='store_true')
    pick.add_argument('--pick-folder', action='store_true')
    args = parser.parse_args(argv)
    root = None
    if args.pick_files or args.pick_folder or not args.paths:
        try:
            import tkinter as tk
            from tkinter import filedialog, messagebox
            root = tk.Tk()
            root.withdraw()
            if args.pick_folder:
                choice = filedialog.askdirectory(title='选择含 L6S 文件的文件夹', parent=root)
                selected = [choice] if choice else []
            else:
                selected = list(filedialog.askopenfilenames(title='选择 L6S 文件（可多选）',
                    filetypes=[('LabSpec6 spectrum', '*.l6s'), ('All files', '*.*')], parent=root))
            if not selected:
                root.destroy()
                return 0
            args.paths.extend(selected)
        except Exception as exc:
            if root is not None:
                root.destroy()
            print(f'Cannot open file picker: {exc}. Pass file/folder paths on the command line.', file=sys.stderr)
            return 2
    files, errors = collect(args.paths, args.recursive)
    lines, successful = [], 0
    try:
        for source in files:
            try:
                target, meta, count = convert(source, args.output)
                line = f'OK | {source} -> {target} | {count} points | metadata: {meta}'
                successful += 1
            except Exception as exc:
                line = f'FAILED | {source} | {exc}'
                errors.append(line)
            lines.append(line)
            print(line, flush=True)
        for error in errors:
            if error not in lines:
                print(error, file=sys.stderr)
        summary = f'成功 {successful} 个；失败/路径问题 {len(errors)} 个。'
        print(summary)
        if root is not None:
            destinations = str(args.output.resolve()) if args.output else '各源文件所在目录的 txt_export 子文件夹'
            message = summary + '\n输出：' + destinations
            if errors:
                message += '\n\n' + '\n'.join(errors[:8]) + '\n完整结果见命令行窗口。'
                messagebox.showwarning('L6S → TXT', message, parent=root)
            else:
                messagebox.showinfo('L6S → TXT', message, parent=root)
        return 1 if errors else 0
    finally:
        if root is not None:
            root.destroy()


if __name__ == '__main__':
    sys.exit(main())
