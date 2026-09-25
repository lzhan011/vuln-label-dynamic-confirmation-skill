# MegaVul Dynamic Confirmation /loop Prompt

> **The "must not be violated" part of this long document has already been condensed into the `CLAUDE.md` at the repository root (`AGENTS.md` is a symlink to it)**,
> which is auto-loaded at the start of every session, so nobody has to remember to read this file. When the two conflict, **this document wins**;
> if you change a hard rule here, remember to change `CLAUDE.md` to match.
> **This document is aligned section by section with `tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md` (2026-09-24)**: section order,
> the four outcomes, the secondary-field vocabularies, the seven gates, the seven rules of evidence self-sufficiency, and the sign-off self-check are all identical; only the paths, the snapshot,
> the dataset characteristics and the outstanding debt are MegaVul's own. When a hard rule changes on the BigVul side, it must be changed here too.

> ## ★★★★★ Read this one first: what this round has to hand over at the end
>
> **Every `target=1` sample must land in exactly one of the four outcomes below, and the four numbers must add up to the denominator.**
> The detailed definitions, the secondary-field vocabularies and the decision order are in **§0a**; the verbatim text you paste into `/loop`
> also carries the same "output ruler" at its end, and **when you paste it you must paste that part along with it**.
>
> | Outcome | In one sentence |
> |---|---|
> | `CONFIRMED` | The attack fired, and it attributes to the labelled function |
> | `LABEL_NOISE_EXCLUDED` | Attacked, and not a single fault fired (all seven gates in place), or the differential that was measured points the wrong way |
> | `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | Genuinely attacked, readings from both sides obtained, but this measurement cannot decide between confirmation and mislabel |
> | `NOT_DYNAMICALLY_TESTED` | No valid dynamic measurement has been obtained yet (never tested / could not reach it / built and ran but produced no result) |
>
> **`INCONCLUSIVE`, `DEFERRED`, `DEFERRED_NEEDS_CALLER`, `DEFERRED_HEAVY_FRAMEWORK`, `DEFERRED_PATH_B`,
> `NOT_TRIGGERABLE`, `NOT_TRIGGERABLE_AS_LABELED`, `NOT_CONFIRMED`, `UNTOUCHED` are no longer outcomes**;
> they may only remain in the `verdict` field of a sample's record (`dynamic_confirmation*.json` / `inspection.json`) as history.

<!-- CURRENT-SNAPSHOT-START -->
## Current auto-updated snapshot (2026-09-24)

Source of truth for the statistics: `megavul_dynamic_status_latest.json`. `target=1` **17,592**; `CONFIRMED` **2,622**; `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` **383** (human re-review judged them conflicting/insufficient, per the user's 2026-09-24 instruction); `INCONCLUSIVE` **6**; `UNTOUCHED` **14,580**; `LABEL_NOISE_EXCLUDED` **0**.

label-noise: **292** in the maintenance ledger, **1** explicit in result files, **293** after merge and dedup. The historical body text is not used as the current count.
<!-- CURRENT-SNAPSHOT-END -->

### How to read and how to refresh the snapshot (hand-written, not inside the auto block; the refresh script only rewrites the block above)

- The `CONFIRMED` number in the auto block above already has the **383** subtracted that human re-review judged conflicting/insufficient and that were marked as the third outcome per the user's 2026-09-24 instruction
  (in `compute_megavul_dynamic_status_statistics.py` that outcome has higher priority than the ledger's or the verdict's CONFIRMED);
  `CONFIRMED` still contains **943** cross-dataset exact-function-body propagations (PrimeVul 865, BigVul 76, DiverseVul 2) that **were never run locally**,
  and which per §0a must be counted separately as `attempted_inherited_crossdataset`; the statistics script does not split them out yet (outstanding debt).
- `UNTOUCHED` 14,580 plus the 2,702 `inspection.json` files (static review, whose verdicts are all of the `DEFERRED_*` / `NOT_TRIGGERABLE*` family) all belong to the fourth outcome.
- The `data/output/dynamic/confirmed/` directory holds 2,890 `megavul_*` files -- **whenever you cite "how many entries the ledger has", you must say whether that is the file count in the directory or the number of entries inside the denominator.**
- **★ There is one unresolved discrepancy in the denominator, and it must be settled before the next recomputation**: the status file's denominator is 17,592, while the 2026-09-14 full scan of
  `data/output/dataset/megavul/` found **15,222** sample directories (`manual_check_megavul_20260914/population_stats.json`).
  Both numbers cannot simultaneously be "the number of target=1 samples". Until this is settled, report both numbers and note the discrepancy.
- Refresh commands (if **any confirmation was published** this round you must run the full set, and run it again before closing out):

```bash
python3 tasks/megavul_reports/compute_megavul_dynamic_status_statistics.py
python3 tasks/megavul_reports/refresh_current_megavul_reports.py
python3 tasks/megavul_reports/build_megavul_inconclusive_deferred_worklist.py
```

> **★ These walk every sample directory, which is very heavy on NFS** (measured 2026-09-24: one full-database pass takes about 20 minutes; even sampling only 3,000 directories to read records did not finish in 600 seconds).
> **Rule: when this round published no confirmations at all, skip the full-database statistics**, and use a lightweight query that reads only the few dozen samples of this batch to check progress;
> **after publishing you must run it once to catch up**. The criteria are **CPU utilization and I/O wait**, not load-avg: **only a high wa means real congestion**.

**The snapshot is an entry point, not proof of completion.** The old reports' "CONFIRMED 3,005 / independent 1,710 / canonical-only 352" are numbers from 2026-07-23, superseded by the 2026-09-24 recomputation, and must not be cited any more.

---

## Wording (★ a hard rule from the global CLAUDE.md, applying to all text written for humans)

The older paragraphs of this document and MegaVul's older records are full of "the two arms", "the sample arm", "the fix arm". **Newly written text must not use the word "arm" any more** --
the user explicitly required this on 2026-08-06; it is unclear what that word refers to here. Say directly what the thing itself is:

- "both arms clean" -> "**the readings from both sides are clean**" or "the build from pre-fix code and the build from the fixed code are both clean"
- "the fix arm also crashes" -> "**the build from the fixed code also crashes**"
- "the sample arm cannot trigger it" -> "**the build from pre-fix code cannot trigger it by itself**"

Likewise, do not use the word "predicate" (say "the decision rule", "the fields this code actually checks") and do not use the word "prose" for narrative text (say "the explanatory text in the document").
When talking about the two label-noise categories you must use the unambiguous full sentences; see the section "these two categories must be stated as full sentences" at the end of this document.

---

## ★★ Reading traps: these pitfalls manufacture false negatives that "look like nothing was measured" (measured 2026-08-15, synced from PrimeVul / BigVul)

Every item below was learned the hard way, and **every one of them can cause a real vulnerability to be recorded as "the attack did not fire"**.
Over **95%** of MegaVul's confirmations are a single Path-A harness (see "dataset characteristics" below), so traps ①②⑤⑥⑧ are more common here.

### ① A positive control that "cannot actually go wrong" proves nothing

Measured on PrimeVul 5540: to prove the oracle was alive, the worker built a positive control -- widening the mask `0xff0000`
to `0xffff00`. **But those bits are constantly zero after the shift**, so the checksum computed by this "defect-injected" control
**was identical to that of the real function body**. The control "passed", while it had in fact measured nothing.

**Rule: a positive control must first prove that it itself responds.** Merely "injecting a defect" is not enough --
**you must see the control's output actually differ from the real function body's** (a different checksum, a different exit code, extra sanitizer lines).
When the control and the real function body give the same result, that is **the control failing**, not "the function being fine".
Same family: clang `-O1` optimizes away the whole allocation injected into the control, so compiling, linking and running all look normal while the control is mute.

### ② `-fsanitize=integer` reports unsigned left shifts, and that is not a defect

`unsigned-shift-base` will be reported **on both sides with the same value** -- an unsigned left shift is **defined behavior**,
and this checker merely treats it as a suspicious idiom. **Identical on both sides = a tool artifact.**
When using `-fsanitize=integer`, turn it off and write in `repro.sh` why it was turned off.
**Same-family cases from MegaVul's human re-review**: the signed-shift UB of `255<<24` inside the harness's own `ato32` stub
(17047/17051/17052/17053/17054/17056/17057) had been recorded as a trigger -- that is how the stub was written, not a mechanism in the labelled function,
and re-review judged it "Invalid Test".

### ③ "The two sides differ" is not a confirmation -- first look at which side is faulting

Measured on PrimeVul 204396: of 500 test cases, 314 separated the two sides, and the numbers looked like a very solid differential.
But **the side that faulted was the build from the fixed code** -- that "fix" was in fact a **compilation patch-up** on top of the upstream patch,
and upstream deleted it the next day. Building another one carrying only the CVE-relevant hunk gave 0/500 --
the entire differential came from a different hunk.

**When you see the two sides separate, ask three things first**:
① **Which side is faulting** (only a fault in the build from pre-fix code can be a confirmation; a fault in the build from the fixed code is inverted polarity);
② **Is it caused by the patch's hunk** (a commit often contains several changes; building another one carrying only the target hunk isolates it);
③ **Is that "fix" really a fix** (some labelled commits are compilation patch-ups after a backport,
and the stored function body may even be an **intermediate state that does not compile**).
**Reading only "the two sides disagree" without looking at the direction records inverted polarity as a confirmation.**
Instances in MegaVul where the two stored function bodies are **inverted**: 1082, 6909 (human re-review batches 3-5) -- the harness compiled `fixed_function.c`,
claimed "the labels are swapped" and reported a confirmation; re-review judged them conflicting. **Inverted polarity must go through §0a's `inverted_polarity` -> the two gates -> label noise, not confirmation.**

### ④ Reading `git show --stat` and looking only at the biggest file will miss a one-line hunk

Measured on PrimeVul 216832: the old record said the commit "just added a test certificate", and on that basis it was judged impossible to produce a differential.
In fact the same commit **also changed one line in another file** -- and that line was exactly where the labelled function lives.
**`--stat` sorts by size, so a one-line change comes last and is the easiest to get truncated away.**

**Before judging that "this commit did not touch the labelled function", you must run `git show <commit> -- <labelled file>` to see that file's full diff on its own.**
This is the same family of error as "the commit touched 41 files, so it is a bulk relabel":
**the size of a commit cannot substitute for reading what it did to this file.**
In MegaVul, both `info.json::commit_id` and the `project` field are 40-character hashes (`project` actually stores the commit from `code_link`),
so **first use `code_link` to verify which one is the fix commit**, then run `git show`.

### ⑤ The two banked binaries may not contain the labelled function at all -- and that looks like "no differential"

Measured on PrimeVul 204794: the pair of binaries marked in the previous round as "both banked, just run them" were **byte-for-byte identical**.
The cause was purely a build one: that coder was wrapped in an `if <DELEGATE>`, and this machine had only the runtime library,
not the `-dev` package, so **the labelled function was in neither binary**. The run gave 0/0, which reads as "both clean".

**Rule: before running any banked binary, first prove that the labelled function really was linked in.**

```bash
nm <binary> | grep -c ' [Tt] <labelled function name>'      # must be == 1 (for C++ use nm -C or match the mangled name)
```

Put this assertion into `repro.sh` so that it **fails immediately** after the build, rather than being read as a negative result after the run.
**"Both clean" says nothing at all until the labelled function has been proven to execute.**
**The same family of problem is even more widespread in MegaVul**: in the human re-review of 1,677 CONFIRMED samples, **199** (11.9%) of the harnesses
**never compiled the labelled function body in at all** (main restates a few lines of the core arithmetic itself, or restates it after renaming to `*_vuln_core`),
so the fault establishes something about the harness author's code -- see item 5 under "dataset characteristics" below. **For a single Path-A harness,
"the labelled function body is compiled in verbatim" must be checked in `repro.sh` with `cmp` against `vulnerable_function.c`.**

### ⑥ Two pitfalls in the sanitizers themselves

1. **ASan's default fast unwinder drops the labelled function out of the stack entirely** -- when passing through libstdc++, which has no frame pointers,
   the stack breaks in the middle. **You need `ASAN_OPTIONS=fast_unwind_on_malloc=0`.**
   This means that some of the earlier conclusions of the form "not a single frame of the labelled function appears in the fault stack"
   **may be an artifact of dropped frames**. Before judging `unattributed_sanitizer_output`, rerun once with this option changed.
2. **clang does not instrument `std::string::empty()`'s read of an out-of-bounds element** -- ASan stays silent the whole way,
   while a raw read of the same byte does get reported. **A "clean" probed through container methods says nothing**; re-check with a raw read.
3. **MegaVul-specific: MSan/ASan "nested crash, no stack frames"** (`MemorySanitizer: nested bug in the same thread, aborting`,
   `SEGV on unknown address (pc 0x0 ...)` carrying only sanitizer-internal frames). In the human re-review this category is the largest share of "insufficient evidence"
   (most of the 104 "fault cannot be attributed" cases are this). A report with not a single frame in the stack **counts neither as a trigger nor as clean**;
   first add `fast_unwind_on_malloc=0` / `handle_segv=1` / switch to `-O0` and rerun before judging.

One more reading rule: **a sanitizer report that is byte-identical on both sides cannot be something the patch changed** --
it is an artifact of the toolchain or the environment; record it as `unattributed_sanitizer_output` (it counts neither as a clean log nor as a trigger),
and **rename that log to `oracle_probe_*` so it does not share a namespace with the differential logs**.

### ⑦ This machine has network access -- actually try once before saying "upstream cannot be verified"

Measured: `git ls-remote https://github.com/<org>/<repo>.git HEAD` returns a commit hash immediately.
This is written here because **two workers have already made judgements they should not have made by assuming "there is no network"**:
one attributed a CVE to a different module from memory, and the other wrote a checkable upstream fact down as "cannot be verified".
Put the upstream source you fetch in `pathb/<lane>/`, and write `git_remote` plus the exact commit into the record -- which rule 4 required anyway.
MegaVul's `info.json::code_link` gives the upstream commit URL directly, so **there is no excuse not to verify**.

### ⑧ After an assertion in the record-writing step fails, do not carry on with the work

Measured, PrimeVul 4461 was nearly lost: an assertion in an inline record-writing script fired and **nothing was written**, while the work pushed on,
leaving a complete measurement on disk next to an empty record.

**Rule: run a field scan before handing over the work** -- any sample that has **neither `tried_dynamic_method`
nor `blocked_reason`** is a write that was missed, and must not be let through.

---

## 0a. ★★ There are only four outcomes (set by PrimeVul 2026-08-21; aligned with DiverseVul §2a on 2026-09-20; MegaVul followed on 2026-09-24)

**This section is this prompt's output ruler: whatever was done this round, every sample handed over at the end can only be one of the four below.**

When reporting numbers outwardly, writing records, or computing statistics, **only the following four outcomes may appear**; each `target=1` sample lands in exactly one,
and the four numbers add up to the denominator (recompute the denominator every round with the refresh commands in section 0; do not cite the old numbers in the snapshot):

