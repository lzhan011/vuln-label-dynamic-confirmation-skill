# PrimeVul Dynamic Confirmation /loop Prompt

> This document takes the latest dynamic-confirmation criteria of `tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md` as the higher-level rules,
> but all paths, sample semantics, pairing, deduplication boundaries, worklists and statistics commands are rewritten for PrimeVul.
> When the two prompts conflict: for the general dynamic criteria the BigVul long prompt wins; for PrimeVul's data layout and execution routing this document wins.

<!-- CURRENT-SNAPSHOT-START -->
## Current auto-updated snapshot (2026-09-02)

Source of truth for the statistics: `primevul_dynamic_status_latest.json`. The original `target=1` denominator is **6,004**. **The four outcomes**: `CONFIRMED` **5,549**; `LABEL_NOISE_EXCLUDED` **81**; `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` **368** (attacked, readings obtained on both sides, but this measurement cannot decide between confirmation and mislabel; breakdown in `dy_attacked_undecided_category`); `BUILD_FAILED` **6** (**never measured**, breakdown in `build_failed_reason`).

For label noise there is only one number: `LABEL_NOISE_EXCLUDED` **81** (attacked, all seven gates passed, no fault fired). Separately there is a static triage ledger of **224** rows waiting to be attacked; they have no effect whatsoever on the partition above. The historical narrative is kept in the rest of this file and is not the current count.

Whether a dynamic tool really ran (a stricter criterion than whether an artifact exists, from `primevul_dynamic_untested.json`): never run by any dynamic tool **19**, of which not in the confirmation registry and still on the to-do list **2**, and registered as CONFIRMED but with no actual run trace on disk **17**; fully meeting the "done" standard of Section 2 of this document **3,014**. The active pending list `primevul_pending_worklist.jsonl` holds **367** samples in total.
<!-- CURRENT-SNAPSHOT-END -->

> **★★ 2026-08-15: a positive control that "cannot actually go wrong" proves nothing.**
>
> Measured on 5540: to show the oracle was alive, a worker built a positive control -- it relaxed the mask
> `0xff0000` into `0xffff00`. **But those bits are constantly zero after the shift**, so this "defect-injected" control
> computed **exactly the same checksum as the real function body**. The control "passed", and it had in fact measured nothing.
> Only after switching to a mask that really changes the result did the two separate.
>
> **Rule: a positive control must first prove that it itself responds.** Merely "injecting a defect" is not enough --
> **you must see the control's output actually differ from the real function body** (a different checksum, a different exit code, an extra sanitizer line).
> When the control and the real body give the same result, that is **the control failing**, not "the function is fine".
> Same family: clang `-O1` optimizes away the whole allocation injected into the control, so compiling, linking and running all look normal while the control is mute.

> **★ 2026-08-15: `-fsanitize=integer` reports unsigned left shifts, and that is not a defect.**
>
> Measured on 5540: `unsigned-shift-base` is reported **with the same values on both sides** -- an unsigned left shift is **defined behavior**,
> this checker just treats it as a suspicious construct. **Same on both sides = a tool artifact** (see the interpretation rule above).
> Turn it off when using `-fsanitize=integer`, and write in `repro.sh` why it is off.

> **★★ 2026-08-15: "the two sides differ" is not a confirmation -- first look at which side is faulting.**
>
> Measured on 204396: out of 500 test cases, **314 separated the two sides**, and by the numbers it looked like a very solid differential.
> But **the side that faulted was the fixed one** -- that "fix" was in fact a **compile-fixup** for the IM7 patch,
> it dereferenced NULL at `tiff.c:4097`, and upstream deleted it the next day (`3c53413eb`).
> Building a third side carrying only the CVE-related hunk gave **0/500** -- the entire differential came from another hunk.
>
> **Rule: when you see the two sides separate, ask three things first** --
> (1) **which side is faulting** (only a fault on the pre-fix side can be a confirmation; a fault on the fixed side is inverted polarity);
> (2) **is it caused by the patch's own hunk** (one commit often carries several changes; building a third side with only the target hunk isolates it);
> (3) **is that "fix" really a fix** (in IM6 some labelled commits are actually **compile-fixups** after backporting the IM7 patch verbatim,
> and the stored function body may even be an **intermediate state that does not compile** -- the `vulnerable_function.c` of 201877 is exactly that).
>
> **Reading only "the two sides disagree" without looking at the direction will record inverted polarity as a confirmation.**

> **★ 2026-08-15: after an assertion in the record-writing script fails, do not let the work move on.**
>
> Measured: 4461 was nearly lost -- an assertion in an inline writing script fired and **nothing was written**, while the work moved on,
> leaving a complete measurement on disk next to an empty record. It was recovered only by a full-batch field scan.
> This is the live version of the old pit "the evidence is on disk, the record does not say so".
>
> **Rule: run a field scan before handing in the work** -- any sample that has **neither `tried_dynamic_method`
> nor `blocked_reason`** is a missed write and must not be let through.
> (This batch wrote it as `route_campaign/loop_20260815/verify_batch6.py`; copy it directly.)

> **★ 2026-08-15: reading `git show --stat` and then looking only at the biggest file will miss a one-line hunk.**
>
> Measured on 216832: the old record said this commit "only added a bad-issuer test certificate", and on that basis it was judged impossible to build a differential.
> In fact the same commit **also changed one line of `fuzz/x509.c`** -- and that line is exactly where the labelled function lives.
> **`--stat` sorts by size, so a one-line change comes last and is the easiest thing to truncate away.**
> Before deciding "this commit did not touch the labelled function", **run `git show <commit> -- <labelled file>` to see that file's full diff on its own**,
> do not read only the first few lines of `--stat`. (This is the same family of error as "the commit touched 41 files, so it is a bulk relabel":
> **the size of a commit cannot substitute for reading what it did to this file.**)

> **★★ 2026-08-15: a banked pair of sides may not contain the labelled function at all -- and it looks like "no differential".**
>
> Measured on 204794: the pair of binaries marked in the previous round as "both sides already banked, just run them" were **byte-for-byte identical**.
> The cause was purely a build one: `coders/jp2.c` is wrapped in `if MAGICKCORE_LIBOPENJP2_DELEGATE`,
> and this machine only has the libopenjp2 **runtime**, not the `-dev` package, so
> **`WriteJP2Image` is in neither binary**. The run gave 0/0, and it reads as "both sides clean".
>
> **Rule: before running any banked binary, first prove the labelled function really was linked in.**
>
> ```bash
> nm <binary> | grep -c ' [Tt] <labelled function name>'      # must == 1 (for C++ use nm -C or match the mangled name)
> ```
>
> Put this assertion into `repro.sh` so it fails right after the build, instead of being read as a negative result after the run.
> **"Both sides clean" says nothing until the labelled function is proven to have executed** -- this is the same thing as the second gate in Section 7,
> except that here even "compiled in" was not achieved.

> **★ 2026-08-15 two newly hit tool pits that produce "looks like nothing was measured" false negatives:**
>
> 1. **ASan's default fast unwinder drops the labelled function out of the stack entirely** -- passing through a libstdc++ without frame pointers,
>    the stack breaks in the middle. **`ASAN_OPTIONS=fast_unwind_on_malloc=0` is required.**
>    This means that some of the old conclusions "not a single frame of the labelled function appeared in the fault stack" **may be an artifact of dropped frames**,
>    not a real miss. Before deciding `unattributed_sanitizer_output`, rerun once with this option.
> 2. **clang does not instrument `std::string::empty()` for reads of out-of-bounds elements** -- ASan stays silent throughout,
>    while a raw read of the same byte does report. **A "clean" probed through a container method says nothing**; re-check with a raw read.
>
> One more interpretation rule, learned from 197359: **a sanitizer report that is identical word for word on both sides
> cannot be something the patch changed** -- it is an artifact of the toolchain or the environment, record it as `unattributed_sanitizer_output`
> (neither a clean log nor a trigger), and **rename that log to `oracle_probe_*`,
> do not let it share a namespace with the differential logs**.

> **★ 2026-08-15: this machine has network access.** Measured: `git ls-remote https://github.com/ImageMagick/ImageMagick.git HEAD`
> returns a commit hash immediately. This has to be written down here, because **two workers have already made wrong judgements by assuming "there is no network"**:
> one attributed a CVE to a different coder from memory (A-10 (3)), and another wrote a checkable upstream fact down as "cannot be verified".
> The second worker probed with `git ls-remote` on their own, found it worked, and pulled down the real fix commit
> (`pathb/android_frameworks_av_20260815/`), resolving a hanging judgement (8557) on the spot.
>
> **Rule: before saying "cannot check upstream / cannot look up NVD", actually try once.** Put the fetched upstream source in
> `pathb/<lane>/` and write `git_remote` + the exact commit into the record -- this was already required by Section 8.
>
**The snapshot is only an entry point, not proof of completion.** Every round must rerun the refresh commands in this document; old numbers must not be cited in place of the current state on disk.

