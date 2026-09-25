---
name: vuln-label-dynamic-confirmation
description: Operating manual for verifying vulnerability labels with dynamic tools across the BigVul, PrimeVul, MegaVul and DiverseVul datasets and any project. Load it before any task that confirms a sample under data/output/dataset/<dataset>/<id> dynamically, decides label noise, repairs evidence, writes dynamic_confirmation.json or craft.json, runs the sign-off checkers, refreshes the statistics reports, or performs a manual spot-check review. It compresses the criteria shared by the four LOOP_PROMPT documents (the four outcomes, the two-sided differential, attribution, the seven gates, evidence self-sufficiency, banned wording) into executable steps, and lists per-dataset paths, fields and quirks in one parameter table. The full long-form prompts live in references/; when they disagree with this file, the dataset's own long-form prompt wins.
license: MIT (see LICENSE)
metadata:
  skill_version: 2026-09-25
  canonical_sources: tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md, tasks/primevul_reports/LOOP_PROMPT.md, tasks/megavul_reports/LOOP_PROMPT.md, tasks/diversevul_reports/LOOP_PROMPT.md, CLAUDE.md
  datasets: bigvul, primevul, megavul, diversevul
---

# Dynamic confirmation of vulnerability labels (cross-dataset, cross-project)

## 0. What this skill is and when to use it

- Purpose: for samples with `label_target==1` in four vulnerability-label datasets, use dynamic tools to prove whether the labelled function really has the vulnerability it was labelled with, and write the evidence as files that someone else can re-run.
- Trigger: the task mentions a dataset sample directory, `dynamic_confirmation.json`, `craft.json`, Path-A / Path-B / extract-stub / harness, label noise, a worklist, `<dataset>_dynamic_status_latest.json`, a manual-check report, or the user says "keep doing dynamic-tool analysis on <dataset>".
- Decide the dataset first, then take paths, fields and quirks from the parameter table in §10. The criteria themselves are shared by all four datasets; the differences live only in the table and in the "dataset characteristics" section of each long-form prompt.
- The long-form prompt is the final authority on criteria. This SKILL.md is a compressed version of the operating order and the hard rules; when it conflicts with the dataset's long-form prompt, the long-form prompt wins, and this compressed version must then be corrected. When the four long-form prompts disagree with each other, the BigVul prompt is the origin (the other three were synchronized from it).

## 1. Mandatory reading before starting (every round, no skipping)

1. The full long-form prompt for the dataset (copies in `references/`, original paths in §10). Focus on: the four outcomes and the decision order, the three closing states, the six CVE-match faithful-trigger criteria, the seven label-noise gates, evidence self-sufficiency rules 1–7, and the dataset characteristics.
2. The repository root `CLAUDE.md` (`AGENTS.md` is a symlink to it): loaded automatically every round; same content as this skill.
3. The dataset's frozen worklist and live audit (§10). The live audit is the current outstanding debt; numbers in old reports are background only.
4. When dispatching work by project, also read `references/PROJECT_AGENT_BRIEF.md` (the concrete per-project procedure and the lessons measured in practice; BigVul edition, reused as-is for the other datasets).

When dispatching a subagent, the prompt must name items 1 and 4 explicitly as required reading, and must separate "adjudication fields" from "proof fields" (see §8).

## 2. What each round must deliver: the four outcomes

Every `label_target==1` sample lands in exactly one cell; the four counts add up to the dataset's denominator.

