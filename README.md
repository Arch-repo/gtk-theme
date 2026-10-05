# Anto426 GTK theme

A maintained Orchis fork with one wallpaper-driven theme and compatibility paths
for GTK3, GTK4 before 4.16, modern GTK4 and libadwaita. Palette and material are
shared with the Anto426 shell, Qt, VS Code and Obsidian.

## Runtime renderer

```sh
python3 palette/render.py --palette palette/default.json \
  --material palette/material.json --output build/theme
```

The desktop downloads checksum-pinned runtime resources from this repository.
`palette/render.py` owns color mapping, SVG recoloring, current libadwaita roles
and background transparency. Text remains opaque. Current libadwaita controls
retain native geometry; the user stylesheet supplies semantic roles.
Older GTK4 runtimes automatically receive named-color CSS; `--gtk4-legacy`
forces this path for artifact checks. GTK3 retains the compiled widget fallback.
The same `anto426` theme name applies to every path.

The renderer also emits `libreoffice.json` for the VCL application canvases
that bypass GTK CSS. Recent-document background/text and the application
background use the shared palette. The desktop applies these three properties
through LibreOffice's configuration API, including while it is open, retaining
the selected scheme and document-specific colors. No document canvas alpha is
claimed: LibreOffice paints its recent-document primitive as opaque RGB.

The complete GTK3 and plain GTK4 widget styles remain in the compiled base.
Shared compatibility rules cover readable action/selection text, placeholders,
semantic states and dynamically colored sliders. Error, warning and success
literals in the historical base are recolored along with the primary palette.

`palette/base.tar.gz` is a deterministic archive of the compiled GTK3/GTK4 base.
To rebuild it after changing SCSS or assets:

```sh
python3 scripts/build-palette.py
python3 scripts/verify-palette.py
```

Build dependency: `sassc`. Runtime renderer: Python 3.10+.
Reference revision, coverage and execution limits: [UPSTREAM.md](UPSTREAM.md).

## Static fallback installation

```sh
git clone https://github.com/Arch-repo/gtk-theme.git
cd gtk-theme
bash install-anto426.sh
```

The wrapper builds the existing `Anto426-Dark` baseline for initial installation.
The dotfiles installer subsequently renders and selects `anto426` from the live
palette. No Git checkout or Sass compilation is needed during wallpaper changes.

GTK CSS overrides cannot style content drawn by an application outside GTK or
accessible only inside a sandbox. Flatpak applications require access to the
user theme/CSS directory. Background blur/refraction comes from the Hyprland
material rules; CSS itself does not implement compositor refraction.

Based on [vinceliuice/Orchis-theme](https://github.com/vinceliuice/Orchis-theme),
with original GPL-3.0 attribution retained in [COPYING](COPYING).