> **★ 2026-08-15 addendum: several of the refresh commands in this section walk all 6,004 sample directories, which is heavy on NFS.**
> With a worker building concurrently, I/O wait was measured reaching **68%** with only 22% CPU idle -- at that point throwing
> another full-library scan at it every 10 minutes is competing for disk with the work you dispatched yourself.
>
> **Rule: when this round published no confirmations, skip the full-library statistics** (`compute_primevul_dynamic_status_statistics.py`,
> `compute_blank_reason_statistics.py`, `refresh_current_primevul_reports.py`),
> and use lightweight queries that read only the few dozen samples in this batch to watch progress. **After publishing you must run them once** --
> the partition numbers and the worklist have to match the registry, and that cannot be skipped.
>
> The criterion is still **CPU utilization and I/O wait**, not load-avg: load 30+ with idle CPU and low wa means the machine is fine;
> **high wa is the real congestion.**

---

## 0. The original /loop prompt (copied verbatim)

```text
Please continue doing defensive vulnerability-dataset label validation on PrimeVul: for target=1 samples, use the same attack input, dynamically compare the source build from pre-fix code with the source build from the fixed code, nail down more samples, and save both confirmed and unconfirmed results as independently rerunnable evidence. Each round, first read in full the repository-root AGENTS.md, tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md and tasks/primevul_reports/LOOP_PROMPT.md, then refresh the current PrimeVul statistics and worklist from disk.

PrimeVul-specific rules: the original *_paired.jsonl usually stores the target=1 pre-fix function paired with the target=0 post-fix function, while data/output/dataset/primevul/<id>/ often materializes only vulnerable_function.c; info.json.has_fix=false only means the current full-manifest did not carry func_after, and cannot be used to assert that upstream has no fix. You must recover the fixed side from the PrimeVul paired original row, from the upstream source at the fix commit, or from an already pinned pathb build, and verify that vulnerable_function.c corresponds to the real function body at fix^ and that the fixed side corresponds to the real function body at the fix commit. Do not guess the pairing from ID numbers.

Handle only info.json.label_target==1. Before confirming, run python3 scripts/is_duplicate.py primevul:<id>; only a twin that is target=1, whose normalized function body really is identical, and whose labelled function is the same as the function where the fault reproduces, may reuse a route, and every sibling must still have its own input, logs from both sides, proof that the function and the disputed lines executed, and an EVIDENCE_MAP.json. A target=0 paired row may only serve as the source of the post-fix function; confirming it or propagating it into a positive sample is strictly forbidden.

For each sample, first read the CVE, the fix diff of commit_id, the upstream source at fix^/fix and the real call direction, then choose the oracle by CWE. Prefer real program entry points; a micro-harness must use the real function bodies of both sides verbatim and preserve the upstream guards, types and call semantics. It is forbidden to manufacture a differential with absurd magic numbers, states upstream would reject, an #ifdef that deletes a guard, or a hand-written "with guard / without guard" pair.

Run both sides with the same input, the same driver, the same compile flags and the same environment; the only variable may be the pre-fix versus post-fix body of the labelled function. Record the real integer vuln_rc/fix_rc, the full output, and proof that the labelled function really executed and that the patch's disputed lines were hit. A fault on the pre-fix side with the fixed side clean is a standard confirmation; triggering another real defect of the labelled function is still a confirmation but write cve_match:false; both sides faulting with the defect entered from the labelled function can still be confirmed as OTHER_DEFECT_UNFIXED; the sample side clean with the fixed side faulting cannot be confirmed.

Before deciding label noise, you must really attack the labelled function with a dynamic tool suited to the CWE and with attack inputs. Static inspection.json, primevul_label_noise.jsonl, diff -w, the commit title, or a sibling function already confirmed can only produce suspected_label_noise, and cannot exclude a sample. Only after attacking with all seven gates passed and still no trigger may you write label_noise:true + label_noise_type:label_noise_dynamic_tools_attacked + label_noise_basis:dynamic_attack_negative, and put the complete attack evidence into <id>/dynamic_evidence/label_noise_attack/. needs-Path-B and a negative dynamic attack are strictly separate.

All reproducible files go into data/output/dataset/primevul/<id>/dynamic_evidence/: repro.sh, driver/harness, body_vuln.inc, body_fix.inc, the PoC input, the full logs of both sides named after the oracle, and EVIDENCE_MAP.json. Scripts must not write to /tmp, ~, directories outside the repository, or hard-code absolute paths. Shared source and builds stay inside the repository under pathb/, pinned by git remote, exact commit, dirty diff and build flags. Paths in records are written relative to the sample directory, like dynamic_evidence/repro.sh.

For every sample handled, additively update the proof fields of dynamic_confirmation.json and update record.md; confirmation registration goes to data/output/dynamic/confirmed/primevul_<id>.craft.json; only append to tasks/RUNLOG_<host>_primevul.md. Do not downgrade an existing confirmation without explicit user authorization. Keep processing all still-open target=1 samples until the live worklist and the compliance checks are really at zero; do not stop to ask about ordinary technical choices.
```

---

## 1. The PrimeVul per-round start-up protocol

Each round do the following first, in this order:

1. Read in full the repository-root `AGENTS.md`, the complete `tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md` and this document;
2. Run the current statistics and routing refresh:

   ```bash
   python3 tasks/primevul_reports/build_primevul_label_noise.py
   python3 tasks/primevul_reports/compute_primevul_dynamic_status_statistics.py \
       --output tasks/primevul_reports/primevul_dynamic_status_latest.md \
       --json-output tasks/primevul_reports/primevul_dynamic_status_latest.json \
       --inconclusive-ids-output tasks/primevul_reports/ALL_inconclusive_target1_ids.json \
       --untouched-ids-output tasks/primevul_reports/ALL_untouched_target1_ids.json
   python3 tasks/primevul_reports/refresh_current_primevul_reports.py
   # * 2026-08-15: the next two **overwrite the active worklist by default**; do not run them directly.
   #    The --csv-output of build_primevul_inconclusive_deferred_worklist.py defaults to
   #    primevul_inconclusive_deferred_route_worklist.csv, and it only recognizes five old states;
   #    running it once was measured to cut the worklist from 746 rows down to 325 (deleting 421 samples that really still owe work).
   #    To see what it computes, redirect the output elsewhere and compare:
   #      python3 tasks/primevul_reports/build_primevul_inconclusive_deferred_worklist.py \
   #        --output <tmp>.jsonl --summary-output <tmp>.md --csv-output <tmp>.csv
   #    Always maintain the active worklist with the following one (it aligns with the three outcomes of Section 2a; dry run first, then --apply):
   python3 tasks/primevul_reports/sync_route_worklist_to_open_states.py
   python3 tasks/primevul_reports/build_primevul_route_worklist_all_states.py
   python3 tasks/primevul_reports/count_primevul_dynamic_untested.py \
       --json-output tasks/primevul_reports/primevul_dynamic_untested.json \
       --ids-output tasks/primevul_reports/PRIMEVUL_DYNAMIC_UNTESTED_IDS.json
   python3 tasks/primevul_reports/build_primevul_pending_worklist.py
   python3 tasks/primevul_reports/refresh_current_primevul_reports.py
   ```

3. Read the freshly generated `primevul_dynamic_status_latest.json`,
   `primevul_open_state_route_worklist.jsonl`,
   `primevul_inconclusive_deferred_route_worklist.jsonl`, the existing RUNLOG, and the sample records and evidence;
4. Re-take all `target=1` IDs from `data/output/full/primevul.jsonl` and build a live master:
   **all samples not registry-confirmed**, plus **samples that are in the registry but lack a field required by this document or lack self-sufficient evidence**.
   The two routing JSONLs are only a convenience for picking routes and cannot replace the master audit;
5. **Merge back into the active worklist those IDs in `primevul_label_noise.jsonl` that still have no compliant dynamic attack.**
   The current `build_primevul_route_worklist_all_states.py` accepts only the five `OPEN_STATES` and misses states such as missing,
   `NEEDS_PATH_B`, `INCONCLUSIVE_NEEDS_PATH_B` and `LABEL_NOISE`, and it treats the static ledger as an
   exclusion by default; that conflicts with the 2026-08-03 rule "attack dynamically first, then decide label noise", so its default output
   cannot on its own serve as proof that the campaign is complete.
   **The only maintenance tool for the active worklist is `sync_route_worklist_to_open_states.py`** --
   it aligns with the three outcomes of Section 2a: it adds back `INCONCLUSIVE` / `NOT_DYNAMICALLY_CONFIRMED` samples,
   removes those already in the craft registry and those with `label_noise:true`, keeps the remaining states unchanged,
   and writes every removed row into `worklist_sync_<date>.json` so it can be looked up again;
6. Process in clusters by `(project, cve, commit_id, labeled_file, labeled_function)`, sharing the banked build,
   but verify the function body, input, execution proof and fault attribution sample by sample.

Old snapshots, static inspection, routing recommendations, an agent's self-report and the number of craft files are none of them a live audit.

## 2. What counts as "done" for one PrimeVul sample

A dynamic measurement counts as complete only when `dynamic_confirmation.json` satisfies both of the following:

1. `tried_dynamic_method` is an object and has a value that really corresponds to an actual run on disk;
2. `differential` is an object and has a value, containing the real integer `vuln_rc` / `fix_rc` of both sides under the same input.

The minimum complete structure of `tried_dynamic_method`:

```json
{
  "tried_dynamic_method": {
    "oracle_kind": "asan",
    "why_this_oracle": "a CWE-125 spatial out-of-bounds read should be detected by ASan",
    "method": "paired-body extract-and-stub",
    "trigger": "dynamic_evidence/inputs/poc.bin",
    "vuln_rc": 1,
    "fix_rc": 0,
    "vuln_observed": "ERROR: AddressSanitizer: heap-buffer-overflow ...",
    "fix_observed": "returns normally on the same input, full output in fix.asan.log"
  },
  "differential": {
    "vuln_rc": 1,
    "fix_rc": 0,
    "vuln_signal": "heap-buffer-overflow READ ...",
    "fix_signal": "clean"
  }
}
```