| Outcome | One sentence | Mandatory secondary fields |
|---|---|---|
| `CONFIRMED` | The attack fired and the fault attributes to the labelled function | `confirmation_class` (`CONFIRMED_CVE_MATCH` / `CONFIRMED_OTHER_DEFECT` / `OTHER_DEFECT_UNFIXED`) + `cve_match` + `confirmation_scope` (only `defect_site` / `reachability`) + `reachability` (`REACHABLE` / `UNREACHABLE` / `UNKNOWN`) |
| `LABEL_NOISE_EXCLUDED` | Attacked and not a single fault fired (all seven gates met), or the measured differential points the wrong way | `label_noise_category` + `label_noise_basis` (only `dynamic_attack_negative` / `dynamic_differential_inverted`) + `label_noise_type`; `cve_match` is `n/a` |
| `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | Really attacked, readings obtained on both sides, but this measurement cannot decide between confirmed and mislabelled | `dy_attacked_undecided_category` (vocabulary: `references/primevul_outcome_taxonomy.py`, shared by all four datasets) |
| `NOT_DYNAMICALLY_TESTED` | No qualifying dynamic measurement yet (never tested / unreachable / built and run but no result) | `not_tested_reason` (same vocabulary; the PrimeVul and DiverseVul prompts still use the old names `BUILD_FAILED` / `build_failed_reason` for this cell, which is the same thing) |

Decision order, first match from the top wins:
1. `verdict` starts with `DYNAMICALLY_CONFIRMED` and `confirmation_class` is valid → cell one;
2. `label_noise: true` and `label_noise_basis` is one of the two allowed values → cell two (a record that only has `suspected_label_noise` does not count; that is cell four);
3. `tried_dynamic_method` is present and `differential` holds real integer exit codes on both sides → cell three;
4. everything else → cell four.

`INCONCLUSIVE`, `DEFERRED`, `NEEDS_PATH_B`, `NOT_CONFIRMED`, `NOT_TRIGGERABLE_AS_LABELED` and `UNTOUCHED` are no longer outcomes; they may only remain in a record's `verdict` as history. When reporting counts, cells three and four must come with the distribution of their secondary field; an empty string, `NONE`, or a whole sentence pasted into the value slot is not a valid value.

## 3. The order of work for one sample

Work by project: clone once and work out the build recipe once per project, keep the lane under `pathb/<project>_<batch-tag>/`, share ccache across samples. But every sample must build its own pair of `fix^` / `fix` (samples of the same project usually have different fix commits; testing with a sibling's build means testing the wrong version; check `info.json::commit_id` to see whether two samples really share a commit, never the directory name).

1. Read the metadata: `label_target` in `info.json` (only `==1`), `cve`, `labeled_cwe`, `commit_id`. In all four datasets `commit_id` is the fix commit; the vulnerable version is always its parent. `file` / `function` are often in `context_meta.json`; an empty `info.json::file_name` does not mean the function identity is unknown. Run `scripts/is_duplicate.py <dataset>:<id>` before confirming.
2. Evidence before action: pull the NVD entry and the fix diff (DiverseVul has no CVE; the ground truth is the diff between the two stored function bodies), and write `real_root_cause` / `trigger_mechanism` / `attacker_controlled_trigger` first. Use `git show --stat` to see how many files the commit touched: a large commit, a merge, or a whitespace-only difference may only be recorded as `suspected_label_noise`, used for prioritising and choosing the attack, never as a substitute for attacking.
3. Build two sides: the same driver, one side compiled with `vulnerable_function.c` (or a whole-tree build at `fix^`), the other with `fixed_function.c` (or a build at the fix commit). Inputs, compiler flags and environment identical; the only variable is the labelled function body. After building, `md5sum` both binaries; they must differ. `setsid` always with `--wait`. The three cases where a single side is allowed: both sides fault the same way, the pre-fix side does not structurally exist, or the two compiled artifacts are byte-identical (still build one side and run the oracle once).
4. Choose the oracle by CWE (by code characteristics for DiverseVul): out-of-bounds / use-after-free → ASan; integer overflow → UBSan; uninitialized memory and information leaks → only MSan or valgrind can see them (ASan structurally cannot); DoS → timeout / resource growth; permission, authentication and injection → behavioural or output differential. MSan and TSan print `WARNING:`, not `ERROR:`; UBSan's format is `<file>:<line>:<col>: runtime error:`.
5. Prefer the real entry point: if the real tool can be built and fed a real crafted file, do not hand-build a struct and call the function directly. Trigger values must be producible by the real entry point and must survive upstream validation; stuffing `INT_MAX`, absurd sizes, or deleting an upstream guard with `#ifdef` all count as synthetic triggers. Check which flags the upstream tests use before running; a hard-coded `-vvv` in a script can route around the vulnerable path. Whether an injected runtime condition counts as a faithful trigger is decided by "would upstream accept it" (rule C).
6. Run both sides on the same input and record real integer exit codes; run with `timeout`, `ulimit -c 0`, `ASAN_OPTIONS=disable_coredump=1`, `unset LD_LIBRARY_PATH`.
7. Attribution: never match stack frames by bare function name; use the line range of the function body. When the harness compiles the labelled function alone into `body_vuln.inc`, attribution by file path is allowed, but first confirm that file holds only that one function. A fault inside a function called by the labelled function is still a confirmation, recorded as `confirmation_scope: "reachability"` + `defect_site` + `call_path`; a fault in its caller, in an unrelated sibling function, or in a harness-written consumer or stub is the case for downgrading. Read the source to verify the call direction before deciding. A log can hold more than one fault; never look only at the first.
8. Execution proof: "it was compiled in" does not count; prove it was executed, and prove it down to the lines the patch changed (gdb breakpoint hit counts or gcov). When gdb counts 0, confirm with a second method before concluding; static functions get inlined at `-O1`.
9. Write the record and the evidence (§5, §6), then self-check: delete the build artifacts and run `bash repro.sh`; it must rebuild both sides from source and print the differential.
10. Sign-off checkers (§7): speak from on-disk results, not from self-reported numbers.

