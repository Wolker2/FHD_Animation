# FHD_Animation — supplied-code review for Nexus Mods

**Status: configuration/code review package; the supplied upload lacks the animation media. This is not a complete installable mod.**

All four DAT files were recovered as editable JSON and rebuilt byte-for-byte. The seven relevant supplied files (four DATs, two PNG emblems and ModuleInfo) reproduce the original SHA-256 hashes. The screenshot montage `РАСЫ.bmp` is excluded from this compact code-review package.

## Included source

| Path | Purpose |
| --- | --- |
| `source/CFG/Main.json` | UI layout configuration |
| `source/CFG/CacheData.json` | Resource names and animation paths |
| `source/CFG/Rus/Lang.json`, `Eng/Lang.json` | Complete localization trees and embedded runtime code |
| `source/DATA/Race/Emblem/*.png` | The two supplied editable emblem assets |
| `source/ModuleInfo.txt` | UTF-8 module metadata; emitted as original CP1251/CRLF |
| `scripts/` | Independent standard-library DAT codec, builder and resource audit |
| `tests/` | Hash checking, source editing and incomplete-build gate checks |
| `original-file-sha256.json` | Original hashes for the seven reproduced files |
| `build-verification.json` | Completed build/check results and all missing resource paths |
| `.github/workflows/review.yml` | Automated verification for GitHub |

No DLL, EXE, SCR or RSON was present in the uploaded archive. The mod's supplied runtime code is inside the two Lang DAT trees, under `ShipInfo.AddInfo.CustomInfos.FHD_StationEmblem_Info.OnActCode`. That code is fully visible and editable in JSON. No RSON recovery or Windows editor is needed.

## Build and verify

Python 3.10+, standard library only. Verified with Python 3.12.14 and zlib 1.3.2.

```sh
python3 scripts/build.py --strict-original
python3 -m unittest discover -s tests -v
```

The builder reproduces the seven supplied relevant files and writes `dist/build-report.json`. Its ZIP output is explicitly named `FHD_Animation_SUPPLIED_FILES_REBUILT.zip`. It remains incomplete and should not be described as the full animation release.

For a strict full-mod completeness check:

```sh
python3 scripts/build.py --strict-original --require-complete
```

With the current upload, this correctly exits with status **2** after reporting the absent animation media. The ordinary review build reports those missing files without concealing them. GitHub CI verifies supplied-source reproducibility; it does not certify full-mod completeness.

## Missing materials and unresolved local references

- **72 referenced media files are absent:** 36 `.gai` animations and 36 `.gi` images under `DATA/BaseHD/` and `DATA/GovHD/`. Their exact paths and CacheData aliases are recorded in `build-verification.json`.
- `Bm.FHDStationEmblem.Fei` and `Bm.FHDStationEmblem.Peleng` are used by the supplied Lang code but are not declared in the supplied CacheData. External definitions were not assumed; these findings are limited to the supplied configuration.
- ModuleInfo mentions the `Maloc V1,V2` alternative folders; those folders were not present in the upload.

The available screenshot montage contains still previews; it does not supply the missing animation frames. No substitute animations or silent changes to the original configuration have been introduced.

## Provenance and limits

Original author: **PrologDE**, as retained in ModuleInfo. Conflict declaration: **MorphyGaalGovHD**. Declared installation root: `Mods/FHD_MODS/FHD_Animation`. Original metadata and configuration values are preserved.

Input archive: `FHD_Animation.rar`, SHA-256 `b651ce56cb82ba641106418a11124fda95eda21b5f64117faf5359e174dd403f`. It contained eight files including the excluded screenshot montage. The four DATs are original source-equivalent reconstructions; the PNGs are already editable source assets.

The independent Python DAT codec was previously implemented using the format conventions studied in Sergei Osminin's MIT-licensed [rangers-utils](https://github.com/murgesku/rangers-utils): UTF-16LE BlockPar trees, CRC32, zlib and the game's stream cipher. No third-party binary tools or game executable are bundled. Existing authorship and licensing are not changed by this preparation.

Checks completed during preparation: four exact DAT roundtrips, seven original file hashes, ZIP integrity, resource-path audit and three Python tests. Game execution, in-game code compilation, antivirus verdicts, GitHub hosted execution and Nexus moderation approval were not performed.
