# vuln-label-dynamic-confirmation

An [Agent Skill](https://agentskills.io) that turns a long research operating manual into an installable, tool-agnostic skill. It tells a coding agent how to verify vulnerability labels in the BigVul, PrimeVul, MegaVul and DiverseVul datasets with dynamic tools (sanitizers, two-sided differentials, behavioural oracles), how to decide label noise honestly, what evidence must be left on disk so that anyone can re-run it, and how to sign off.

The same folder works for **Claude Code** and for **OpenAI Codex** (the coding agent in ChatGPT, the Codex CLI and the Codex desktop app): both read the Agent Skills format, a folder with a `SKILL.md` carrying YAML front matter plus optional `references/` and `scripts/`.

## What is in the folder

```
vuln-label-dynamic-confirmation/
├── SKILL.md                            the skill body: operating order, hard rules, per-dataset parameter table
├── README.md                           this file
├── references/
│   ├── BIGVUL_LOOP_PROMPT.md           full English translations of the four long-form prompts
│   ├── PRIMEVUL_LOOP_PROMPT.md
│   ├── MEGAVUL_LOOP_PROMPT.md
│   ├── DIVERSEVUL_LOOP_PROMPT.md
│   ├── PROJECT_AGENT_BRIEF.md          per-project working brief
│   ├── CONFIRMATION_SCOPE.md           note on confirmation scope (defect_site vs reachability)
│   ├── primevul_outcome_taxonomy.py    the four outcomes and their secondary-field vocabularies
│   └── SOURCE.json                     origin path and sha256 of every reference
└── scripts/
    ├── run_checkers.sh <dataset> <project> [ids]   sign-off checkers
    ├── refresh_stats.sh <dataset>                  statistics and report refresh
    └── sync_references.sh                          re-sync references/ from the repository originals
```

`SKILL.md` is the compressed version. The long-form prompts in `references/` are the final authority on criteria; when they disagree, the dataset's own prompt wins, and among the four prompts the BigVul one is the origin from which the other three were synchronized.

## What the skill encodes

- **Four outcomes only.** Every positive sample ends in exactly one of `CONFIRMED`, `LABEL_NOISE_EXCLUDED`, `DY_Attacked_But_can_not_decide_confirmed_or_label_noise`, `NOT_DYNAMICALLY_TESTED`, each with mandatory secondary fields; the four counts must add up to the denominator.
- **Two-sided differential as the standard path.** Build the pre-fix and the post-fix code with the same driver and the same input; the only variable is the labelled function body; record real integer exit codes for both sides.
- **Attribution by line range, never by bare function name.** A fault in a callee reached from the labelled function still confirms (`reachability`); a fault in a caller, a sibling, or harness-written code does not.
- **Label noise only after a real dynamic attack.** Seven gates, including proof that the stored body matches upstream and that the patched lines were executed. Reading the code alone yields only a suspicion.
- **Evidence self-sufficiency.** A fixed `dynamic_evidence/` layout with a one-command `repro.sh`, both bodies, the input, both logs and a sha256 map; no absolute paths; nothing outside the repository.
- **Honest failure classes.** Synthetic triggers, harness tautologies, inverted polarity, both sides faulting, unattributable sanitizer output, and untested samples are named and kept apart instead of being folded into "confirmed" or "not confirmed".

## Install

### Claude Code

Project-level (auto-discovered inside the repository that uses it):

```bash
mkdir -p .claude/skills
ln -s "$(pwd)/path/to/vuln-label-dynamic-confirmation" .claude/skills/vuln-label-dynamic-confirmation
```

User-level (available in every project):

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/lzhan011/vuln-label-dynamic-confirmation-skill ~/.claude/skills/vuln-label-dynamic-confirmation
```

Invoke with `/vuln-label-dynamic-confirmation`, or just describe the task; matching tasks load it automatically.

### Codex (CLI, desktop, ChatGPT)

Project-level:

```bash
mkdir -p .agents/skills
ln -s "$(pwd)/path/to/vuln-label-dynamic-confirmation" .agents/skills/vuln-label-dynamic-confirmation
```

User-level:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/lzhan011/vuln-label-dynamic-confirmation-skill ~/.codex/skills/vuln-label-dynamic-confirmation
```

Invoke with `$vuln-label-dynamic-confirmation` or by describing the task.

### ChatGPT web (no file system)

Paste the full text of `SKILL.md` into the project instructions or at the top of the conversation, and upload the long-form prompt of the dataset you are working on from `references/` as a project file. Wherever `SKILL.md` says `references/...`, read the uploaded file. The scripts cannot run there; treat them as command lists.

## Context the skill assumes

The skill was written for a research repository with this layout, and its paths are relative to that repository root:

- samples under `data/output/dataset/<dataset>/<id>/`, each with `vulnerable_function.c`, `fixed_function.c`, `info.json`, and evidence in `dynamic_evidence/`;
- a confirmation registry under `data/output/dynamic/confirmed/<dataset>_<id>.craft.json`;
- per-dataset report directories under `tasks/<dataset>_reports/` holding the long-form prompt, the statistics scripts, and (for BigVul and PrimeVul) the sign-off checkers under `evidence_repair/`;
- shared build trees under `pathb/`.

If you use it elsewhere, adapt the parameter table in `SKILL.md` §10 and the two wrapper scripts. Internal host names and absolute paths in the translated prompts were replaced with placeholders such as `<host>`, `<REPO_ROOT>`, `<SCRATCH>` and `<HOME>`.

## Keeping the references in sync

`references/` holds copies. `SOURCE.json` records the origin path and sha256 of each one. Inside the source repository, after changing an original, run `bash scripts/sync_references.sh`; it re-copies the originals and rewrites `SOURCE.json`. (The public repository ships the English translations, so the hashes in `SOURCE.json` refer to the Chinese originals they were translated from.)

## License

All rights reserved. This is a research artifact published for reference and discussion. Contact the repository owner for reuse beyond reading.