"Done" does not mean "confirmed". When no differential was measured, honestly save the results of both sides and a specific reason of at least 40 characters;
it is forbidden to fabricate exit codes, scope, reachability, sanitizer output or execution proof in order to clear the worklist.

Only the following structural situations allow there to be no normal second side, and even then the actual single-side run must be recorded honestly:

- the labelled function structurally does not exist at upstream `fix^`;
- the two sides differ in source but end up `CODEGEN_IDENTICAL`;
- the PrimeVul pairing or the upstream fixed body really cannot be recovered, and the real retrieval/build attempts have been saved and the sample has entered Path-B.

"Both sides fault the same way" is not a reason to skip building the fixed side: it is a candidate measured result of `OTHER_DEFECT_UNFIXED`.

## 2a. There are only four outcomes (the user fixed three on 2026-08-14; the fourth was added 2026-08-17)

For reporting numbers, writing records and computing statistics, **only the following four outcomes may appear**; every `target=1` sample falls in exactly one of them,
and the four numbers add up to the denominator 6,004:

| Outcome | Meaning | Secondary field |
|---|---|---|
| `CONFIRMED` | the labelled function triggered a real defect under a faithful input | `confirmation_class` (one of three), `cve_match` (true/false), `confirmation_scope` (`defect_site`/`reachability`), `reachability` (`REACHABLE`/`UNREACHABLE`/`UNKNOWN`) |
| `LABEL_NOISE_EXCLUDED` | the label is overturned: **either** it was attacked with a tool matched to the CWE, nothing triggered, and all seven gates are in place, **or** a differential was measured whose direction is inverted | `label_noise_category` (vocabulary in Section 7), `label_noise_basis` (`dynamic_attack_negative` or `dynamic_differential_inverted`), `label_noise_type`; write `n/a` for `cve_match` |
| `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | **really attacked with a dynamic tool, readings obtained on both sides, but this measurement cannot decide whether it is a confirmation or a mislabel** | `dy_attacked_undecided_category`, see the table below |
| `BUILD_FAILED` | **never measured**: could not be built, could not be reached, or simply has not been tested yet | `build_failed_reason`, see the table below |

**The following strings are no longer outcomes** and none of them may appear in the result partition:
`INCONCLUSIVE`, `NOT_DYNAMICALLY_CONFIRMED`, `DEFERRED`, `INCONCLUSIVE_NEEDS_PATH_B`,
`NEEDS_PATH_B`, `NOT_TRIGGERABLE_AS_LABELED`, `DYNAMIC_INCONCLUSIVE`,
`<MISSING_OR_UNPARSEABLE_VERDICT>`, `UNTOUCHED`.
They may remain in a sample record's `verdict` as history. **Whether the statistics place a sample in the third or the fourth outcome turns on one question only:
was this sample really attacked by a dynamic tool, with readings obtained on both sides?**

- **It was attacked** -> `DY_Attacked_But_can_not_decide_confirmed_or_label_noise`,
  with `dy_attacked_undecided_category` saying which kind of "cannot decide" it is;
- **The attack did not succeed / it has not been attacked yet** -> `BUILD_FAILED`, with `build_failed_reason` saying which kind of "never measured" it is.

### ★ The fourth outcome was added on 2026-08-17, and the reason for adding it must be remembered

Before that there were only three outcomes, **and "measured but not a confirmation" had no box of its own**. So that meaning was stuffed into a
field named `build_failed_reason` (**build failure reason**) -- and **not one** of those 230 samples was a build failure.

The consequences are concrete, not aesthetic:

1. **Anyone who reads the field by its name will read it wrong.** A snapshot once said `BUILD_FAILED 712`, while on disk there was
   **not a single `verdict` equal to `BUILD_FAILED` and not a single `build_failed: true`**.
2. **It directly violates Section 2b** -- Section 2b requires `build_failed` (could not be built) and `attack_exhausted`
   (attacked and no fault fired) to be **strictly separate, never merged**, while that field also held a third kind of thing.
3. **It forced out "two fields telling two stories in the same record".** Twice in the single day of 2026-08-17:
   the `label_noise_basis_suggested` of 214365 and 201328 said `dynamic_attack_negative`
   (attacked and nothing happened), while `build_failed_reason_suggested` said `inverted_polarity`
   (measured, and the direction is inverted) -- **these two statements cannot both be true**.

### The `dy_attacked_undecided_category` vocabulary (the secondary field of the fourth outcome, **required**, must not be left empty)

These samples have only one thing in common: **a dynamic tool really attacked them and readings were obtained on both sides.**
The reasons for "cannot decide" are completely different from one another, and so are the next actions --
**which is why reporting only the total of the fourth outcome is meaningless; the distribution of this table must be given alongside it.**

| Value | Meaning | What can be inferred about this function |
|---|---|---|
| **`nominated_awaiting_adjudication`** | readings obtained on both sides, **and a legal confirmation class has already been nominated** | **what it owes is neither a measurement nor a write-up, but one adjudication** (added 2026-08-17, see below) |
| `attacked_no_trigger` | both sides were really built and run, attacked with a matched tool, nothing fired, but one or more of the seven gates is still missing | **this is a conclusion about the function**; once the gates are filled it should move to `LABEL_NOISE_EXCLUDED` |
| `guard_never_evaluated` | the disputed lines were never executed at all | **the opposite: that "clean" is not a conclusion about this function**. Change the input so that they execute |
| `decision_diff_no_impact` | **a real difference was measured, but it has no security consequence.** Both phrasings belong here: (1) there is a clean decision-level differential at the patch point, but no sanitizer fault, no out-of-bounds/leak; (2) there is a real behavioral difference (a rendering difference, by design), but it does not reach a security boundary | First ask whether it can still be rescued (hook up a real consumer / switch to a matched oracle) -- **this class is the most likely to flip into a confirmation**; only when it cannot be rescued does it fall to a human to adjudicate "how large a behavioral difference counts as a vulnerability" |
| ~~`no_security_consequence`~~ | **merged into the row above on 2026-08-21** (owner's ruling). Kept as an **alias** so old records on disk can still be read, but the interpreter always folds it into `decision_diff_no_impact` | -- |
| `fault_not_attributable` | a fault fired, but it does not attribute to the labelled function (a sibling function / a caller / the harness's own code) | counts as neither clean nor triggered |
| `inverted_polarity` | inverted polarity: the faulting one is the build from the fixed code, and the build from the pre-fix code is clean | terminal state |
| `no_differential_possible` | by construction the two sides are necessarily the same code | terminal state; **a single side must be attacked on its own to decide whether this function has a defect** |
| `synthetic_trigger` | the trigger condition was manufactured by the harness and cannot be produced by a real input | switch to a real input |
| `reachability_unproven` | the fault is inside the function body, but it was not proven that an attacker can reach it | supply a real entry path |
| `cve_mismatch` | the labelled CVE does not belong to this commit or this function | a CVE mismatch does not veto a confirmation; first look at whether the function itself has a real defect |
| `single_arm_only` | only one side could be built and run; the second structurally does not exist | handle as the structural single-side case of Section 2 |
| `unclassified_reason` | a reason was written but the existing matching rules do not recognize it | **fix the rules; it is not the sample's problem** |

> **★ 2026-08-21 owner's ruling: `no_security_consequence` is merged into `decision_diff_no_impact`.**
> These two ask **the same question** -- a real difference was measured, but it has no security consequence.
> Writing them separately was only two phrasings: one starts from "there is a decision differential at the patch point", the other from "there is a behavioral difference"; they land in the same place.
>
> **The cost is countable**: among the samples pending adjudication, **27** hit both rules at once,
> and since the interpreter is designed so that "ambiguity must not be resolved by ordering" (see the `unclassified_reason` row),
> it sent them into `unclassified_reason`. **They did not fail to write a reason;
> we created this ourselves by splitting one question into two rules.** Merging them disambiguated on the spot:
> `unclassified_reason` 181 -> **154**, `decision_diff_no_impact` 62+19+27 -> **108**,
> the total pending adjudication unchanged (363).
>
> The implementation lives in `matching_blank_reasons()` of `primevul_outcome_taxonomy.py`
> (`_MERGED_KEYS`, folding **at the hit-set layer**), so the rule "multiple hits = cannot decide" benefits automatically
> without having to be written again at every call site. **Both patterns stay in effect**,
> and `no_security_consequence` is kept as an alias -- records already on disk carry that value, and deleting it would make them unreadable.

> **★ `nominated_awaiting_adjudication` was added on 2026-08-17, for the same reason as the fourth outcome itself.**
> Before that these samples were counted into `no_reason_recorded`, because the interpreter **looked only at the single field `confirmation_class_suggested_note`**,
> while the rule required that note only **when the class was left empty**. So a record carrying a nominated class, a real integer two-sided differential, execution proof and a positive control
> was still counted as "no reason written" -- **and the action attached to that box is "dispatch a batch to write it up", and they find nothing when they get there**.
> **Only vocabulary values count**: `NONE`, or a whole sentence pasted into the value slot, is **a different defect**, which must stay visible and must not be washed into this box.
>
> **★ One value missing from this vocabulary is a known outstanding debt (A-79 / A-424 / A-430).**
> The two kinds of "measured, and the direction or the era is misaligned", namely `inverted_polarity` and version mismatch,
> **have no corresponding legal value on the `label_noise_basis` side** (there are only `dynamic_attack_negative`
> and `static_reading` there). So a worker can only write the real meaning into this field,
> **and when adjudicating you must read the body of the record, not just that one field** -- 201328 on 2026-08-17 was adjudicated exactly that way.

### The `build_failed_reason` vocabulary (**required**, must not be left empty)

**Not a single sample in this bucket has been successfully measured**, so it supports no conclusion at all about these functions --
it speaks about **our own capability or progress being insufficient**, and these samples **must stay on the to-do list waiting to be attacked**.

| Value | Meaning | What can be inferred about this function |
|---|---|---|
| `could_not_build` | after several attempts it still could not be built or could not be reached, so no attack succeeded at all | **nothing can be inferred** (our capability is insufficient) |
| `suspected_only_never_attacked` | only the code was read and it looked mislabelled; no tool was ever run | **stays on the to-do list waiting to be attacked** |
| `not_measured_yet` | not tested yet | dispatch the work |
| `no_reason_recorded` | the record does not say at all why it stopped here | go back to the sample and write it up |

## 2b. The three closing states for "attacked repeatedly and still no result" (never merge them)

"Tried many times and still no result" corresponds in this campaign to **three completely different situations**, whose next actions,
conclusions about the dataset, and eligibility for sign-off all differ. Merging them is exactly the error Section 7 of this document is meant to prevent:
**"could not be reached" is our capability falling short; "attacked and no fault fired" is the only one that is a conclusion about the function.**

Write it into `dynamic_confirmation.json`, choosing one of three:

### (1) `blocked_reason: "build_failed"` -- could not be built, so no attack succeeded at all

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "blocked_reason": "build_failed",
  "build_failure": {
    "attempts": 3,
    "what_was_tried": "at-commit clone + ASan; extract-and-stub; reuse the already-built binary in pathb/<lane>",
    "where_it_stops": "the **verbatim** error of the first failure + file and line number",
    "why_not_recoverable_now": "a missing unobtainable SDK / the era's toolchain will not install / the dependency has been taken down",
    "logs": ["dynamic_evidence/build_vuln.log", "dynamic_evidence/build_fix.log"]
  }
}
```

