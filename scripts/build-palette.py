#!/usr/bin/env python3
"""Compile the GTK base once and write a deterministic runtime resource archive."""
from pathlib import Path
import gzip
import io
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='anto-gtk-build-') as folder:
    temp = Path(folder)
    checkout = temp / 'source'
    shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns('.git', '.github', 'release', 'palette', '__pycache__'))
    subprocess.run(['bash', str(checkout / 'install-anto426.sh'), '-d', str(temp / 'themes'), '--round', '12px'], check=True)
    base = temp / 'themes/Anto426-Dark'
    with (ROOT / 'palette/base.tar.gz').open('wb') as output:
        with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for source in sorted(base.rglob('*')):
                    relative = source.relative_to(base)
                    if not source.is_file() or relative.parts[0] not in ('gtk-3.0', 'gtk-4.0'):
                        continue
                    data = source.read_bytes()
                    info = tarfile.TarInfo(str(relative))
                    info.size, info.mode, info.mtime = len(data), 0o644, 0
                    archive.addfile(info, io.BytesIO(data))