## 4. Reading rules (learned the hard way)

- "This commit did not change this function" only rules out a differential, not a vulnerability. When the two stored bodies differ only in whitespace, comments or signature, identical behaviour on both sides is a structural certainty, not a measurement; to judge whether the function has a defect, build another side and run the oracle.
- A CVE mismatch is no longer a veto: if the labelled function has a real defect of its own that a faithful input triggers, it is `CONFIRMED` with `cve_match: false` + `cve_attribution_note` + `real_vuln`.
- Unreachability is no longer a veto: if the defect really is in the body and was not created by the harness, record `reachability: "UNREACHABLE"`; if you merely failed to find a path, write `UNKNOWN` and list the entry points you searched. Unreachability is measured, not inferred.
- Both sides fault: if the defect is inside the labelled function and the pre-fix side triggers it by itself, record `OTHER_DEFECT_UNFIXED` + `fix_arm_also_vulnerable: true`. Both sides clean means this run did not trigger it; it does not prove the function safe. Pre-fix side clean while the post-fix side faults is inverted polarity; that sample is not vulnerable.
- A positive control must really fail; an unsigned left shift reported by `-fsanitize=integer` is not a defect; find out which side is faulting before calling it "a differential".
- The stored body must be complete: before writing `label_noise: true`, compare it word for word with the upstream file at `fix^`. Attacking a truncated stored body necessarily fails to fire; that is attacking the wrong object, recorded as `stored_body_incomplete` + needs-Path-B.
- Harness tautology: a harness that restates the labelled function by hand and switches the patch with `#ifdef FIXED / #else` produces a differential designed by the harness author. Detect it by checking whether the harness `#include`s the sample's own `vulnerable_function.c` / `body_vuln.inc`.
- When something cannot be counted, write "unreadable", never 0; never truncate logs with `head` / `grep -m2`; when a hash mismatches, never simply recompute it; first find out which round overwrote it.
- Sanitizer output whose stack contains no frame of the labelled function is recorded as `unattributed_sanitizer_output` (count + signature + sample); it counts neither as clean nor as a trigger.
- When a checker reports "missing", `ls` the directory before believing it; C++ stack frames contain spaces in function names, so `\S+` must not be used to match them.
- For confirmations inherited across datasets (`propagated_from`), follow the pointer to the twin sample directory and read the latest two-sided evidence bundle there; the old harness in the local directory may be stale.