**The criterion is not "I think it cannot be built", it is that failing build logs are on disk.** `attempts` must be >= 2,
and `what_was_tried` must list **different** routes (rerunning the same command three times is not three attempts).

This state **supports no conclusion at all about the function** -- it is neither a mislabel nor an absence of vulnerability.
Statistically it goes into `BUILD_FAILED`, meaning "after several attempts it still could not be built, therefore it could not be attacked".

### (2) `attack_exhausted: true` -- it was built, really attacked, attacked repeatedly, and still nothing fired

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "attack_exhausted": {
    "rounds": 4,
    "oracles_tried": ["asan", "ubsan", "msan"],
    "why_these_oracles": "chosen by the mechanism in the fix diff: out-of-bounds writes go to ASan, uninitialized memory goes to MSan (which prints WARNING: not ERROR:), shifts/integers go to UBSan",
    "entries_tried": ["the real CLI", "the decoder entry point", "extract-stub"],
    "inputs": "313 malformed samples + the official regression material, ~22 minutes in total",
    "positive_control": "dynamic_evidence/poscontrol.asan.log does respond -- proving the oracle is not dead",
    "seven_gates": "all passed / gate N missing (say which one)"
  }
}
```

**This state is the real "tested many times with no result".** But note where it goes:

- **all seven gates passed** -> it should not stop here; per Section 7 write `label_noise: true` +
  `label_noise_basis: "dynamic_attack_negative"`, and move it into `LABEL_NOISE`;
- **any gate missing** -> stay in `attack_exhausted`, write down which gate is missing, and the sample **stays on the to-do list**.

**The most common gap is the fourth gate: the oracle must be chosen against the mechanism, not against the labelled CWE.**
If the mechanism is uninitialized memory but it was only attacked with ASan -- that "clean" is not a negative result, it is **not measured**,
because ASan structurally cannot see this class.

### (3) Something fired, but it does not attribute to the labelled function

Not covered by this section. A fault in a **callee** is still a confirmation (`confirmation_scope: "reachability"` +
`defect_site` + `call_path`); only when it is in a **caller** or in a **sibling** with no call relationship do you write
`unattributed_sanitizer_output` (count + signature + examples), which **may be treated neither as a clean log nor as a trigger**.

### The three side by side

| Situation | Field | Statistical category | What can be inferred about this function |
|---|---|---|---|
| could not be built / could not be reached | `blocked_reason: "build_failed"` + `build_failure` | `BUILD_FAILED` | **nothing can be inferred** |
| attacked, attacked repeatedly, nothing fired | `attack_exhausted` | all gates passed -> `LABEL_NOISE`; otherwise still on the to-do list | only with all gates passed may you say "this function is mislabelled" |
| something fired but it does not attribute | `unattributed_sanitizer_output` | still on the to-do list | neither clean nor triggered |

**Do not write strings like `differential.vuln_rc: "build_failed"`.** Exit-code fields hold integers only;
if no integer came out of a run, then there was no differential this time, and the reason goes in the fields above.
`blocked_reason: "build_failed"` and a real integer differential **cannot coexist** -- coexistence means the marker is stale,
auditor R12 will report it, and the old marker must be demoted to `prior_route_build_failure` with `build_performed` written.


## 3. PrimeVul pairing semantics: the BigVul file layout cannot be copied over

The key structures of the PrimeVul raw data are:

- in `*_paired.jsonl` there is usually one `target=1` pre-fix function paired with one `target=0` post-fix function;
- the `vulnerable_function.c` of a positive sample directory comes from the original `func`;
- the full-manifest PrimeVul ingest explicitly wrote `func_after: ""`, so many positive sample directories have no
  `fixed_function.c`, and `info.json.has_fix` is often `false`;
- `commit_id` denotes the fix commit, and the standard historical sides are still `fix^` and `fix`, but the polarity must be re-checked against the real upstream history;
- `file_name` is often the string `"None"`; when `context_meta.json` / `containing_file.c` exists, prefer it,
  and when it does not, locate the file from the function signature, the paired row and the fix diff; never treat `"None"` as a real path.

The priority order for recovering the two sides:

1. find the target=0 partner in the corresponding PrimeVul `*_paired.jsonl`;
2. cross-check with `(project, commit_id, cve, function identity)` and the pairing order; **do not guess the pairing from an ID plus a fixed offset**;
3. extract the function verbatim from the upstream files at `fix^` and `fix`, and check the partner's polarity and completeness;
4. save the two function bodies actually tested as this sample's
   `dynamic_evidence/body_vuln.inc` / `body_fix.inc`, and write the origin, sha256,
   paired source row and upstream commit into `EVIDENCE_MAP.json`;
5. use `cmp` to verify `body_vuln.inc` against the sample's `vulnerable_function.c`. If they differ, first determine whether the stored body is truncated,
   the version is offset, or the function extraction is wrong; do not go on treating another piece of upstream code as this sample.

The target=0 partner in `data/output/dataset/primevul_only_non_vulnerable/<id>/function.c`
may serve as a candidate source for the fixed body, but it is still a negative sample: **it may only feed the fixed side, and must never create a confirmation registration.**

## 4. The two-sided differential and the three confirmation classes

The two sides must satisfy:

```text
arm_vuln = the same driver + the real pre-fix body of the labelled function
arm_fix  = the same driver + the real post-fix body of the labelled function
```

Input, compile flags, macros, dependencies, runtime environment and command-line flags are all identical; the only variable is the labelled function body.
After the build completes you must record:

```bash
md5sum arm_vuln arm_fix
```

If the two hashes are identical, stop first and check for crossed builds, concurrent overwriting, polarity, or codegen; every `setsid` must be written as
`setsid --wait`. Never let several builds write the same source tree concurrently.

There are only three confirmation classes:

| `confirmation_class` | Condition |
|---|---|
| `CONFIRMED_CVE_MATCH` | the same faithful input triggers the labelled CVE; the sample side faults, the fixed side is clean |
| `CONFIRMED_OTHER_DEFECT` | another real defect is triggered from the labelled function, the fixed side is clean; `cve_match:false` |
| `OTHER_DEFECT_UNFIXED` | the sample side can faithfully trigger a real defect, and the fixed side has that defect as well |

When `verdict` starts with `DYNAMICALLY_CONFIRMED` there must be a `confirmation_class`.
The fixed side also faulting does not automatically veto; you must write:

```json
{
  "fix_arm_also_vulnerable": true,
  "defect_present_both_arms": true,
  "fix_arm_signal": "<the real fault in the full log of the fixed side>"
}
```

The sample side clean with the fixed side faulting is inverted polarity, and the fixed side's fault must not be credited to the sample.

## 5. `confirmation_scope` and `reachability` are both required for CONFIRMED

The two fields are independent of each other and must not be conflated:

```json
{
  "confirmation_scope": "defect_site",
  "reachability": "REACHABLE"
}
```

- `confirmation_scope` may only be `defect_site` or `reachability`;
- `reachability` may only be `REACHABLE`, `UNREACHABLE` or `UNKNOWN`.

The counterfactual criterion: **if only the labelled function is fixed, does the defect disappear?**

- It does: `confirmation_scope:"defect_site"`. The labelled function under-allocating with the fault written in a downstream `memcpy` still belongs to
  `defect_site`, explained additionally with `frame_note{alloc_site,fault_site}`;
- It does not: the labelled function merely passes the input to a callee that is itself defective; write
  `confirmation_scope:"reachability"` and fill in:

  ```json
  {
    "defect_site": {
      "function": "<the function that really contains the defect>",
      "file": "<file>",
      "reached_via": "<labelled function -> ... -> defective function>",
      "defect": "<the verbatim oracle output>"
    },
    "callee_of_labelled_function": true,
    "call_path": "<the call chain with source file and line numbers>",
    "reachability_note": "<why the labelled function is the reaching point and not the deciding point>"
  }
  ```

A fault in a caller, in a sibling function, or in a function with no call relationship cannot be attributed to the labelled function.

An unreachable real defect can still be confirmed: if the defect really is inside the labelled function and was not manufactured by the harness, write
`reachability:"UNREACHABLE"`, a specific `reachability_note` and
`attacker_controlled_trigger:null`. When you merely failed to find an entry point, write `UNKNOWN` and list the entry points already examined;
unreachability must be supported by an actual experiment, and may not be inferred from memory sizes or intuition.

## 6. The six steps of a faithful CVE-match trigger

Every CONFIRMED is verified in this order:

1. **Read the real fix evidence**: the CVE description, the fix commit, the source at `fix^`/`fix`, and the paired positive and negative rows; record
   `real_root_cause`, `trigger_mechanism`, `attacker_controlled_trigger`;
2. **Build the real two sides**: prefer a real historical build; extract-stub must also come from two real function bodies, and the driver must not hand-write
   "the vulnerable logic" and "the fixed logic";
3. **Prefer real entry points**: when a parser, decoder, daemon, CLI or kernel syscall/packet path can be used, go through the real entry point;
   a micro-harness must preserve the real types, guards, state invariants and call direction;
4. **Realistic trigger values**: sizes, counts, lengths, object states and scheduling must be producible from the saved input and must pass the upstream checks;
5. **Mechanism and attribution agree**: the observed fault, the fix mechanism and the deciding point in the labelled function must connect; when another real defect is triggered,
   write `cve_match:false`, `cve_attribution_note` and `real_vuln{class,site,trigger}`;
6. **Distinguish the deciding point from the fault point**: determine the scope using source line numbers, the full stack and the counterfactual check.

`cve_match:false` is not a reason to veto; when `labeled_cwe` is wrong but there is a real defect inside the function you may write `cwe_correction`.
The only things that still block a confirmation are: a synthetic trigger, a defect manufactured by the harness, and the build from pre-fix code not being able to trigger anything itself.


> ## WARNING: this rule **has not yet been adopted** -- attribution corrected by the dispatcher on 2026-08-17
> The section below was written in on 2026-08-17 by an agent and signed as "**decided by the user**". **The user never decided it.**
> What was in front of the user at the time were three candidate rules (A strict / B loose / C whether upstream acknowledges it), the dispatcher recommended C,
> **and the user had not yet answered**. The agent took a recommendation for an adjudication.
>
> **Adjudicated: the owner explicitly chose rule C on 2026-08-17.** The verbatim authorization, its timestamp and the point at issue in A-460
> are recorded word for word in `tasks/primevul_reports/evidence_repair/RULE_C_AUTHORISATION_20260817.md`.
> Before that, this section was marked "proposal, not adopted" and publishing on its basis was forbidden; that marking was correct --
> at the time the authorization really was not visible on disk. **Now it is.**

> **WARNING: 2026-08-17 further correction: the sentence above, "the user never decided it", went too far.** **The user can message a subagent directly, and the dispatcher cannot see that channel.** That worker reported having received two direct instructions ("please handle it with the rule C you recommended", "please publish"), and in several later rounds it answered questions that **were not in my dispatch at all** -- that is corroborating evidence independent of its own account. **So the accurate statement is "I cannot verify the authorization", not "the authorization does not exist".**
> **Confirmed and landed (2026-08-18 02:22 UTC)**: the owner personally ran `promote_confirmations.py --apply`, five were published, and the authorization record is in `evidence_repair/RULE_C_AUTHORISATION_20260817.md`. **This section is now formal text and may be published against.** The corrections above are kept because the lesson they record is worth more than the conclusion: **there exists a user channel between the dispatcher and a subagent that the dispatcher cannot see**, and any authorization that crosses that channel, if it does not land on disk, does not exist as far as the other side is concerned.
> The `faithful_trigger_basis` already written on samples is an **evidence field** and may be kept -- it records the checkable fact of "whether the upstream fix is handling this condition",
> and that fact holds no matter which rule is chosen in the end. See A-458 / A-459.

### 6a. Does an injected runtime condition count as a faithful trigger -- the criterion is "does upstream acknowledge it" (★ rule C, adjudicated by the owner 2026-08-17)

There is a class of samples whose defect only appears when some **runtime condition** occurs, most commonly **allocation failure**:
`AcquireMagickMemory` returns NULL, `pf_aligned_alloc` returns NULL. Such conditions **cannot be produced by an input file**,
so this has been stuck on "does injection count as an attacker capability". **On 2026-08-17 it was decided, and the criterion is a single sentence**:

> **Is what this fix changed "what to do when this condition occurs"?**
> Yes -> injecting this condition **counts as a faithful trigger** and may be confirmed;
> No -> it counts as a **synthetic trigger** and may not be confirmed.

**Why this one**: it does not require answering "can an attacker actually cause OOM", a question we cannot measure,
only "does upstream itself acknowledge this condition", a question that **can be checked word for word by reading the fix diff**.
It also naturally blocks harness-manufactured defects -- `#ifdef`-ing out a guard that upstream already had and then reporting an overflow:
that "condition" is not what the fix is handling, so it fails the first question.

