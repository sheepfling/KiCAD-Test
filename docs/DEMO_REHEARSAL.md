# External KiCad demo rehearsal

Rehearsed on 2026-09-08 using a temporary copy of the candidate workflow and a local
collection of 36 KiCad demo projects. External project files were neither staged nor
committed. All 719 original files retained their SHA-256 hashes. Temporary designs,
receipts, native exports and detailed JSON results stay outside tracked source.

## Results

| Exercise | Observed result |
| --- | --- |
| Import | 35/36 imported with native filenames, hierarchy and local assets preserved; the microwave PCB-only demo is explicitly unsupported |
| Portable project gate | 17 pass; 18 identify nonportable or missing dependencies |
| Native execution | All 35 imported designs exercised in the digest-pinned KiCad 10.0.5 container; all source inventories unchanged |
| Netlist adapter | All 35 real exports parse after the fixes, including large hierarchical designs, buses, supply names and unassigned footprints |
| Temporary island unit suites | 35 pass; an intentional source mutation fails the local suite and selected CI gate; restoration returns that gate to PASS |
| Connectivity mutation | Changing an actual StickHub exported connector pin is rejected against the measured regression snapshot |
| Template native controls | All six reference projects pass their respective 10.0.0/10.0.5 pinned lanes |
| Native negative controls | All seven controller probes detect the intended malformed PCB, missing library/tool, open pin, unrouted track, parity mismatch and unregistered project |
| Imported full gate | Shared tooling tests, all 36 local suites and generation pass; 525 dependency findings across 18 projects and four upstream-document findings keep the overall gate red |
| Shared quality gate | 159 shared tests, the example firmware test, Ruff, strict Pyright and documentation policy pass |

No imported demo received engineering approval. Their initial native gates all fail:
there are real findings, disabled-check policies and unfinished PCB test contracts.
The preservation suites test import/workflow behavior; the measured netlist snapshot
is regression evidence, not an independently established electrical specification.

As a stricter development experiment, all four ignored ERC checks were enabled in a
temporary Sallen-Key copy. Native ERC then reported five findings, which the gate
rejected. The original source remained untouched and the temporary copy was restored.
This demonstrates why a clean report under disabled defaults is insufficient evidence.

The actual Docker commands and dependency preparation used by CI ran locally. No
GitHub-hosted run, Windows/Linux portable job, artifact upload, branch protection or
release workflow was exercised. Hosted execution was not attempted because this rehearsal kept imported designs local.

## Workflow defects corrected

- Added `tools.template import-project` with dry-run receipts, source hashing,
  hierarchy handling, explicit omissions and no-overwrite behavior.
- Fixed native dependency setup: the pinned images have no pip. The host now prepares
  Linux wheels for the image's actual Python ABI from the repository's requirements.
- Accepted real native net names and empty footprint assignments in the typed adapter.
  Empty PCB test scaffolds still fail, and connectivity mismatches identify changed
  references/nets rather than dumping an entire large circuit.
- Corrected Markdown link decoding for percent-encoded and angle-bracketed filenames
  with spaces, while retaining repository containment checks.
- Recognized embedded model records as local dependencies; missing records still fail.
- Added repository/dependency preflight to native entry points and retained ERC/DRC
  finding counts when KiCad exits with violations.
- Corrected three schematic training contracts to the four disabled rules actually
  reported by their pinned toolchain. Development/production rules remain strict.
- Repaired the unregistered-project fault probe's old folder path and isolated native
  probes from adopted projects/catalogs so an unrelated import cannot mask a defect.

These fixes have self-contained shared regression coverage; the external demo
collection is not required for normal tests. Use the [import workflow](IMPORT_WORKFLOW.md),
[test guide](../tests/README.md) and [CI guide](CHECKS_AND_CI.md) to repeat the process.
Detailed local receipts and reports are generated under `build/demo-rehearsal/`;
`workspace.txt` identifies the separate temporary design copy.

## Remaining adoption work

Resolve old `KICAD6/8/9` library variables against actual approved dependencies,
absolute workstation paths and missing libraries/models in imported designs.
The template intentionally does not guess replacement assets. PCB-only artwork needs
a separate supported project kind; simulation model import is not a SPICE simulation
lane. Excluded upstream media may require a deliberate documentation-asset policy.
The imported full gate also reports four upstream-document issues: a missing image,
trailing whitespace and two license-layout findings. Preserve upstream license text;
use the existing narrowly scoped Markdown exceptions when an unchanged license needs
one. Engineering requirements, part identities and release evidence still need authoring.

## Per-project measurements

ERC/DRC cells show **findings / disabled rules**, including exclusions in finding
counts. They describe the initial, unmodified imported designs, not passing gates.
Portable results include the corrected embedded-model policy. Every imported project
also passed its temporary import-preservation unit suite.

