---
name: app-icons-and-logos
description: Use whenever you build, package, or ship anything with a face — a desktop .exe/.dmg/.AppImage, an installer, a PWA, a web app, a browser extension, or a repo README. Also use when the user mentions icons, logos, favicons, app icons, taskbar icons, desktop shortcuts, branding, or "make it a normal app". Catches the classic failure of shipping framework default artwork.
---

# App Icons and Logos

Shipping software means shipping a face. An app with the framework's default
logo (React atom, Electron logo, Vite bolt, Next.js triangle) reads as
unfinished no matter how good the code is.

## The rule

**Every artifact that can display an icon must get a real, product-specific
icon — and the same master artwork must drive all of them.**

Framework defaults are placeholders, not assets. Before declaring any build
done, grep the project for them:

```bash
grep -rn "logo192\|logo512\|favicon\|React App\|Create React App Sample\|electron.svg\|vite.svg" \
  --include="*.json" --include="*.html" --include="*.tsx" --include="*.js" . | grep -v node_modules
```

If a hit exists in shipped output, the job is not done.

## Checklist: every surface

| Surface | Artifact | Requirement |
| --- | --- | --- |
| Windows exe | `build/icon.ico` | 16, 20, 24, 32, 40, 48, 64, 96, 128, 256 px in one ICO |
| Windows window/taskbar | same ICO | Electron: `BrowserWindow({ icon })` or the embedded exe icon |
| Windows installer | same ICO | electron-builder `win.icon` |
| macOS | `build/icon.icns` | 16–512 @1x/@2x, from a 1024 master |
| Linux | `build/icon.png` | 512×512, plus hicolor sizes if packaging |
| Web/PWA | `favicon.ico`, `apple-touch-icon.png` (180), `logo192.png`, `logo512.png` | manifest `name`/`short_name`/`theme_color` must be the product, not the template |
| In-app chrome | header/logo mark | 32–40 px, readable on the app bar colour |
| README / social | `social-preview.png` | 1280×640 |

## Design rules (Microsoft Fluent guidance)

- **One metaphor.** A single, literal, self-evident symbol. Two max. No text —
  the OS already shows the app name.
- **Silhouette first.** Design the black shape. If it is not identifiable at
  16×16, simplify it. Few shapes, few corners.
- **Grid.** Design on a 48×48 grid, scale up. Exterior rounded corners ≈ 2 px
  at 48 (≈ 4% of size); modern tiles use 18–23% radius — pick one and keep it.
- **Contrast.** At least half the icon should pass 3:1 against both light and
  dark backgrounds. White-on-deep-teal or dark-on-white both work.
- **Colour.** One subtle gradient ramp (120°, 1–2 steps). No glossy bevels, no
  drop shadows except to separate overlapping objects.
- **Small-size test.** Render at 16, 24, 32, 48 and look at them. If the 16 px
  version is mush, the design is wrong, not the renderer.
- **Transparent corners.** Rounded tile on transparency, not a full-bleed square.

## Production workflow

1. Author one **1024×1024 master** (SVG preferred; PIL/Canvas/Cairo acceptable).
2. Render at **4×** and downsample with LANCZOS/Lanczos3 — never draw straight
   at 16 px.
3. Derive every size from that master. Never hand-draw a second version.
4. Verify:
   - open the 16/32/48 PNGs and actually look at them;
   - `[System.Drawing.Icon]::ExtractAssociatedIcon($exe)` on Windows to confirm
     the ICO is embedded;
   - launch the built app and check the taskbar/window icon;
   - check `client/build/favicon.ico` after a web build (public assets are copied).
5. Rebuild the package after changing icons — the exe embeds a copy.

## Electron-specific gotchas

- `electron-builder` reads `build/icon.ico` (or `win.icon`). Without it you get
  the default Electron logo on the exe, taskbar, and installer.
- A `BrowserWindow` icon path pointing inside `app.asar` will silently fail.
  Use the embedded exe icon or ship the PNG via `extraResources`.
- The portable target extracts to `%TEMP%`; the taskbar icon comes from the
  embedded exe resources, so the ICO must be correct at build time.
- Unsigned builds still show the icon; signing is a separate concern.

## Anti-patterns

- Reusing the CRA/Vite/Next default artwork "for now" and shipping it.
- A 1024 PNG dropped in as favicon (browsers downscale badly; ship an ICO).
- Gradient-and-glow AI art that turns to noise below 48 px.
- Text or the app's initials in the icon.
- One icon for the exe and a different one in the header.
- Changing the icon but forgetting `manifest.json` (`"name": "React App"`).