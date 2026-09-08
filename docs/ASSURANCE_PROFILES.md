# Assurance profiles

The repository supports two deliberately different project classes. A project must
declare the same `assurance_profile` in its registry entry and validation JSON.
Changing profile is an engineering decision, not a label change.

| Profile | Intended use | `not_for_manufacture` | Identity and checks |
| --- | --- | --- | --- |
| `training` | Workflow rehearsal and synthetic examples | `true` | Generic parts and documented ignored-check inventory are allowed. |
| `production` | A real engineering board | `false` | Approved parts and libraries, a mechanical handoff, GitHub governance record, and zero disabled ERC/DRC checks are required. |

## Training profile

Training projects remain visibly marked **NOT FOR MANUFACTURE**. Their validation
configuration records every intentionally ignored ERC/DRC check so a new suppression
cannot silently pass. Training libraries may contain generic footprints solely for
instruction; they are never an approved manufacturing source.

## Production profile

Start from `templates/production-project-config.example.json` and
`templates/production-project-registry.example.json`. The static gate rejects a
production project unless every declared part has reviewed manufacturer, MPN,
datasheet, lifecycle, and `approved` status; every declared shared library is
approved; and no ERC or DRC check is disabled.

The registry entry must also point to a project-specific mechanical-handoff record
and a completed GitHub governance record. CI enforces the presence and completeness
of those records; the team must still configure the corresponding GitHub controls.

Passing a production-profile check is engineering evidence, not authority to order or
manufacture. The release manifest and designated release authority remain required.

## Release assurance floors

`catalog/release-policies.json` sets the minimum assurance for every retained
connection, harness and mechanical claim in a release candidate: `unknown` for
engineering review, `observed` for prototype, `manufacturer_documented` for pilot,
and `verified` for production. The release-readiness gate enforces this catalog in
addition to product maturity, blocking items, deviations, artifacts and approvals.
Raising a release class therefore cannot silently promote an unresolved semantic
claim; change the claim only with appropriate scoped evidence and review.
