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

## References

### Bundled with the skill (read these; `SKILL.md` tells you when)

| File | What it is | When to read it |
|---|---|---|
| `SKILL.md` | The compressed operating manual: four outcomes, order of work, reading rules, seven label-noise gates, evidence layout, sign-off, wording, per-dataset parameter table | Always, first |
| `references/BIGVUL_LOOP_PROMPT.md` | The BigVul long-form prompt. The origin of the criteria; the other three prompts were synchronized from it. Contains the six CVE-match criteria, the seven gates with their case history, evidence rules 1–7, the outcome vocabulary and the measured lessons | Before any BigVul work, and whenever two prompts disagree |
| `references/PRIMEVUL_LOOP_PROMPT.md` | The PrimeVul long-form prompt: pairing semantics, the three closing states, the `dy_attacked_undecided_category` and `build_failed_reason` vocabularies, the cross-dataset reuse rules | Before any PrimeVul work |
| `references/MEGAVUL_LOOP_PROMPT.md` | The MegaVul long-form prompt: flat single-sided evidence layout, the hash-valued `project` field, the inherited confirmations, the implementation debts | Before any MegaVul work |
| `references/DIVERSEVUL_LOOP_PROMPT.md` | The DiverseVul long-form prompt: no CVE/CWE metadata, ground truth is the function-body diff, CWE must be derived from observation, rule C adapted | Before any DiverseVul work |
| `references/PROJECT_AGENT_BRIEF.md` | The per-project working brief: build once per project, one lane per project, what may and may not be shared between samples, the lessons measured on 2026-08-29 | When dispatching work by project or writing a subagent prompt |
| `references/CONFIRMATION_SCOPE.md` | The `defect_site` versus `reachability` distinction with worked examples | When a fault lands outside the labelled function's own lines |
| `references/primevul_outcome_taxonomy.py` | The single source of truth for the four outcomes and every secondary-field value, with the meaning and next action of each value | When classifying a sample or reporting counts by secondary field |
| `references/SOURCE.json` | Origin path and sha256 of each Chinese original the references were translated from | When checking whether a copy is stale |

### External references and citations

Datasets whose labels the skill verifies:

- BigVul: Jiahao Fan, Yi Li, Shaohua Wang, Tien N. Nguyen. "A C/C++ Code Vulnerability Dataset with Code Changes and CVE Summaries." MSR 2020. https://doi.org/10.1145/3379597.3387501
- DiverseVul: Yizheng Chen, Zhoujie Ding, Lamya Alowain, Xinyun Chen, David Wagner. "DiverseVul: A New Vulnerable Source Code Dataset for Deep Learning Based Vulnerability Detection." RAID 2023. https://doi.org/10.1145/3607199.3607242
- PrimeVul: Yangruibo Ding, Yanjun Fu, Omniyyah Ibrahim, Chawin Sitawarin, Xinyun Chen, Basel Alomair, David Wagner, Baishakhi Ray, Yizheng Chen. "Vulnerability Detection with Code Language Models: How Far Are We?" ICSE 2025. https://arxiv.org/abs/2403.18624
- MegaVul: Chao Ni, Liyu Shen, Xiaohu Yang, Yan Zhu, Shaohua Wang. "MegaVul: A C/C++ Vulnerability Dataset with Comprehensive Code Representations." MSR 2024. https://doi.org/10.1145/3643991.3644886

Dynamic tools and oracles named in the criteria:

- AddressSanitizer: Konstantin Serebryany, Derek Bruening, Alexander Potapenko, Dmitry Vyukov. "AddressSanitizer: A Fast Address Sanity Checker." USENIX ATC 2012. https://www.usenix.org/conference/atc12/technical-sessions/presentation/serebryany
- MemorySanitizer: Evgeniy Stepanov, Konstantin Serebryany. "MemorySanitizer: Fast Detector of Uninitialized Memory Use in C++." CGO 2015. https://doi.org/10.1109/CGO.2015.7054186
- UndefinedBehaviorSanitizer, ThreadSanitizer, LeakSanitizer: LLVM sanitizer documentation, https://clang.llvm.org/docs/ (the manual's rules that MSan and TSan print `WARNING:` rather than `ERROR:`, and that UBSan prints `<file>:<line>:<col>: runtime error:`, follow these tools' output formats).
- Valgrind Memcheck: Nicholas Nethercote, Julian Seward. "Valgrind: A Framework for Heavyweight Dynamic Binary Instrumentation." PLDI 2007. https://doi.org/10.1145/1250734.1250746
- ARVO: Xiang Mei, Pulkit Singh Singaria, Jordi Del Castillo, Haoran Xi, Abdelouahab Benchikh, Tiffany Bao, Ruoyu Wang, Yan Shoshitaishvili, Adam Doupé, Hammond Pearce, Brendan Dolan-Gavitt. "ARVO: Atlas of Reproducible Vulnerabilities for Open Source Software." arXiv:2408.02153, 2024. https://arxiv.org/abs/2408.02153 (used for exact-commit reproduction where a BigVul fix commit coincides with an ARVO record).
- gdb breakpoint hit counts and gcov line coverage (GNU toolchain documentation) are used as execution proof down to the patched lines.
- The failure types "Mock", "Invalid Test" and "none" used by the manual-check protocol follow the failure taxonomy (Table 7) of the CVE-Factory reproduction study referenced in the source repository's manual-check reports.

Skill format and hosts:

- Agent Skills specification: https://agentskills.io
- Claude Code skills: https://docs.claude.com/en/docs/claude-code/skills
- OpenAI Codex skills: https://developers.openai.com/codex/skills

### Citing this skill

```bibtex
@misc{lzhan011_vuln_label_dynamic_confirmation_2026,
  title        = {vuln-label-dynamic-confirmation: an Agent Skill for dynamic-tool verification of vulnerability labels},
  author       = {lzhan011},
  year         = {2026},
  howpublished = {\url{https://github.com/lzhan011/vuln-label-dynamic-confirmation-skill}},
  note         = {MIT License}
}
```

A machine-readable `CITATION.cff` is included; GitHub renders it as "Cite this repository".

## License

MIT. See `LICENSE`. The translated long-form prompts and supporting references are covered by the same license.