| Outcome | Meaning | Secondary fields |
|---|---|---|
| `CONFIRMED` | The labelled function triggered a real defect under faithful input | `confirmation_class` (one of the three tiers), `cve_match`, `confirmation_scope` (`defect_site`/`reachability`), `reachability` (`REACHABLE`/`UNREACHABLE`/`UNKNOWN`) |
| `LABEL_NOISE_EXCLUDED` | The label is overturned: **either** it was attacked with a tool matching the CWE, nothing triggered, and all seven gates are in place, **or** a differential was measured and its direction is inverted | `label_noise_category` (vocabulary in the section "explicit marking rules for label noise"), `label_noise_basis` (`dynamic_attack_negative` or `dynamic_differential_inverted`), `label_noise_type`; write `n/a` for `cve_match` |
| `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | **It really was attacked with a dynamic tool and readings from both sides were obtained, but this measurement cannot decide whether it is a confirmation or a mislabel** | `dy_attacked_undecided_category`, see the table below, **required** |
| `NOT_DYNAMICALLY_TESTED` | **No valid dynamic measurement has been obtained yet**: never tested, could not reach it, or built and ran but produced no result | `not_tested_reason`, see the table below, **required** |

> **★ 2026-09-20: the fourth outcome was renamed from `BUILD_FAILED` to `NOT_DYNAMICALLY_TESTED`,
> and the secondary field from `build_failed_reason` to `not_tested_reason`** (DiverseVul changed it first on 2026-08-19, BigVul followed on 2026-09-20, MegaVul uses the new name directly).
> **The rename is not a matter of wording.** What it really means is "no valid dynamic measurement has been obtained yet", and most of these **were never worked on at all** --
> MegaVul's 14,580 `UNTOUCHED` samples and 2,702 `inspection.json` files are the bulk of this cell, and not one of them is a "build failure".
> `build_failed` is demoted to a subcategory under it, reserved for samples that genuinely recorded a build failure.
> The old names `BUILD_FAILED` / `build_failed_reason` **serve only as aliases** so that old scripts and old records on disk can still be read;
> **newly written records, reported numbers and partitions must all use the new names.**

**The following strings are no longer outcomes**, and none of them may appear in a result partition:
`INCONCLUSIVE`, `NOT_DYNAMICALLY_CONFIRMED`, `DEFERRED`, `DEFER`, `DEFERRED_STATEFUL`, `DEFERRED_NEEDS_CALLER`,
`DEFERRED_HEAVY_FRAMEWORK`, `DEFERRED_PATH_B`, `DEFERRED_PURE_DOS`, `DEFERRED_NONDETERMINISTIC_OOM`,
`DEFERRED_LOGIC_SECURITY_BYPASS`, `NOT_TRIGGERABLE`, `NOT_TRIGGERABLE_AS_LABELED`, `NOT_TRIGGERABLE_STANDALONE`,
`NOT_CONFIRMED`, `not_confirmed`, `NOT_CONFIRMED_LABEL_NOISE`, `NOT_CONFIRMABLE`, `CANNOT_CONFIRM`,
`INFEASIBLE_*`, `FEASIBLE_UNTRIED`, `LABEL_NOISE`, `NEEDS_PATH_B`, `<MISSING_OR_UNPARSEABLE_VERDICT>`, `UNTOUCHED`.
They may stay on in the `verdict` of `dynamic_confirmation*.json` / `inspection.json` as history.
**MegaVul's `inspection.json` is always nothing more than a static review, not a dynamic measurement**: any verdict in it lands in the fourth cell.

**Statistically, whether a sample lands in the third or the fourth outcome turns on a single question: was this sample really attacked with a dynamic tool,
and were readings from both sides obtained?** Attacked -> the third; the attack did not succeed / has not been attempted -> the fourth.

> **★ The fourth outcome was added by PrimeVul on 2026-08-17, and the reason for adding it must be remembered.**
> Before that there were only three outcomes, **and "measured but not a confirmation" had no cell of its own**, so that meaning was stuffed into a field
> named `build_failed_reason` (**reason for build failure**) -- and **not one** of those 230 samples was a build failure.
> The consequences were concrete: (1) anyone who reads the field by its name gets it wrong; (2) it directly violates the rule in section 0b below
> that "could not be built" and "attacked and nothing fired" must be kept strictly apart; (3) it forced out
> **two fields in the same record telling two different stories** -- one saying `dynamic_attack_negative` (attacked, nothing happened),
> the other saying `inverted_polarity` (measured, and the direction is inverted); **these two statements cannot both be true.**

### The `dy_attacked_undecided_category` vocabulary (the third outcome's secondary field, **required**)

These samples have exactly one thing in common: **a dynamic tool really did attack them, and readings from both sides were obtained.**
The reasons for "cannot decide" are completely different from one another, and so is the next action --
**which is why reporting only the total of the third outcome is meaningless; the distribution of this table must be given alongside it.**

| Value | Meaning | What can be inferred about this function |
|---|---|---|
| `nominated_awaiting_adjudication` | Readings from both sides were obtained, **and a valid confirmation class has already been nominated** | **What it lacks is neither a measurement nor a write-up, but one adjudication** |
| `attacked_no_trigger` | Both sides were really built and run, it was attacked with a tool matching the CWE, nothing fired, but one or more of the seven gates is still missing | **It is a conclusion about this function**; once the gates are complete it should become `LABEL_NOISE_EXCLUDED` |
| `guard_never_evaluated` | The disputed lines were never executed at all | **Exactly the opposite: that "clean" is not a conclusion about this function.** Change the input so that it executes |
| `decision_diff_no_impact` | **A real difference was measured, but it has no security consequence.** Both phrasings belong here: (1) there is a clean two-sided decision differential at the patch point, but no sanitizer fault, no out-of-bounds access and no leak; (2) there is a real behavioral difference (a rendering difference, by design), but it does not reach a security boundary | First ask whether it can still be salvaged (attach a real consumer / switch to a matching oracle) -- **this category is the most likely to flip to a confirmation**; only when salvage fails does it go to human adjudication |
| ~~`no_security_consequence`~~ | **Merged into the row above by the owner's ruling, PrimeVul 2026-08-21.** Kept as an **alias** so old records on disk can still be read; the classifier always folds it into `decision_diff_no_impact` | -- |
| `fault_not_attributable` | A fault fired, but it does not attribute to the labelled function (a sibling function / a caller / the harness's own code) | Counts neither as clean nor as a trigger. **In MegaVul's human re-review, 199 "Mock (labelled function not compiled in / rewritten)" and 104 "fault cannot be attributed" cases would mostly land here if reclassified into the four outcomes** |
| `inverted_polarity` | Inverted polarity: the side that faults is the build from the **fixed** code, while the build from the pre-fix code is clean | **★ 2026-09-20 ruler change (consistent with DiverseVul): this is no longer "cannot decide", it is label noise.** It may exist only as a **temporary state pending adjudication** -- once the two gates in the "label noise" section are passed (the two bodies are not swapped; the nonzero code on the fixed side is a real fault and attributes to the labelled function), write `label_noise: true` + `label_noise_category: "inverted-polarity"` + `label_noise_basis: "dynamic_differential_inverted"`, and the outcome becomes `LABEL_NOISE_EXCLUDED`; if the gates cannot be passed, record `stored_body_arms_swapped` or `fault_not_attributable`, and **do not close out sitting on `inverted_polarity`** |
| `no_differential_possible` | The two sides are by construction necessarily the same code | Terminal state; **only building a single side and attacking it can decide whether this function has a defect** |
| `synthetic_trigger` | The triggering condition is manufactured by the harness and real input cannot produce it | Switch to real input |
| `reachability_unproven` | The fault is inside the function body, but it was not proven that an attacker can reach it | Supply a real entry path |
| `cve_mismatch` | The labelled CVE does not belong to this commit or this function | A CVE mismatch does not veto a confirmation; first look at whether the function itself has a real defect |
| `single_arm_only` | Only one side was built and produced a result; the second does not exist structurally | Handle as a structurally single side. **Note: all 1,664 of MegaVul's Claude-crafted confirmations built only the pre-fix side**, but they are **not** cases of "the second side does not exist structurally" -- `fixed_function.c` is right there in the directory, it just was not built; this value is only for samples where a second side genuinely cannot be built |
| `unclassified_reason` | A reason was written but the existing matching rules do not recognize it | **Fix the rules; it is not the sample's problem** |

> **★ The cost of merging `no_security_consequence` is countable; remember this shape.**
> The two ask the same question: a real difference was measured, but it has no security consequence. Writing them separately was just two phrasings.
> On the PrimeVul side, **27** samples pending adjudication **matched both**, and since the classifier by design
> "must not resolve ambiguity by ordering", it sent them into `unclassified_reason` --
> **they had not failed to write a reason; we had split one question into two rules.**
> The folding must happen at **the level of the matched set**, so that the rule "multiple matches = cannot decide" benefits automatically.

> **★ Why `nominated_awaiting_adjudication` exists.** Without it, these samples were counted as
> "no reason written", because the classifier looked only at one particular note field, while the rule required that note **only when the category was left empty**.
> So a record carrying a nominated class, real integer two-sided differentials, execution proof and a positive control was still counted as "no reason written" --
> **and the action hanging on that cell is "dispatch a batch to fill in the write-ups", and they would find nothing to do.**

> **★ Only values from the vocabulary count.** `NONE`, an empty string, or a whole sentence pasted into the value slot is **a different kind of defect**,
> which must stay visible, and **must not be washed into `unclassified_reason`**.

### The `not_tested_reason` vocabulary (the fourth outcome's secondary field, **required**; the old name `build_failed_reason` serves only as an alias)

**Not one sample in this bucket was ever successfully tested**, so it supports no conclusion whatsoever about these functions --
it speaks to **our capability or our progress being insufficient**, and these samples **must stay on the to-do list waiting to be attacked**.

**★ Decide the value from the actual state on disk; do not rely on that reason field in the record, which is mostly empty.**
The lesson from the DiverseVul side is countable: the old vocabulary's `no_reason_recorded` swallowed
**10,178** of 16,268 -- two thirds reported as "unknown", while the folders themselves plainly showed which had been worked on and which had never been touched.
When deciding, go and look directly: is there a `repro.sh`, are there run logs, is there an `inspection.json`,
is there a `propagated_from` / `confirmation_type: crossdataset-*` provenance key, is there any dynamic record at all.

| Value | Meaning | Decision basis (look at disk, not at the field) | What can be inferred about this function |
|---|---|---|---|
| `attempted_no_usable_result` | **It was built / run**, it just produced no valid result | There is a `repro.sh` / `dynamic_evidence/repro.sh` or run logs, but no integer `vuln_rc`/`fix_rc` | Nothing can be inferred; but **the environment and the entry point are most likely working, so this is the cheapest**, do it first |
| `needs_path_b_not_attempted` | Marked as unreachable, with no trace of any attempt on disk | `inspection.json` says `DEFERRED_*` / `NOT_TRIGGERABLE_STANDALONE` / `needs-Path-B`, with no script and no logs | Nothing can be inferred (our capability is insufficient). **Apart from the 404 already confirmed, essentially all of MegaVul's 2,702 `inspection.json` files fall under this value** |
| `never_attempted` | No dynamic record and no artifacts at all | No record, no script, no logs, no `inspection.json` | Dispatch work. **MegaVul's 14,580 `UNTOUCHED` samples are exactly this value** |
| `build_failed` | A build failure was **actually** recorded | `blocked_reason:"build_failed"` or `build_failure` present on disk | Nothing can be inferred. **Note: this is a subcategory, not the whole bucket** |
| `attempted_inherited_crossdataset` | The evidence was produced by a PrimeVul/BigVul/DiverseVul twin sample and propagated here; **it was never run locally** | The record carries `propagated_from: primevul:*` / `bigvul:*` / `diversevul:*` or `confirmation_type: crossdataset-*`, and there is no local measurement of its own | A dynamic tool really did attack the twin sample, **but not this one**. In MegaVul's current snapshot there are **943** of these (PrimeVul 865, BigVul 76, DiverseVul 2), and **they must be separately countable; today they still carry the name `CONFIRMED`, and when repartitioning they must first be taken out of `CONFIRMED`** |
| `confirmation_withdrawn_nothing_measured_since` | A dynamic confirmation was once published here and was removed by a recorded, rollback-able withdrawal, and **since the withdrawal there has been no local dynamic measurement on disk** | The directory contains a `prior_confirmation_*/`, there are no new files after the moment of withdrawal, and the record has no `tried_dynamic_method` plus integer two-sided rcs | **Nothing can be inferred**: the withdrawal took away evidence, not counter-evidence |
| `unclassified_reason` | The existing rules do not recognize the state on disk | -- | **Fix the rules; it is not the sample's problem** |

> **Again, only vocabulary values count**: "not written in the record", i.e. `no_reason_recorded`, **is no longer a value** --
> not written in the record does not mean invisible on disk; go and look at the folder first.

### How to place a sample into these four cells (**decision order; the first match from the top wins**)

1. The record has a `verdict` starting with `DYNAMICALLY_CONFIRMED` and a `confirmation_class` that is one of the three tiers
   -> `CONFIRMED`;
2. `label_noise: true` and `label_noise_basis` is `dynamic_attack_negative` or
   `dynamic_differential_inverted` -> `LABEL_NOISE_EXCLUDED`
   (**writing only `suspected_label_noise` does not count**; that is the fourth cell; nor do the 292 static ledger entries in `megavul_label_noise.jsonl`);
3. The record has `tried_dynamic_method` **and** both sides in `differential` are **real integer** rcs
   -> `DY_Attacked_But_can_not_decide_confirmed_or_label_noise`, fill in `dy_attacked_undecided_category`;
4. Everything else -> `NOT_DYNAMICALLY_TESTED`, fill in `not_tested_reason` according to the state on disk.

**The boundary between steps 3 and 4 turns on a single question: was this sample really attacked with a dynamic tool, and were readings from both sides obtained?**
`"identical"` / `"n/a"` / `null` / the string `"1"` are **not** integer rcs, and land in the fourth cell.

> **★ By step 1, a large number of MegaVul's Claude-crafted records (`dynamic_confirmation.record.json`) would be judged `CONFIRMED`,
> but they generally have no `confirmation_class` and no two-sided integer rcs (`tool_matrix` carries only `run_rc`).**
> Strictly by step 1, those lacking `confirmation_class` **do not satisfy** the `CONFIRMED` condition; and since they also have no two-sided readings,
> they fall into the fourth cell as `attempted_no_usable_result` -- **this is not a bug in the classifier, the records themselves are missing fields.**
> How to handle it is item 4 under "implementation debt" below; do not default them to `CONFIRMED` to make the numbers look better.

### MegaVul's implementation debt (**record it honestly, do not treat it as done**)

1. PrimeVul has `primevul_outcome_taxonomy.py` to classify and fold these four outcomes; **neither MegaVul nor BigVul has an equivalent module**;
   `compute_megavul_dynamic_status_statistics.py` still partitions by the old verdict strings (`CONFIRMED` / `INCONCLUSIVE` /
   `UNTOUCHED` / `<MISSING...>`). Until a MegaVul version of the classifier is written, the four outcomes can only be **written per sample by hand**,
   and the report must note that the statistical ruler is a manual classification. **This is the biggest debt in this section: the decision-order table above currently has no code executing it.**
2. The snapshot's 14,580 `UNTOUCHED`, 2,702 `inspection.json` files and 6 `INCONCLUSIVE` must be repartitioned into the third/fourth outcome by
   "was it really attacked with a dynamic tool, and were readings from both sides obtained", and given
   `dy_attacked_undecided_category` / `not_tested_reason`.
3. **MegaVul has no checkers of its own.** Under `tasks/bigvul_reports/evidence_repair/`, the scripts
   `check_loop_prompt_compliance.py` / `check_loop_prompt_FULL.py` / `verify_batch.py` / `locate_evidence.py`
   **all hard-code the dataset path as `data/output/dataset/bigvul`** (verified by grep on 2026-09-24), and none of them can be run against MegaVul.
   Per §8c of the repository-root `CLAUDE.md`: **a rule written only into the document and not into a checker does not exist.**
   The next round must first parameterize these four scripts (or copy them to `tasks/megavul_reports/evidence_repair/`) before dispatching work in bulk.
4. **The record fields of MegaVul's existing confirmations generally do not meet this document's ruler**: the 1,664 Claude-crafted ones built only the pre-fix side
   (`tool_matrix[].run_rc` is a one-sided exit code; there is no `differential.vuln_rc/fix_rc`, no `confirmation_class`,
   `confirmation_scope`, `reachability`, or `tried_dynamic_method` object); the 27 Path-B ones have a `differential_fixed.log`
   but their records do not necessarily carry an integer `fix_rc` either. **Verified on 2026-09-24 by sampling 3,000 directories**: of 627 dynamic records,
   **0** had `confirmation_class`, 126 had `cve_match`, and only 21 had `differential`; the record files come in two spellings
   (`dynamic_confirmation.record.json` 266, `dynamic_confirmation.json` 247, both present in 57). **Either build the fixed side as well and write both integer rcs into the record, or honestly demote them to the third cell
   with the correct value other than `single_arm_only`** -- do not keep reporting confirmations whose fix effectiveness was never measured as a whole batch as `CONFIRMED_CVE_MATCH`.
5. **Human re-review has already measured the credibility of this batch of confirmations** (2026-09-14 -> 09-24,
   `tasks/megavul_reports/manual_check_megavul_20260914/CAMPAIGN_SUMMARY_20260924.md`):
   of the eligible pool of 1,816 (tested locally, not cross-dataset inherited, flat evidence complete), **all 1,677 with complete evidence packages were read by a human**,
   giving **supports 1,294 (77.2%) / conflicts 208 (12.4%) / insufficient evidence 175 (10.4%)**.
   Of the 208 "conflicts", 199 were harnesses that **never compiled the labelled function body in** (Mock), and 9 triggered something other than the labelled mechanism;
   of the 175 "insufficient", 104 had faults that do not attribute to the labelled function body, 62 had bodies heavily modified or faults inside a modelling stub, and 5 were Invalid Tests.
   **The user's 2026-09-24 instruction has been carried out**: the records of these 383 have been marked as the third cell `DY_Attacked_But_can_not_decide_confirmed_or_label_noise`
   (`dy_attacked_undecided_category`: `fault_not_attributable` 367 / `synthetic_trigger` 16; `verdict` changed to the uppercase outcome string, with the original value stored in
   `verdict_before_manual_check_20260924`; script `apply_manual_check_undecided_20260924.py`, manifest `manual_check_undecided_manifest_20260924.jsonl`),
   and the three statistics scripts now count them under that outcome with priority over the ledger's CONFIRMED. **`craft.json` / `info.json` were not touched** -- withdrawing from the ledger (the four places of rule 7) requires another explicit instruction.
   The remaining 139 samples in the eligible pool have incomplete evidence packages (missing harness/driver or poc input), **were never read by a human**, and are separately countable.

> **★ Added 2026-09-24: do not confuse the existing artifacts that are "adjacent but not equivalent" to these four outcomes.**
> The `manual_check_megavul_20260914/` material (`ALL_ADJUDICATIONS_MEGAVUL.csv` with 1,677 rows,
> each batch's `_overrides.json`, the automatic judgements of `_classify_mv.py`, the line-by-line body-check scripts) is the result of **humans re-reviewing the evidence on disk**,
> using the **three-state review ruler** of "supports / conflicts / insufficient evidence"; it is **not** this section's four-outcome partition and cannot be used as one directly:
> - It re-reviewed only the 1,677 within `CONFIRMED` whose evidence was complete; the 14,587 in the third and fourth outcomes **were not covered at all**;
> - Its "insufficient evidence" may correspond either to the third outcome (attacked but undecidable) or to the fourth (never successfully measured),
>   and must be split again using the `paper_failure_type` column (`none (fault cannot be attributed)` is mostly the third outcome's `fault_not_attributable`,
>   `Mock (body heavily modified or fault inside a modelling stub)` is mostly the third outcome's `synthetic_trigger` / `fault_not_attributable`).
>
> **But it can be fed straight into that classifier as input**: each batch's line-by-line body check (the proportion of the stored body present in the harness) and
> the frame line-number landing check answer exactly the question "is this measurement really measuring this function", and that is the precondition for the third outcome to hold at all.
> When writing the MegaVul version of the classifier, wire these two in first.

---

## 0b. ★★ Three closing states after repeated attacks still produce no result (must not be merged)

"Tried many times and still no result" corresponds in this campaign to **three completely different situations**, whose next actions,
conclusions about the dataset and eligibility to close out all differ. Merging them is exactly the error that this document's highest-priority rule exists to prevent:
**"could not reach it" means our capability is insufficient; only "attacked and nothing fired" is a conclusion about this function.**

Write one of the three into `dynamic_confirmation.json`:

### ① `blocked_reason: "build_failed"` -- it cannot be built, so no attack ever happened

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "blocked_reason": "build_failed",
  "build_failure": {
    "attempts": 3,
    "what_was_tried": "at-commit clone + ASan; extract-and-stub; reuse the binaries already built in pathb/<lane>",
    "where_it_stops": "the **verbatim** error of the first failure + file and line number",
    "why_not_recoverable_now": "an unobtainable SDK is missing / the period-appropriate toolchain cannot be installed / the dependency has been taken down",
    "logs": ["dynamic_evidence/build_vuln.log", "dynamic_evidence/build_fix.log"]
  }
}
```