| Original project | Imported | Portable | ERC | DRC |
| --- | --- | --- | --- | --- |
| `cm5_minima/CM5_MINIMA_3.kicad_pro` | Yes | FAIL | 114 / 4 | 181 / 7 |
| `complex_hierarchy/complex_hierarchy.kicad_pro` | Yes | FAIL | 40 / 2 | 68 / 3 |
| `ecc83/ecc83-pp.kicad_pro` | Yes | FAIL | 6 / 4 | 8 / 3 |
| `ecc83/ecc83-pp_v2.kicad_pro` | Yes | FAIL | 10 / 4 | 10 / 3 |
| `interf_u/interf_u.kicad_pro` | Yes | FAIL | 22 / 3 | 24 / 7 |
| `jetson-agx-thor-baseboard/jetson-agx-thor-baseboard.kicad_pro` | Yes | FAIL | 3012 / 4 | 335 / 5 |
| `kit-dev-coldfire-xilinx_5213/kit-dev-coldfire-xilinx_5213.kicad_pro` | Yes | FAIL | 59 / 4 | 194 / 5 |
| `microwave/microwave.kicad_pro` | Unsupported PCB-only | — | — | — |
| `multichannel/multichannel_mixer.kicad_pro` | Yes | FAIL | 42 / 4 | 218 / 7 |
| `openair-max/One-Air-Max.kicad_pro` | Yes | FAIL | 1026 / 4 | 482 / 13 |
| `pic_programmer/pic_programmer.kicad_pro` | Yes | FAIL | 44 / 3 | 41 / 4 |
| `royalblue54L_feather/RoyalBlue54L-Feather.kicad_pro` | Yes | FAIL | 203 / 5 | 305 / 8 |
| `royalblue54L_feather/nfc_antenna/RoyalBlue54L-NFC-Antenna/RoyalBlue54L-NFC-Antenna.kicad_pro` | Yes | FAIL | 1 / 4 | 9 / 7 |
| `simulation/amplifier-ac/amplifier-ac.kicad_pro` | Yes | PASS | 39 / 4 | — |
| `simulation/analog-multiplier/a-multi.kicad_pro` | Yes | PASS | 8 / 4 | — |
| `simulation/class-d/Class-D.kicad_pro` | Yes | PASS | 46 / 4 | — |
| `simulation/gain_control/mult_vca810.kicad_pro` | Yes | PASS | 17 / 4 | — |
| `simulation/generic_models/generic_opamp_bip.kicad_pro` | Yes | PASS | 28 / 4 | — |
| `simulation/ibis/ibis.kicad_pro` | Yes | PASS | 40 / 4 | — |
| `simulation/laser_driver/laser_driver.kicad_pro` | Yes | PASS | 2 / 3 | — |
| `simulation/power_supplies/LM317_power_supply/power_supply.kicad_pro` | Yes | PASS | 21 / 4 | — |
| `simulation/power_supplies/boost/smps-com.kicad_pro` | Yes | FAIL | 27 / 4 | — |
| `simulation/power_supplies/buck_conv/buck_conv.kicad_pro` | Yes | PASS | 15 / 3 | — |
| `simulation/power_supplies/hv_converter/hv_converter.kicad_pro` | Yes | PASS | 123 / 4 | — |
| `simulation/power_supplies/royer/royer1.kicad_pro` | Yes | PASS | 26 / 4 | — |
| `simulation/q17/Q17ng.kicad_pro` | Yes | PASS | 527 / 4 | — |
| `simulation/rectifier/rectifier.kicad_pro` | Yes | PASS | 1 / 3 | — |
| `simulation/sallen_key/sallen_key.kicad_pro` | Yes | PASS | 0 / 4 | — |
| `simulation/subsheets/mainsheet.kicad_pro` | Yes | PASS | 19 / 3 | — |
| `simulation/up-down-counter/up-down-c.kicad_pro` | Yes | PASS | 9 / 4 | — |
| `simulation/v_i_sources/v_i_sources.kicad_pro` | Yes | PASS | 11 / 3 | — |
| `sonde xilinx/sonde xilinx.kicad_pro` | Yes | FAIL | 31 / 2 | 26 / 4 |
| `stickhub/StickHub.kicad_pro` | Yes | FAIL | 0 / 4 | 0 / 8 |
| `tiny_tapeout/tinytapeout-demo.kicad_pro` | Yes | FAIL | 187 / 4 | 666 / 6 |
| `video/video.kicad_pro` | Yes | FAIL | 21 / 4 | 290 / 8 |
| `vme-wren/vme-wren.kicad_pro` | Yes | FAIL | 3276 / 4 | 467 / 16 |
