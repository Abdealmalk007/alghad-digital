# Official Windows utility logos — provenance and usage

The Windows utilities directory displays the programs' **original publisher branding**, not generated substitutes. These marks identify third-party products only; **ALGHAD DIGITAL / ProTech does not claim ownership, endorsement, or affiliation**.

Each logo's original HTTPS source, original pixel dimensions, normalized PNG checksum (SHA-256), and source asset are recorded in [`assets/tools/vendor/SOURCES.json`](../assets/tools/vendor/SOURCES.json).

| Program | Publisher logo source |
| --- | --- |
| Everything | [voidtools original icon pack](https://www.voidtools.com/Everything-Icons.zip), `voidtools-15-Everything-1.5.ico` |
| Ventoy | [Ventoy upstream GitHub icon](https://github.com/ventoy/Ventoy/blob/master/ICON/logo_512.png) |
| Rufus | [rufus.ie icon](https://rufus.ie/pics/rufus-256.png) |
| IrfanView | [IrfanView official site graphic](https://www.irfanview.com/images/logo-download.png) |
| File Converter | [File Converter publisher app icon](https://file-converter.io/images/application-icon.png) |
| VLC | [VideoLAN original icon](https://images.videolan.org/images/VLC-IconSmall.png) |
| Free Download Manager | [FDM original favicon](https://www.freedownloadmanager.org/favicon.ico) |
| Microsoft PowerToys | [Microsoft PowerToys official GitHub PNG](https://github.com/microsoft/PowerToys/tree/main/doc/images/icons/PowerToys%20icon/PNG) |

The vendor images are stored in `assets/tools/vendor` and embedded in local self-contained `assets/tools/{id}.svg` cards. **No external images or ad/analytics endpoints are contacted to render these logos.** `python scripts/build_real_tool_art.py` regenerates and verifies covers offline. `python scripts/generate_tool_art.py` delegates to the same verified builder, preserving compatibility. The site does not redistribute vendor installers; existing official download-site links remain unchanged.

The images are not licensed as ALGHAD DIGITAL assets. Brand owners retain their rights. Keep provenance visible to maintainers; do not imply any partnership. If a publisher requires removal or replacement, update that single product only after verifying a compliant replacement.

QA: `node tests/vendor-icons-test.cjs` validates each embedded image byte-for-byte against the local publisher-logo PNG and its SHA-256 record.