**The criteria are not "I think it cannot be built", they are failed build logs on disk.** `attempts` must be >= 2,
and `what_was_tried` must list **different** approaches (rerunning the same command three times is not three attempts).
This state **supports no conclusion whatsoever about this function**, and counts statistically as `NOT_DYNAMICALLY_TESTED` / `build_failed`.
**The `DEFERRED_HEAVY_FRAMEWORK` / `DEFERRED_NEEDS_CALLER` entries in MegaVul's `inspection.json` are not this category** --
they never even attempted a build; they are `needs_path_b_not_attempted`.

### ② `attack_exhausted` -- it was built, really attacked, attacked repeatedly, and still nothing fired

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "attack_exhausted": {
    "rounds": 4,
    "oracles_tried": ["asan", "ubsan", "msan"],
    "why_these_oracles": "chosen by the mechanism in the fix diff: out-of-bounds writes via ASan, uninitialized memory via MSan (which prints WARNING:, not ERROR:), shifts/integers via UBSan",
    "entries_tried": ["the real CLI", "the decoder entry point", "extract-stub"],
    "inputs": "313 malformed samples + the official regression material, about 22 minutes in total",
    "positive_control": "dynamic_evidence/poscontrol.asan.log does respond -- proving the oracle is not dead",
    "seven_gates": "all passed / gate N missing (say which one)"
  }
}
```

**This state is what "tested many times with no result" means.** Where it goes:

- **All seven gates passed** -> it should not stop here; write `label_noise: true` +
  `label_noise_basis: "dynamic_attack_negative"`, and move to `LABEL_NOISE_EXCLUDED`;
- **Any gate missing** -> stay in `attack_exhausted`, say clearly which one is missing, the sample **stays on the to-do list**,
  and it counts statistically as the third outcome's `attacked_no_trigger`.

**The most common gap is gate 4: pick the oracle to match the mechanism, not the labelled CWE.**
If the mechanism is uninitialized memory but the attack only used ASan, that "clean" is not a negative result, it is **not measured at all**,
because ASan structurally cannot see this class. In MegaVul's `tool_matrix`, `msan` is often `run_rc=0`, `fired=False`
while `asan_ubsan` reported something -- **read `tool_matrix` tool by tool, do not look only at `tools_fired`.**

### ③ Something fired, but it does not attribute to the labelled function

This does not belong in this section. A fault inside a **callee** is still a confirmation (`confirmation_scope: "reachability"` +
`defect_site` + `call_path`); only a fault in a **caller** or in a **sibling function** with no call relationship gets
`unattributed_sanitizer_output` (count + signature + samples), which **counts neither as a clean log nor as a trigger**.
**The most common shape in MegaVul's single harnesses**: the out-of-bounds access happens in a **consumer written by the harness itself** (called directly by `main`, never going through the labelled function),
or MSan reports only at `main`'s `write()` / `copy_out` sink, with not a single frame of the labelled function in the fault stack (human re-review cases 3907, 2040, 9661, 14851) --
all of these are `unattributed_sanitizer_output`, not confirmations.

### The three side by side

| Situation | Fields | Statistical category | What can be inferred about this function |
|---|---|---|---|
| Cannot be built / cannot be reached | `blocked_reason: "build_failed"` + `build_failure` | `NOT_DYNAMICALLY_TESTED` + `not_tested_reason: build_failed` | **Nothing can be inferred** |
| Attacked, attacked repeatedly, nothing fired | `attack_exhausted` | All gates passed -> `LABEL_NOISE_EXCLUDED`; otherwise `attacked_no_trigger` | Only with all gates passed may you say "this function is mislabelled" |
| Something fired but it does not attribute | `unattributed_sanitizer_output` | `fault_not_attributable` | Neither clean nor a trigger |

**Do not write strings like `differential.vuln_rc: "build_failed"`.** Exit-code fields hold only integers;
if no integer came out of the run, there was no differential this time, and the reason goes in the fields above.
`blocked_reason: "build_failed"` and a real integer differential **cannot coexist** -- coexistence means the marker is stale,
and the old marker must be demoted to `prior_route_build_failure` with `build_performed` written.

---

## 0c. ★★ Build once per project, reuse within the batch (PrimeVul, user instruction 2026-08-15; applies equally to BigVul / MegaVul)

**Always group dispatched work by project**: the samples under one project go to one agent,
**that project is cloned and its build method worked out exactly once**, and then its samples are dynamically tested one after another.
Several small projects with the same build method (for example self-contained small parsers that are all autotools + ASan)
may be merged into one agent, but the dispatch ledger must say which ones were merged and on what basis.
**lane directory**: `pathb/<project>_<batch-tag>/`, one per project; do not create one per sample.
**MegaVul's `info.json::project` stores a 40-character commit hash, not a project name** -- infer the project for grouping from `code_link`'s
`github.com/<org>/<repo>` or from `file_name`, and state the inference method in the dispatch ledger.

### What this saves and what it does not -- be clear first, or you will "save" your way into fake evidence

**★ What it does not save is "the two things built from pre-fix and from fixed code".**
Two samples under the same project **usually do not share the same fix commit**. Measured on PrimeVul 2026-08-15:
the 99 never-tested samples in the worklist were spread over **97 different fix commits**, with only 2 pairs genuinely sharing a commit. Therefore:

> **Each sample must build its own `fix^` / `fix` pair.**
> Using a sibling sample's build to test another sample measures something other than this sample's version pair --
> which is exactly the "the pre-built binary is from the wrong period / the wrong CVE" family. **Verify the version and the diff before running.**

**What genuinely can be done once is this**:

1. **The clone and the submodules** -- for a big repository this step is the most expensive;
2. **Working out dependencies, `configure` / `cmake` arguments, compilers and flags** -- the largest chunk of human cost;
3. **ccache, which must be on and shared across samples** -- many object files are identical between different commits, and this is the real source of compile-time savings;
4. **The harness / driver / PoC generator / input-construction scripts**;
5. **How to write the positive control**, and this project's specific oracle pitfalls.

### Concretely

- Clone a project once, and **for each sample open a `git worktree` at that sample's own commit inside the same clone**;
- **Turn on ccache and share it across samples**;
- Write the `configure` / `cmake` arguments, dependency list, harness, PoC generator and this project's oracle pitfalls into a
  **lane-level `README.md`**, which later samples cite directly instead of working them out again;
- **When two samples genuinely share a commit** (verify first with `info.json::commit_id` / `code_link`, **not with the directory name**),
  build only one pair, share it between the two samples, and state in both records which pair was shared and on what basis;
- The lane is **exclusive to the batch**; do not put tool scripts under a shared path -- collisions in a shared staging directory happened eight times in one day.
  **MegaVul's `repro.sh` currently tends to compile binaries into `/tmp/vv_repro_bin` (measured on 1463 and others)** -- a shared path with the same name,
  so concurrent reruns overwrite one another; this is the first batch of things rule 2 has to fix.

**Report per project when handing over the work**: how many times this project was cloned/configured, how many pairs were built, ccache hit rates,
and **which samples shared the same pair and on what basis**.

---

## ★★★★★ Criteria change (user, 2026-08-03): **before judging label noise you must first attack it with a dynamic tool**

> "Even if you believe it is label noise, it can only be confirmed as label noise after a dynamic tool has attacked it
> and no vulnerability was triggered"
>
> "**This change must take effect for all label noise, not for one particular label-noise category.**"

**This is a global gate governing every exit to `label_noise: true`, and no category may bypass it.**
Whether you are judging `whole-commit-relabel`, `whitespace-only-relabel`, `cosmetic-refactor`,
`wrong-function`, `version-skew`, `mass-hardening-sweep`, `library-import-relabel`,
`wrong-cwe`, `test-file-labeled`, `multi-function-relabel` or `inverted-polarity` --
**attack first; only after the attack fires nothing may you judge.**

| Your situation | What to write |
|---|---|
| **Attacked, and the vulnerability did not come out** (all **seven gates** passed) | `label_noise: true` + `label_noise_type: "label_noise_dynamic_tools_attacked"` + `label_noise_category: <one of the 11 above>` + `label_noise_basis: "dynamic_attack_negative"`. **Do not write `NOT_MEASURED` / unconfirmed** |
| **Only read the code, not yet attacked** | `label_noise: false` + `suspected_label_noise: true` + `suspected_label_noise_category` + `label_noise_basis: "static_reading"`. **This does not trigger exclusion; the sample stays on the to-do list waiting to be attacked** |
| **Cannot attack it** (needs a whole-tree build / KASAN+QEMU etc.) | `label_noise: false` + `reason` containing `"needs-Path-B"`. **Could not reach it != attacked and nothing fired** |

**Attack records and logs always go into `data/output/dataset/megavul/<id>/dynamic_evidence/label_noise_attack/`
(`attack.sh` + inputs + the complete log of every shot + `ATTACK_LOG.md` + `EVIDENCE_MAP.json`).
No such directory = this label-noise finding does not hold, and the sample goes back on the to-do list.**

**MegaVul's current state against this gate**: the **292** entries of `megavul_label_noise.jsonl` are static triage,
and the 296 `NOT_TRIGGERABLE_AS_LABELED` plus 1 `NOT_CONFIRMED_LABEL_NOISE` in `inspection.json` were also judged by reading code --
**not one of them was ever attacked; they all count only as `suspected_label_noise`, fall statistically in the fourth cell, and must not be treated as `LABEL_NOISE_EXCLUDED`.**
The old prompt's rule that "writing `NOT_TRIGGERABLE_AS_LABELED` in `inspection.json` is enough" is void.

**Why**: "this commit did not change this function" and "this function has no vulnerability" are two different things --
whether a function has a vulnerability depends on its own code, not on whether some commit touched it.
The full text is in the section "explicit marking rules for label noise" below (**seven** hard gates + the category vocabulary + the evidence-directory checklist);
for background see **P25** in `tasks/bigvul_reports/evidence_repair/PROBLEM_REGISTER_20260803.md`.

**Three older instructions are void at the same time** (all of them decide cases straight from a static pre-filter, which conflicts with this gate):
"identical under `diff -w` -> mark label_noise directly, no need to dispatch a subagent", ">4-6 files -> INCONCLUSIVE-relabel directly, do not waste a build",
and the "INCONCLUSIVE+label_noise:true" clause in the full-coverage provision.

---

## ★★★★★ Criteria change (user, 2026-07-28): **a CVE mismatch is no longer a veto**

> "You may drop the CVE; as long as the sample really can trigger a vulnerability that is enough, and you can annotate that its CVE is wrong"

**New criteria**: as long as the **labelled function** can be made to trigger a real vulnerability under faithful input, it counts as CONFIRMED -- even if it is not the CVE the sample is labelled with. In that case write `cve_match: false`, and explain in the record what the real defect is and why the CVE attribution is wrong.
("Reachable by an attacker" is **not** a gate: a real defect that is unreachable is confirmed just the same, only with an extra `reachability: "UNREACHABLE"` field. User, 2026-07-31.)

So before downgrading because "the labelled function has nothing to do with this CVE", **you must ask one more question**: does this labelled function **itself** have a real, triggerable defect? If yes -> confirm, and record:

```json
{"cve_match": false,
 "cve_attribution_note": "the labelled CVE-XXXX is actually at <real location>; this function's defect is a different one",
 "real_vuln": {"class": "CWE-125 out-of-bounds read", "site": "<function:line>", "trigger": "<real input>"}}
