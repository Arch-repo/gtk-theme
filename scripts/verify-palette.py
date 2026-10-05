#!/usr/bin/env python3
"""Check modern and compatibility artifacts, semantic coverage and safe input."""
from pathlib import Path
import importlib.util
import json
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('palette', ROOT / 'palette/render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
PALETTE = json.loads((ROOT / 'palette/default.json').read_text())
MATERIAL = json.loads((ROOT / 'palette/material.json').read_text())


class Palette(unittest.TestCase):
    def test_modern_and_legacy_runtime_paths(self):
        for modern in (True, False):
            with tempfile.TemporaryDirectory() as folder:
                output = Path(folder)
                renderer.render(PALETTE, MATERIAL, output, gtk4_modern=modern)
                gtk3 = (output / 'gtk-3.0/palette.css').read_text()
                gtk4 = (output / 'gtk-4.0/palette.css').read_text()
                self.assertNotIn('{{', gtk3 + gtk4)
                self.assertIn(PALETTE['accent'], gtk3 + gtk4)
                self.assertEqual(':root' in gtk4, modern)
                if modern:
                    for group, fields in {
                        'accent': ('bg', 'fg'), 'window': ('bg', 'fg'),
                        'view': ('bg', 'fg'), 'headerbar': ('bg', 'fg', 'border', 'backdrop', 'shade', 'darker-shade'),
                        'sidebar': ('bg', 'fg', 'backdrop', 'border', 'shade'),
                        'secondary-sidebar': ('bg', 'fg', 'backdrop', 'border', 'shade'),
                        'card': ('bg', 'fg', 'shade'), 'overview': ('bg', 'fg'),
                        'thumbnail': ('bg', 'fg'), 'active-toggle': ('bg', 'fg'),
                        'dialog': ('bg', 'fg'), 'popover': ('bg', 'fg', 'shade'),
                        'destructive': ('bg', 'fg'), 'success': ('bg', 'fg'),
                        'warning': ('bg', 'fg'), 'error': ('bg', 'fg'),
                    }.items():
                        for field in fields:
                            self.assertIn('--' + group + '-' + field + '-color:', gtk4)
                    self.assertNotIn('--disabled-opacity:', gtk4)
                    self.assertNotIn('--document-font-family:', gtk4)
                else:
                    for text in (gtk4, (output / 'gtk-4.0/base.css').read_text()):
                        self.assertNotRegex(text, r'var\(|color-mix\(|--[a-z-]+\s*:')
                self.assertTrue((output / 'COPYING').is_file())
                self.assertIn('@import url("palette.css")', (output / 'gtk-3.0/gtk.css').read_text())

    def test_bad_palette_and_material_are_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'theme'
            for palette, material in (({**PALETTE, 'accent': 'red; color: white'}, MATERIAL),
                                      (PALETTE, {**MATERIAL, 'material': {'opacity': True}}),
                                      (PALETTE, {**MATERIAL, 'radius': {'control': -5}})):
                with self.assertRaises(ValueError):
                    renderer.render(palette, material, output)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
