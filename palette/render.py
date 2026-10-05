#!/usr/bin/env python3
"""Render the maintained GTK base and current GTK/libadwaita role overlays."""
from pathlib import Path
import argparse
import ctypes
import ctypes.util
import json
import re
import tarfile

ROOT = Path(__file__).resolve().parent


def modern_gtk4():
    """Inspect the runtime, including systems without pkg-config/dev packages."""
    library = ctypes.util.find_library('gtk-4')
    return not library or ctypes.CDLL(library).gtk_get_minor_version() >= 16


def render(palette, material, output, gtk4_modern=True):
    roles = dict(palette)
    for name, value in roles.items():
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"Invalid palette role: {name}")
    for name, fallback in (("titlebar", "surface"), ("titlebar_backdrop", "base_alt"), ("popover", "surface")):
        roles.setdefault(name, roles[fallback])
    opacity = material["material"]["opacity"]
    if type(opacity) not in (float, int) or not 0 < opacity <= 1:
        raise ValueError("Invalid material opacity")
    radius = material['radius']['control']
    if type(radius) not in (float, int) or not 0 < radius <= 64:
        raise ValueError('Invalid control radius')
    alphas = dict(window=opacity, view=opacity * .4, sidebar=opacity * .7,
                  header=opacity, popover=1, dialog=1)
    roles['control_radius'] = str(radius)
    def rgba(role, alpha):
        color = roles[role]
        return "rgba(" + ", ".join(str(int(color[i:i + 2], 16)) for i in (1, 3, 5)) + f", {alpha:.4g})"
    def substitute(text):
        def value(match):
            name = match[1]
            if name.startswith("rgba_"):
                role, alpha = name[5:].rsplit("_", 1)
                return rgba(role, alphas[alpha] if alpha in alphas else float(alpha.replace("p", ".")))
            return roles[name]
        return re.sub(r"\{\{(\w+)\}\}", value, text)
    mapping = json.loads((ROOT / "colors.json").read_text())
    def recolor(text):
        # One pass avoids replacing a newly generated color as an old source color.
        text = re.sub(r"#[0-9a-fA-F]{6}(?![0-9a-fA-F])",
                      lambda m: roles.get(mapping.get(m[0][1:].lower(), ""), m[0]), text)
        def rgb(match):
            original = "".join(f"{int(match[i]):02x}" for i in (2, 3, 4))
            role = mapping.get(original)
            if not role:
                return match[0]
            color = roles[role]
            return match[1] + "(" + ", ".join(str(int(color[i:i + 2], 16)) for i in (1, 3, 5)) + ("," if match[1] == "rgba" else ")")
        return re.sub(r"(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*[,)]", rgb, text)
    output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(ROOT / "base.tar.gz") as archive:
        for item in archive:
            relative = Path(item.name)
            if not item.isfile() or relative.is_absolute() or ".." in relative.parts or relative.parts[0] not in ("gtk-3.0", "gtk-4.0"):
                raise ValueError("Invalid GTK base archive entry")
            content = archive.extractfile(item).read()
            if relative.suffix in (".css", ".svg"):
                content = recolor(content.decode()).encode()
            if not gtk4_modern and relative.parts[0] == 'gtk-4.0' and relative.suffix == '.css':
                text = re.sub(r':root\s*\{[^{}]*\}', '', content.decode())
                # Preserve the state declarations rather than dropping controls
                # whose updated upstream CSS uses modern color expressions.
                text = re.sub(r'color-mix\(in srgb, var\(--([\w-]+)\) (\d+)%?, transparent\)',
                              lambda m: f'alpha(@{m[1].replace("-", "_")}, {int(m[2])/100:g})', text)
                text = text.replace('color-mix(in srgb, var(--accent-bg-color) var(--dim-opacity), transparent)',
                                    'alpha(@accent_bg_color, 0.5)')
                for index, role in enumerate(('accent', 'purple', 'pink')):
                    text = text.replace(f'@background_color_{index}', roles[role])
                    text = text.replace(f'var(--background-color-{index})', roles[role])
                for role in ('accent-bg-color', 'accent-fg-color', 'window-bg-color'):
                    text = text.replace(f'var(--{role})', '@' + role.replace('-', '_'))
                text = re.sub(r'^.*(?:--[a-z-]+\s*:|var\(|color-mix\().*\n', '', text, flags=re.M)
                content = text.encode()
            if relative.name in ("gtk.css", "gtk-dark.css"):
                relative = relative.with_name("base.css" if relative.name == "gtk.css" else "base-dark.css")
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    for version, template in (("3.0", "gtk3.css.in"), ("4.0", "gtk4.css.in" if gtk4_modern else "gtk4-legacy.css.in")):
        directory = output / ("gtk-" + version)
        overlay = substitute((ROOT / template).read_text() + '\n' + (ROOT / 'compat.css.in').read_text())
        (directory / "palette.css").write_text(overlay)
        for filename, base in (("gtk.css", "base.css"), ("gtk-dark.css", "base-dark.css")):
            (directory / filename).write_text(f'@import url("{base}");\n@import url("palette.css");\n')
    (output / "index.theme").write_text("[X-GNOME-Metatheme]\nName=anto426\nGtkTheme=anto426\nComment=Anto426 dynamic GTK palette\n")
    # LibreOffice's VCL recent-document canvas bypasses GtkStyleContext and
    # hardcodes #666666. Its native configuration uses opaque 24-bit RGB.
    office_roles = json.loads((ROOT / 'libreoffice.json').read_text())
    office = {group: {key: int(roles[role][1:], 16) for key, role in entries.items()}
              for group, entries in office_roles.items()}
    (output / 'libreoffice.json').write_text(json.dumps(office, indent=2) + '\n')
    license_path = ROOT / 'COPYING'
    if not license_path.is_file():
        license_path = ROOT.parent / 'COPYING'
    (output / 'COPYING').write_bytes(license_path.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", type=Path, required=True)
    parser.add_argument("--material", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gtk4-legacy", action='store_true', help='Force named-color fallback for GTK4 before 4.16')
    args = parser.parse_args()
    render(json.loads(args.palette.read_text()), json.loads(args.material.read_text()), args.output, not args.gtk4_legacy and modern_gtk4())