## 5. Deciding label noise: seven gates, missing any one means not done

Before calling something label noise, the labelled function must actually have been attacked with a dynamic tool, and no vulnerability must have fired. Reading code alone allows only `suspected_label_noise: true` + `label_noise_basis: "static_reading"`, and the sample stays on the to-do list.

1. A real integer exit code was produced, with `repro.sh` and a non-empty log on disk;
2. `labelled_fn_executed: true` + `execution_proof`; being compiled in does not count;
3. `attack_inputs` are attack inputs; running the function normally once does not count;
4. `oracle_kind` chosen correctly for the CWE + `oracle_rationale`;
5. `attack_surface_note` states which entry points were tried, whether values were swept, and how long it ran;
6. The stored body was first proven word-for-word identical to upstream at `fix^`;
7. Execution proof reaches the lines the patch changed, with hit counts written into the record.

Attack evidence always lives in `<id>/dynamic_evidence/label_noise_attack/` (`attack.sh`, driver, body verified with `cmp`, `inputs/`, the complete log of every shot, `ATTACK_LOG.md`, `EVIDENCE_MAP.json`). Without this directory the verdict does not stand. Keep the three situations strictly apart: attacked and nothing fired → `label_noise: true` + `label_noise_basis: "dynamic_attack_negative"`; only read the code → `suspected_label_noise`; could not attack (cannot build / cannot reach) → needs-Path-B, which is a limit of our capability, not a property of the function.

## 6. Evidence self-sufficiency: the files someone else can re-run are the verdict

For every sample (confirmed or not) the reproducible files live in `data/output/dataset/<dataset>/<id>/dynamic_evidence/`, directory name fixed:

```
dynamic_evidence/
├── repro.sh            builds both sides, runs both, prints the differential, in one command
├── driver.c            real entry point / harness
├── body_vuln.inc       pre-fix code under test (or stub.h + #ifdef FIXED)
├── body_fix.inc        post-fix code under test
├── <poc input file>    binary, stored as-is
├── vuln.asan.log       actual output of the pre-fix side (renamed by oracle: msan / ubsan / valgrind / timeout)
├── fix.clean.log       actual output of the post-fix side
└── EVIDENCE_MAP.json   purpose + sha256 of every file; git pin for any external build tree
```

- Logs are not reproduction files; a directory holding only `.log` files does not qualify; the existence of `craft.json` does not mean a differential was run.
- No absolute paths in scripts; before handing over, `grep -rn '/scratch/\|/tmp/\|/home/' *.sh` must print nothing. Relativize by `cd "$(dirname "$0")"` first and compute the repository root after that; never use `$0` after the cd. Before changing any script, `cp x.log x.log.bak`.
- Never write artifacts to `/tmp`, `~`, or anywhere outside the repository; third-party build trees stay in `pathb/<lane>/`, source packages in `pathb/_srcpkg/` with the original archive and its sha256.
- Paths in records are written relative to the sample directory, as in `dynamic_evidence/repro.sh`; `dynamic_confirmation.json`, `craft.json` and the disk must agree in all three places.
- Update the sample's `record.md` for every sample touched; project-level progress is only appended to the dataset's RUNLOG (§10), never to a new RUNLOG.
- The CONFIRMED registry is `data/output/dynamic/confirmed/<dataset>_<id>.craft.json`; there is no `data/output/confirmed/`.
- Withdrawing a confirmation changes four places: `dynamic_confirmation.json`; `craft.json` moved into `<id>/prior_confirmation_<stamp>/`; `info.json` changed with the existing vocabulary (`label_target` never changes); and `dynamic_evidence/` keeps a re-runnable script for the negative result. Never downgrade without the user's explicit consent.
- Cross-dataset writes are allowed in exactly one direction, `bigvul:<id> -> primevul:<id>`; every other direction fails closed before writing. Historical records carrying `propagated_from` must keep their lineage and must not be rewritten as independent re-runs just because logs exist in the directory. Cluster propagation may only go to twin samples with `label_target==1` whose labelled function is the same function that reproduced the fault.