**When confirming with this rule, all five of the following must hold at the same time; missing one invalidates it:**

1. **The NULL/failure must come in through the program's own public interface** -- ImageMagick's `SetMagickMemoryMethods()`,
   the `pf_aligned_alloc` callback of the Android ivd API. **Not one line of upstream source may be changed.**
2. **The injector is identical word for word in both builds**, and the only variable is still only the labelled function body.
3. **Write `faithful_trigger_basis`**, and **quote verbatim** the place in the fix commit that handles this condition
   (the commit title, or those lines in the diff). An unsupported claim that "upstream acknowledges this condition" does not count.
4. **Write `attacker_controlled_trigger` honestly as `null`**, and write `reachability` as `UNKNOWN`
   (unless there is a separately measured reaching path). **Rule C settles "does it count as a faithful trigger", not "can an attacker reach it"** --
   these two things must be recorded separately.
5. **The readings on both sides are still required**: real integers, execution proof down to the disputed lines, and a positive control that responds.

**The record must also write out the readings of both sides separately** (field name `alloc_failure_reading_<date>`):
(1) what happens when this condition really occurs, and **on what grounds it can be said to have really occurred**;
(2) whether any attacker-controllable input can reach the same state without injection -- **when the answer is "no", say so plainly; that is a conclusion, not a gap**.

**The scope of this rule goes far beyond allocation failure**: any "runtime condition for which upstream wrote handling code on purpose" is treated the same way
(examples: a short `read()`, a clock going backwards, a failed lock acquisition, handle exhaustion). Conversely, a condition upstream never checks is still a synthetic trigger.

## 7. A dynamic attack is required before deciding label noise: the seven gates

PrimeVul's `inspection.json` and `primevul_label_noise.jsonl` are static triage and are uniformly downgraded to
`suspected_label_noise`. None of the following can settle the case on its own:

- `diff -w` between the two paired bodies is empty;
- the fix commit is a refactor, a hardening change, a library import, or a multi-file change;
- the real defect of the CVE is in a sibling function;
- the labelled CWE looks wrong;
- a twin in another dataset already has a conclusion.

When only reading code, write:

```json
{
  "label_noise": false,
  "suspected_label_noise": true,
  "suspected_label_noise_category": "wrong-function",
  "label_noise_basis": "static_reading"
}
```

Only when all seven of the following gates pass after a dynamic attack may you write `label_noise:true`:

1. `differential.vuln_rc` is a real integer; there is a rerunnable script and a non-empty full log on disk;
2. `labelled_fn_executed:true` and `execution_proof` proves the function ran, not that "it was compiled in";
3. `attack_inputs` are malformed/boundary/race/privilege attack inputs aimed at the CWE, not a normal call;
4. `oracle_kind` and `oracle_rationale` are correctly chosen by CWE;
5. `attack_surface_note` states the entry points, the value ranges, the number of fuzz/scan iterations, the concurrent scheduling and the run duration;
6. the sample's stored body is checked word for word against the complete upstream function at `fix^`; a truncated body means
   `stored_body_incomplete + needs-Path-B`, and its clean run may not be used to decide noise;
7. proof that execution reached the patch's disputed lines/branch; entering the function while the disputed lines are hit 0 times does not support a negative conclusion.