```

**What has not changed**:

- **A differential is the standard path, but not the only path**. Same input, the build from pre-fix code faults and the build from the fixed code is clean = a standard confirmation.

  **The case where the fixed version is also vulnerable** -- ruled by the user 2026-07-28 (original wording: "if the sample is vulnerable and its fix is also vulnerable,
  then as long as a dynamic tool can trigger this sample's vulnerability, this sample can also be confirmed as vulnerable.
  It is enough to annotate honestly that its fix is also vulnerable"):

  > **If the build from pre-fix code can be triggered by a dynamic tool = CONFIRMED. The fixed build also faulting is a fact to be recorded honestly, not a veto.**
  Required fields:
  ```json
  {"verdict": "DYNAMICALLY_CONFIRMED",
   "fix_arm_also_vulnerable": true,
   "defect_present_both_arms": true,
   "confirmation_class": "OTHER_DEFECT_UNFIXED",
   "fix_arm_signal": "<the actual sanitizer output of the build from the fixed code>"}
  ```
  Cases: `bigvul/178795` (file/libmagic, `cdf_read_property_info` out-of-bounds read),
  `bigvul/181140` (IM, `WriteJP2Image` leaking 1,054,040 bytes).
  MegaVul's same family: 5532 (LibRaw `bad_pixels`, the two stored bodies differ only in `#line`, division by zero inside the function itself) -- but its harness changed 32 of the 59 lines of the body,
  and human re-review judged it "body heavily modified"; **confirming it requires rerunning with the verbatim body first**.

  **All three preconditions are required** (otherwise it becomes "any bug you happen to find counts"):
  1. The defect **is reachable from the labelled function** -- inside the labelled function's body, or inside a callee it calls (directly or indirectly).
     ★★★★★ **A defect in a callee is not grounds for downgrading (user, 2026-08-01)**: when both sides fault alike,
     the defect **need not** be inside the labelled function's body, it only needs to be **clearly annotated**. Write:
     ```json
     "confirmation_scope": "reachability",
     "defect_site": "<the name and location of the function that actually faults>",
     "callee_of_labelled_function": true,
     "call_path": "<labelled function -> ... -> defect_site, noting which file and which lines this was read from>"
     ```
     **What must still be blocked is "not reachable from it"**: a fault occurring in a **caller** of the labelled function,
     or in a sibling function with no call relationship to it, is not "reachable from the labelled function", and is downgraded as before.
     BigVul counterexamples 187879 / 187880 (`Cluster::CreateBlockGroup` is not in the labelled function's call closure);
     BigVul positive example 187869 (**corrected 2026-08-02**: originally listed as a counterexample; measurement showed the call direction is
     `ParseBlockGroup -> CreateBlock -> CreateBlockGroup`, so it is reachable, and it has been re-judged as a reachability confirmation).
     **Before judging you must actually read the upstream source to confirm the call direction; do not presume it from similar names.**
     MegaVul cases: the faults of 12462 / 12458 are in the sibling `calculate_operand_data_length` (which is 12456's defect),
     and the labelled function's own defect was never reached -> not a confirmation.
  2. Triggered by **faithful input**, with empirical output from a sanitizer or an equivalent oracle.
     This blocks two things: synthetic triggers (absurd magic numbers, values upstream would reject) and harness-manufactured defects
     (changing the upstream code and then reporting the consequence). **It does not require an attacker path to exist in the real program** --
     if the defect is real and inside the labelled function but no attacker-controllable path to it can be found, it is still confirmed,
     with `reachability: "UNREACHABLE"` added instead of a downgrade. See the ★★★★★ unreachability section below.
  3. **The build from pre-fix code must be able to trigger it by itself** -- counterexamples `bigvul/183295`, MegaVul 1082 / 6909: inverted polarity,
     where the stored "vulnerable version" is clean and the "fixed version" is what crashes; that does not make this sample vulnerable.
- **A synthetic trigger still does not count.** Absurd magic numbers, values upstream would reject, parameters real input cannot produce -- none of these is a confirmation.
- The labelled function **genuinely having no defect at all** -> downgrade as before.

**Why this matters**: in the first round of BigVul evidence repair, 21 of 39 samples were downgraded, and **not one was "we could not reproduce it"**; all were "the labelled function has no real relationship to this CVE". Under the new criteria those 21 must be re-examined: the function may have a real bug of its own. Skipping this step before downgrading = throwing away real samples.

Statistics come in three tiers; do not mix them:
| Tier | Condition |
|---|---|
| `CONFIRMED_CVE_MATCH` | What was triggered is the labelled CVE, and there is a differential between the two sides |
| `CONFIRMED_OTHER_DEFECT` | Another real defect inside the labelled function, with a differential between the two sides, `cve_match:false` |
| `OTHER_DEFECT_UNFIXED` | Another real defect inside the labelled function that upstream did not fix -> both sides fault alike |

**Not one of MegaVul's existing confirmations records these three tiers** (the records carry only `verdict` + `method` + `fault` + `tool_matrix`);
by step 1 of §0a, without `confirmation_class` it is not `CONFIRMED`. When filling in the fields, **do not default to `CONFIRMED_CVE_MATCH`** --
a single harness never tested the fixed side, so "there is a differential between the two sides" cannot be filled in; the only honest option is to build the fixed side, get an integer `fix_rc`, and only then assign a tier.

---

## ★★★★★ Confirmation scope is required (user, 2026-07-31): **defect site vs reachability, you must declare which one it is**

> "It is the latter that is wanted; 180356 should be changed to 'keep the confirmation + annotate it as reachability rather than defect site', clearly annotating that what is vulnerable is the callee"

**Every CONFIRMED must carry `confirmation_scope`, one of two values.** Not writing it is a missing field.
The reason: without the distinction, "this function contains a defect" and "this function delivers attacker input to the defect" are mixed under one label,
and a downstream detector trained on it learns "recognize call sites" instead of "recognize defects".

```json
"confirmation_scope": "defect_site" | "reachability",
"reachability": "REACHABLE" | "UNREACHABLE" | "UNKNOWN",   // [required] orthogonal to scope, see the unreachability section below
"defect_site": {                       // [required] when scope is reachability
  "function": "<the function that actually contains the defect>",
  "file": "<the file it is in>",
  "reached_via": "<the call chain from the labelled function to it>",
  "defect": "<the observed defect, with the verbatim sanitizer text>"
},
"reachability_note": "<why the labelled function itself is not the defect site>"
```

**The criteria are a counterfactual question: if you change only this labelled function, does the vulnerability go away?**

- **Yes** -> `defect_site`. It does not matter where the crash lands. The existing `frame_note` (alloc_site/fault_site) belongs here:
  the labelled function under-allocates and the overflow happens in a `memcpy` it calls or in a helper in the same file -- the defect is still the labelled function's.
  The many MegaVul human re-review cases of "the fault is in a modelling accessor/sink called by the labelled function, and the bad value comes from its body"
  (`get_te32`, `swapl`, `copy_to_user`, `strlcat`, `AP4_BytesToUInt32BE`, ...) are exactly this, and re-review judged them as supporting.
- **No** -> `reachability`. The labelled function has no defective operation of its own and the upstream patch does not touch it, but it delivers attacker-controllable input
  to the defect. **You must name the specific function in `defect_site`.**

Template BigVul 180356 (php-src CVE-2016-5093): the labelled function is four lines, one forwarding statement, zero memory operations,
the overflow is in the callee `get_icu_value_internal`'s `strlen()`, and the differential was really produced by a run (vuln_rc=1 / fix_rc=0)
-> `confirmation_scope: "reachability"`, `defect_site.function = "get_icu_value_internal"`.
MegaVul's same family (upstream whole-tree build, fault in a callee, the labelled function appearing in the stack as the caller): 12692 (libarchive `archive_write_open2`
-> `__archive_write_allocate_filter`), 6900 (opusfile `op_get_data` -> the read callback's `memcpy`), 2479 (tcpdump `juniper_atm1_print`
-> `juniper_parse_header`) -- all of these should be written as `reachability` + `defect_site`; human re-review recorded them as supporting, and the fields have not been filled in yet.

### Three lines not to cross

**1. `reachability` is not label noise; never set `label_noise: true`.**
In this repository `label_noise: true` is an **unconditional hard exclusion**, and setting it makes the sample disappear outright -- "keep the confirmation and also mark it as noise" is self-contradictory.
To record the fact that "the upstream patch does not touch the labelled function", write it into `reachability_note`, not into `label_noise`.

**2. Reachability must be observed, not inferred.**
Reachability is transitive -- once you accept that "it calls a defective function" counts, every level of the call chain up to `main()` counts too.
So judging `reachability` still requires that **a differential really was produced by a run**: real input reaching the defect via the labelled function
and becoming clean under the real patch. **This does not get relaxed just because the reachability criterion is being used.**

**3. `defect_site` must name a specific function.** Writing "the defect is elsewhere" is not an annotation, it is an evasion;
being unable to point at a specific function means it has not been investigated, and then it should not be judged CONFIRMED.

### ★★★★★ Unreachable is still CONFIRMED (user, 2026-07-31): **add a field, do not downgrade**

> "Even if it is unreachable it still needs to be annotated as confirmed, it just needs a special field marking it as unreachable"

**"No attacker-controllable path to it can be found" is not grounds for downgrading.** As long as the defect is **genuinely inside the labelled function's body**
and is **real** (not manufactured by the harness), record `verdict: DYNAMICALLY_CONFIRMED`,
and add a field stating that it is unreachable -- rather than throwing out the whole sample.

```json
"reachability": "UNREACHABLE",
"reachability_note": "<what the defect is, which line it is on, which oracle observed it;
                      and what precondition is needed to reach it, and why that precondition is not attacker-constructible>",
"attacker_controlled_trigger": null
```

`reachability` is **orthogonal** to the three tiers: an unreachable sample still lands in one of
`CONFIRMED_CVE_MATCH` / `CONFIRMED_OTHER_DEFECT` / `OTHER_DEFECT_UNFIXED`,
decided by whether there is a differential and whether upstream fixed it. Unreachability only adds a qualifier to that tier; it does not change the tier.

**Template BigVul 187837** (Android CVE-2016-2464, `ContentEncoding::GetCompressionByIndex`):
`count` is a `ptrdiff_t`, and `idx >= static_cast<unsigned long>(count)` turns a negative count into a huge unsigned upper bound;
the defect is real and sits on the labelled function's own bounds check, but producing `count < 0` requires a class invariant to be broken, which is not input this function can be driven with
-> keep `DYNAMICALLY_CONFIRMED`, `reachability: "UNREACHABLE"`, `OTHER_DEFECT_UNFIXED`, `cve_match: false`.
In MegaVul, the proportion of Claude-crafted harnesses that hand-assemble a struct and call the labelled function directly is extremely high (`main` `calloc`s an object,
sets some field to NULL or an extreme value, then calls it), and **the `reachability` of these confirmations can mostly only be written honestly as `UNKNOWN`**; do not default to `REACHABLE`.

**Do not merge three different things into one** -- only the first goes with UNREACHABLE:

| | How to record it |
|---|---|
| The defect is real, inside the labelled function, but there is no attacker-controllable path to it | **CONFIRMED + `reachability: UNREACHABLE`** |
| Nothing was measured (not built, not run, wrong oracle) | Not unreachable, but **not finished**; go back and do it |
| **Really attacked, and the vulnerability did not come out** (all **seven gates** passed) | **`label_noise_dynamic_tools_attacked`**, see the label-noise section below. **Do not write NOT_MEASURED / unconfirmed** |
| A defect manufactured by the harness itself | Downgrade. See BigVul 187416 / MegaVul 16067 in the table below |

Before writing UNREACHABLE, ask yourself: **did I really prove it unreachable, or did I merely fail to find a path?**
The two are written differently -- the latter gets `reachability: "UNKNOWN"` with a list of the entry points that were searched; do not pass it off as a conclusion.
Negative example BigVul 181875: it once asserted "it needs a 16 GB allocation so it is unreachable"; measurement showed that allocation succeeded and the out-of-bounds write happened all the same. **Unreachability is to be measured, not deduced.**

### Two kinds where reachability does not apply and a downgrade still stands (cases measured 2026-07-31)

| Situation | Case | Criteria |
|---|---|---|
| Never measured at all | BigVul 180376 | `differential` itself says `not measured -- no build attempted` |
| A defect manufactured by the harness itself | BigVul 187416; MegaVul 16067 (the tail of `WavpackPackInit` replaced by a `memset` sink written by the harness), 5757 (what UBSan reported is the `SUBSAMPLE*n` computed by the harness inside `main`) | The harness uses `#ifdef` to delete a guard that **already existed before the upstream fix**, or adds a sink of its own, and then reports the resulting fault |

These two are **not** reachability -- reachability requires that a differential really was observed.
"Both sides fault identically, no differential" **is not by itself grounds for downgrading**: if the defect is inside the labelled function, that is
`OTHER_DEFECT_UNFIXED` (upstream did not fix it), with the `reachability` field recording whether it can be reached.
The complete standard is in `tasks/bigvul_reports/evidence_repair/CONFIRMATION_SCOPE.md` (dataset-independent, MegaVul uses it directly).

## ★★★★ Hard rules for evidence self-sufficiency (user, 2026-07-28; these override every other path convention)

**The verdict is not the product; the set of files that lets someone else rerun it is.** If the recipient of a `DYNAMICALLY_CONFIRMED` cannot get anything runnable, it is just an assertion in the dataset.

Measured on BigVul 2026-07-28 (a disk-wide scan of 4,894 confirmations): 136 sample directories contained no reproducible files at all; the evidence for 2,021 samples lay outside the dataset, of which 329 references pointed at `/tmp/claude-<pid>/...`; after the first migration, only 1 of 164 scripts actually ran.
**MegaVul scan, 2026-09-14**: the entire dataset had **0** `dynamic_evidence/` directories (at the time the user decided to accept the flat layout as the denominator for the human re-review);
the evidence is `repro.sh` + `dynamic_confirmation.harness.c` + `dynamic_confirmation.*.log` sitting flat in the sample directory;
**139** of the 1,816 in the eligible pool have incomplete evidence packages (missing harness/driver or poc input), and among the candidates skipped during sampling, 258 were "missing harness/driver + poc_input" and 20 were "missing harness/driver only";
`repro.sh` generally compiles binaries into `/tmp/vv_repro_bin`. So what follows is mandatory, not advisory.

### Rule 1 -- per-sample artifacts always land in `data/output/dataset/megavul/<id>/dynamic_evidence/`

The directory name is fixed as `dynamic_evidence`. It is **forbidden** to write into `/tmp`, `~`, `<SCRATCH>/wl_campaign/`, `<SCRATCH>/pathb_builds/` (existing historical build trees, see rule 4), an agent's self-created temporary workspace, or anywhere outside `VulValidate/`. If you need temporary space, use `TMPDIR="$(dirname "$0")"/tmp` and keep it after the run.

A valid `dynamic_evidence/` contains at least:

```
dynamic_evidence/
├── repro.sh            builds both sides, runs both, prints the differential, one command end to end
├── driver.c            the real entry point / harness
├── body_vuln.inc       the code under test from the pre-fix side (or stub.h + #ifdef FIXED) -- checked with cmp against ../vulnerable_function.c
├── body_fix.inc        the code under test from the fixed side -- checked with cmp against ../fixed_function.c
├── <poc input file>    the real crafted input (.mat/.pdf/.pcap/...), stored byte-for-byte
├── vuln.asan.log       the actual output of the pre-fix side
├── fix.clean.log       the actual output of the fixed side
└── EVIDENCE_MAP.json   each file's purpose + sha256; write a pin when referencing an external build tree
```

**MegaVul's existing flat layout (`dynamic_confirmation.harness.c` / `dynamic_confirmation.asan.log` / `repro.sh` placed directly in the sample directory) is a historical legacy, and the human re-review was done against it;
from this round on, newly written or repaired samples all go into `dynamic_evidence/`, while old flat files are neither moved nor deleted (moving them would desynchronize `EVIDENCE_MAP` and the ledger),
but `EVIDENCE_MAP.json` must list them.** The checkers must recognize both layouts (see item 3 of "implementation debt").

**Unconfirmed samples must keep the same material**: what was run, how it was run, and why there was no differential must also be verifiable by rerunning. Put it in the same directory.

Log file names are fixed per the table above. If you used something other than ASan, rename accordingly and state it in `EVIDENCE_MAP.json`
(`vuln.msan.log` / `vuln.ubsan.log` / `vuln.valgrind.log` / `vuln.timeout.log`),
but **do not** use names like `vuln.out` or `log.txt` from which the oracle cannot be told.

### Rule 1b -- `tried_dynamic_method` is required: **which tool was used, and why that one**

Every `dynamic_confirmation.json` must carry `tried_dynamic_method`, not scattered notes in a reason field:

```json
"tried_dynamic_method": {
  "oracle_kind": "asan | ubsan | msan | tsan | valgrind-memcheck | kasan | kmsan |
                  hang/timeout | authorization-decision | output-differential | alloc-failure",
  "why_this_oracle": "<why this defect type calls for it; required for non-memory defect classes>",
  "method": "<extract-and-stub / whole-file-stub / Path-B build-at-fix^ / corpus replay ...>",
  "trigger": "<the specific input, pointing at a file name inside dynamic_evidence/>",
  "vuln_rc": 1, "fix_rc": 0,
  "vuln_observed": "<the verbatim sanitizer text or verbatim behavior, not empty words like 'the vulnerability was triggered'>",
  "fix_observed": "<the actual output of the fixed program under the same input>"
}
```

`oracle_kind` must match the defect type. **`rc=0/0` is not "no differential" for authorization bypass, command injection or forgery-class defects**
-- when the attack succeeds the process still exits normally. For those, the oracle is the authorization decision, whether the command executed, or the identity determination itself.
**MegaVul's existing `tool_matrix` (`tool` / `compile_rc` / `run_rc` / `fired`) is only a table of one-sided readings and cannot replace this object**;
when filling in records, fold it into `tried_dynamic_method` and add `fix_rc` / `fix_observed` (if the fixed side was never built, write `null` honestly and explain).

### Rule 2 -- no absolute paths in scripts

```bash
cd "$(dirname "$0")"                  # not cd <SCRATCH>/.../work/1463
D="$(dirname "$0")/.."                # the sample directory (for reading vulnerable_function.c)
export TMPDIR="$(dirname "$0")"/tmp
CC=${CC:-gcc}                          # get the toolchain from an environment variable, do not hard-code a path
```

**Swapping in a different absolute path = not fixed.** The next time the dataset is copied elsewhere it breaks just the same.
**MegaVul's `-o /tmp/vv_repro_bin` is the textbook violation of this rule**: change it to `-o "$TMPDIR"/arm_vuln`.

### Rule 3 -- paths in records are always written relative to the sample directory

For every field in `dynamic_confirmation.json` and `craft.json` that points at a file:

- Write `dynamic_evidence/repro.sh`, **not** `repro.sh` (a bare file name makes complete evidence look nonexistent);
  MegaVul's old records with `reproduce: "./repro.sh"` and `input.harness_file: "dynamic_confirmation.harness.c"` are the historical spelling of the flat layout,
  and newly written ones follow this rule;
- **Do not write** `<SCRATCH>/.../wl_campaign/x/repro.sh` or `<SCRATCH>/pathb_builds/<id>/...` (outside the repository, unavailable to the recipient);
- **Do not write** shell brace expansions like `pathb/x/{a,b,c}`;
- Do not put the pointer only in `README.txt` / `INFO.md`.

### Rule 4 -- third-party software, source and builds all live inside `VulValidate/`

| Thing | Where it goes |
|---|---|
| at-commit build trees / banked ASan binaries | `pathb/<lane>/<name>_{vuln,fix}/` |
| upstream tarballs, source packages | `pathb/_srcpkg/` (keep the original archive + sha256, not just the unpacked tree) |
| cross / period-appropriate toolchains, sysroots | `pathb/_toolchain/` |
| kernel images / rootfs | `pathb/kasan/` |
| shared stub headers, cross-sample harnesses | `pathb/_shared/` |

`pathb/` is inside the repository and gets shared along with all of `VulValidate/`, **so banked binaries need not be copied into every sample directory** -- but `repro.sh` must reference them by a **repository-relative** path (`R="$(dirname "$0")/../../../../.."` or by reading `VULVALIDATE_ROOT`), and `EVIDENCE_MAP.json` must carry the pin:

```json
{"build_tree": "pathb/gpac_2020",
 "git_remote": "https://github.com/gpac/gpac", "commit": "...",
 "dirty_files": 0, "configure": "./configure --enable-sanitizer ..."}
```

`dirty_files != 0` means there are changes git cannot restore, and then the diff must be stored in `dynamic_evidence/` as well.
**Some of MegaVul's 27 Path-B confirmations have build trees under `<SCRATCH>/pathb_builds/<id>/` (outside the repository; measured on 12692, 6900, 1499, 3158, 6670)**,
and the paths in their logs point there too -- these must either have the tree moved into `pathb/<lane>/` with a pin written, or be marked honestly in `EVIDENCE_MAP.json` as `build_tree_outside_repo: true`; do not pretend they are reproducible.

**Do not** copy the upstream build tree per sample -- measured, that is 6.13 GB / 520,000 files, of which 3.19 GB are locally built `.o` files. Pinning the commit is enough.

### Rule 5 -- self-check before handing over the work: run it, do not just look at whether files exist

```bash
cd data/output/dataset/megavul/<id>/dynamic_evidence
rm -f *.o arm_vuln arm_fix            # delete the build artifacts, to prove it comes up from source
bash repro.sh                          # both sides must build, and a differential must really come out
grep -rn '/scratch/\|/tmp/\|/home/' *.sh   # must print nothing
cmp body_vuln.inc ../vulnerable_function.c # a single Path-A harness must pass this too
```

**Three easily mistaken criteria** (all learned the hard way):

- **A log is not a reproduction file.** `dynamic_confirmation.asan.log` is evidence that it "was run"; it cannot let you "run it again". Only logs in the directory = not valid.
- **The existence of `craft.json` != a differential was run.**
- **Both sides clean does not mean there is no vulnerability** -- the harness may never have compiled the labelled function in (measured on BigVul: 90% of 125 harnesses never compiled the labelled function; in MegaVul's human re-review, 199 of 1,677), or HW-accel may have bypassed the vulnerable path. Prove the labelled code really executed before drawing a conclusion.

### Rule 6 -- the three places recording `dynamic_evidence` must agree

The path fields in `dynamic_confirmation.json`, the path fields in `data/output/dynamic/confirmed/megavul_<id>.craft.json`, and the real files on disk must all match. If you move something, change all three. The ledgers (RUNLOG, registry) themselves are not moved into the sample directory; only the paths they describe are changed.

### Rule 7 -- withdrawing a confirmation means changing **four** places, and `info.json` is the one most often missed

Measured on BigVul 2026-07-28: of 21 downgraded samples, **21/21 still had `tier: dynamically_confirmed` / `is_vulnerable: YES` in `info.json`**.
MegaVul's `info.json` likewise carries `tier` / `is_vulnerable` / `determination_reason` (measured on 1463: `tier: dynamically_confirmed`, `is_vulnerable: YES`), and it is the first thing downstream tools read.

When downgrading, change all four at once:

1. `dynamic_confirmation.json` (or the older `dynamic_confirmation.record.json`) -> `verdict: NOT_DYNAMICALLY_CONFIRMED` + an honest reason + the `label_noise` family of fields
2. `craft.json` **moved into** `<id>/prior_confirmation_<stamp>/` (**moved, not deleted**)
3. `info.json` -> use the repository's existing vocabulary for `tier` and `is_vulnerable`; do not invent your own:
   - `label_noise: true` -> `tier: mislabel`, `is_vulnerable: NO`
   - `label_noise: false` (a real patch but it cannot be triggered) -> `tier: not_dynamically_confirmed`, `is_vulnerable: NOT_CONFIRMED`
   - `label_noise_type: label_noise_dynamic_tools_attacked` (really attacked, nothing fired, all seven gates passed) -> likewise `tier: mislabel`, `is_vulnerable: NO`, plus `label_noise_basis: dynamic_attack_negative`
   - **`label_target` is never touched.** MegaVul's label is its own business; what changes is our dynamic verdict.
4. **Leave a rerunnable script for the negative result** in `dynamic_evidence/`

Tool: `tasks/bigvul_reports/evidence_repair/reconcile_info_json.py` (`--ids a,b,c --apply`) -- **it too hard-codes the path to bigvul, so parameterize it before using it on MegaVul** (implementation debt item 3).
**No downgrading without the user's explicit consent** (`CLAUDE.md` §4); for the 383 "conflicts / insufficient" from the human re-review, first produce a list and leave the records alone.

---

## ★★★ What the PATH-B campaign looks like in MegaVul

MegaVul has no separate list of 2,119 needs-Path-B samples the way BigVul does; its equivalent is the **2,702 `inspection.json` files**
(`DEFERRED*` 1,764, `NOT_TRIGGERABLE*` 762, the rest a long tail) plus the **14,580 samples that were never touched**. The old routing tables
`megavul_inconclusive_deferred_route_worklist.jsonl` (11,332 entries) and `megavul_method_recommendation_remaining.csv` (11,979 entries)
each carry a `recommended_method`, which is **only a starting point, not something already executed**.

**Per-sample criteria (following the faithfulness rule)**: build both the pre-fix and the fixed side (or an fn-local `#ifdef`), and use real crafted input to make the pre-fix build crash/leak/hang while the fixed build stays clean under the same input (the differential is the acceptance test). **The fixed build also crashing is no longer a veto** -- if the defect is inside the labelled function and the pre-fix build can trigger it, it still counts as CONFIRMED, recorded honestly with `fix_arm_also_vulnerable:true`. A fault forced by a synthetic magic number != a confirmation. Temporal DoS (assert/panic/infinite loop) = CONFIRMED.

**★ Compliance (for every assigned id)**: rewrite `data/output/dataset/megavul/<id>/dynamic_confirmation.json` additively (keeping the original fields), adding: `path_b_attempted:true`, `path_b_route`, `path_b_differential{vuln_rc,fix_rc}` (real integers), `path_b_reason`. For an established one, also write `data/output/dynamic/confirmed/megavul_<id>.craft.json` and change the verdict to `DYNAMICALLY_CONFIRMED`. For ones that could not be reached but **were genuinely built and run**: `path_b_attempted:true` + an honest `path_b_reason`. For ones genuinely in the **untestable class** (Spectre/side-channel/timing, the 2^31 memory wall, needing a whole browser or a whole runtime with no extractable library): mark `path_b_terminal:true` + the reason. A bare "DEFERRED" or missing `path_b_*` = non-compliant. **`inspection.json` is not the home of these fields; it records only static review; dynamic attempts always go into `dynamic_confirmation.json`.**

**LANE routing + concurrency model (build-once-per-commit)**: prefer userspace parsers/daemons/libraries (MegaVul's confirmed CWE distribution: CWE-125 480, 787 448, 476 321, 190 311, 119 299 -- mostly memory classes, matched by ASan/UBSan/MSan); Linux goes through a `kernel_stub.h` micro-harness first and then KASAN/QEMU; Android/media goes through extract-and-stub; logic/permission/injection classes go through behavioral differentials; side channels/Windows-only/whole browser get an honest `path_b_terminal`.

**★★ ANTI-STORM**: cap rebuild concurrency at 2-3; QEMU/KASAN boots at <=2-3 concurrent with a hard 120s timeout; every tick check real CPU occupancy + iowait (**not load-avg**): if iowait>50, wait for it to drain; `pkill -f` / `killall` are forbidden, start with `setsid --wait`, record the PGID, and `kill -- -$PGID`; `ASAN_OPTIONS=disable_coredump=1` + `ulimit -c 0`; `make -j8` as the cap; **builds only inside `pathb/`**; a SKIP-if-craft.json-exists guard; frame subagent wording as defensive-label-verification.

**Completion criteria**: every non-terminal sample has `path_b_attempted:true`, or is already confirmed, or already has `path_b_terminal:true`; every sample lands in one of the four outcomes of §0a.

---

## ★★ Persistence hard rule (user, 2026-07-22): do not stop until the worklist is fully covered

**Never stop the loop until every `label_target==1` sample in the worklist has an honest verdict.** Do not stop because "there are no new confirmations / what is left is all needs-Path-B / this class of samples has been checked" -- unconfirmed != unprocessed. Every unprocessed sample must land in one of the four outcomes of §0a with its secondary fields filled in.

Computing what remains: iterate the worklist ids and count those with neither a `data/output/dynamic/confirmed/megavul_<id>.craft.json` nor a `data/output/dataset/megavul/<id>/dynamic_confirmation.json` (or the older `.record.json`) and with `info.json::label_target==1`. **`inspection.json` does not count as "having a verdict"** -- it is a static review.

### ★★ Escalation rule (user, 2026-07-22): every remaining sample needs an "actual dynamic tool test", not just a static classification

**Every sample in the worklist -- whatever its old verdict, `DEFERRED_*` / `NOT_TRIGGERABLE*` / `INCONCLUSIVE` / `UNTOUCHED` -- must really be run once through a dynamic tool for a differential**; you may not close out on a static verdict based only on `diff -w` / commit-stat. **You are not bound by `recommended_method`**: based on the sample's project / CWE / commit / function, pick the most suitable dynamic method yourself and actually execute it:
- Linux kernel -> first a `kernel_stub.h` micro-harness + ASan/`-fsanitize=bounds`/`-m32`/MSan; if that cannot reach it, then KASAN+QEMU / KMSAN / KCSAN.
- Userspace lib/daemon -> Path-B build-at-fix^/fix + ASan/UBSan/LSan + a differential using the fix's own regression tests or real crafted input.
- Android/media -> extract-and-stub / reviving a banked fuzzer + attribution / m32 / MSan.
- 32-bit-only integer overflow -> m32; uninitialized info leak -> MSan (which prints `WARNING:`); fuzzer-found -> revive the crash under libFuzzer.
- Side channel/Spectre, Windows-only, whole browser -> still an honest `path_b_terminal`, but **the record must state "the dynamic methods already attempted + why that class of tool cannot produce a differential"** (`tried_dynamic_method`); a purely static "needs-Path-B" is not enough.

A differential is the standard path (revised 2026-07-28): the pre-fix build faults and the fixed build is clean under the same input = `CONFIRMED_CVE_MATCH`; both sides fault alike but the defect is inside the labelled function and the pre-fix build can trigger it = CONFIRMED + `fix_arm_also_vulnerable:true` + `OTHER_DEFECT_UNFIXED`; the pre-fix build cannot trigger it at all = record honestly in the third/fourth cell of §0a, but the tool must actually have been run. Every record carries `tried_dynamic_method` + `differential` (integer vuln_rc/fix_rc).

---

_Rewritten section by section from `tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md` (the 2026-09-20 version) and adapted to MegaVul. **Last updated 2026-09-24 -- the whole document is aligned with BigVul's logic**: (1) a quick-reference block of the four outcomes, "read this one first: what this round has to hand over at the end", added at the top; (2) §0a added with the four outcomes and the two required secondary-field vocabularies (`dy_attacked_undecided_category` / `not_tested_reason`), voiding more than 20 old strings such as `DEFERRED_*` / `NOT_TRIGGERABLE*` / `INCONCLUSIVE` / `UNTOUCHED` as outcomes, with `inspection.json` always counting only as a static review; (3) §0b added on the three closing states that must not be merged, and §0c on building once per project; (4) the gates are counted as seven, `label_noise_basis` has three values, rule C; (5) the seven rules of evidence self-sufficiency rewritten against MegaVul's current state (the flat layout is a historical legacy, new material goes into `dynamic_evidence/`, and `/tmp/vv_repro_bin` plus the out-of-repository build trees under `pathb_builds/` are the things to fix); (6) six items of **honest debt** recorded: there is no four-outcome classifier module, all four checkers hard-code bigvul paths, the 1,664 Claude-crafted confirmations built only the pre-fix side and lack `confirmation_class`/`confirmation_scope`/`reachability`, the 943 cross-dataset propagations must be taken out of `CONFIRMED` separately, the 383 conflicts/insufficient from human re-review await the user's adjudication, and the denominator 17,592 vs 15,222 has not been reconciled; (7) the "output ruler" written into the end of the verbatim `/loop` text to be pasted. The backup is `LOOP_PROMPT.md.bak_before_bigvul_align_20260924`. **Previous update: 2026-07-23** (snapshot); **2026-07-21** (synced from BigVul: CVE-match faithful triggering, exact function-body propagation, explicit label-noise distinctions, output-path discipline)._

## The original /loop prompt (verbatim, copy straight into /loop)

> **★ 2026-09-24: the block below has been rewritten to match the BigVul 2026-09-20 version. Remember four things before pasting** --
> (1) there are **seven** gates, not five; (2) there are only four outcomes (see §0a), and the `DEFERRED_*` / `NOT_TRIGGERABLE_AS_LABELED` values in `inspection.json`
> **are no longer outcomes**, and may only stay in records as history; (3) in newly written text, "arm" is always replaced by "the build from pre-fix code / the fixed build" or "both sides";
> (4) **the output ruler is written at the end, and when you paste you must paste it along with the rest.** When dispatching a subagent, the full text of this document plus this round's briefing must be named in the prompt for it to read; pasting only this block is not enough.

```
Please continue the dynamic-tool analysis on MegaVul and establish more samples. The result files and intermediate files to be saved also follow the existing logic (write back into the sample folder + repro.sh + the ledger). Available methods: the ones recommended in <REPO_ROOT>/tasks/megavul_reports (the recommended_method in megavul_method_recommendation_remaining.csv / megavul_inconclusive_deferred_route_worklist.jsonl is only a starting point and does not bind you). Key rules: before confirming you must check info.json's label_target and confirm only label_target==1; never do unfiltered cluster propagation (cross-dataset work may only reuse the existing exact-body propagation code, requiring target=1 on the target, an exactly identical function-body hash, and that the target is not yet confirmed; a propagated confirmation was never run locally, counts statistically as attempted_inherited_crossdataset, and is not a local CONFIRMED); avoid low-yield network-protocol / cryptographic-arithmetic / pure-fuzzer classes, and prefer self-contained file/format parsers. Run as concurrently as possible as long as both real CPU occupancy and I/O wait are low (the criteria are CPU utilization and iowait, not load-avg; 2-3 rebuild channels). At the start of each round check /proc/stat, free -g, disk and I/O to make the gating decision; exclude ids that already have megavul_<id>.craft.json, canonical confirmed, label_target!=1, or in-flight (the 292 static ledger entries in megavul_label_noise.jsonl are NOT excluded -- they were never attacked, so they still have to be attacked); honestly skip logic/authentication classes with non-deterministic sanitizer faults; append results only to tasks/RUNLOG_<host>_megavul.md. Every sample, confirmed by a dynamic tool or not, needs its corresponding files saved per the existing logic. Ones dynamically confirmed as vulnerable need reproducible files saved; ones that are not reproducible need a corresponding explanation file saved.

★★★★ Criteria change (user, 2026-07-28, highest priority): a CVE mismatch is no longer a veto. As long as the labelled function can be made to trigger a real vulnerability by real, reachable input, it counts as CONFIRMED -- even if it is not the CVE it is labelled with. In that case write cve_match:false + cve_attribution_note + real_vuln{class,site,trigger}. So before downgrading because "the labelled function has nothing to do with this CVE", you must ask one more question: does this function itself have a real, triggerable defect? If yes, confirm it. ★ The fixed version also being vulnerable is not a veto (user, added 2026-07-28): as long as a dynamic tool can trigger the build from pre-fix code, this sample is confirmed vulnerable -- you only need to annotate honestly that its fix is also vulnerable. Record verdict:DYNAMICALLY_CONFIRMED + fix_arm_also_vulnerable:true + defect_present_both_arms:true + confirmation_class:OTHER_DEFECT_UNFIXED + fix_arm_signal (the actual sanitizer output of the fixed build). All three preconditions are required: (1) the defect must be reachable from the labelled function -- inside its body or inside a callee it calls (relaxed by the user 2026-08-01); a defect in a callee is not downgraded, it only gets confirmation_scope:"reachability" + defect_site + callee_of_labelled_function:true + call_path. Only when it is not reachable from the labelled function at all is it label noise -- the fault being in a caller, or in a sibling function with no call relationship; before judging you must read the upstream source to verify the call direction (MegaVul cases 12462/12458: the fault is in the sibling calculate_operand_data_length, so not a confirmation); (2) triggered by real reachable input, with empirical output from a sanitizer or an equivalent oracle; synthetic triggers (absurd magic numbers, values upstream would reject) still do not count; (3) the build from pre-fix code must be able to trigger it by itself -- inverted polarity (the stored "vulnerable version" is clean and the "fixed version" is what crashes; MegaVul cases 1082/6909) does not make this sample vulnerable; take it through §0a's inverted_polarity and the two gates and turn it into label noise. Only when the function genuinely has no defect at all, or the pre-fix build cannot trigger anything, do you downgrade. Statistics come in three tiers that must not be mixed: CONFIRMED_CVE_MATCH / CONFIRMED_OTHER_DEFECT (cve_match:false) / OTHER_DEFECT_UNFIXED (both sides fault alike). ★★★★ Unreachability is not a veto (user, added 2026-07-31): if the defect is genuinely inside the labelled function's body and is real (not manufactured by the harness changing upstream code), then even if no attacker-controllable path to it can be found, still record verdict:DYNAMICALLY_CONFIRMED and only add the fields reachability:"UNREACHABLE" + reachability_note + attacker_controlled_trigger:null. reachability is orthogonal to the three tiers above and does not change the tier. Keep three things apart; only the first goes with UNREACHABLE: (1) the defect is real, inside the labelled function, with no attacker path -> CONFIRMED+UNREACHABLE; (2) not built, not run, or the wrong oracle -> not unreachable, just not finished; go back and do it; (3) the harness uses #ifdef to delete a guard upstream already had, or adds a sink of its own and then reports the fault -> downgrade (MegaVul cases 16067/5757). Before writing UNREACHABLE, ask yourself: did I really prove it unreachable, or did I merely fail to find a path? The latter gets reachability:"UNKNOWN" plus a list of the entry points searched. MegaVul harnesses that hand-assemble a struct and call the labelled function directly always get an honest UNKNOWN; do not default to REACHABLE. Unreachability is to be measured, not deduced.

★★★ Hard rules for evidence self-sufficiency (these override the other path conventions): the verdict is not the product; the set of files that lets someone else rerun it is. MegaVul's current state: the entire dataset has 0 dynamic_evidence/ directories, the evidence sits flat in the sample directories, repro.sh generally compiles binaries into /tmp/vv_repro_bin (a shared path with the same name, so concurrent runs overwrite one another), and some of the 27 Path-B confirmations have build trees outside the repository under <SCRATCH>/pathb_builds/. Therefore:
(1) From this round on, every sample (confirmed or not, alike) has its newly written or repaired reproducible files placed in data/output/dataset/megavul/<id>/dynamic_evidence/, with the directory name fixed. It contains at least: repro.sh (one command to build both sides + run + print the differential), driver.c/harness, the code under test for both sides (body_vuln.inc/body_fix.inc, or stub.h+#ifdef FIXED, checked with cmp against the sample's own vulnerable_function.c / fixed_function.c), the real PoC input file (stored byte-for-byte), the actual output log of each side, and EVIDENCE_MAP.json (each file's purpose + sha256). Old flat files are neither moved nor deleted, but must be listed in EVIDENCE_MAP.json. Unconfirmed samples must also leave behind the scripts and logs actually run.
(2) It is strictly forbidden to leave any artifact in /tmp, ~, <SCRATCH>/pathb_builds/, <SCRATCH>/wl_campaign/, or anywhere outside VulValidate/. If you need temporary space, export TMPDIR="$(dirname "$0")"/tmp and keep it after the run.
(3) No absolute paths in scripts: use cd "$(dirname "$0")", D="$(dirname "$0")/..", CC=${CC:-gcc}. Swapping in a different absolute path is the same as not fixing it. Before handing over, grep -rn '/scratch/\|/tmp/\|/home/' *.sh must print nothing.
(4) Paths in records are written relative to the sample directory: in dynamic_confirmation.json and craft.json write "dynamic_evidence/repro.sh", not a bare file name, not an absolute path outside the repository, not a shell brace expansion, and do not put the pointer only in INFO.md. Three places must agree: the record's path fields, craft.json's path fields, and the real files on disk.
(5) Third-party software/source/builds all live inside VulValidate/: at-commit build trees and banked ASan binaries -> pathb/<lane>/<name>_{vuln,fix}/, upstream tarballs -> pathb/_srcpkg/ (keep the original archive + sha256), toolchains/sysroots -> pathb/_toolchain/, kernel images -> pathb/kasan/, shared cross-sample stub headers -> pathb/_shared/. repro.sh references banked binaries by repository-relative paths and writes the pin into EVIDENCE_MAP.json (git_remote+commit+dirty_files+the configure line; if dirty_files!=0 the diff must be stored in dynamic_evidence/ as well). Do not copy the upstream build tree per sample.
(6) Self-check before handing over: run it, do not just look at whether files exist. cd into dynamic_evidence/, rm the build artifacts, and bash repro.sh must build both sides from source and really produce a differential; a single Path-A harness must also pass a cmp check that the labelled function body is compiled in verbatim. Three easily mistaken criteria: a log is not a reproduction file (only logs in the directory = not valid); the existence of craft.json != a differential was run; both sides clean does not mean there is no vulnerability (in the human re-review of 1,677 MegaVul confirmations, 199 harnesses never compiled the labelled function in), so prove the labelled code really executed before drawing a conclusion.
(7) Withdrawing a confirmation means changing four places, and info.json is the one most often missed: (1) the record's verdict+reason+the label_noise family; (2) craft.json moved into <id>/prior_confirmation_<stamp>/ (moved, not deleted); (3) info.json changed using the repository's existing vocabulary -- label_noise:true uses tier=mislabel/is_vulnerable=NO, label_noise:false (a real patch but it cannot be triggered) uses tier=not_dynamically_confirmed/is_vulnerable=NOT_CONFIRMED, and ones really attacked with a dynamic tool where the vulnerability did not come out get label_noise_type:label_noise_dynamic_tools_attacked + label_noise_basis:dynamic_attack_negative (the seven gates are in the section "explicit marking rules for label noise"), and label_target is never touched; (4) leave a rerunnable script for the negative result in dynamic_evidence/. No downgrading without the user's explicit consent.
(8) Run the batch-level checkers before closing out; MegaVul currently has no checkers of its own (the four scripts under bigvul_reports/evidence_repair hard-code bigvul paths), so parameterize them first and then run them, and samples added this round must not appear in the "evidence outside the sample directory" list.

★ Hard criteria for CVE-match faithful triggering (all must hold for CONFIRMED):
In one sentence: only what can be reached by real crafted input through a real call chain is a real trigger; what is forced out by absurd parameters, which real input cannot produce, is synthetic. (From 2026-07-28: "the patch does not stop it" no longer equals synthetic -- upstream not fixing this bug != this bug not existing.)
(1) Read the real CVE first: before confirming, pull NVD plus the fix diff of code_link/commit_id, and write real_root_cause / trigger_mechanism / attacker_controlled_trigger.
(2) The differential is the standard path: under the same input, the vulnerable version (built at fix^) faults and the real fixed version (built at the fix commit) passes clean = CONFIRMED_CVE_MATCH. extract-stub must also compile both sides for comparison -- fixed_function.c sits right there in MegaVul's directory, so there is no excuse for building only one. Both versions crash -> if the defect is inside the labelled function and the pre-fix build can trigger it, it is still CONFIRMED, recorded with fix_arm_also_vulnerable:true + OTHER_DEFECT_UNFIXED; only when the defect is not inside the labelled function is it label noise. Neither version crashes = the pre-fix build cannot trigger it at all -> not a confirmation; and here you may not stop at unconfirmed -- if it really was attacked with attack input (all seven gates passed), record label_noise_dynamic_tools_attacked; if the gates were not passed it is simply not finished, so go back and do it.
(3) Prefer "build-at-commit + real input", going through the real demux/parse/decode call chain rather than hand-assembling a struct and calling the labelled function directly.
(4) Trigger values must be realistic and reachable: sizes/lengths/counts must be producible by a real crafted file and must reach the labelled function through a real entry point; absurd magic numbers are forbidden unless that exact value is attacker-reachable via a real path; a value upstream validation would reject = unreachable = invalid.
(5) Mechanism must match: the fault type/location must be consistent with the mechanism the fix repairs; another real vulnerability inside the labelled function -> cve_match=false but still CONFIRMED; forcing it with out-of-bounds/contract-violating parameters at an unrelated statement, or a fault inside the harness's own stub logic (255<<24 in the ato32 stub, the get_alen stub, the gf_bifs_dec_name stub, the XcursorImageCreate stub) = synthetic / Invalid Test -> does not count.
(6) Allocation site != write site is allowed: the labelled function "under-allocating" and the out-of-bounds write happening in a downstream callee in the same file is faithful -- record frame_note (alloc_site/fault_site), and do not synthesize in order to make frame#0 be the labelled function; but a fault inside a consumer written by the harness and called directly by main (MegaVul cases 3907/2040/4492) does not count -- not a single frame of the labelled function is in the fault stack.
Save both kinds: the record and craft.json record cve_match, triggered_vuln, cve_vuln, synthetic_trigger, differential (integer vuln_rc/fix_rc), frame_note.

★ Explicit marking of label noise: ★★ changed by the user 2026-08-03: before judging label noise you must first attack the labelled function with a dynamic tool and fail to trigger a vulnerability; reading the diff / counting files / looking at the commit title can only produce suspected_label_noise:true + suspected_label_noise_category, and the sample stays on the to-do list waiting to be attacked. NOT_TRIGGERABLE_AS_LABELED in inspection.json and the 292 entries in megavul_label_noise.jsonl are all merely suspected and do not count as LABEL_NOISE_EXCLUDED. Attack scripts, inputs and complete logs always go into <id>/dynamic_evidence/label_noise_attack/; without that directory the finding does not hold. For ones where the attack really fired nothing, write in the record label_noise:true, label_noise_type:label_noise_dynamic_tools_attacked, a reason containing the literal words "label noise", and real_vuln_location; also fill in label_noise_category: whole-commit-relabel / multi-function-relabel / whitespace-only-relabel / wrong-function / version-skew / mass-hardening-sweep / library-import-relabel / cosmetic-refactor / wrong-cwe / test-file-labeled / inverted-polarity. The seven gates must all be passed: a real integer exit code actually produced + the labelled function really executed + attack input was used + the oracle chosen to match the fix mechanism + a clear statement of attack-surface coverage + first proving the stored body is verbatim identical to upstream at fix^ + the execution proof reaching the exact lines the patch changed (with the hit counts written into the record). Conversely, a real vulnerability the tools cannot reach gets label_noise:false + a reason containing "needs-Path-B"; the two are strictly distinguished.

★★★★★ Output ruler (user instruction 2026-09-20, the last step, not to be skipped): every target=1 sample touched this round must end up in exactly one of the four outcomes below, with that outcome's secondary fields filled in. The four outcomes have only these four names; old strings such as INCONCLUSIVE / DEFERRED / DEFERRED_NEEDS_CALLER / DEFERRED_HEAVY_FRAMEWORK / NOT_TRIGGERABLE / NOT_TRIGGERABLE_AS_LABELED / NOT_CONFIRMED / UNTOUCHED may no longer appear as outcomes (they may only remain in a record's verdict field as history):
(1) CONFIRMED -- the labelled function triggered a real defect under faithful input. Fill in confirmation_class (one of the three tiers CONFIRMED_CVE_MATCH / CONFIRMED_OTHER_DEFECT / OTHER_DEFECT_UNFIXED) + cve_match + confirmation_scope (defect_site or reachability, only these two values) + reachability (REACHABLE / UNREACHABLE / UNKNOWN). Ones where only the pre-fix side was built and there is no integer fix_rc cannot be assigned a tier, and must not default to CONFIRMED_CVE_MATCH.
(2) LABEL_NOISE_EXCLUDED -- the label is overturned: either it was attacked with a tool matching the CWE, nothing triggered, and all seven gates are in place, or a differential was measured whose direction is inverted. Fill in label_noise_category + label_noise_basis (only the two values dynamic_attack_negative / dynamic_differential_inverted) + label_noise_type; write n/a for cve_match. Ones that merely look mislabelled from reading the code never belong in this cell; write suspected_label_noise, leave them on the to-do list, and count them statistically in cell (4).
(3) DY_Attacked_But_can_not_decide_confirmed_or_label_noise -- it really was attacked with a dynamic tool and readings from both sides were obtained, but this measurement cannot decide between confirmation and mislabel. dy_attacked_undecided_category is required, and its value may only come from the vocabulary in §0a (nominated_awaiting_adjudication / attacked_no_trigger / guard_never_evaluated / decision_diff_no_impact / fault_not_attributable / inverted_polarity (only a temporary state pending adjudication; once the two gates are passed it moves to cell (2)) / no_differential_possible / synthetic_trigger / reachability_unproven / cve_mismatch / single_arm_only / unclassified_reason).
(4) NOT_DYNAMICALLY_TESTED -- no valid dynamic measurement has been obtained yet: never tested, could not reach it, or built and ran but produced no result. not_tested_reason is required, its value may only come from the vocabulary in §0a (attempted_no_usable_result / needs_path_b_not_attempted / never_attempted / build_failed / attempted_inherited_crossdataset / confirmation_withdrawn_nothing_measured_since / unclassified_reason), and it is decided from the actual state on disk (is there a repro.sh, are there run logs, is there an inspection.json, was it propagated via propagated_from / confirmation_type:crossdataset-*), not from that mostly-empty reason field in the record. MegaVul's 943 cross-dataset propagated confirmations go to attempted_inherited_crossdataset and must be separately countable.
The boundary between cell (3) and cell (4) turns on a single question: was this sample really attacked with a dynamic tool, and were readings from both sides obtained? Attacked -> (3); the attack did not succeed or has not been attempted -> (4). "identical" / "n/a" / null / the string "1" are not integer exit codes and always go to (4).
When reporting at sign-off, the four numbers must add up to this round's denominator, and the secondary-field distributions of cells (3) and (4) must be given at the same time -- reporting only the total of cell (3) is meaningless. An empty string, NONE, or a whole sentence pasted into the value slot is not a valid value; it must stay visible and must not be washed into unclassified_reason.
```

## Paths and ledgers (MegaVul-specific)

- Dataset samples: `data/output/dataset/megavul/<id>/` (containing `info.json` / `context_meta.json` / `vulnerable_function.c` / `fixed_function.c` / `containing_file.c` / `dependencies/` / `compilable_unit/` / `INFO.md`). **Reproducible files -> `<id>/dynamic_evidence/`** (see rule 1 at the top); the historical flat evidence `dynamic_confirmation.harness.c` / `dynamic_confirmation.asan.log` / `repro.sh` sits directly in the sample directory and is not moved. Note that metadata such as `file`/`function` actually lives in `context_meta.json`, and `info.json::file_name` is a JSON list of strings.
- Dynamic records: newly written ones are always `dynamic_confirmation.json`; the historical Claude-crafted record is `dynamic_confirmation.record.json` (keys: `id` / `cve` / `cwe` / `verdict` / `method` / `tools_fired` / `fault` / `input` / `tool_matrix` / `reproduce`); recognize both when reading, and write only the former (or modify the latter additively; do not let the two contradict each other).
- Static review: `inspection.json` (`verdict` / `feasibility` / `analysis`) -- **counts only in the fourth cell; it is not a dynamic measurement**.
- The registry (source of truth): `data/output/dynamic/confirmed/megavul_<id>.craft.json` (2,890 files as of 2026-07-23). **Note it is `data/output/dynamic/confirmed/`; `data/output/confirmed/` does not exist.**
- The static label-noise ledger: `tasks/megavul_reports/megavul_label_noise.jsonl` (292 entries) -- static triage, not a dynamic conclusion; it is not excluded and must be attacked.
- Builds and third-party material: `pathb/` (inside the repository). See the partition table under rule 4 at the top. **`<SCRATCH>/pathb_builds/` is outside the repository and is something to be migrated.**
- Ledger: `tasks/RUNLOG_<host>_megavul.md` (append only; creating other RUNLOG_* files is forbidden). Reindex: `nohup python3 scripts/build_dedup_index.py` (do not block on it every round).
- Key fields of `info.json`: `label_target` (**confirm only ==1**), `cve`, `labeled_cwe` (a list), `project` (**a 40-character commit hash, not a project name**), `commit_id` (check against `code_link` which one is the fix commit; Path-B builds at its parent=fix^), `code_link` (the upstream commit URL), `file_name`, `has_fix`, `static_verdict` / `static_evidence` / `detectors_matching`, `before_cwes` / `after_cwes`, `is_vulnerable` / `tier` / `determination_reason` (our verdict, to be changed on withdrawal); some samples also carry `inspection`, `dynamic_confirmation`, `dynamic_confirmation_source` / `dynamic_confirmation_type` (the cross-dataset provenance lives here), and a `reproduce` block. In a sample of 3,000, 50 `info.json` files could not be read; when reporting, count them as "unreadable", not as 0.
- Human re-review (2026-09-14 -> 09-24): `tasks/megavul_reports/manual_check_megavul_20260914/`, summary `CAMPAIGN_SUMMARY_20260924.md`, full table `ALL_ADJUDICATIONS_MEGAVUL.csv`; index `tasks/manual_check_reports_index.html`.

## ★ Hard criteria for CVE-match faithful triggering (strengthened by the user 2026-07-20, effective together with the prompt)

The acceptance standard in one sentence: **only what can be reached by real crafted input through a real call chain is a real trigger; what is forced out by absurd parameters, which real input cannot produce, is synthetic. (From 2026-07-28: "the patch does not stop it" no longer equals synthetic -- upstream not fixing this bug != this bug not existing.)**

Six hard criteria (all must hold for CONFIRMED):
1. **Evidence before action**: before confirming, read NVD plus the fix diff of `code_link` / `commit_id`, and write `real_root_cause` / `trigger_mechanism` / `attacker_controlled_trigger` into the record.
2. **The differential is the standard path (revised 2026-07-28; no longer the only path)**: under the same input, the vulnerable version (built at `fix^`) faults and the real fixed version (built at the fix commit) passes clean = `CONFIRMED_CVE_MATCH`. Prefer a real build-at-commit binary; extract-stub must also compile both sides for comparison.
   - **Both versions fault** -> if the defect is **inside the labelled function** and **the pre-fix build can trigger it by itself**, it is still CONFIRMED, recorded with `fix_arm_also_vulnerable:true` + `OTHER_DEFECT_UNFIXED`. **A defect in a callee that the labelled function calls is confirmed too** (user, 2026-08-01), adding `confirmation_scope:"reachability"` + `defect_site` + `callee_of_labelled_function:true` + `call_path`. Only when it is **not reachable from the labelled function at all** is it label noise -- before judging you must read the upstream source to verify the call direction.
   - **Neither version faults** -> the pre-fix build cannot trigger it at all -> not a confirmation.
   - **Inverted polarity** (the pre-fix build is clean and the fixed build faults) -> this sample is not vulnerable; handle it via §0a's `inverted_polarity`.
3. **Prefer real entry points**: if you can "build the real tool + feed a real crafted file through the real decode path", do not use a miniature harness that hand-assembles struct state and calls the labelled function directly.
4. **Trigger values must be realistic and reachable**: sizes/lengths/counts must be values that real crafted input can produce and that reach the labelled function through a real call chain. **Absurd magic numbers are forbidden** unless that exact value is attacker-reachable via a real path.
5. **Mechanism must match**: the triggered fault's type/location must be consistent with the mechanism the fix diff repairs. **Another real vulnerability** inside the labelled function -> `cve_match=false` but still CONFIRMED; forcing it = synthetic.
6. **Allocation site != write site is allowed**: record `frame_note` (alloc_site=the labelled function, fault_site=the callee). **(Added 2026-07-31) This belongs to `confirmation_scope: "defect_site"`**; if the labelled function **has no defective operation of its own**, that is `confirmation_scope: "reachability"`. The dividing line is the counterfactual question: **if you change only the labelled function, does the vulnerability go away?**

Saving: the record + craft.json record `cve_match`, `triggered_vuln`, `cve_vuln`, `synthetic_trigger`, `differential` (vuln_rc/fix_rc), `frame_note`.

### Counterexample vs positive example

- BigVul 179087 / CVE-2013-7022 (FFmpeg `g2m_init_buffers`): the extract-stub stuffed in `40000x40000` to force an integer overflow, and the fixed version did the same thing -> synthetic; building real FFmpeg + a G2M4 AVI crafted with a 17x17 frame / 16x16 tile -> the vulnerable version gives an ASan heap-overflow WRITE and the fixed version is clean under the same input -> a real trigger.
- **The three kinds of case from MegaVul's human re-review** (the rules for all 1,677 are in `CAMPAIGN_SUMMARY_20260924.md` §5):
  - **Supporting**: the body is compiled in verbatim, and the fault frame lands within the labelled function body's line range, or in a modelling accessor it calls where the bad value comes from inside the body (16595 `ptr_get_be16`, 9795 `copy_to_user`, 5220 `php_strnlen`); an upstream whole-tree build with the labelled function present in the fault stack (16646 apedec, 12183 gpac).
  - **Conflicting (Mock)**: the labelled function body is not compiled in and `main` restates the core arithmetic itself (13267 / 16546 / 5156 / 7223 / 8283 ...); the log comes from a renamed `*_vuln_core` harness under a different BigVul id (10079 / 1971 / 2662 / 3227); the harness compiled `fixed_function.c` (1082 / 6909).
  - **Insufficient evidence**: the body was heavily modified by >=40 lines (12746 / 1220 / 16106 / 3424); the fault is inside a stub the harness wrote (82 / 80 / 81 `get_alen`); a nested crash with no stack frames; MSan reporting only at `main`'s sink (14851 / 14853 / 14860); the log comes from a harness that does not exist on disk (15526).

## ★ Explicit marking rules for label noise (added 2026-07-21; **the user rewrote the entry condition on 2026-08-03**)

### ★★★★★ Highest priority: before judging label noise you must first attack it with a dynamic tool (user, 2026-08-03)

> **Reading code alone cannot establish label noise.**
> Even if you are already convinced it is a mislabel -- the commit touched 41 files, `diff -w` is empty, the changes are all whitespace --
> **you must first really attack the labelled function with a dynamic tool, and only if no vulnerability is triggered may you judge it label noise.**

**Why this rule was added**: measured on BigVul 2026-08-03 across 1,160 samples of the "no-op change" class, 843 (72.7%) had text comparisons such as `diff -w` written in `tried_dynamic_method`, and 1,057 did not even have a `dynamic_evidence/` directory. **MegaVul's 292 `megavul_label_noise.jsonl` entries + 296 `NOT_TRIGGERABLE_AS_LABELED` are the same shape: all of them were read, not run.**
"This commit did not change this function" and "this function has no vulnerability" are two different things. See **P25** in `tasks/bigvul_reports/evidence_repair/PROBLEM_REGISTER_20260803.md`.

### Three terminal states, each written differently

**① Attacked, and the vulnerability did not come out -> this is label noise**

```json
"verdict": "NOT_DYNAMICALLY_CONFIRMED",
"label_noise": true,
"label_noise_type": "label_noise_dynamic_tools_attacked",
"label_noise_category": "<one from the vocabulary below>",
"label_noise_basis": "dynamic_attack_negative",
"real_vuln_location": "<the function/file where the real vulnerability lives, if it can be located>",
"reason": "<must contain the literal words label noise; state what was attacked, how, and why it is judged this category>"
```

`label_noise_category` values:

| category | Meaning |
|---|---|
| `whole-commit-relabel` | The fix touches >4-6 files and every touched function gets labelled |
| `multi-function-relabel` | The commit really is fixing this CVE, but this function is a bit player |
| `whitespace-only-relabel` | `diff -w` is empty |
| `cosmetic-refactor` | Plumbing such as signatures/renames/`#line` (MegaVul case 5532: the two stored bodies differ only in `#line`) |
| `wrong-function` | The fault is in a sibling function (**note: a fault in a callee does not count**, see the three-way split below) |
| `version-skew` | MegaVul's before/after does not match the real fix commit |
| `mass-hardening-sweep` | One defensive guard swept across ~100 files at once |
| `library-import-relabel` | A wholesale re-vendoring of an upstream library |
| `wrong-cwe` | The CWE/CVE classification itself is wrong |
| `test-file-labeled` | Labelled on test/example/generated code (MegaVul case 16429: labelled on a `main` under `tests/`) |
| `inverted-polarity` | The commit that introduced the vulnerability was collected as if it were the fix commit |

**② Only read the code, not yet attacked -> not label noise but "suspected", and the sample stays on the to-do list**

```json
"label_noise": false,
"suspected_label_noise": true,
"suspected_label_noise_category": "<same vocabulary as above>",
"label_noise_basis": "static_reading",
"reason": "<what was read; how you intend to attack it next>"
```

**`suspected_label_noise` does not trigger exclusion; the sample still has to be attacked.** Do not close out treating it as a conclusion. The old prompt's practice of "writing `NOT_TRIGGERABLE_AS_LABELED` into `inspection.json`" amounts only to this one.

**③ needs-Path-B (a real vulnerability the tools cannot reach)**: the label is right, the vulnerability is real, but a docker-free extract-stub/micro-harness cannot reach it. Write `label_noise: false` + a `reason` containing **"needs-Path-B"**. **This class is strictly distinguished from ①**: could not reach it != attacked and nothing fired.

### ★ Attack records and logs must be stored in the sample's own subdirectory

The fixed path is **`data/output/dataset/megavul/<id>/dynamic_evidence/label_noise_attack/`**, containing at least:

| File | Content |
|---|---|
| `attack.sh` | One command to rerun the whole attack (relative paths; `/tmp` and paths outside the repository are forbidden) |
| `driver.c` / `harness.*` | The driver used for the attack |
| `body_vuln.inc` (plus `body_fix.inc` when there are two sides) | **Copied verbatim from the sample's own `vulnerable_function.c`**, checked with `cmp` inside `attack.sh` |
| `inputs/` | Every attack input, stored byte-for-byte |
| `attack.<n>.log` | The **complete** actual output of each run, no truncation |
| `ATTACK_LOG.md` | What was attacked, the intent of each shot, the result, and why you stopped |
| `EVIDENCE_MAP.json` | Each file's purpose + sha256 |

**No such directory = this label-noise finding does not hold**, and the sample goes back on the to-do list.

### ★ Reaching ① has **seven** hard gates; missing any one forbids judging label noise

| # | Gate | How to prove it (required fields) |
|---|---|---|
| ① | **It was really built and run**, not a text comparison | `label_noise_attack/` contains `attack.sh` + a **non-empty** log; `vuln_rc` in `differential` is a **real integer** exit code, and must not be `"identical"` / `"n/a"` / `"unknown"` |
| ② | **The labelled function really executed**, not merely got compiled in | `labelled_fn_executed: true` + `execution_proof`: instrumented output inside the function / a gdb breakpoint hit / a gcov count / the function's frame appearing in an ASan backtrace. **"It was compiled in" does not count** |
| ③ | **Attack input was used, not normal input** | `attack_inputs`: list the inputs actually fed in and the intent behind constructing them |
| ④ | **The oracle was chosen correctly** (**chosen by the mechanism in the fix diff**, not by the labelled CWE, and certainly not always ASan) | `oracle_kind` + `oracle_rationale`. CWE-125/787 -> ASan; CWE-401/772 -> LSan; CWE-190/191/369 -> UBSan or m32; CWE-457/665/908/200 -> **MSan or Valgrind**; CWE-476 -> ASan/SEGV; CWE-362 -> TSan/KCSAN/real concurrency; DoS -> timeout/signals/resource growth; logic/permission/injection classes -> behavioral differentials. **"ASan reported nothing" says nothing at all about an integer overflow or an information leak** |
| ⑤ | **Attack-surface coverage stated clearly** | `attack_surface_note`: which entry points / value ranges were tried, whether a value sweep or fuzzing was done, and for how long it ran |
| ⑥ | **First prove the stored body is complete** (P67) | Compare it **verbatim** against the upstream file at `fix^` (line count, first and last lines, brace balance), checked with `cmp` inside `attack.sh`. If it does not match, this is not "attacked and nothing triggered", it is **attacking the wrong object** -- record `stored_body_incomplete` + `needs-Path-B`. **A truncated body that does not compile is actually safe; the dangerous kind is the one that compiles and runs clean.** |
| ⑦ | **The execution proof must reach "the exact lines the patch changed", not "the function was entered"** (P68) | Set breakpoints on the lines the patch changed, run to completion, read the hit counts from `info breakpoints`, and write the **per-line counts** into the record. A count of 0 means **this measurement never reached the disputed point** |

**★ The seventh gate needs a mandatory companion check (P104): a gdb hit count of 0 != it did not execute.** A `static` function gets inlined at `-O1`, and `break` resolves only to the copy that was not inlined. **When the gdb count is 0 you must confirm with a second method** (ASan/UBSan frames, gcov, or an output string unique to that function), **otherwise you may not write `labelled_fn_executed: false`**.

**★ There is one more unnumbered check that can veto everything just as hard (P36 / 8h): a command-line flag hard-coded in the script can mask a real vulnerability.** The criteria are not "it ran and reported nothing", they are **"is what ran the path upstream thinks should be run"**. Before running, go and look at which flags the upstream tests use.

**Special note for samples whose two sides are semantically identical (no-op changes / hardening sweeps)**: they cannot produce a differential, so you can only build **one** side and run the oracle; in that case the "real exit code" of gate ① refers to that one side's. **Do not treat "both sides behave the same" as an attack result.**

### The `label_noise_basis` vocabulary (**only these three values**)

| Value | When to write it |
|---|---|
| `dynamic_attack_negative` | **Attacked, and nothing fired**, with all seven gates passed |
| **`dynamic_differential_inverted`** | **A differential was measured and its direction is inverted** -- what goes wrong is the build from the **fixed** code |
| `static_reading` | **Only the code was read.** **Does not trigger exclusion**; the sample stays on the to-do list waiting to be attacked |

> **`dynamic_differential_inverted` says "the label got which side is vulnerable wrong", not "this function has no defect"** -- the latter requires a separate one-sided attack before it can be said.

**How to write it in info.json**: `label_noise: true` -> `tier: mislabel` + `is_vulnerable: NO`; `suspected_label_noise` does not change info.json; `label_target` is never touched.

★ **The three-way split (revised 2026-07-31): wrong-function vs frame_note vs reachability**. A fault inside a callee the labelled function **really calls**, reachable through a real call chain -> a faithful CONFIRMED (`frame_note` or `reachability`, `label_noise=false`); only when the labelled function has **no real call relationship** to the faulting function (a pure sibling) is it wrong-function. Never mistake "allocation site/entry point != fault site" for wrong-function.

## ★ Whether an injected runtime condition counts as a faithful trigger -- the criterion is "does upstream accept it" (rule C, ruled by the PrimeVul owner 2026-08-17, applies to MegaVul too)

There is a class of samples whose defect appears only when a certain **runtime condition** occurs, most commonly **an allocation failure**. **The criterion is one sentence**:

> **Is what this fix changed "what to do when this condition occurs"?** Yes -> injecting that condition **counts as a faithful trigger**; no -> it counts as a **synthetic trigger**.

MegaVul already has two positive examples: 12692 (libarchive, `--wrap=calloc` makes the one `calloc` inside `__archive_write_allocate_filter` return NULL, and the fix is precisely adding a NULL check) and 6900 (opusfile, `--wrap=malloc` makes `ogg_sync_buffer` return NULL, and the fix is precisely adding a `buffer==NULL` check).

**When confirming under this rule, all five of the following must hold; missing one invalidates it:**

1. **The failure/NULL must come in through the program's own public interface or a link-time `--wrap`**, and **not one line of upstream source may be changed.**
2. **The injector is byte-identical in both builds**, so the only variable is still the labelled function body.
3. **Write `faithful_trigger_basis`**, and **quote verbatim** the place in the fix commit that handles this condition.
4. **Write `attacker_controlled_trigger` honestly as `null`**, and `reachability` as `UNKNOWN` (unless there is another measured path to reach it).
5. **Readings from both sides are still required**: real integers, execution proof reaching the disputed line, and a positive control that responds.

**The record must also write the two sides' readings separately** (field name `alloc_failure_reading_<date>`): (1) what happens when this condition really occurs and on what grounds you say it really occurred; (2) whether any attacker-controllable input can reach the same state without the injection -- **when the answer is "no", say so plainly**.

---

## ★ Sign-off self-check and stopping conditions (aligned with PrimeVul 2026-08-21)

### Per-sample self-check (run it for every id processed this round)

```bash
python3 -m json.tool data/output/dataset/megavul/<id>/dynamic_confirmation.json >/dev/null
python3 -m json.tool data/output/dataset/megavul/<id>/dynamic_evidence/EVIDENCE_MAP.json >/dev/null
grep -rn '/scratch/\|/tmp/\|/home/' data/output/dataset/megavul/<id>/dynamic_evidence --include='*.sh'
cd data/output/dataset/megavul/<id>/dynamic_evidence
ls arm_vuln arm_fix *.o 2>/dev/null   # see how many the glob matches before deleting
rm -f arm_vuln arm_fix *.o
bash repro.sh
```

`grep` must print nothing. **Deleting with a wide glob from the dataset root is forbidden.**
**Add one more field scan**: any sample in this batch that has **neither `tried_dynamic_method` nor `blocked_reason`** is a write that was missed.

### Batch-level checkers (run both; missing one means not closed out)

```bash
cd tasks/bigvul_reports/evidence_repair
python3 verify_batch.py --ids <the list of ids for this round>
python3 check_loop_prompt_compliance.py <project>
python3 check_loop_prompt_FULL.py <project>
python3 locate_evidence.py
```

**★ All four of these scripts currently hard-code the dataset path as `data/output/dataset/bigvul`, and produce nothing at all for MegaVul.**
Per §8c of the repository-root `CLAUDE.md`: **a rule written only into the document and not into a checker does not exist.** So the first thing to do for MegaVul this round is to parameterize them
(`--dataset megavul` or copy them into `tasks/megavul_reports/evidence_repair/`) and make them recognize both the flat layout (historical) and `dynamic_evidence/` (newly written).
**Until they are parameterized, "the checker reported nothing" does not count as passing.**

### The mistake the checkers themselves are most prone to: recognizing only "a value was filled in", not "it was measured and cannot be decided"

Mechanically filling in `defect_site` (P56), reporting an honestly written `labelled_fn_executed: false` as "missing field" (P97), and reporting "it ran, the two sides did not separate, so it cannot be decided" as "missing field" (P107) -- **the common shape: the checker forces people to invent a value.**
**Rule: every time you add a required field, the same change must work out "what is the valid way to write it when it cannot be measured", and make the checker accept that.** Boolean fields are only checked with `is None`; `confirmation_scope` left empty but accompanied by `confirmation_scope_undetermined` + a reason counts as done.

### Three hard rules for bulk record edits

1. **Read-decide-write must stay together; "read everything into memory then write everything" is forbidden.** Re-read and re-decide before every write to disk; skip entirely any project that has an agent running on it (P93).
2. Every bulk script must carry this assertion:
   ```python
   after = dict(d)
   for k in NEW_KEYS: after.pop(k)
   assert after == before, sid      # apart from the keys I mean to add, nothing may change
   ```
3. **Before an `rm` with a glob, `ls` the same glob first.**

### Stopping conditions for the campaign

It counts as complete only when all of the following hold at once:

- Every active `target=1` sample has a real `tried_dynamic_method` and a real two-sided `differential`, or a valid structural exception that was measured and has complete evidence;
- Every sample lands in exactly one of the four outcomes of §0a, with its secondary fields **all filled in**;
- The 943 cross-dataset propagated confirmations have been taken out of `CONFIRMED` and counted separately (`attempted_inherited_crossdataset`), or have been rerun locally and obtained readings from both sides of their own;
- Every `suspected_label_noise` produced by static judgement (including the 292 entries in `megavul_label_noise.jsonl` and the 296 `NOT_TRIGGERABLE_AS_LABELED`) has really been attacked, or remains on the active list; **it must not disappear through a default exclusion**;
- Every processed sample's scripts, inputs, source for both sides, complete logs and `EVIDENCE_MAP.json` are inside the sample directory and rerunnable;
- `dynamic_confirmation.json`, craft.json, `info.json` and the registry agree on the same ruler;
- After the final rerun of the statistics and the worklist generator, there is no discrepancy on disk that can only be explained by an old snapshot, a static classification or an agent's self-report;
- The denominator question (17,592 vs 15,222) has been resolved and written into the report.

**Only needs-Path-B left, both sides clean, the tools cannot reach it for now, it looks mislabelled statically -- none of these is an automatic reason to stop.** Neither is `blocked_reason: "build_failed"`. **"It cannot be built" can never imply "this function has no vulnerability".**

---

## ★ These two categories must be stated as full sentences (user instruction 2026-08-08, in effect for every prompt)

| Do not write it this way | Write it this way | Short tag |
|---|---|---|
| "the exclusion stands" | **attacked and not a single fault fired ⇒ the label-noise finding stands, the function really is mislabelled** | `(mislabel confirmed)` |
| "the exclusion probably does not stand, awaiting your ruling" | **a fault fired and it attributes to the labelled function ⇒ the label-noise finding is probably wrong, the function may genuinely be vulnerable, pending human adjudication** | `(may genuinely be vulnerable - pending adjudication)` |
| "does not count yet - not finished this round" | **no conclusion this round** (never attacked / the measurement does not hold / the fault does not attribute to this function) | `(no conclusion)` |

Writing requirements: (1) **the full sentence must be used the first time it appears**; (2) the sentence must mention both "attack" and "whether a fault fired"; (3) when reporting numbers, state the **direction** along with them. **The same applies in the prompts for dispatched subagents.**

---

## MegaVul dataset characteristics (key differences from BigVul / PrimeVul)

1. **Almost all confirmations are a single Path-A harness**: method families `Claude-crafted` 1,664 / `Path-B build-at-fix replay` 27 / `Extract/stub` 19 / cross-dataset propagation 943 / verdict from the sample itself only 352 (2026-07-23). The Claude-crafted approach is: compile `vulnerable_function.c` into `dynamic_confirmation.harness.c`, model the surrounding types/callees, hand-assemble the triggering state in `main`, and run ASan+UBSan (+MSan / m32) to see whether anything is reported -- **the fixed side was never built, and `tool_matrix[].run_rc` is a one-sided exit code**. By this document's ruler they lack `differential.fix_rc`, `confirmation_class`, `confirmation_scope` and `reachability`. **`fixed_function.c` sits right there in the directory, so building the fixed side is the cheapest way to fill in the measurement.**
2. **The `project` field is a commit hash**, and `code_link` is the upstream URL; `labeled_cwe` is a list; `file_name` is a JSON list of strings. Grouping by project and finding the fix diff both start from `code_link`.
3. **Cross-dataset propagation is inbound**: the 943 `CONFIRMED` come from exact-body propagation out of PrimeVul (865) / BigVul (76) / DiverseVul (2) (`crossdataset_copy_primevul_to_megavul/`, `crossdataset_copy_bigvul_to_megavul/`). They were never run locally and count statistically as `attempted_inherited_crossdataset`; the `propagated_from` / `confirmation_type: crossdataset-*` lineage in the record must be preserved permanently, and must not be rewritten as a local rerun merely because "there are logs in the directory". The propagation rules are the same as BigVul's: propagate only to twin samples with `label_target==1`, an exactly identical function-body hash, and not yet confirmed; before confirming, run `scripts/is_duplicate.py megavul:<id>`.
4. **`inspection.json` is a static review, not a dynamic record**: 2,702 files, all with verdict strings of the `DEFERRED_*` / `NOT_TRIGGERABLE*` family, 404 of which overlap with confirmations. The old prompt treated it as "where unconfirmed samples land"; **now it counts only in the fourth cell**, and dynamic attempts always go into `dynamic_confirmation.json`.
5. **Human re-review has measured the credibility of this batch of confirmations** (2026-09-14 -> 09-24, 17 batches, 1,677 samples, `CAMPAIGN_SUMMARY_20260924.md`): supports 77.2% / conflicts 12.4% / insufficient 10.4%. The bulk of the conflicts is **Mock** (199: the labelled function body was not compiled in, `main` restates it, a renamed core `*_vuln_core`, logs coming from a harness under a different BigVul id, or `fixed_function.c` being the one compiled); the bulk of the insufficient is **the fault cannot be attributed** (104: nested crashes with no stack frames, a NULL function pointer with pc=0, MSan reporting only at `main`'s sink, out-of-bounds access in a consumer written by the harness and called directly by `main`, an upstream whole-tree build whose stack does not contain the labelled function) and **body heavily modified / fault inside a modelling stub** (62). **These 383 were marked as the third cell on 2026-09-24 per the user's instruction** (see item 5 of §0a's implementation debt); they are the first batch of targets for this loop's additional measurement (build the fixed side, switch to a faithful harness). The full criteria are in §5 of the summary, and the case numbers are in each batch's `_overrides.json`.
6. **The evidence layout is flat**: 0 `dynamic_evidence/` directories; `repro.sh` compiles into `/tmp/vv_repro_bin` (a shared path with the same name); some of the Path-B build trees are outside the repository under `<SCRATCH>/pathb_builds/`. Rules 1/2/4 all have ready-made violations to fix in MegaVul.
7. **target=0 negative samples**: a target=0 dynamic-confirmation purge was done on 2026-07-17 (`megavul_target0_dynamic_confirmation_purge_20260717.md`, deletion manifest `..._deletion_manifest_20260717.jsonl`); the directory `data/output/dataset/megavul_only_non_vulnerable/` does not exist (verified 2026-09-24), and whether negative samples are still mixed into `data/output/dataset/megavul/` **has not been verified across the whole set** (2026-09-24 sampling of the first 3,000 directories: 2,950 with `label_target==1`, 50 with unreadable `info.json`, 0 with target=0) -- this is also something to check together with the 17,592 vs 15,222 denominator question. **Always check `label_target`**, and it is **strictly forbidden** to propagate to or confirm a target=0.
8. **The label-noise ledger**: `megavul_label_noise.jsonl` holds 292 static triage entries (5 categories), with 1 explicitly declared in a result file; `LABEL_NOISE_EXCLUDED` is 0. **Not one of them has been attacked**; they are all `suspected_label_noise`.

## Method routing and output (chosen by project/CWE/CVE-year)

**Do these first (docker-free, high yield)**:
- **Build the fixed side**: for the 1,664 Claude-crafted confirmations, recompile the same harness against `fixed_function.c` (`#ifdef FIXED` or `body_fix.inc`) and run the same input once to obtain `fix_rc`. This is the cheapest way to turn a "one-sided reading" into "readings from both sides", and it is the precondition for turning the 1,294 human re-review "supports" into real `CONFIRMED`s.
- **Behavioral differential with `#ifdef FIXED`** (access control/injection/DoS/permissions/memory-fault gates; kernel CVEs can also be confirmed without booting a kernel).
- **Kernel micro-harness**: `kernel_stub.h` + extract the labelled kernel function + ASan.
- **extract-stub** (self-contained parsers; recursion DoS).
- **Path-B build-at-fix^ ASan**: reuse the banked `pathb/` binaries (gpac_2020 etc.); **give the subagent a hard no-rebuild constraint**.

**Low yield / honest DEFER**: hardening-relabel; needing a whole browser or a whole runtime with no extractable library; era-mismatched kernels; cryptographic arithmetic/side channels -- but each of them must still get a `tried_dynamic_method` plus why that class of tool cannot produce a differential, landing in the fourth cell as `needs_path_b_not_attempted` or `attempted_no_usable_result`; a bare DEFER is not allowed.

## How to dispatch

- About 12 ids per batch; when **both real CPU occupancy and iowait are low**, run 6-8 concurrent channels; during a co-tenant storm drop to 1-2.
- **Pre-filter to UNIQUE before dispatching**: classify using `data/output/dynamic/duplicate_samples.json` and dispatch only UNIQUE; DUP-canonical-unconfirmed goes to the propagation-specific flow. A `diff -w` pre-filter may only mark `suspected_label_noise`, and **the sample still has to be dispatched and attacked**; its value is reducing the work to a single attack.
- Deduplicate before dispatching: exclude ids where `megavul_<id>.craft.json` already exists + canonical already confirmed + `label_target!=1` + cross-dataset DUP + already processed in the RUNLOG + the in-flight set. **Do not exclude** the static suspects in `megavul_label_noise.jsonl`.
- **Subagent wording (to avoid cyber safety flags)**: frame it as "defensive vulnerability-dataset label-verification by differential sanitizer testing (pre-fix vs post-fix, same input); NOT exploit development".
- **★ Output-path discipline**: per-sample artifacts are written only under `data/output/dataset/megavul/<id>/`, and **reproducible files always go into `<id>/dynamic_evidence/`**; the record file name must be `dynamic_confirmation.json`; craft.json -> `data/output/dynamic/confirmed/megavul_<id>.craft.json`; the RUNLOG is only **appended** to `tasks/RUNLOG_<host>_megavul.md`. It is **strictly forbidden** to leave artifacts in `/tmp`, `~`, `<SCRATCH>/pathb_builds/`, `<SCRATCH>/wl_campaign/` or anywhere outside `VulValidate/`. Write these paths explicitly and literally into the dispatch prompt.
- **Cap recompilation concurrency at 2-3**; **builds go inside `pathb/<lane>/`**; the subagent carries a `make -j8` cap + a SKIP-if-craft.json-exists guard.
- **Every dispatched subagent prompt must embed the "hard criteria for CVE-match faithful triggering" above and the "output ruler"**. The wording must separate the **verdict fields** from the **proof fields**: what is forbidden is `verdict` / `confirmation_class` / `label_noise` / `label_target` / `cve_match` / `info.json` / `data/output/dynamic/confirmed/`; **the proof fields must be written** (`tried_dynamic_method`, `differential` with integer rcs, `oracle_kind`+`oracle_rationale`, `labelled_fn_executed`+`execution_proof`, `attack_inputs`, `attack_surface_note`, `labeled_function`, `labeled_file`). **Numbers an agent reports about itself are all wrong until spot-checked against the files.**
- **DoS rulings**: hangs/timeouts, unbounded recursion -> stack overflow, infinite loops, division by zero SIGFPE, unbounded allocation = CONFIRMED (a two-sided differential is still required).
- Saving: confirmed -> **`<id>/dynamic_evidence/`** + `dynamic_confirmation.json` (DYNAMICALLY_CONFIRMED + the four-outcome secondary fields + cve_match/triggered_vuln/cve_vuln/synthetic_trigger/differential/frame_note, with path fields written as `dynamic_evidence/...`) + craft.json + INFO.md/record.md + the RUNLOG; unconfirmed -> `dynamic_confirmation.json` (the third/fourth cell of §0a + secondary fields; no craft.json) + **the scripts and logs actually run, likewise left in `<id>/dynamic_evidence/`**, with the `label_noise` family of fields set per the rules above (only a real attack that fired nothing earns `label_noise:true`, with a `label_noise_attack/` directory) or `label_noise:false` + a reason containing "needs-Path-B".

## Current progress anchors

- MegaVul's current statistical anchor (**snapshot 2026-07-23**, denominator target=1 = 17,592): `CONFIRMED` **3,005** (17.1%), of which independent dynamic runs / historical registry entries **1,710**, canonical-only **352**, and exact-function-body cross-dataset propagation **943** (PrimeVul 865, BigVul 76, DiverseVul 2). The rest: `UNTOUCHED` **14,580**, `INCONCLUSIVE` **6**, `<MISSING_OR_UNPARSEABLE_VERDICT>` **1**; `inspection.json` **2,702** files; the static label-noise ledger **292**.
  **"confirmed" uses the census rule**: the registry has an entry within the denominator **or** the sample's own verdict is `DYNAMICALLY_CONFIRMED`, taking the union (registry_only 1,445, both 1,208, exact_verdict_only 352). The `data/output/dynamic/confirmed/` directory holds **2,890** `megavul_*` files.
- **By this document's ruler, not one of those 3,005 meets the field requirements for `CONFIRMED` today** (missing `confirmation_class` and others), 943 are inherited, and 383 were judged conflicting/insufficient by human re-review; the real four-outcome partition **has never been computed**.
- Ledger/report tooling: `compute_megavul_dynamic_status_statistics.py` (writes `megavul_dynamic_status_latest.{md,json}`), `refresh_current_megavul_reports.py`, `build_megavul_inconclusive_deferred_worklist.py`, and the authoritative summary `MEGAVUL_DYNAMIC_STATUS_SUMMARY.md`.

## Related reports (tasks/megavul_reports/)

`MEGAVUL_DYNAMIC_STATUS_SUMMARY.md` (authoritative summary), `MEGAVUL_LABEL_NOISE_REPORT.md` (static triage, 5 categories), `MEGAVUL_METHOD_RECOMMENDATION_SUMMARY.md` (routing), `LEDGER_STATUS.md`, `UNTOUCHED_BY_METHOD_ASSIGNMENT.md`, `megavul_target0_dynamic_confirmation_purge_20260717.md`, `manual_check_megavul_20260914/CAMPAIGN_SUMMARY_20260924.md` (human re-review of 1,677 samples), `gpt5.6_terr_megavul_dynamic_current_statistics_20260713.*` (statistical snapshot). For the full set of methods and criteria see `tasks/bigvul_reports/DYNAMIC_METHODS_CATALOG.md`, `tasks/bigvul_reports/evidence_repair/CONFIRMATION_SCOPE.md` and `PROBLEM_REGISTER_20260803.md` (the dataset-independent provisions apply directly).
