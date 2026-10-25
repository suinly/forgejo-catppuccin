"""Run with: python3 -m unittest discover -s tests -v."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "public/assets/css"
PALETTES = {
    "latte": ("light", "#eff1f5", "#4c4f69", "#1e66f5"),
    "frappe": ("dark", "#303446", "#c6d0f5", "#8caaee"),
    "macchiato": ("dark", "#24273a", "#cad3f5", "#8aadf4"),
    "mocha": ("dark", "#1e1e2e", "#cdd6f4", "#89b4fa"),
}


def declarations(css):
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+);", css))


def contrast(a, b):
    def luminance(color):
        channels = [c / 255 for c in rgb(color)]
        return sum(weight * (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
                   for weight, c in zip((0.2126, 0.7152, 0.0722), channels))
    light, dark = sorted((luminance(a), luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)) if isinstance(color, str) else color


def resolve_color(value, variables):
    """Resolve the opaque hex/var/sRGB mixes used by our contrast checks."""
    if re.fullmatch(r"#[\da-f]{6}", value):
        return rgb(value)
    if match := re.fullmatch(r"var\((--[\w-]+)\)", value):
        return resolve_color(variables[match[1]], variables)
    match = re.fullmatch(r"color-mix\(in srgb, (var\(--[\w-]+\)|#[\da-f]{6}) (\d+)%, (var\(--[\w-]+\)|#[\da-f]{6})\)", value)
    if not match:
        raise ValueError(f"Unsupported color in contrast check: {value}")
    a, b = resolve_color(match[1], variables), resolve_color(match[3], variables)
    weight = int(match[2]) / 100
    return tuple(x * weight + y * (1 - weight) for x, y in zip(a, b))


class ThemesTest(unittest.TestCase):
    def test_four_installable_themes_with_official_blue_palettes(self):
        expected_files = {f"theme-catppuccin-{name}-blue.css" for name in PALETTES}
        expected_files.add("theme-catppuccin-auto-blue.css")
        self.assertEqual({p.name for p in CSS.glob("theme-*.css")}, expected_files)
        for name, (scheme, base, text, blue) in PALETTES.items():
            with self.subTest(flavour=name):
                css = (CSS / f"theme-catppuccin-{name}-blue.css").read_text()
                values = declarations(css)
                self.assertIn(f'@import url("./theme-forgejo-{scheme}.css");', css)
                self.assertIn('@import url("./catppuccin.css");', css)
                self.assertEqual(values["--ctp-base"], base)
                self.assertEqual(values["--ctp-text"], text)
                self.assertEqual(values["--ctp-blue"], blue)
                self.assertEqual(len(values), 27)
                self.assertTrue(all(re.fullmatch(r"#[\da-f]{6}", v) for v in values.values()))

    def test_auto_theme_uses_exclusive_system_color_schemes(self):
        path = CSS / "theme-catppuccin-auto-blue.css"
        self.assertTrue(path.exists(), "System-following theme is missing")
        imports = re.findall(r'@import url\("\./([\w.-]+)"\)\s*([^;]*);', path.read_text())
        self.assertEqual(imports, [
            ("theme-catppuccin-latte-blue.css", "(prefers-color-scheme: light)"),
            ("theme-catppuccin-macchiato-blue.css", "(prefers-color-scheme: dark)"),
        ])
        for filename, _ in imports:
            self.assertTrue((CSS / filename).exists())

    def test_readable_diff_counters(self):
        common = (CSS / "catppuccin.css").read_text()
        for name in PALETTES:
            values = declarations(common + (CSS / f"theme-catppuccin-{name}-blue.css").read_text())
            for index in (1, 2, 3):
                selector = f".repository .diff-detail-box .diff-detail-stats strong:nth-of-type({index})"
                rule = re.search(re.escape(selector) + r"\s*\{\s*color:\s*([^;]+);", common)
                self.assertIsNotNone(rule, f"Readable diff counter rule is missing: {selector}")
                ratio = contrast(resolve_color(rule[1], values), resolve_color(values["--color-body"], values))
                self.assertGreaterEqual(ratio, 4.5, f"{name}: diff counter {index}: {ratio:.2f}")

    def test_no_missing_or_circular_theme_variables(self):
        common = (CSS / "catppuccin.css").read_text()
        for name in PALETTES:
            with self.subTest(flavour=name):
                values = declarations(common + (CSS / f"theme-catppuccin-{name}-blue.css").read_text())

                def visit(key, path):
                    self.assertNotIn(key, path, f"Variable cycle: {path} -> {key}")
                    self.assertIn(key, values, f"Undefined variable: {key}")
                    for ref in re.findall(r"var\((--[\w-]+)\)", values[key]):
                        visit(ref, path + [key])

                for key in values:
                    visit(key, [])
                for key in ("--color-primary-hover", "--color-primary-active", "--color-thin-blue",
                            "--color-selection-bg", "--color-console-bg", "--color-danger-bg"):
                    self.assertIn(key, values)

    def test_readable_text_links_and_primary_buttons(self):
        common = (CSS / "catppuccin.css").read_text()
        for name in PALETTES:
            with self.subTest(flavour=name):
                values = declarations(common + (CSS / f"theme-catppuccin-{name}-blue.css").read_text())
                pairs = [("--color-text", "--color-body"), ("--color-primary", "--color-body"),
                         ("--color-input-text", "--color-input-background"),
                         ("--color-selection-fg", "--color-selection-bg")]
                pairs += [("--color-primary-contrast", state) for state in
                          ("--color-primary", "--color-primary-hover", "--color-primary-active")]
                pairs += [("--color-white", f"--color-{color}") for color in
                          ("red", "orange", "yellow", "green", "teal", "blue", "purple", "pink")]
                for foreground, background in pairs:
                    ratio = contrast(resolve_color(values[foreground], values), resolve_color(values[background], values))
                    self.assertGreaterEqual(ratio, 4.5, f"{name}: {foreground} on {background}: {ratio:.2f}")


if __name__ == "__main__":
    unittest.main()