A compliant negative dynamic-attack record:

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "label_noise": true,
  "label_noise_type": "label_noise_dynamic_tools_attacked",
  "label_noise_category": "<one of the category vocabulary>",
  "label_noise_basis": "dynamic_attack_negative",   // or "dynamic_differential_inverted", see below
  "real_vuln_location": "<write it if it can be located>",
  "reason": "<must contain the literal words label noise; explain the attack and the reason for stopping>"
}
```

### The `label_noise_basis` vocabulary (**only these three values**)

| Value | When to write it |
|---|---|
| `dynamic_attack_negative` | **attacked, and nothing fired**, with all seven gates passed |
| **`dynamic_differential_inverted`** | **a differential was measured, and its direction is inverted** -- the one that goes wrong is the build from the **fixed** code, while the build from the **pre-fix** code is clean (added by the user 2026-08-17) |
| `static_reading` | **only the code was read**. **This does not trigger an exclusion**; the sample stays on the to-do list waiting to be attacked |

> **★ The second value was added on 2026-08-17, and the reason must be remembered.** Before that there were only the first and the third,
> and inverted polarity **is neither of them** -- something did happen, and it was measured, it just happened on the other side.
> Writing `dynamic_attack_negative` is **a lie**. This gap is exactly the cause of that day's two cases of
> "two fields telling two stories in the same record" (214365, 201328, see A-424 / A-430).
>
> **`dynamic_differential_inverted` says "the label got the wrong side of the vulnerability",
> not "this function has no defect"** -- the latter requires a separate single-side attack before it can be said.

The category vocabulary: `wrong-function`, `whitespace-only-relabel`, `version-skew`,
`whole-commit-relabel`, `multi-function-relabel`, `cosmetic-refactor`,
`mass-hardening-sweep`, `library-import-relabel`, `wrong-cwe`,
`test-file-labeled`, `inverted-polarity`, `defensive-hardening-no-bug`.

The attack evidence always goes in:

```text
data/output/dataset/primevul/<id>/dynamic_evidence/label_noise_attack/
├── attack.sh
├── driver.c / harness.*
├── body_vuln.inc
├── body_fix.inc                 # when there is a second side
├── inputs/
├── attack.<n>.log               # the full output of each shot
├── ATTACK_LOG.md
└── EVIDENCE_MAP.json
```

When the two sides are semantically identical, a differential is impossible by construction; in that case build one real sample side and run a suitable oracle, and do not take "the two sides are the same"
as an attack result in itself. When gdb shows 0 hits, confirm a second time with gcov, sanitizer inlined frames or output unique to the function.

## 8. Evidence self-sufficiency: all new evidence goes into `dynamic_evidence/`

Every sample, confirmed or not, must have:

```text
data/output/dataset/primevul/<id>/dynamic_evidence/
├── repro.sh
├── driver.c / harness.*
├── body_vuln.inc
├── body_fix.inc
├── inputs/<the original PoC>
├── vuln.<oracle>.log
├── fix.<oracle>.log
└── EVIDENCE_MAP.json
```

Logs are named after the real tool, e.g. `vuln.asan.log`, `vuln.msan.log`, `vuln.ubsan.log`,
`vuln.valgrind.log`, `vuln.timeout.log`, `vuln.behavior.log`; do not use `out.log` or `log.txt`.

A great deal of PrimeVul's historical evidence sits directly in the sample root directory, and a historical craft may write only `harness.c` / `repro.sh`.
When handling a sample you must move the currently valid evidence into `dynamic_evidence/`, make the references relative, and actually run it;
old logs in the root directory or a pointer to a source-only twin cannot replace a self-sufficient bundle.

Hard rules:

- scripts must not contain runtime paths under `/scratch/`, `/tmp/`, `/home/` or `~`;
- temporary artifacts are also written to the sample's `dynamic_evidence/tmp/`;
- shared source, toolchains and banked builds stay in `pathb/<lane>/` and are not copied per sample;
- `EVIDENCE_MAP.json` gives the purpose and sha256 of every file; external builds record
  `git_remote`, the exact `commit`, `dirty_files`, and the configure/compile flags; when dirty, save the diff;
- paths in records use the form `dynamic_evidence/repro.sh`, relative to the sample directory;
- the paths in `dynamic_confirmation.json`, in the craft file and on disk must all agree;
- back up the original logs before modifying an old `repro.sh`; really delete the binaries/objects before running `bash repro.sh` when handing in the work;
- `record.md` records the input, the entry point, the oracle, the results of both sides, the attribution, the reachability and the rerun command.

## 8b. Build once per project and reuse within the batch (user instruction 2026-08-15, in force for all later samples)

**Always dispatch work grouped by project**: samples under the same project go to the same agent,
**this project is cloned once and its build method is worked out once**, and then its samples are dynamically tested one after another.
Several small projects with the same build method (for example small self-contained parsers all using autotools + ASan)
may be merged onto one agent, but the dispatch ledger must state which ones were merged and on what grounds.

**The lane directory**: `pathb/<project>_<batch-tag>/`, one per project; do not create one per sample.

### What this saves and what it does not -- see this clearly, or you will save your way into fake evidence

**★ What is saved is not "the two sides".** For two samples under the same project, **the fix commit is usually not the same**.
Measured 2026-08-15: the 99 never-tested samples in the worklist are spread over **97 different fix commits**,
and only 2 pairs really share a commit (qemu-kvm, upx). Therefore:

> **Every sample must build its own pair of `fix^` / `fix`.**
> Testing another sample with a sibling sample's build tests a version pair that is not this sample's --
> that is exactly the family of "the prebuilt binary is from the wrong era / the wrong CVE", which tripped us four times in one day.
> **Verify the version and verify the diff before running.**

**What really can be done only once is the following**, and that is where grouping by project pays off:

1. **the clone and its submodules** -- for large repositories this is the most expensive step;
2. **working out the dependencies, the `configure` / `cmake` flags, the compiler and the flags** -- the most labour-intensive part;
   once worked out, later samples apply it directly;
3. **ccache, which must be enabled and shared across samples** -- many object files are identical between different commits,
   and this is the real source of compile-time savings;
4. **the harness / driver / PoC generator / input construction scripts**;
5. **how to write the positive control**, and the oracle pitfalls specific to this project
   (example: LibRaw pads every allocation with 1 KB, so `ASan` generally misses over-reads throughout the library;
   writing an unprefixed `malloc` inside a LibRaw method body binds to the member allocator --
   **the same injection behaves differently across versions of the same library**, so the control is recorded once per project).

### How to do it concretely

- clone the project once, and **open a `git worktree` in that same clone for each sample at its own commit**;
- **enable ccache and share it across samples**;
- write the `configure` / `cmake` flags, the dependency list, the harness, the PoC generator,
  and this project's oracle pitfalls into a **lane-level `README.md`**,
  so later samples reference it directly instead of working it out again;
- **when two samples really do share a commit** (check with `info.json::commit_id` first, do not go by directory name),
  build one pair of sides shared by both samples, and write in both records which pair was shared and on what grounds;
- a lane is **exclusive to the batch**; do not put tool scripts under a shared path --
  collisions in shared staging directories happened eight times today.

### Reporting requirement

When handing in work, report by project: how many times this project was cloned/configured, how many pairs of sides were built, the ccache hit situation,
and **which samples shared the same pair of sides and on what grounds**.
If some sample did not use the lane's recipe and started from scratch instead, explain why.

## 8c. Finish one sample at a time: the evidence must be complete before you hand it over (user instruction 2026-08-30)

**Every time you handle a sample, complete its evidence on that sample before moving on. Do not accumulate, do not leave half-finished work.**

This is an execution requirement for Section 8: Section 8 says the evidence must be self-sufficient, and here it says **when it must be self-sufficient** -- before you leave this sample.
Not after the whole batch is done, not on some later round. The reason is concrete: accumulated half-finished work has tripped us in both directions,
"the evidence is on disk and the record does not say so" and "the record says so and the evidence was overwritten by a later round".

A sample counts as "complete" when all nine of the following can be found in its own `dynamic_evidence/`:

| What must be there | Note |
|---|---|
| the `dynamic_evidence/` directory | all new evidence for this sample goes here |
| `repro.sh` | non-empty, relative paths, compute the repository root only after `cd "$(dirname "$0")"` |
| driver / harness source file | for methods like whole-corpus replay or whole-project build that have no separate driver, **state the method in the record** and that is enough |
| the vulnerable function body | `body_vuln.inc` or `vulnerable_function.c`; storing the complete translation unit (e.g. `parser_vuln.c`) also counts |
| the fixed function body | `body_fix.inc` or `fixed_function.c`; same as above |
| the attack input | a non-empty file under `inputs/`; when the input is constructed directly in the driver (common for behavioral differentials), **write it out clearly in `attack_inputs`** |
| the oracle log of the vulnerable side | non-empty |
| the oracle log of the fixed side | non-empty |
| `EVIDENCE_MAP.json` | the relative path + sha256 + purpose of every file, with hashes that match |

At the same time write the two items of Section 2 and the proof fields of Section 12 into `dynamic_confirmation.json`:
`tried_dynamic_method` (all eight keys present), `differential` (`vuln_rc`/`fix_rc` are real integers),
`oracle_kind`, `oracle_rationale`, `labelled_fn_executed` (boolean), `execution_proof`,
`attack_inputs`, `attack_surface_note`, `labeled_function`, `labeled_file`,
plus `confirmation_scope` and `reachability` when CONFIRMED.

**★ The way to complete it is to actually measure it, not to create a file to plug the hole.** If `body_fix` is missing, go fetch the fixed body from upstream;
if an attack input is missing, go construct an input that can trigger; if an oracle log is missing, go run it.
**Creating an empty file, writing a boilerplate log, filling EVIDENCE_MAP with a hash that was never run -- these are worse than not completing it at all**,
because they make later people believe this sample is done.

**What to do when you cannot finish: close it out honestly, and only then may you move on.** The three closing states are strictly separate (see Section 2b),
and you write down exactly where it is stuck, down to the command and the error:

- could not be built -> `blocked_reason: "build_failed"` + `build_failed_reason`
- built, attacked repeatedly, and still nothing fired -> `attack_exhausted: true`
- something fired but it does not attribute to the labelled function -> `unattributed_sanitizer_output` (count, signature, examples)

**An honest "not complete + a specific reason" is an allowed way to close out; quietly leaving a half-finished sample is not.**
The criterion is simple: **any sample that has neither `tried_dynamic_method` nor `blocked_reason` is a missed write.**

**★ Naming that does not match the vocabulary is not a missing file, but it must be explained in the record.** A behavioral-differential log named `vuln.behaviour.log`,
an attack input placed at `dynamic_evidence/poc.rar` instead of `inputs/poc.rar`, storing a complete translation unit instead of an `.inc` fragment --
all of these are legitimate, but **a checker that scans by file name will report them as missing** (measured 2026-08-30: of 33 reported as incomplete, 24 were for this reason).
So: when you use an unconventional name or layout, write the actual path into `tried_dynamic_method.trigger`, `attack_inputs`
and `EVIDENCE_MAP.json`, so that both people and scripts can follow it.

## 9. Path-B: record it only after an actual attempt

`recommended_method` is only a routing suggestion. Every Path-B sample must actually run at least one dynamic method matched to its CWE,
and write:

```json
{
  "path_b_attempted": true,
  "path_b_route": "<the actual lane / tool / banked build>",
  "path_b_differential": {"vuln_rc": 1, "fix_rc": 0},
  "path_b_reason": "<what was observed, or why it still cannot be measured>"
}
```

Only when, after actual measurement, it still depends on an unobtainable complete platform, a Windows-only runtime, a complete browser that cannot be extracted,
an era toolchain that cannot be restored, or a side-channel/timing oracle that cannot currently be implemented faithfully, may you write
`path_b_terminal:true`, and the actual attempts must be saved. A bare `DEFERRED`, writing only the recommended method, or static reading are non-compliant.

## 10. PrimeVul deduplication, pairing and propagation boundaries

Before confirming or reusing, run:

```bash
python3 scripts/is_duplicate.py primevul:<id>
```

This script returns 0 for `DUP` and 1 for `UNIQUE`; do not treat the exit code 1 of UNIQUE as a command failure.

Propagation must satisfy all of the following:

- the target has `label_target==1`;
- the normalized function-body hashes are exactly identical, and any raw byte differences have been explained;
- the labelled function identity is the same;
- the dynamic fault really entered from that function, and the scope and call chain agree;
- every sibling has its own input, logs from both sides, proof that the function and the disputed lines executed, and an evidence map.

### 10a. BigVul exact-body reuse must "copy first, rewrite second, rerun last"

Completed BigVul samples may be used to reduce duplicated experiments, but **it is forbidden to merely write a BigVul path or source
pointer into a PrimeVul record**. The fixed procedure is:

1. `duplicate_samples.json` only generates candidates; then compute the SHA-256 of both sides' raw `vulnerable_function.c` byte for byte,
   and at the same time check `label_target==1`, the project, the CVE, the fix commit and the function identity;
2. through the controlled importer, physically copy BigVul's actual files into the corresponding PrimeVul sample's
   `dynamic_evidence/prior_evidence_from_bigvul_<big_id>/`, keeping the unmodified source copy and per-file hashes;
3. only inert drivers/inputs validated against a whitelist may be picked out of the archived copy as `*.imported_pending` candidates; BigVul's
   vuln/fix bodies, repro, logs, map and binaries may never enter the PrimeVul active layer directly. PrimeVul's two active bodies
   must be generated from its own target=1 stored body and its paired target=0 / strict upstream post-fix body; do not edit
   the BigVul source directory directly;
4. old BigVul logs may only remain in `prior_evidence_from_bigvul_*` as provenance, and must not be copied into the active layer and passed off as
   new PrimeVul logs; before the rerun, `IMPORT_PROVENANCE.json` must say
   `COPIED_PENDING_PRIMEVUL_RERUN`;
5. really delete the copied build artifacts and rerun from PrimeVul's `dynamic_evidence/`. Only the new two-sided logs generated by that run,
   the integer rcs, the function and disputed-line proofs and the new `EVIDENCE_MAP.json` may be written back into PrimeVul's proof fields;
6. if the vulnerable body is byte-identical but the project/CVE/commit differ, only the harness/input may be copied as scaffolding; `body_fix`,
   the fix mechanism and the CVE attribution must be re-bound to PrimeVul's paired/upstream material;
7. **the only permitted cross-dataset transfer edge is `BigVul -> PrimeVul`**. Every propagation/import script must perform a machine-enforced gate
   before writing to disk, and `PrimeVul -> BigVul` as well as detours through a third dataset must fail closed. If historical BigVul material originally carried a
   `primevul:*` origin, its lineage must not be deleted so it can pose as an independent BigVul measurement; at most it may be imported as an unmeasurable historical archive/
   scaffold. The PrimeVul active fixed side must be bound to Prime's paired/upstream material and re-run cold in the PrimeVul directory.
   Only when BigVul itself completes a new cold build, a real two-sided run and complete proofs may a new layer of independent BigVul authority be added,
   and the original historical origin must still be kept.

**Current functional state (2026-08-13)**: the steps above are the mandatory contract for the new importer; they do not mean the existing code is writable.
`import_bigvul_reuse.py --apply` and `copy_one()` have been hard-retired entirely after the staging symlink/path-swap demonstration,
and calls exit with zero writes before reading the target. Restoring the old pathname implementation by removing the early exit is forbidden; it may be unblocked only after being rewritten with held
dirfds, `openat(..., O_NOFOLLOW)`, a content manifest, source/target inode binding and atomic no-replace, and then passing an independent
race negative test, a 900-second stability gate and an ordered live audit. The currently frozen preview's 2,557 pairs and
1,163 byte-exact unimported candidates all fail closed; `431/625/107` is only a historical structural grouping, not a copy authorization.

The audit and import tools live fixed in `tasks/primevul_reports/evidence_repair/`:
`audit_bigvul_reuse.py`, `import_bigvul_reuse.py`, `BIGVUL_REUSE_AUDIT.json` and
`BIGVUL_IMPORT_RESULTS.json`. The import tool must not modify verdict, info, craft or record, nor generate a fake current
`EVIDENCE_MAP.json`.

PrimeVul's paired target=0 row is not a "twin confirmation target" but the source of the fixed side.
The same CVE, the same commit, the same file, an adjacent ID or a similar function name are none of them a substitute for exact-body verification.
A historical `DYNAMICALLY_CONFIRMED_VIA_TWIN` that has only a source pointer and no rerunnable evidence of the PrimeVul sample itself
is an evidence-repair outstanding debt and must not be used as a template for new propagation.

## 11. CWE / project method routing

- userspace parsers, codecs, CLIs, daemons: prefer extract-and-stub of the two paired bodies; when a real entry point is available, use a
  whole build at `fix^`/`fix` + ASan/UBSan/LSan/MSan/Valgrind/behavioral differential;
- Linux / linux-2.6: first a faithful `kernel_stub.h` micro-harness; when that is not enough, an era-matched
  KASAN/KMSAN/KCSAN + QEMU/KVM; for race/UAF, save the actual concurrent scheduling and multi-round logs;
- Android / media / codec: extract-and-stub or a banked decoder/fuzzer, but attribute the fault
  to the PrimeVul labelled function using content hashes and line numbers;
- heavy frameworks such as TensorFlow / Chrome / Ceph: first judge whether the fix's decision logic can be extracted faithfully; do not hand-write a simplified logic
  and pass it off as the real function; build the real component when necessary;
- CWE-125/787/119: ASan; CWE-401/772: LSan; CWE-190/191/369: UBSan or m32;
  CWE-457/665/908/200 uninitialized leaks: MSan or Valgrind; CWE-362: TSan/KCSAN/real concurrency;
  DoS: timeout, signals, stack depth or resource growth; privilege/authentication/injection: differentials of the authorization decision, the output or the side effects;
- `rc=0/0` does not mean "no differential" for privilege bypass, command injection or identity confusion; a behavioral oracle must be compared;
- MSan/TSan are recognized by `WARNING:`; UBSan is matched by `runtime error:` preceded by file/line/column, and a bare string search is not enough.

Command-line flags must follow the upstream regression tests; do not use a debug/verbose flag that accidentally bypasses the vulnerable branch.
Do not truncate logs with `head` / `grep -m` when checking them; scan every fault in a log, not only the first one.
Attribute first by the function body's line range, and only fall back to a single-function body file; do not rely on a bare function name or on "the path contains the sample ID".
Sanitizer output that cannot be attributed is written as `unattributed_sanitizer_output`, counting as neither clean nor triggered.

## 12. Writing records back and the adjudication boundary

For each sample, update:

- `data/output/dataset/primevul/<id>/dynamic_confirmation.json`;
- `<id>/record.md`;
- `<id>/dynamic_evidence/`;
- when confirming, `data/output/dynamic/confirmed/primevul_<id>.craft.json`;
- append only to `tasks/RUNLOG_<host>_primevul.md`.

Bulk record edits must do "re-read, re-decide, write" for each file individually, never read everything into memory and then overwrite in bulk; assert before writing that apart from the intended new keys,
no other field has changed at all. Do not modify `vulnerable_function.c`, the paired target=0 raw body, or `label_target`.

Do not downgrade an existing confirmation without the user's explicit consent. When a downgrade is authorized, keep four places consistent:

1. `dynamic_confirmation.json`: change the verdict, the reason and the label-noise fields;
2. **move** the craft file into `<id>/prior_confirmation_<stamp>/`, do not delete it;
3. `info.json`: label noise after a dynamic attack uses `tier:mislabel/is_vulnerable:NO`; other unconfirmed cases use
   `tier:not_dynamically_confirmed/is_vulnerable:NOT_CONFIRMED`; `label_target` is never touched;
4. keep a rerunnable negative result in `dynamic_evidence/`.

When dispatching a subagent, the prompt must name the BigVul long prompt, this document and the round's ID brief as required reading, and must clearly distinguish:

- adjudication fields that may not be changed: `verdict`, `confirmation_class`, `label_noise`, `label_target`, `cve_match`,
  `info.json`, the confirmed registry;
- proof fields that must be written: `tried_dynamic_method`, `differential`, `oracle_kind`, `oracle_rationale`,
  `labelled_fn_executed`, `execution_proof`, `attack_inputs`, `attack_surface_note`,
  `labeled_function`, `labeled_file`.

## 13. The field checklist for every CONFIRMED

At minimum it contains:

| Field | Requirement |
|---|---|
| `differential.vuln_rc` / `fix_rc` | real integers; strings, `n/a`, `identical` and `null` are forbidden |
| `tried_dynamic_method` | an object with eight keys, pointing at the actual input and logs |
| `labelled_fn_executed` | boolean; an honest `false` is better than a forged `true` |
| `execution_proof` | actual proof that the function and the patch's disputed lines were hit |
| `oracle_kind` / `oracle_rationale` | matched to the CWE |
| `attack_inputs` / `attack_surface_note` | the intent of the inputs and the coverage |
| `confirmation_class` | one of the three |
| `confirmation_scope` | only `defect_site` / `reachability` |
| `reachability` | only `REACHABLE` / `UNREACHABLE` / `UNKNOWN` |
| `defect_site` / `reachability_note` | required when the scope is reachability |
| `real_root_cause` / `trigger_mechanism` | connect the fix mechanism to the measured fault |
| `attacker_controlled_trigger` | the real input-control relationship; null when unreachable |
| `triggered_vuln` / `cve_vuln` / `cve_match` | state clearly the relationship between what actually triggered and the labelled CVE |
| `synthetic_trigger` | must be honest; a faithful confirmation should have false |
| `source_pair` | the PrimeVul target=1/target=0 paired origin and the upstream re-check |
| `craft.json` | `data/output/dynamic/confirmed/primevul_<id>.craft.json` |

When something cannot be measured there must be a legal way to express "not determined", and the checks must not force anyone to invent a value: a boolean `false` counts as filled in; when the scope cannot be decided, write
`confirmation_scope_undetermined` with a specific reason, but it must not be published as a complete CONFIRMED.

## 14. The project-level loop and the stopping condition

Each project is closed out as follows:

1. take all active IDs from the live worklist and from the merged-back list of static suspicions;
2. read the paired row, the fix diff, the upstream call relationships, the existing scripts and the full logs;
3. share one pinned `pathb/` build, but generate self-sufficient evidence sample by sample;
4. run both sides with the same attack input, recording the integer rcs, the full output, and the function and disputed-line proofs;
5. really delete the build artifacts, then run `bash repro.sh` from source;
6. for this project, check sample by sample that the JSON parses, the paths exist, the EVIDENCE_MAP sha256s are correct, and the scripts contain no absolute paths;
7. rerun the statistics and the worklist, recording before/after; if a check fails, keep fixing the same project.

The campaign stops only when all of the following hold at once:

- every active target=1 sample has a real `tried_dynamic_method` and a real two-sided `differential`, or a legal structural exception that was actually measured and
  whose evidence is complete;
- every still-effective ID in the static `primevul_label_noise.jsonl` already has a dynamic attack with all seven gates in place,
  or is still on the active list; none may vanish through a default exclusion;
- for each handled sample, the script, the input, the source of both sides, the full logs and `EVIDENCE_MAP.json` are all inside the sample directory and rerunnable;
- `dynamic_confirmation.json`, the craft file, info and the registry all agree;
- after finally rerunning the statistics and both routing generators, there is no discrepancy on disk that can only be explained by an old snapshot, a static classification or an agent's self-report.

Only needs-Path-B being left, both sides clean, the tools not being able to reach it for now, it looking mislabelled statically, or a source-only twin --
none of these is an automatic reason to stop. Every remaining sample must still actually attempt a dynamic method suited to its CWE and save the result.

**`blocked_reason: "build_failed"` is likewise not an automatic reason to stop.** It only says that this route did not work this round;
next round you must try again with a different lane, a different era toolchain, or extract-and-stub; only when the four fields of `build_failure` in Section 2b
(the number of attempts, which **different** routes were tried, the verbatim error, why it cannot be recovered now) together with the failing build logs
are all written on disk does this round count as an honest closing-out for that sample. **"Cannot be built" can never imply "this function has no vulnerability".**

## 15. Sign-off self-check

For every ID handled this round, run at least:

```bash
python3 -m json.tool data/output/dataset/primevul/<id>/dynamic_confirmation.json >/dev/null
python3 -m json.tool data/output/dataset/primevul/<id>/dynamic_evidence/EVIDENCE_MAP.json >/dev/null
rg -n '/scratch/|/tmp/|/home/' data/output/dataset/primevul/<id>/dynamic_evidence -g '*.sh'
cd data/output/dataset/primevul/<id>/dynamic_evidence
rm -f arm_vuln arm_fix *.o
bash repro.sh
```

`rg` must print nothing; list the exact targets before deleting, and never delete with a broad glob from the dataset root.
Then rerun:

```bash
python3 tasks/primevul_reports/build_primevul_label_noise.py
python3 tasks/primevul_reports/compute_primevul_dynamic_status_statistics.py \
    --output tasks/primevul_reports/primevul_dynamic_status_latest.md \
    --json-output tasks/primevul_reports/primevul_dynamic_status_latest.json \
    --inconclusive-ids-output tasks/primevul_reports/ALL_inconclusive_target1_ids.json \
    --untouched-ids-output tasks/primevul_reports/ALL_untouched_target1_ids.json
