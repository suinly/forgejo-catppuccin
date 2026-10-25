# Catppuccin for Forgejo 17

Four themes with a **Blue** accent: Latte, Frappé, Macchiato, and Mocha,
plus an automatic theme that follows your system color scheme.
Ready-to-use CSS files are in [`public/assets/css`](public/assets/css). No build step is required.

| Flavor | Forgejo theme name | Background | Blue |
| --- | --- | --- | --- |
| Latte | `catppuccin-latte-blue` | `#eff1f5` | `#1e66f5` |
| Frappé | `catppuccin-frappe-blue` | `#303446` | `#8caaee` |
| Macchiato | `catppuccin-macchiato-blue` | `#24273a` | `#8aadf4` |
| Mocha | `catppuccin-mocha-blue` | `#1e1e2e` | `#89b4fa` |
| Follow system | `catppuccin-auto-blue` | Latte / Macchiato | Blue |

The themes cover navigation, forms, buttons, menus, notifications, status
indicators, diffs, the Actions console, Chroma syntax highlighting, and the
EasyMDE Markdown editor. Fonts, sizing, and layout follow Forgejo's defaults.
The primary color is slightly darker than Blue to keep links readable in Latte.

## Installation

1. Find your installation's **CustomPath** using `forgejo help` or
   **Site Administration → Configuration**. The example below uses
   `/var/lib/forgejo/custom`; replace it with your own path.

   ```sh
   install -d /var/lib/forgejo/custom/public/assets/css
   install -m 644 public/assets/css/*.css /var/lib/forgejo/custom/public/assets/css/
   ```

   Copy **all six files**, including `catppuccin.css`.
   Forgejo already ships `theme-forgejo-light.css` and `theme-forgejo-dark.css`;
   you do not need to download or replace them.

2. Append the five theme names to the existing `THEMES` setting in the `[ui]`
   section of your `app.ini`. Example with the main built-in themes:

   ```ini
   [ui]
   THEMES = forgejo-auto,forgejo-light,forgejo-dark,catppuccin-auto-blue,catppuccin-latte-blue,catppuccin-frappe-blue,catppuccin-macchiato-blue,catppuccin-mocha-blue
   ; Optional: default theme for users who have not selected their own.
   DEFAULT_THEME = catppuccin-auto-blue
   ```

   If `THEMES` already lists other themes, including color vision accessibility
   variants, keep them and append Catppuccin to the list.
   Do not add the shared `catppuccin.css` file to `THEMES`.

3. Restart Forgejo, then select a theme in your personal appearance settings.

Select **catppuccin-auto-blue** to use Latte when your system prefers light mode
and Macchiato when it prefers dark mode. The CSS responds to
`prefers-color-scheme` changes automatically, without JavaScript. The two
imports use mutually exclusive media queries so that light-only and dark-only
Markdown content remains correct. An editor already open during a system theme
change may need a page reload to update its JavaScript-generated highlighting.

In the standard Docker image, CustomPath is usually `/data/gitea` and the
configuration file is `/data/gitea/conf/app.ini`. Copy the CSS files into the
corresponding persistent volume directory: `/data/gitea/public/assets/css`.
For other images, check CustomPath first.

Each theme loads the built-in light or dark theme through a relative `@import`,
followed by the shared `catppuccin.css` file and its own palette. This preserves
Forgejo's native Markdown rules and light/dark mode detection.
The themes require no third-party requests, JavaScript, or external fonts.

If the colors do not update, perform a hard refresh to clear the browser cache.
When using a separate `STATIC_URL_PREFIX` or CDN, place all six files alongside
the built-in CSS files and purge their cached copies.

## Verification and limitations

```sh
python3 -m unittest discover -s tests -v
```

The tests check all four palettes, filenames and imports, missing or circular
CSS variables, automatic theme imports, and contrast for body text, links,
primary buttons, and diff counters.
Python is only required for testing. The themes require a modern browser
with support for `color-mix()` and `:is()`.

Variables and selectors have been checked against the source code tagged
`v17.0.0`. All four fixed themes have been checked in Chrome on a running
Forgejo 17.0.0 instance using the appearance settings and commit diff. Macchiato
has also been checked on the repository, issue creation, and Actions console pages. The automatic
theme and the updated diff counter colors have not yet been checked in the
deployed instance. Check compatibility again after upgrading Forgejo.

**CodeMirror 6 file editor:** the background, text, selection, and active line
use the theme colors. Individual syntax tokens retain their default colors:
Forgejo 17 defines them in JavaScript using generated classes.
Syntax highlighting in file views and diffs (Chroma), as well as EasyMDE,
uses Catppuccin colors.

To uninstall, first change your personal theme and `DEFAULT_THEME`, remove
the five names from `THEMES`, and restart Forgejo. Then delete the six
installed CSS files.

## Sources

- [Catppuccin palette](https://github.com/catppuccin/palette) — official colors.
- [Forgejo 17.0.0 themes](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.0/web_src/css/themes).
- [Forgejo 17 interface customization](https://forgejo.org/docs/v17.0/contributor/customization/).
- [`[ui]` configuration](https://forgejo.org/docs/v17.0/admin/config-cheat-sheet/#ui-ui).

An unofficial port, not affiliated with the Forgejo or Catppuccin teams.