Complete field list for every CONFIRMED: `differential.vuln_rc` / `fix_rc` (real integers), `labelled_fn_executed` (`false` is an honest value), `execution_proof`, `tried_dynamic_method` (an object with 8 keys: `oracle_kind` `why_this_oracle` `method` `trigger` `vuln_rc` `fix_rc` `vuln_observed` `fix_observed`), `oracle_kind` + `oracle_rationale`, `attack_inputs`, `attack_surface_note`, `confirmation_scope`, `reachability`, and when scope is `reachability` the `defect_site` object and `reachability_note`, plus `craft.json`. DiverseVul additionally requires `cwe` (array), `cwe_chain` and `cwe_basis`, with the CWE derived from what was observed, not copied from the commit message.

## 7. Sign-off standard

For the datasets that have checkers (BigVul, PrimeVul) run both checkers, via `scripts/run_checkers.sh <dataset> <project> [ids]`:

```bash
cd tasks/<dataset>_reports/evidence_repair
python3 verify_batch.py --ids <a,b,c>
python3 check_loop_prompt_compliance.py <project>
python3 check_loop_prompt_FULL.py <project>      # no argument means the whole worklist
python3 locate_evidence.py                        # samples added this round must not appear in the external/missing list
python3 recompute_current_repair_audit.py         # register this round's progress with before/after
```

MegaVul and DiverseVul have no checkers of their own yet (the BigVul checkers hard-code the dataset path; this debt is recorded in the MegaVul long-form prompt). Their sign-off is the delete-and-rebuild re-run of step 9 in §3 plus reconciliation against the dataset's statistics script, and the RUNLOG must state that no checker was run.

If any confirmation was published this round, refresh the dataset's statistics and reports before signing off (`scripts/refresh_stats.sh <dataset>`), make the partition numbers and the worklist agree with the registry, then update the CURRENT-SNAPSHOT block in the long-form prompt by hand from the new JSON. If nothing was published, skip the full-dataset scan; it is heavy on NFS (about 15 minutes for BigVul, about 20 for MegaVul).

The mistake checkers themselves make most often is accepting only "a value is filled in" and not "it was measured and could not be decided": boolean fields are checked only for `is None`; an empty `confirmation_scope` accompanied by `confirmation_scope_undetermined` + a reason counts as done. Any hard rule added to a long-form prompt must be added to a checker in the same commit.

Campaign stop conditions: the live audit's active debt is 0; every row's scripts, inputs, both source sides, complete logs and `EVIDENCE_MAP.json` are inside the sample directory and re-runnable; a full run of the checkers reports no active issue belonging to the worklist. "Only needs-Path-B left", "both sides clean", "tool cannot reach it", "looks like a mislabel statically" are none of them reasons to stop.

## 8. Dispatching subagents and batch edits

