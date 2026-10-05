# Upstream compatibility

Reference checked on 2026-10-05: vinceliuice/Orchis-theme at
`a4c48a425e63808345e824495964bd9c2f462e04` (2026-09-14).
The updated Nautilus selectors are integrated. Fork-specific typography,
dark palette, sidebar icon selectors and shadow tuning remain maintained.

GTK3 uses the compiled Orchis fallback. GTK4/libadwaita applications retain
native widget geometry and receive semantic color roles from `palette/gtk4.css.in`.
GTK4 before 4.16 and older libadwaita receive named-color compatibility CSS.
System fonts, accessibility opacity helpers and standard GNOME color ramps
remain native. This is one theme with compatibility paths, not separate themes.

Semantic coverage was checked against the official libadwaita CSS-variable
reference (including the 1.10 documentation). Runtime validation covers
GTK 3.24.52, GTK 4.22.5 and libadwaita 1.9.4; historical GTK4 is covered by
artifact checks, not a claim of execution on an old installation.

- https://github.com/vinceliuice/Orchis-theme
- https://docs.gtk.org/gtk4/css-properties.html
- https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/css-variables.html

Original GPL-3.0 licensing and attribution are retained in `COPYING`.