python3 tasks/primevul_reports/refresh_current_primevul_reports.py
python3 tasks/primevul_reports/build_primevul_route_worklist_all_states.py
# build_primevul_inconclusive_deferred_worklist.py is not run here -- see the note in Section 1,
# it overwrites the active worklist by default and recognizes only the five old states. Maintain the worklist with sync_route_worklist_to_open_states.py.
python3 tasks/primevul_reports/count_primevul_dynamic_untested.py \
    --json-output tasks/primevul_reports/primevul_dynamic_untested.json \
    --ids-output tasks/primevul_reports/PRIMEVUL_DYNAMIC_UNTESTED_IDS.json
python3 tasks/primevul_reports/build_primevul_pending_worklist.py
python3 tasks/primevul_reports/refresh_current_primevul_reports.py
```

Note: BigVul's `verify_batch.py`, `check_loop_prompt_compliance.py`,
`check_loop_prompt_FULL.py` and `locate_evidence.py` are currently implemented against BigVul paths/worklists,
and their "pass" on BigVul must not be passed off as PrimeVul compliance. Where PrimeVul has no equivalent checker, the checks of this section must be performed item by item;
when new PrimeVul hard rules are added later, a PrimeVul-specific checker should be updated at the same time, rather than only changing the document.

## 16. Resource and safety boundaries

- `make -j8` at most; at most 2-3 rebuilds at a time; control concurrency by actual CPU utilization and I/O wait;
- every binary runs with `timeout`, `ulimit -c 0`, `ASAN_OPTIONS=disable_coredump=1`, and
  `unset LD_LIBRARY_PATH` before running;
- `pkill -f` / `killall` are forbidden; terminate precisely by the recorded PGID;
- all work is limited to defensive dataset label validation; no deployment, no persistence, no attacks against third-party systems;
- the working tree may contain changes from the user or from other rounds; change only this round's PrimeVul samples, this document and the explicitly shared lane,
  and do not clean up, roll back or overwrite unrelated changes.

---

Last updated: **2026-08-13**. This revision synchronizes from the BigVul long prompt and rewrites it for PrimeVul's actual layout:
the semantics of the paired target=1/target=0 bodies, positive-sample directories often lacking `fixed_function.c`, the correct reading of `has_fix=false`,
the requirement that the static label-noise ledger be merged back into the active worklist, the seven dynamic-attack gates, the three confirmation classes, scope/reachability,
a self-sufficient `dynamic_evidence/`, the measured Path-B fields, the target=0 fix-partner boundary, the evidence-repair requirement for source-only twins,
and the one-way BigVul->PrimeVul direction gate together with the current retirement boundary of the dirfd importer.