- Phrase "adjudication fields" and "proof fields" separately: the forbidden fields are `verdict` / `confirmation_class` / `label_noise` / `label_target` / `cve_match` / `info.json` / `data/output/dynamic/confirmed/`; the proof fields must be written, listed one by one (`tried_dynamic_method`, `differential`, `oracle_kind` + `oracle_rationale`, `labelled_fn_executed` + `execution_proof`, `attack_inputs`, `attack_surface_note`, `labeled_function`, `labeled_file`).
- Numbers self-reported by an agent are all wrong until checked against the files; write both the self-report and the on-disk verification into the ledger, mark disagreements on the spot, and do not choose for the user.
- Subagents may not edit the problem register themselves; oddities go into the `oddity` field of `proj_<project>_RESULT.json`. DiverseVul agents may not write the RUNLOG themselves; they return one RUNLOG_LINE that the coordinator appends serially.
- Batch edits: read, decide and write adjacent to each other, re-reading before every write; every batch script carries the assertion "nothing changes except the keys I add"; skip any project an agent is currently working on; `ls` the glob before any `rm` with a glob.
- Resources: `make -j8` at most, at most 2–3 heavy rebuilds at once, limit concurrency by CPU utilisation and I/O wait, not load average. `pkill -f` / `killall` are forbidden; to kill, start with `setsid --wait`, record the PGID, `kill -- -$PGID`.

## 9. Wording (applies to every human-facing text)

- Do not use the word "predicate"; say "decision rule" or "the fields this code actually checks".
- Do not use the word "prose" for narrative text; say "the explanatory text in the document".
- Do not call the two builds "arms"; say "the build from pre-fix code / the build from the fixed code" or "the two sides".
- The three label-noise states must be written as full sentences the first time; short labels only afterwards:
  - attacked and not a single fault fired ⇒ the label-noise finding stands, the function really is mislabelled (mislabel stands);
  - a fault fired and it attributes to the labelled function ⇒ the label-noise finding is probably wrong, the function may genuinely be vulnerable, pending human adjudication (possibly vulnerable, pending);
  - no conclusion this round (no conclusion).
- State the direction together with the number; field names such as `exclusion_earned` must be expanded when they appear in human-facing text.
- No unexplained jargon; the first occurrence of a term gets one sentence saying what it means here.

## 10. Per-dataset parameter table

