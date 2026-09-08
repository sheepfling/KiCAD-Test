# Release-readiness gate

The release gate validates a typed candidate record. It is read-only: it never
creates a tag, changes GitHub settings, uploads artifacts, orders parts, or sets
`build_authorized` to true. Human approval and the designated release system remain
separate authorities.

## Candidate record

Start with `templates/release-manifest.example.json`, replace every placeholder,
and store a real candidate in the repository path approved by the adopting team.
The generated schema is `schemas/release-manifest-v1.schema.json`.

```sh
python -B -m tools.ci --release --manifest release/<release-id>.json
```

The gate requires a clean worktree, a manifest commit equal to `HEAD`, each selected
product and variant revision, exact library provenance/licensing hashes, exact
interface revisions, and one exact toolchain identity for the selected project set.
It also requires passing repository/product/generation/harness/KiCad checks and
retained artifact hashes. Artifact kinds are maturity-specific: review candidates
retain a review record; prototype candidates retain a BOM, schematic/PCB exports and
validation report; pilot and production candidates add the applicable harness,
fabrication and assembly outputs. A non-review candidate also requires a maturity-
appropriate product, an approved release record, an annotated tag resolving to the
recorded commit, and a named approval record.

The repository's [assurance profiles](ASSURANCE_PROFILES.md) define another
maturity-specific floor. Every retained connection, harness and mechanical claim
must reach the `catalog/release-policies.json` assurance level for the selected
release class. A release deviation records a bounded approved departure; it never
silently turns an `unknown` or `assumed` claim into a stronger assurance state.

## Deviations

Each deviation has a stable ID, selected-release scope, owner, reason, status,
expiry and scoped evidence. Open, expired, unknown-scope, duplicate or unevidenced
deviations fail the candidate. This makes a deviation visible review data rather
than a note used to make a release look green.

## Scope boundary

The included training fixtures are intentionally not mature enough to pass this
gate. That is expected: the command demonstrates controls for a future real project;
it does not promote synthetic examples, establish server-side rules, or make a
manufacturing release.