| Item | BigVul | PrimeVul | MegaVul | DiverseVul |
|---|---|---|---|---|
| Sample directory | `data/output/dataset/bigvul/<id>/`, numeric id | `data/output/dataset/primevul/<id>/`, numeric id | `data/output/dataset/megavul/<id>/`, numeric id | `data/output/dataset/diversevul/<id>/`, id of the form `97208_<hash>` |
| Denominator (target=1) | 10,900 | 6,004 | 17,592 (only 15,222 directories on disk; the gap is unreconciled) | 9,604; about 5,139 positive samples have no materialized folder, filter with `os.path.exists(vulnerable_function.c)` first |
| Long-form prompt (original) | `tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md` | `tasks/primevul_reports/LOOP_PROMPT.md` | `tasks/megavul_reports/LOOP_PROMPT.md` | `tasks/diversevul_reports/LOOP_PROMPT.md` |
| Registry file prefix | `bigvul_<id>.craft.json` | `primevul_<id>.craft.json` | `megavul_<id>.craft.json` | `diversevul_<id>.craft.json` |
| RUNLOG (append only) | `tasks/RUNLOG_<host>_bigvul.md` | `tasks/RUNLOG_<host>_primevul.md` | `tasks/RUNLOG_<host>_megavul.md` | `tasks/RUNLOG_<host>_diversevul.md` |
| Worklist / live audit | `evidence_repair/FULL_WORKLIST_20260803.csv` (1,517 rows) + `CURRENT_REPAIR_AUDIT.json` | same-named scripts under `evidence_repair/` + `build_primevul_*worklist*.py` | `build_megavul_inconclusive_deferred_worklist.py` | `diversevul_current_dynamic_method_worklist.jsonl` + `diversevul_triaged_worklist.jsonl` |
| Statistics / report refresh | `compute_bigvul_dynamic_status_statistics.py` → `refresh_current_bigvul_reports.py` → `compute_bigvul_outcome_taxonomy.py` → `build_current_dynamic_method_worklist.py` → `evidence_repair/recompute_current_repair_audit.py` → `check_zh_en_report_numbers_agree.py` | `compute_primevul_dynamic_status_statistics.py` → `refresh_current_primevul_reports.py` | `compute_megavul_dynamic_status_statistics.py` → `refresh_current_megavul_reports.py` → `build_megavul_inconclusive_deferred_worklist.py` | `compute_diversevul_dynamic_status_statistics.py` → `refresh_current_diversevul_reports.py` |
| Sign-off checkers | `evidence_repair/check_loop_prompt_compliance.py`, `check_loop_prompt_FULL.py`, `locate_evidence.py`, `verify_batch.py` | same names under `tasks/primevul_reports/evidence_repair/` | none (debt; the BigVul ones hard-code the path) | none |
| Manual-check directory | `bigvul_reports/manual_check_bigvul_20260913/` | `primevul_reports/manual_check_primevul_20260914/` | `megavul_reports/manual_check_megavul_20260914/` | see its reports directory |
| Evidence layout | `<id>/dynamic_evidence/` (§6) | as BigVul, but the pairing semantics differ, so the file layout cannot be copied blindly (long-form prompt §3) | historical evidence is flat (`dynamic_confirmation.harness.c` / `.asan.log` / `repro.sh`, the record may be in `dynamic_confirmation.record.json`), all single-sided with no post-fix side; `repro.sh` compiles into `/tmp/vv_repro_bin`, which is a debt; all new evidence follows §6 | as §6; the Path-B workspace historically lived outside the repository in `pathb_builds/`, new work goes into the in-repository `pathb/` |
| Metadata quirks | `commit_id` is the fix commit; heavy whole-file / whole-commit relabel noise, classify with `git show --stat` first; cross-dataset writes only `bigvul -> primevul` | paired samples; `BUILD_FAILED` is the old name of cell four; BigVul exact-body reuse must "copy first, rewrite, then re-run" | `info.json::project` holds a 40-character commit hash, not a project name, and `code_link` is the upstream commit URL; `context_meta.json` often lacks `function`, so take the function name from the stored body's signature; 943 CONFIRMED are inherited across datasets | no CVE / CWE; the ground truth is the diff of the two stored bodies; `cve_match` can never be decided, but a CWE must be derived from observation and written; target=1 directories contain no `function.c` |
| Name of cell four | `NOT_DYNAMICALLY_TESTED` / `not_tested_reason` | called `BUILD_FAILED` / `build_failed_reason` in its prompt | `NOT_DYNAMICALLY_TESTED` | called `BUILD_FAILED` in its prompt |

The cross-project procedure is at the start of §3 and in `references/PROJECT_AGENT_BRIEF.md`; method routing (which attack for which kind of project / CWE) is in `tasks/bigvul_reports/DYNAMIC_METHODS_CATALOG.md` and in the "method routing" section of each long-form prompt.

## 11. Files shipped with this skill

- `references/BIGVUL_LOOP_PROMPT.md`, `references/PRIMEVUL_LOOP_PROMPT.md`, `references/MEGAVUL_LOOP_PROMPT.md`, `references/DIVERSEVUL_LOOP_PROMPT.md`: full English translations of the four long-form prompts.
- `references/PROJECT_AGENT_BRIEF.md`, `references/CONFIRMATION_SCOPE.md`: the per-project working brief and the confirmation-scope note.
- `references/primevul_outcome_taxonomy.py`: the single source of truth for the four outcomes and the secondary-field vocabularies (shared by all four datasets). This public copy is a translated reference; its Chinese-language regex alternatives were replaced by English glosses, so use the repository original for actual classification.
- `references/SOURCE.json`: origin path and sha256 of every reference; when a copy disagrees with the repository original, the original wins, and `scripts/sync_references.sh` re-syncs.
- `scripts/run_checkers.sh <dataset> <project> [ids]`: the sign-off checkers of §7.
- `scripts/refresh_stats.sh <dataset>`: the statistics and report refresh after publishing confirmations.
- `scripts/sync_references.sh`: re-copy the references from the repository originals and update SOURCE.json.
