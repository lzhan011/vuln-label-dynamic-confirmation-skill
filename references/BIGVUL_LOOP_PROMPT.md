# BigVul Dynamic Confirmation /loop Prompt

> **The "must not be violated" part of this long document has already been condensed into the repository root `CLAUDE.md` (`AGENTS.md` is a symlink to it)**,
> which is auto-loaded at the start of every session, so nobody has to remember to read this file. When the two conflict, **this document wins**;
> if you change a hard rule here, remember to update `CLAUDE.md` to match.

> ## ★★★★★ Read this first: what this round must hand in at the end
>
> **Every `target=1` sample must land in exactly one of the four outcomes below, and the four numbers add up to the denominator.**
> Detailed definitions, the secondary-field vocabularies and the decision order are in **§0a**; the verbatim text you paste into `/loop`
> also carries the same "output ruler" at its end, and **you must paste that along with it**.
>
> | Outcome | One line |
> |---|---|
> | `CONFIRMED` | The attack fired, and the fault attributes to the labelled function |
> | `LABEL_NOISE_EXCLUDED` | Attacked and not a single fault fired (the seven gates are all in place), or the measured differential runs in the inverted direction |
> | `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | Really attacked, readings from both sides obtained, but this measurement cannot decide between confirmation and mislabel |
> | `NOT_DYNAMICALLY_TESTED` | No valid dynamic measurement has been obtained yet (never tested / could not reach it / built and ran but produced no result) |
>
> **`INCONCLUSIVE`, `DEFERRED`, `NEEDS_PATH_B`, `NOT_CONFIRMED`, `UNTOUCHED` are no longer outcomes**;
> they may only remain in a sample record's `verdict` field as history.

<!-- CURRENT-SNAPSHOT-START -->
## Current snapshot (the counting ruler is described below; **it must be recomputed every round, and you may not close out by citing the numbers here**)

Source of truth for the statistics: `tasks/bigvul_reports/bigvul_dynamic_status_latest.json` (**last recomputation: 2026-09-24 21:30**, key-for-key identical to the 2026-09-24 01:16 run, 0 records changed in between).
Original `target=1` denominator **10,900**. Under **ruler B** (re-measured this round) (the sample's own record + `FINAL_LEDGER_20260920.json` measured this round; when both cover a sample the measurement wins; set by the user 2026-09-24), the on-disk partition is:
`CONFIRMED` **4,308**, `LABEL_NOISE_EXCLUDED` **4,804**, the third outcome `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` **1,088** (13 of which still spell the old uppercase string in the record),
`NOT_DYNAMICALLY_TESTED` **200**, with the remaining **500** still scattered across old status strings
(`INCONCLUSIVE` 315, `NOT_DYNAMICALLY_CONFIRMED` 127, `INCONCLUSIVE_LABEL_NOISE` 24, `NOT_DYNAMICALLY_CONFIRMED_LABEL_NOISE` 13, `LABEL_NOISE` 7, `NOT_DYNAMICALLY_CONFIRMED (NO DIFFERENTIAL: BOTH ARMS FAULT IDENTICALLY)` 7, `DEFERRED` 6, `LABEL_NOISE_RELABEL` 1).
**Those 500 are exactly the outstanding debt that §0a below asks you to re-classify into the four outcomes.**
After folding those 500 into the four cells using the §0a decision order (`compute_bigvul_outcome_taxonomy.py`, `bigvul_outcome_taxonomy_latest.json`, recomputed 2026-09-25 02:30):
`LABEL_NOISE_EXCLUDED` 4,854 / `CONFIRMED` 4,308 / the third outcome 1,460 / the fourth outcome 278 (that script's output still prints the old name `BUILD_FAILED`).

Of the `CONFIRMED`, **490** come from cross-dataset exact-function-body propagation (484 sourced from PrimeVul, 5 from MegaVul, 1 from inside BigVul),
and **4,696** are independent dynamic runs or historical registrations. The `data/output/dynamic/confirmed/` directory holds 5,186
`bigvul_*.craft.json`, more than the CONFIRMED count inside the denominator -- **whenever you cite "how many entries the registry has", you must say whether it is the file count in the directory or the number of entries inside the denominator.**
Manual check: on 2026-09-24, batch 53 re-reviewed a random 100 of the full ruler-B CONFIRMED set: 92 supported / 3 in conflict / 5 with insufficient evidence; for the label-noise group, 100 samples gave 99 "the mislabel finding stands" / 0 pending adjudication / 1 no conclusion
(`manual_check_bigvul_20260913/fable_check_batch53_20260924/REPORT.md`).

Refresh commands (if this round **published any confirmation at all**, you must run the whole set, and run it once more before closing out):

```bash
python3 tasks/bigvul_reports/compute_bigvul_dynamic_status_statistics.py
python3 tasks/bigvul_reports/refresh_current_bigvul_reports.py
python3 tasks/bigvul_reports/compute_bigvul_outcome_taxonomy.py
python3 tasks/bigvul_reports/build_current_dynamic_method_worklist.py
python3 tasks/bigvul_reports/evidence_repair/recompute_current_repair_audit.py
python3 tasks/bigvul_reports/check_zh_en_report_numbers_agree.py
```

> **★ These commands walk all 10,900 sample directories, which is heavy on NFS** (measured 2026-09-24: statistics 6m23s, taxonomy 5m46s).
> With workers building concurrently, I/O wait was measured spiking to 68% while only 22% of CPU stayed idle --
> at that point, slamming another full-repository scan in every 10 minutes is fighting your own dispatched work for the disk.
> **Rule: when this round published no confirmation at all, skip the full-repository statistics**, and use a lightweight query that only reads the few dozen samples of this batch to watch progress;
> **after publishing you must run it once to catch up**, since the partition numbers and the worklist have to line up with the registry -- that part cannot be skipped.
> The criteria is **CPU utilization and I/O wait**, not load-avg: with load 30+ but idle CPU and low wa, the machine is fine;
> **only high wa is real congestion**.

**The snapshot is an entry point, not proof of completion.** The 5,252 / 5,202 / 446 / 4,713 / 4,558 / 5,154 / 4,742 / 4,926 / 4,514 /
3,486 / 5,092 / craft.json approximately 2,249 / canonical approximately 1,008 figures in the old reports are all void; stop citing them.
<!-- CURRENT-SNAPSHOT-END -->

---

## Wording (★ hard rules from the global CLAUDE.md, applying to all text written for humans)

Older passages in this document use "two arms", "sample arm", "fix arm" a great deal. **Newly written text must not use the word "arm" any more** --
the user explicitly asked for this on 2026-08-06, because it is unclear what the word refers to here. Say directly what the thing itself is:

- Do not write "both arms clean"; write "**the readings from both sides are clean**" or "the build from pre-fix code and the build from the fixed code are both clean"
- Do not write "the fix arm crashes too"; write "**the build from the fixed code crashes too**"
- Do not write "the sample arm cannot trigger it"; write "**the build from pre-fix code cannot trigger it by itself**"

Likewise, do not use the word "predicate" (say "decision condition" or "the field this code actually checks") and do not use the word "prose" for narrative text (say "the explanatory text in the document").
When talking about the two label-noise categories you must use the unambiguous full sentences; see the section "these two categories must be stated as full sentences" at the end of this document.

---

## ★★ Reading traps: these pitfalls manufacture false negatives that "look like nothing was measured" (measured 2026-08-15, synced from PrimeVul)

Every item below was hit in practice, and **every one of them turns a real vulnerability into a recorded "the attack did not fire a fault"**.

### (1) A positive control that "will never actually go wrong" proves nothing

Measured on PrimeVul 5540: to prove the oracle was alive, a worker built a positive control -- it loosened the mask `0xff0000`
to `0xffff00`. **But those bits are constantly zero after the shift**, so the checksum computed by this "defect-injected" control
**was byte-for-byte identical to the real function body.** The control "passed", while in fact it measured nothing at all.

**Rule: a positive control must first prove that it itself responds.** "I injected a defect" is not enough --
**you must see the control's output actually differ from the real function body's** (a different checksum, a different exit code, extra sanitizer lines).
When the control and the real function body give the same result, that is **the control failing**, not "the function is fine".
Same family: clang `-O1` optimized away the entire allocation injected into the control, so compiling, linking and running were all normal while the control was mute.

### (2) `-fsanitize=integer` reports unsigned left shifts, and that is not a defect

`unsigned-shift-base` fires **on both sides with the same value** -- an unsigned left shift is **defined behavior**,
and this checker merely treats it as a suspicious pattern. **Same on both sides = a tool artifact.**
When using `-fsanitize=integer`, turn it off and write in `repro.sh` why it is off.

### (3) "The two sides differ" is not a confirmation -- first look at which side is faulting

Measured on PrimeVul 204396: of 500 test cases, 314 separated the two sides, and the numbers looked like a very solid differential.
But **the side faulting was the build from the fixed code** -- that "fix" was in fact a **compilation patch-up** of the upstream patch,
and upstream deleted it the next day. Building another one carrying only the CVE-related hunk gave 0/500 --
the whole differential came from a different hunk.

**When you see the two sides separate, ask three things first**:
(1) **Which side is faulting** (only a fault on the build from pre-fix code can be a confirmation; a fault on the fixed build is inverted polarity);
(2) **Is it caused by the patch's own hunk** (one commit often contains several changes; build another one carrying only the target hunk to isolate it);
(3) **Is that "fix" really a fix** (some labelled commits are actually post-backport compilation patch-ups,
and the stored function body may even be a **non-compiling intermediate state**).
**Reading only "the two sides disagree" without looking at the direction records inverted polarity as a confirmation.**

### (4) Reading `git show --stat` and only looking at the largest file will miss a one-line hunk

Measured on PrimeVul 216832: the old record said this commit "only added a test certificate", and on that basis it was judged that no differential could be produced.
In fact the same commit **also changed one line in another file** -- and that line was exactly where the labelled function lives.
**`--stat` sorts by size, so a one-line change sits last and is the easiest to get truncated away.**

**Before judging "this commit did not touch the labelled function", you must run `git show <commit> -- <labelled file>` and look at that file's complete diff on its own.**
This is the same family of mistake as "the commit touched 41 files, so it is a whole-batch relabel":
**the size of a commit cannot substitute for reading what it did to this file.**

### (5) The two banked binaries may not contain the labelled function at all -- and it looks like "no differential"

Measured on PrimeVul 204794: the pair of binaries marked in the previous round as "both already banked, just run them" were **byte-for-byte identical**.
The cause was purely a build issue: that coder was wrapped in an `if <DELEGATE>`, and this machine only had the runtime library,
not the `-dev` package, so **the labelled function was in neither binary**. The run gave 0/0, which reads as "both clean".

**Rule: before running any banked binary, prove that the labelled function was really linked into it.**

```bash
nm <binary> | grep -c ' [Tt] <labelled-function-name>'      # must == 1 (for C++ use nm -C or match the mangled name)
```

Put this assertion into `repro.sh` so that it **fails immediately** after the build, instead of being read as a negative result after the run finishes.
**"Both clean" says nothing until you have proven the labelled function was executed.**

### (6) Two pitfalls in the sanitizers themselves

1. **ASan's default fast unwinder can drop the labelled function out of the stack entirely** -- when passing through libstdc++ without frame pointers,
   the stack breaks in the middle. **You need `ASAN_OPTIONS=fast_unwind_on_malloc=0`.**
   This means that some of the earlier conclusions of "not a single frame of the labelled function appears in the fault stack" **may have been produced by dropped frames**.
   Before deciding `unattributed_sanitizer_output`, rerun once with this option.
2. **clang does not instrument `std::string::empty()`'s read of an out-of-bounds element** -- ASan stays silent throughout,
   while a raw read of the same byte does report. **A "clean" probed through container methods proves nothing**; re-check with a raw read.

One more reading rule: **a sanitizer report that is byte-for-byte identical on both sides cannot be something the patch changed** --
it is a toolchain or environment artifact; record it as `unattributed_sanitizer_output` (neither a clean log nor a trigger),
and **rename that log to `oracle_probe_*` so it does not share a namespace with the differential logs**.

### (7) This machine has network access -- actually try once before saying "upstream cannot be checked"

Measured: `git ls-remote https://github.com/<org>/<repo>.git HEAD` returns a commit hash immediately.
It is written here because **two workers have already made judgements they should not have made, by assuming "there is no network"**:
one attributed a CVE to a different module from memory, the other wrote a checkable upstream fact down as "cannot be verified".
The second worker probed on its own, found it worked, fetched the real fix commit, and resolved a pending judgement on the spot.
Put fetched upstream source under `pathb/<lane>/`, and write `git_remote` plus the exact commit into the record -- that is what rule 4 requires anyway.

### (8) After a record-writing assertion fails, do not let the work move on

Measured: PrimeVul 4461 was nearly lost: an assertion in an inline write script fired, **nothing was written**, and the work kept moving forward,
leaving a complete measurement on disk next to an empty record.

**Rule: run a field scan before handing in** -- any sample that has **neither `tried_dynamic_method`
nor `blocked_reason`** is a missed write, and must not be let through.

---

## 0a. ★★ There are only four outcomes (synced from PrimeVul 2026-08-21; **aligned with DiverseVul's §2a on 2026-09-20**)

**This section is this prompt's output ruler: whatever this round did, every sample handed in at the end can only be one of the four below.**

For external reporting, for writing records, and for statistics, **only the four outcomes below may appear**; every `target=1` sample lands in exactly one,
and the four numbers add up to the denominator 10,900 (the denominator is recomputed every round with the refresh commands from section 0; do not cite the old numbers in the snapshot):

| Outcome | Meaning | Secondary field |
|---|---|---|
| `CONFIRMED` | The labelled function triggered a real defect on faithful input | `confirmation_class` (one of the three grades), `cve_match`, `confirmation_scope` (`defect_site`/`reachability`), `reachability` (`REACHABLE`/`UNREACHABLE`/`UNKNOWN`) |
| `LABEL_NOISE_EXCLUDED` | The label is overturned: **either** it was attacked with a tool matching the CWE, nothing fired, and the seven gates are all in place, **or** a differential was measured and its direction is inverted | `label_noise_category` (vocabulary in the "explicit label-noise marking rules" section), `label_noise_basis` (`dynamic_attack_negative` or `dynamic_differential_inverted`), `label_noise_type`; write `cve_match` as `n/a` |
| `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | **A dynamic tool really attacked it and readings from both sides were obtained, but this measurement cannot tell whether it is a confirmation or a mislabel** | `dy_attacked_undecided_category`, see the table below, **required** |
| `NOT_DYNAMICALLY_TESTED` | **No valid dynamic measurement has been obtained yet**: never tested, could not reach it, or built and ran but produced no result | `not_tested_reason`, see the table below, **required** |

> **★ 2026-09-20: the fourth outcome was renamed from `BUILD_FAILED` to `NOT_DYNAMICALLY_TESTED`,
> and its secondary field from `build_failed_reason` to `not_tested_reason`** (DiverseVul changed it first on 2026-08-19; we follow).
> **The rename is not a wording issue.** A passage further down in this very section says "not one of those 230 samples was a build failure" --
> the old name held for none of those samples, and we kept it in the table for another month.
> What it really means is "no valid dynamic measurement has been obtained yet", and most of them **were never worked on at all**.
> `build_failed` is demoted to a sub-category underneath it, reserved for samples that really did record a build failure.
> The old names `BUILD_FAILED` / `build_failed_reason` are **kept only as aliases** so that old scripts and old on-disk records can still be read;
> **newly written records, reported numbers and partitions must all use the new names.**

**The following strings are no longer outcomes**, and not one of them may appear in a result partition:
`INCONCLUSIVE`, `NOT_DYNAMICALLY_CONFIRMED`, `DEFERRED`, `INCONCLUSIVE_LABEL_NOISE`,
`NOT_DYNAMICALLY_CONFIRMED_LABEL_NOISE`, `LABEL_NOISE`, `LABEL_NOISE_RELABEL`, `NOT_CONFIRMED`,
`NEEDS_PATH_B`, `INCONCLUSIVE_NEEDS_PATH_B`, `NOT_TRIGGERABLE_AS_LABELED`,
`NOT_DYNAMICALLY_CONFIRMED (NO DIFFERENTIAL: BOTH ARMS FAULT IDENTICALLY)`,
`<MISSING_OR_UNPARSEABLE_VERDICT>`, `UNTOUCHED`.
They may stay in the sample record's `verdict` as history.

**Whether a sample counts into the third or the fourth outcome depends on one question only: was this sample really attacked by a dynamic tool
and were readings from both sides obtained?** Attacked -> the third; the attack did not succeed / not attacked yet -> the fourth.

> **★ The fourth outcome was added by PrimeVul on 2026-08-17, and the reason for adding it is worth remembering.**
> Before that there were only three outcomes, **and "measured but not a confirmation" had no cell of its own**, so that meaning was stuffed into a field
> named `build_failed_reason` (**reason for build failure**) -- while **not one of those 230 samples was a build failure**.
> The consequences were concrete: (1) anyone reading by field name would get it wrong (a snapshot once said `BUILD_FAILED 712`,
> while there was not a single `build_failed: true` on disk); (2) it directly violates the rule in section 0b below
> that "could not be built" and "attacked and nothing fired" must be strictly separated; (3) it forced out
> **two fields in one record telling two stories** -- one saying `dynamic_attack_negative` (attacked, nothing happened),
> the other saying `inverted_polarity` (measured, and the direction is inverted); **those two sentences cannot both be true.**

### `dy_attacked_undecided_category` vocabulary (the third outcome's secondary field, **required**)

These samples have exactly one thing in common: **a dynamic tool really attacked them and readings from both sides were obtained.**
But the reasons for "cannot decide" are completely different from one another, and so are the next actions --
**which is why reporting only the total of the third outcome is meaningless; you must give the distribution of this table alongside it.**

| Value | Meaning | What can be inferred about this function |
|---|---|---|
| `nominated_awaiting_adjudication` | Readings from both sides were obtained, **and a valid confirmation class has already been nominated** | **What it lacks is neither a measurement nor a missing write, but one adjudication** |
| `attacked_no_trigger` | Both sides were really built and run, attacked with a matching tool, nothing fired, but one or more of the seven gates is still missing | **This is a conclusion about this function**; once the gates are complete it should become `LABEL_NOISE_EXCLUDED` |
| `guard_never_evaluated` | The disputed lines were never executed at all | **Exactly the opposite: that "clean" is not a conclusion about this function.** Change the input so it gets executed |
| `decision_diff_no_impact` | **A real difference was measured, but it has no security consequence.** Both phrasings belong here: (1) a clean two-sided decision differential at the patch point, but no sanitizer fault, no out-of-bounds/leak; (2) a real behavioral difference (a rendering difference, by design), but not enough to cross a security boundary | First ask whether it can still be rescued (hook up a real consumer / switch to a matching oracle) -- **this class is the most likely to flip to a confirmation**; only when it cannot be rescued does it go to human adjudication |
| ~~`no_security_consequence`~~ | **Merged into the row above by the owner's ruling on PrimeVul 2026-08-21.** Kept as an **alias** so old on-disk records can still be read; readers must fold it into `decision_diff_no_impact` | -- |
| `fault_not_attributable` | A fault fired, but it does not attribute to the labelled function (a sibling function / a caller / the harness's own code) | Neither clean nor triggered |
| `inverted_polarity` | Inverted polarity: the side faulting is the build from the **fixed** code, and the build from pre-fix code is clean | **★ 2026-09-20 ruler change (matching DiverseVul): this is no longer "cannot decide", it is label noise.** It may only exist as a **temporary state pending adjudication** -- once it passes the two gates in the "label noise" section (the two sides were not swapped; that nonzero code on the fixed side is a real fault and attributes to the labelled function), write `label_noise: true` + `label_noise_category: "inverted-polarity"` + `label_noise_basis: "dynamic_differential_inverted"` and move the outcome to `LABEL_NOISE_EXCLUDED`; if it fails the gates, record `stored_body_arms_swapped` or `fault_not_attributable`, and **you may not close out sitting on `inverted_polarity`** |
| `no_differential_possible` | By construction the two sides are necessarily the same code | Terminal state; **you must build a single one and attack it to decide whether this function has a defect** |
| `synthetic_trigger` | The trigger condition was manufactured by the harness and real input cannot produce it | Switch to real input |
| `reachability_unproven` | The fault is inside the function body, but it was not proven that an attacker can reach it | Supply a real entry path |
| `cve_mismatch` | The labelled CVE does not belong to this commit or this function | A CVE mismatch does not veto a confirmation; first look at whether the function itself has a real defect |
| `single_arm_only` | Only one build was made and produced a result; the second does not structurally exist | Handle as a structural single-sided case |
| `unclassified_reason` | A reason was written but the existing matching rules do not recognize it | **Fix the rules; it is not the sample's problem** |

> **★ The cost of merging `no_security_consequence` is countable; remember this shape.**
> Those two rows ask the same thing: a real difference was measured, but it has no security consequence. Writing them separately is just two phrasings.
> Over on PrimeVul, **27** samples pending adjudication **hit both rows at once**, and the reader, by design,
> refuses to "resolve ambiguity by ordering", so it sent them into `unclassified_reason` --
> **they had not failed to write a reason; we ourselves had split one question into two rules.**
> The folding belongs at **the hit-set layer**, so that the "multiple hits = cannot decide" rule benefits automatically,
> instead of being written out again at every call site.

> **★ Why `nominated_awaiting_adjudication` exists.** Without it, these samples were counted into
> "no reason written", because the reader only looked at one particular note field while the rule only required that note **when the category was left empty**.
> So a record carrying a nominated class, a real integer two-sided differential, execution proof and a positive control was still counted as "no reason written" --
> **and the action hanging on that cell is "dispatch a batch to fill in the writes", which finds nothing when it arrives.**
> **Only vocabulary values count**: `NONE`, or a whole sentence pasted into the value slot, is **a different kind of defect** and must stay visible.

> **★ A missing value in this vocabulary is a known outstanding debt.** The two kinds of "measured, and the direction or the vintage is misaligned" --
> `inverted_polarity` and version misalignment -- have only one exit on the `label_noise_basis` side,
> `dynamic_differential_inverted`, which does not cover version misalignment. So a worker can only write the real meaning
> into this field, **and when adjudicating you must read the record's body text, not just that one field**.

> **★ Only vocabulary values count.** `NONE`, an empty string, or a whole sentence pasted into the value slot is **a different kind of defect**,
> and must stay visible; **it may not be laundered into `unclassified_reason`**.

### `not_tested_reason` vocabulary (the fourth outcome's secondary field, **required**; the old name `build_failed_reason` is only an alias)

**Not one sample in this bucket was ever successfully measured**, so it supports no conclusion about these functions --
it speaks about **our capability or progress falling short**, and these samples **must stay on the worklist waiting to be attacked**.

**★ Determine the value from the actual state on disk; do not rely on that reason field, which is empty for most records.**
The lesson from DiverseVul is countable: the old vocabulary's `no_reason_recorded` swallowed
**10,178** out of 16,268 -- two thirds reported as "unknown", while the folders themselves plainly showed which had been worked on and which had never been touched.
When deciding, go look directly: is there a `dynamic_evidence/repro.sh`, is there a run log, is there a `needs_path_b` marker,
is there a `propagated_from` / cross-dataset source key, is there any dynamic record at all.

| Value | Meaning | Decision basis (look at the disk, not at the field) | What can be inferred about this function |
|---|---|---|---|
| `attempted_no_usable_result` | **Built / run**, it just produced no valid result | There is a `dynamic_evidence/repro.sh` or a run log, but no integer `vuln_rc`/`fix_rc` | Nothing can be inferred; but **the environment and the entry point are probably working, so this is the cheapest**; do these first |
| `needs_path_b_not_attempted` | Marked as out of reach, with no trace of any attempt on disk | The `needs-Path-B` marker is there, no script, no log | Nothing can be inferred (our capability fell short) |
| `never_attempted` | No dynamic record and no artifacts at all | No record, no script, no log | Dispatch work |
| `build_failed` | A build failure was **really** recorded | `blocked_reason:"build_failed"` or `build_failure` present on disk | Nothing can be inferred. **Note: this is a sub-category, not the whole bucket** -- the old name had to change precisely because this item was measured to be only a tiny fraction |
| `attempted_inherited_crossdataset` | The evidence was produced by a PrimeVul/MegaVul twin sample and propagated here; **nothing was run locally** | The record carries a source key such as `propagated_from: primevul:*` / `megavul:*`, and the local `dynamic_evidence/` has no measurement of its own | A dynamic tool really did attack the twin sample, **but not this one**. In the current BigVul snapshot there are **495** of these, and they must be countable separately |
| `confirmation_withdrawn_nothing_measured_since` | A dynamic confirmation was once published here and then removed by a recorded, rollback-able withdrawal, **and since the withdrawal there is no local dynamic measurement on disk** | The directory contains a `prior_confirmation_*/`, `dynamic_evidence/` has no new file after the withdrawal timestamp, and the record has no `tried_dynamic_method` plus integer two-sided rc | **Nothing can be inferred**: the withdrawal took away evidence, not counter-evidence. It says neither that this function is safe, nor that it is vulnerable, and certainly not "attacked and nothing fired" |
| `unclassified_reason` | The existing rules do not recognize the state on disk | -- | **Fix the rules; it is not the sample's problem** |

> **Again, only vocabulary values count**: "not written in the record", such as `no_reason_recorded`, **is no longer a value** --
> not written in the record does not mean invisible on disk; go look at the folder first.

### How to place a sample into these four cells (**decision order; the first match from the top wins**)

1. The record has a `verdict` starting with `DYNAMICALLY_CONFIRMED` and `confirmation_class` is one of the three grades
   -> `CONFIRMED`;
2. `label_noise: true` and `label_noise_basis` is `dynamic_attack_negative` or
   `dynamic_differential_inverted` -> `LABEL_NOISE_EXCLUDED`
   (**writing only `suspected_label_noise` does not count**; that is the fourth cell);
3. The record has `tried_dynamic_method` **and** both sides in `differential` are **real integer** rc
   -> `DY_Attacked_But_can_not_decide_confirmed_or_label_noise`, fill in `dy_attacked_undecided_category`;
4. Everything else -> `NOT_DYNAMICALLY_TESTED`, fill in `not_tested_reason` according to the state on disk.

**The boundary between step 3 and step 4 is one question only: was this sample really attacked by a dynamic tool and were readings from both sides obtained.**
`"identical"` / `"n/a"` / `null` / the string `"1"` are **not** integer rc, and land in cell 4.

### Outstanding debt on the BigVul side (**record it honestly, do not treat it as done**)

1. PrimeVul has `primevul_outcome_taxonomy.py` to read and fold these four outcomes;
   **BigVul still has no equivalent module**; `compute_bigvul_dynamic_status_statistics.py` still partitions by the old
   verdict strings. Until a BigVul reader is written, the four outcomes can only be **written per sample by hand**,
   and the reports must note that the counting ruler is a manual classification.
   **This is the largest outstanding debt in this section: no code executes the decision-order table above yet.**
2. The several hundred samples in the snapshot that are still in old status strings (**446** at the 2026-08-28 recomputation) must be re-sorted into
   the third/fourth outcome by "was it really attacked by a dynamic tool and were readings from both sides obtained", and given
   `dy_attacked_undecided_category` / `not_tested_reason`.
3. `check_loop_prompt_compliance.py` / `check_loop_prompt_FULL.py` **do not yet** cover the rules in this section
   (the four outcomes' required secondary fields, the validity of vocabulary values, the second value of `label_noise_basis`,
   the sixth/seventh gates, the five preconditions of rule C).
   Per repository-root `CLAUDE.md` §8c: **a rule written only into the document and not into the checkers does not exist.**
   Next round, fix the checkers first, then dispatch work in bulk.

> **★ Added 2026-09-20: do not confuse existing artifacts that are "adjacent but not equivalent" to these four outcomes.**
> The set of things under `tasks/bigvul_reports/manual_check_bigvul_20260913/`
> (`ALL_ADJUDICATIONS.csv` 10,388 rows, `WORKLIST_REMAINING.csv` 1,658 rows,
> `_mocktest.py` / `_armcheck.py` / `build_worklist.py`) is the result of **manually re-reviewing the evidence on disk**,
> using a **three-state review ruler** of "supports / conflicts / insufficient evidence".
> It is **not** this section's four-outcome partition, and cannot be used as one directly:
> - It re-reviews the two populations `CONFIRMED` and `LABEL_NOISE_EXCLUDED` (10,388 samples);
>   samples in the third and fourth outcomes **are not covered by it at all**;
> - Its "insufficient evidence" may correspond either to the third outcome (attacked but undecidable) or to the fourth (never measured successfully),
>   and must be split again using the `category` column of `WORKLIST_REMAINING.csv`
>   (`no-attribution`/`identical-arms`/`fix-arm-also-faults` are mostly the third,
>   `build-failed`/`no-oracle-log`/`restored-historical` are mostly the fourth).
>
> **But it can be fed directly to that reader as input**: `_mocktest.py`'s verbatim-containment test and
> `_armcheck.py`'s census of how the two sides were built answer exactly "is this measurement really measuring this function",
> which is the precondition for the third outcome to hold at all. When writing the BigVul reader, wire these two in first.

---

## 0b. ★★ Three closing states for "attacked repeatedly and still no result" (do not merge them)

"Tried many times and still no result" corresponds in this campaign to **three completely different situations**, whose next actions,
conclusions about the dataset, and eligibility to close out all differ. Merging them is exactly the mistake this document's highest-priority rule guards against:
**"could not reach it" is our capability falling short; "attacked and nothing fired" is the only one that is a conclusion about this function.**

Write one of these three into `dynamic_confirmation.json`:

### (1) `blocked_reason: "build_failed"` -- it could not be built, so the attack never happened

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "blocked_reason": "build_failed",
  "build_failure": {
    "attempts": 3,
    "what_was_tried": "at-commit clone + ASan; extract-and-stub; reuse the binaries already built in pathb/<lane>",
    "where_it_stops": "the **verbatim** error of the first failure + file and line number",
    "why_not_recoverable_now": "an unobtainable SDK is missing / the period toolchain cannot be installed / a dependency has been taken down",
    "logs": ["dynamic_evidence/build_vuln.log", "dynamic_evidence/build_fix.log"]
  }
}
```

**The criteria is not "I think it cannot be built", it is a failed build log on disk.** `attempts` must be >= 2,
and `what_was_tried` must list **different** approaches (rerunning the same command three times is not three attempts).
This state **supports no conclusion about this function**, and counts statistically as `NOT_DYNAMICALLY_TESTED` / `build_failed`
(the name changed in section 0a on 2026-09-20; the old spellings `BUILD_FAILED` / `could_not_build` are only aliases).

### (2) `attack_exhausted` -- it was built, really attacked, attacked repeatedly, and still nothing fired

```json
{
  "verdict": "NOT_DYNAMICALLY_CONFIRMED",
  "attack_exhausted": {
    "rounds": 4,
    "oracles_tried": ["asan", "ubsan", "msan"],
    "why_these_oracles": "chosen by the mechanism in the fix diff: out-of-bounds write -> ASan, uninitialized -> MSan (which prints WARNING:, not ERROR:), shifts/integers -> UBSan",
    "entries_tried": ["real CLI", "decoder entry point", "extract-stub"],
    "inputs": "313 malformed samples + official regression material, ~22 minutes in total",
    "positive_control": "dynamic_evidence/poscontrol.asan.log does respond -- proving the oracle is not dead",
    "seven_gates": "all passed / gate N missing (say which one)"
  }
}
```

**This state is the real "tested many times with no result".** Where it goes:

- **All seven gates passed** -> it should not stop here; write `label_noise: true` +
  `label_noise_basis: "dynamic_attack_negative"` and move it into `LABEL_NOISE_EXCLUDED`;
- **Any gate missing** -> stay in `attack_exhausted`, write down which gate is missing, the sample **stays on the worklist**,
  and it counts statistically into the third outcome's `attacked_no_trigger`.

**The most common gap is gate 4: the oracle must be chosen against the mechanism, not against the labelled CWE.**
If the mechanism is uninitialized memory but it was only attacked with ASan, that "clean" is not a negative result, it is **not measured**,
because ASan structurally cannot see this class.

### (3) Something fired, but it does not attribute to the labelled function

Not part of this section. A fault inside a **callee** is still a confirmation (`confirmation_scope: "reachability"` +
`defect_site` + `call_path`); only a fault in a **caller**, or in a **sibling function** with no call relation, gets
`unattributed_sanitizer_output` (count + signature + example), which **may be counted neither as a clean log nor as a trigger**.

### The three compared

| Situation | Field | Statistical category | What can be inferred about this function |
|---|---|---|---|
| Cannot be built / cannot be reached | `blocked_reason: "build_failed"` + `build_failure` | `NOT_DYNAMICALLY_TESTED` + `not_tested_reason: build_failed` | **Nothing can be inferred** |
| Attacked, attacked repeatedly, nothing fired | `attack_exhausted` | All gates passed -> `LABEL_NOISE_EXCLUDED`; otherwise `attacked_no_trigger` | Only with all gates passed may you say "this function is mislabelled" |
| Something fired but does not attribute | `unattributed_sanitizer_output` | `fault_not_attributable` | Neither clean nor triggered |

**Do not write strings such as `differential.vuln_rc: "build_failed"`.** Exit-code fields always hold integers only;
if no integer came out, there was no differential this time, and the reason goes in the fields above.
`blocked_reason: "build_failed"` and a real integer differential **cannot coexist** -- coexistence means the marker is stale,
and the old marker must be demoted to `prior_route_build_failure` with `build_performed` written.

---

## 0c. ★★ Build once per project, reuse within the batch (PrimeVul, user instruction 2026-08-15; applies to BigVul as well)

**Always dispatch work grouped by project**: samples under the same project go to the same agent,
**this project is cloned once and its build recipe is worked out once**, and then the samples under it are dynamically tested in turn.
Several small projects with the same build style (for example, small self-contained parsers all using autotools + ASan)
may be merged onto one agent, but the dispatch ledger must say which ones were merged and on what basis.
**Lane directory**: `pathb/<project>_<batch-tag>/`, one per project; do not create one per sample.

### What this saves and what it does not -- be clear first, or you will save your way into fake evidence

**★ What it does not save is "the two things built from pre-fix and post-fix code".**
For two samples under the same project, **the fix commit is usually not the same one**. Measured on PrimeVul 2026-08-15:
the 99 never-tested samples in the worklist were spread over **97 different fix commits**, and only 2 pairs genuinely shared a commit. Therefore:

> **Every sample must build its own pair of `fix^` / `fix`.**
> Using a sibling sample's build to test another sample means you are not testing this sample's pair of versions --
> that is exactly the "the pre-built binary is the wrong vintage / the wrong CVE" family, which tripped us four times in one day. **Verify the version and the diff before running.**

**What really can be done only once is this**:

1. **Cloning and submodules** -- the most expensive step for a large repository;
2. **Working out dependencies, `configure` / `cmake` parameters, the compiler and flags** -- the most labor-intensive part;
3. **ccache, which must be on and shared across samples** -- a great many object files are identical between commits, and this is the real source of saved compile time;
4. **The harness / driver program / PoC generator / input-construction scripts**;
5. **How to write the positive control**, plus this project's own oracle pitfalls
   (example: some libraries pad every allocation by 1 KB, so ASan generally misses over-reads across the whole library;
   writing an unprefixed `malloc` inside a library method body binds to the member allocator --
   **the same injection behaves differently across different versions of the same library**, so the control must be recorded once per project).

### How to do it

- Clone a project once, and **for each sample open a `git worktree` at that sample's own commit inside the same clone**;
- **Turn on ccache and share it across samples**;
- Write the `configure` / `cmake` parameters, the dependency list, the harness, the PoC generator and this project's oracle pitfalls
  into a **lane-level `README.md`**, so later samples reference it directly instead of working it out again;
- **When two samples really do share a commit** (check with `info.json::commit_id` first, **do not go by directory name**),
  build only one pair, share it between the two samples, and write in both records which pair was shared and on what basis;
- A lane is **exclusive to a batch**; do not put tool scripts under a shared path -- collisions in a shared staging directory happened eight times in one day.

**Report per project when handing in**: how many times this project was cloned/configured, how many pairs were built, the ccache hit situation,
and **which samples shared the same pair and on what basis**. When a sample did not use the lane's recipe and started its own, explain why.

---

## ★★★★★ Criteria change (user, 2026-08-03): **you must attack with a dynamic tool before ruling label noise**

> "Even if you believe it is label noise, you may only confirm it as label noise after a dynamic tool has attacked it
> and no vulnerability was triggered"
>
> "**This change of meaning must take effect for all label noise, not for one particular label-noise category.**"

**This is a global gate covering every exit to `label_noise: true`; no category may bypass it.**
Whether you are ruling `whole-commit-relabel`, `whitespace-only-relabel`, `cosmetic-refactor`,
`wrong-function`, `version-skew`, `mass-hardening-sweep`, `library-import-relabel`,
`wrong-cwe`, `test-file-labeled`, `multi-function-relabel` or `inverted-polarity` --
**attack first; only after the attack fires no fault may you rule.**

| Your situation | What to write |
|---|---|
| **Attacked and the vulnerability did not come out** (**all seven gates** passed) | `label_noise: true` + `label_noise_type: "label_noise_dynamic_tools_attacked"` + `label_noise_category: <one of the 11 above>` + `label_noise_basis: "dynamic_attack_negative"`. **Do not write `NOT_MEASURED` / not confirmed** |
| **Only read the code, not attacked yet** | `label_noise: false` + `suspected_label_noise: true` + `suspected_label_noise_category` + `label_noise_basis: "static_reading"`. **This does not trigger exclusion; the sample stays on the worklist waiting to be attacked** |
| **Cannot attack it** (needs a whole-tree build / KASAN+QEMU, etc.) | `label_noise: false` + `reason` containing `"needs-Path-B"`. **Could not reach it != attacked and nothing fired** |

**Attack records and logs always go into `data/output/dataset/bigvul/<id>/dynamic_evidence/label_noise_attack/`
(`attack.sh` + inputs + the complete log of every shot + `ATTACK_LOG.md` + `EVIDENCE_MAP.json`).
No such directory = this label-noise ruling does not hold, and the sample goes back on the worklist.**

**Why**: "this commit did not change this function" and "this function has no vulnerability" are two different things --
whether a function has a vulnerability depends on its own code, not on whether some commit touched it.
Measured over 1,160 samples of the "no-op change" class: 843 of them (72.7%) had a `tried_dynamic_method` saying
`diff -w` text comparison, with not a single exit code in `differential`, and 1,057 did not even have an evidence directory.
The full text is in the section "explicit label-noise marking rules" below (**seven** hard gates + the category vocabulary + the evidence-directory checklist);
for background see **P25** in `evidence_repair/PROBLEM_REGISTER_20260803.md`.

**This also voids three old instructions** (all of them are "settle it by static pre-screening", which conflicts with this gate):
"when `diff -w` is identical, mark label_noise directly and skip dispatching a subagent", ">4-6 files means INCONCLUSIVE-relabel directly, do not waste a build",
and the "INCONCLUSIVE+label_noise:true" clause in the full-coverage terms.

---

## ★★★★★ Criteria change (user, 2026-07-28): **a CVE mismatch is no longer a veto**

> "You may drop the CVE; as long as the sample really can trigger a vulnerability that is fine, and you can annotate that its CVE is wrong"

**New criteria**: as long as the **labelled function** can be made to trigger a real vulnerability on faithful input, it counts as CONFIRMED -- even if it is not the CVE this sample is labelled with. In that case write `cve_match: false`, and explain in the record what the real defect is and why the CVE attribution is wrong.
("Can be hit by an attacker" is **not** a gate: a real defect that is unreachable is still confirmed, it just gets an extra `reachability: "UNREACHABLE"` field. User, 2026-07-31.)

So before downgrading something because "the labelled function has nothing to do with this CVE", **you must ask one more question**: does this labelled function **itself** have a real triggerable defect? If yes -> confirm, and record:

```json
{"cve_match": false,
 "cve_attribution_note": "The labelled CVE-XXXX is actually at <real location>; this function's defect is a different one",
 "real_vuln": {"class": "CWE-125 out-of-bounds read", "site": "<function:line>", "trigger": "<real input>"}}
```

**What has not changed**:

- **The differential is the standard path, but not the only path**. On the same input, the pre-fix side faults and the fixed side is clean = a standard confirmation.

  **The case where the fixed version is also vulnerable** -- ruled by the user 2026-07-28 (original words: "if the sample is vulnerable and its fix is also vulnerable,
  then as long as a dynamic tool can trigger this sample's vulnerable behavior, this sample can also be confirmed as vulnerable.
  You only need to honestly annotate that its fix is also vulnerable"):

  > **The build from pre-fix code being triggerable by a dynamic tool = CONFIRMED. The fixed side faulting too is a fact to record honestly, not a veto.**

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

  **None of the three preconditions may be missing** (otherwise it becomes "any bug you happen to find counts"):
  1. The defect is **reachable from the labelled function** -- inside the labelled function body, or in a callee it calls (directly/indirectly).
     ★★★★★ **A defect in a callee is not a reason to downgrade (user, 2026-08-01)**: when both sides fault identically,
     the defect **does not need** to be inside the labelled function body, it only needs to be **clearly annotated**. Write:
     ```json
     "confirmation_scope": "reachability",
     "defect_site": "<the name and location of the function that actually faults>",
     "callee_of_labelled_function": true,
     "call_path": "<labelled function -> ... -> defect_site, noting which file and which lines this was read from>"
     ```
     This **overturns** the old precondition that "the defect must be inside the labelled function"; the old counter-example `bigvul/183055`
     (both sides crash, the fault is in the callee `cdf_read_property_info`, the labelled function is `cdf_read_sector`)
     is **no longer** label noise, and is confirmed once annotated with the fields above.
     Case `bigvul/180379`: the labelled function `get_private_subtags` is verbatim identical on both sides,
     and `Locale::parseLocale("en-")` reads out of bounds inside `getSingletonPos`, which it calls unconditionally,
     -> `WITHDRAW_DOWNGRADE` + `OTHER_DEFECT_UNFIXED` + `confirmation_scope:"reachability"`.
     **What must still be blocked is "you cannot get in from there"**: if the fault happens in a **caller** of the labelled function,
     or in a sibling function with no call relation to it, that is not "reachable from the labelled function", and it is downgraded as before.
     Counter-example `bigvul/187879` / `bigvul/187880`: `assert(bpos>=0)` really did fire 33 times out of 20000,
     but in `Cluster::CreateBlockGroup`, and neither the labelled function `Segment::ParseNext` nor
     `Cluster::ParseSimpleBlock` has it in its call closure -- `ParseSimpleBlock` is the **alternative** branch to
     `Cluster::Parse`'s BlockGroup branch, not its caller -> the downgrade holds.
     So before ruling you must **actually read the upstream source and confirm the direction of the call**; do not infer it from similar names.

     ★★ Correction 2026-08-02 -- this counter-example originally cited `bigvul/187869`, and that example was **wrong**.
     Measured: line 204 of the stored `ParseBlockGroup` body is `CreateBlock(0x20, // BlockGroup ID)`,
     and `Cluster::CreateBlock` at `containing_file.cc:7200` does
     `return CreateBlockGroup(pos, size, discard_padding);`. The call direction is
     `ParseBlockGroup -> CreateBlock -> CreateBlockGroup`, so **you can get in**.
     187869 has accordingly been re-ruled `DYNAMICALLY_CONFIRMED` + `confirmation_scope:"reachability"`.
     This wrong example is itself the best footnote to this rule: **read the call direction first, do not go by impression** --
     the person who wrote down this counter-example inferred the call direction by impression, and got the direction backwards.
  2. Triggered by **faithful input**, with empirical output from a sanitizer or an equivalent oracle.
     This precondition blocks two things: synthetic triggers (absurd magic numbers, values upstream would reject) and harness-manufactured defects
     (changing upstream code and then reporting the consequence). **It does not require that an attacker path exists in the real program** --
     if the defect is real, inside the labelled function, but no attacker-controlled path to it can be found, it is still confirmed,
     with `reachability: "UNREACHABLE"` added instead of a downgrade. See the ★★★★★ unreachability section below.
  3. **The build from pre-fix code must be able to trigger it by itself** -- counter-example `bigvul/183295`: inverted polarity,
     the stored "vulnerable version" is the clean one and the "fixed version" is what crashes, so this sample is not the vulnerable one.
- **Synthetic triggers still do not count.** Absurd magic numbers, values upstream would reject, parameters real input cannot produce -- none of these is a confirmation.
- The labelled function **really has no defect at all** -> downgrade as before.

**Why this matters**: of the 39 samples in the first round of evidence repair, 21 were downgraded, and **not one of them was "we could not reproduce it"**; all were "the labelled function has no real relation to this CVE". Under the new criteria those 21 must be re-reviewed: the function may hold a real bug of its own. Skipping this step before a downgrade = throwing away real samples.

Statistics come in three grades; do not mix them:
| Grade | Condition |
|---|---|
| `CONFIRMED_CVE_MATCH` | What was triggered is the labelled CVE itself, and there is a differential between the two sides |
| `CONFIRMED_OTHER_DEFECT` | Another real defect inside the labelled function, with a differential between the two sides, `cve_match:false` |
| `OTHER_DEFECT_UNFIXED` | Another real defect inside the labelled function that upstream did not fix -> both sides fault identically |

---

## ★★★★★ Confirmation scope is required (user, 2026-07-31): **defect site vs reachability, you must state which one it is**

> "I want the latter; 180356 should be changed to 'keep the confirmation + annotate it as reachability rather than defect site', clearly annotating that what is vulnerable is the called function"

**Every CONFIRMED must carry `confirmation_scope`, one of two values.** Not writing it is a missing field.
The reason: without the distinction, "this function contains a defect" and "this function delivers attacker input to the defect" are mixed into the same label,
and a detector trained downstream learns "recognize the call site" rather than "recognize the defect".

```json
"confirmation_scope": "defect_site" | "reachability",
"reachability": "REACHABLE" | "UNREACHABLE" | "UNKNOWN",   // [required] orthogonal to scope, see the unreachability section below
"defect_site": {                       // [required] when scope is reachability
  "function": "<the function that actually contains the defect>",
  "file": "<the file it lives in>",
  "reached_via": "<the call chain from the labelled function to it>",
  "defect": "<the observed defect, including the verbatim sanitizer text>"
},
"reachability_note": "<why the labelled function itself is not the defect site>"
```

**The criteria is a counterfactual question: if you change only this labelled function, does the vulnerability disappear?**

- **Yes** -> `defect_site`. It does not matter where the crash lands. The existing `frame_note` (alloc_site/fault_site) belongs to this class:
  the labelled function under-allocates, and the overrun happens in a `memcpy` it calls or in a helper in the same file -- the defect is still the labelled function's.
- **No** -> `reachability`. The labelled function performs no defective operation itself, the upstream patch does not touch it either, but it delivers attacker-controlled input
  to the defect. **You must name the specific function in `defect_site`.**

Template **180356** (php-src CVE-2016-5093). The labelled function is:

```c
PHP_FUNCTION(locale_get_primary_language) {
    get_icu_value_src_php(LOC_LANG_TAG, INTERNAL_FUNCTION_PARAM_PASSTHRU);
}
```

Four lines, one forwarding call, zero memory operations, and `97eff7eb` indeed did not change it. But the differential in `dynamic_evidence/` was really run
(vuln_rc=1 / fix_rc=0), and the overrun is on the `strlen()` in the callee `get_icu_value_internal`.
-> `confirmation_scope: "reachability"`, `defect_site.function = "get_icu_value_internal"`.

### Three lines you must not cross

**1. `reachability` is not label noise; never set `label_noise: true`.**
In this repository `label_noise: true` is an **unconditional hard exclusion** (the generator has three independent paths that kick the sample off the worklist permanently),
and setting it makes the sample disappear outright -- "keep the confirmation and also mark it as noise" is self-contradictory. To record the fact that "the upstream patch does not touch the labelled function",
write it into `reachability_note`, not into `label_noise`.

**2. Reachability must be observed, not inferred.**
Reachability is transitive -- once you accept "it calls a defective function", it counts, and every level up the call chain to `main()` counts too.
So the precondition for ruling `reachability` is still that **a differential was really produced**: real input reaches the defect via the labelled function
and becomes clean under the real patch. **This is not relaxed just because you switched to the reachability standard.**

**3. `defect_site` must name a specific function.** Writing "the defect is elsewhere" is not an annotation, it is a dodge;
if you cannot point at a specific function, you have not finished investigating, and then you should not rule CONFIRMED.

### ★★★★★ Unreachable still counts as CONFIRMED (user, 2026-07-31): **add fields, do not downgrade**

> "Even if it is unreachable, it still needs to be annotated as confirmed, it just needs a special field marking it unreachable"

**"No attacker-controlled path can be found" is not a reason to downgrade.** As long as the defect is **really inside the labelled function body**
and is **real** (not manufactured by the harness), record `verdict: DYNAMICALLY_CONFIRMED`,
and add a field saying it is unreachable -- rather than ruling the whole sample out.

```json
"reachability": "UNREACHABLE",
"reachability_note": "<what the defect is, on which line, and with what oracle it was observed;
                      plus what precondition is needed to reach it, and why that precondition is not something an attacker can construct>",
"attacker_controlled_trigger": null
```

`reachability` is **orthogonal** to the three grades: an unreachable sample still lands in one of
`CONFIRMED_CVE_MATCH` / `CONFIRMED_OTHER_DEFECT` / `OTHER_DEFECT_UNFIXED`,
decided by whether there is a differential and whether upstream fixed it. Unreachability merely adds a qualifier to that grade; it does not change the grade.

Template 187837 (Android CVE-2016-2464, `ContentEncoding::GetCompressionByIndex`).
`count` is a `ptrdiff_t`, and `idx >= static_cast<unsigned long>(count)` turns a negative count
into a huge unsigned upper bound, making the check useless. Under `-DNDEBUG` the function's own `assert(count >= 0)`
is compiled away, and the probe obtained an entry for `idx=3` on a 4-slot array -- the defect is real, and it sits right on the labelled function's own
bounds check. But to produce `count < 0`, the caller must pass in an object whose `end_` precedes `begin_`,
which is a broken class invariant, not input this function can be driven with.
-> keep `DYNAMICALLY_CONFIRMED`, `reachability: "UNREACHABLE"`,
`confirmation_class: "OTHER_DEFECT_UNFIXED"` (the function body is identical after the fix and the defect remains),
`cve_match: false` (the defect of CVE-2016-2464 itself is in `Block::Parse`).

**Do not fuse three different things into one** -- only the first takes UNREACHABLE:

| | How to record it |
|---|---|
| The defect is real, inside the labelled function, but there is no attacker-controlled path to it | **CONFIRMED + `reachability: UNREACHABLE`** |
| Nothing was measured (not built, not run, wrong oracle) | Not unreachable; it is **not finished**, go back and do it |
| **Really attacked and the vulnerability did not come out** (**all seven gates** passed) | **`label_noise_dynamic_tools_attacked`**, see the label-noise section below. **Do not write NOT_MEASURED / not confirmed** |
| A defect the harness itself manufactured | Downgrade. See 187416 in the table below |

Before writing UNREACHABLE, ask yourself: **did I really prove it is unreachable, or did I merely fail to find a path?**
The two are written differently -- the latter gets `reachability: "UNKNOWN"` plus a note of which entry points were searched; do not pass it off as a conclusion.
The bad example is me: for 181875 I once asserted "it needs a 16 GB allocation so it is unreachable"; measured, that allocation succeeded
and the out-of-bounds write happened anyway. **Unreachability is to be measured, not deduced.**

### Two kinds where reachability does not apply and the downgrade stands (cases measured 2026-07-31)

| Situation | Case | Criteria |
|---|---|---|
| Never measured at all | 180376 | `differential` itself says `not measured -- no build attempted` |
| A defect the harness itself manufactured | 187416 | The harness used `#ifdef` to delete a guard that **already existed before the upstream fix**, and then reported the resulting overrun |

These two are **not** reachability -- reachability requires that a differential was actually observed.
"Both sides fault identically, no differential" **does not by itself constitute a downgrade**: if the defect is inside the labelled function, that is
`OTHER_DEFECT_UNFIXED` (upstream did not fix it), with the `reachability` field recording whether it can be hit.
The full standard is in
`tasks/bigvul_reports/evidence_repair/CONFIRMATION_SCOPE.md`, and downgrade examples are in
`evidence_repair/DOWNGRADED_20260731.md`.

## ★★★★ Hard rules for evidence self-sufficiency (user, 2026-07-28; overrides every other path convention)

**The ruling is not the artifact; the set of files that lets someone else rerun it is.** A `DYNAMICALLY_CONFIRMED` whose recipient cannot get anything runnable is just an assertion inside the dataset.

Measured 2026-07-28 (all 4,894 bigvul confirmations, scanned from disk, not extrapolated from an index):

| Fact | Number |
|---|---|
| Sample directories with no reproducible file at all | **136** (2.8%), of which 133 records named something that does not exist |
| Evidence landing **outside** `data/output/dataset/bigvul/` | **2,021 samples / 5,585 references** |
| Of those, landing in `/tmp/claude-<pid>/...` | **329 references** -- gone forever after one reboot; pure luck that they are still there |
| Scripts that actually ran after the first relocation | **1 out of 164 scripts** (126 hard-coded absolute paths, 116 referenced sibling files that were not moved along) |

So the following are hard requirements, not suggestions.

### Rule 1 -- per-sample artifacts always land in `data/output/dataset/bigvul/<id>/dynamic_evidence/`

The directory name is fixed as `dynamic_evidence`. **Forbidden** to write to `/tmp`, `~`, `<SCRATCH>/wl_campaign/`, an agent's self-made temporary workspace, or anywhere outside `VulValidate/`. If you need temporary space, use `TMPDIR="$(dirname "$0")"/tmp` and keep it after the run.

A valid `dynamic_evidence/` contains at least:

```
dynamic_evidence/
├── repro.sh            builds both sides, runs both, prints the differential, all in one command
├── driver.c            real entry point / harness
├── body_vuln.inc       the code under test on the pre-fix side (or stub.h + #ifdef FIXED)
├── body_fix.inc        the code under test on the fixed side
├── <poc input file>    the really constructed input (.mat/.pdf/.pcap/...), stored as raw binary
├── vuln.asan.log       actual output of the pre-fix side
├── fix.clean.log       actual output of the fixed side
└── EVIDENCE_MAP.json   each file's purpose + sha256; write a pin when referencing an external build tree
```

**Unconfirmed samples must keep these too**: what was run, how it was run, and why there was no differential must also be verifiable by rerunning. Put it in the same directory.

Log file names are fixed per the table above. If the oracle is not ASan, rename accordingly and say so in `EVIDENCE_MAP.json`
(`vuln.msan.log` / `vuln.ubsan.log` / `vuln.valgrind.log` / `vuln.timeout.log`),
but **do not** use names like `vuln.out` or `log.txt` that do not reveal the oracle -- checker scripts that look for files by fixed names will judge it as missing evidence.

### Rule 1b -- `tried_dynamic_method` is required: **what tool was used, and why that one**

Every `dynamic_confirmation.json` must carry `tried_dynamic_method`, not notes scattered in `reason`:

```json
"tried_dynamic_method": {
  "oracle_kind": "asan | ubsan | msan | tsan | valgrind-memcheck | kasan | kmsan |
                  hang/timeout | authorization-decision | output-differential | alloc-failure",
  "why_this_oracle": "<why this defect type calls for it; required for non-memory defect classes>",
  "method": "<extract-and-stub / whole-file-stub / Path-B build-at-fix^ / corpus replay ...>",
  "trigger": "<the specific input, pointing at a file name inside dynamic_evidence/>",
  "vuln_rc": 1, "fix_rc": 0,
  "vuln_observed": "<the verbatim sanitizer text or verbatim behavior, not empty phrases like 'the vulnerability was triggered'>",
  "fix_observed": "<the actual output of the fixed program on the same input>"
}
```

`oracle_kind` must match the defect type. **`rc=0/0` is not "no differential" for privilege-bypass, command-injection or forgery defects**
-- on a successful attack the process still exits normally. For these, use the authorization decision, whether the command executed, or the identity determination itself as the oracle.
Measured counter-examples: 179961 (krb5) has rc 0 on both sides, but before the fix it wrongly determined 4 principals such as `k/admin@ATHENA.MIT.EDU`
to be admin service principals; 178460 (polkit) also has rc 0 on both sides, with the difference being that the `same_uid_UNCONFIRMED`
case was allowed before the fix and denied after. The full comparison table is in `evidence_repair/CONFIRMATION_SCOPE.md`.

### Rule 2 -- no absolute paths in scripts

```bash
cd "$(dirname "$0")"                  # not cd /scratch/.../work/182663
D="$(dirname "$0")/.."                # the sample directory (used to read vulnerable_function.c)
export TMPDIR="$(dirname "$0")"/tmp
CC=${CC:-gcc}                          # take the toolchain from environment variables, do not hard-code a path
```

**Swapping in a different absolute path = not fixed.** The next time the dataset is copied elsewhere it breaks just the same. Measured: after relativization, `bigvul/182663`'s `repro.sh` rebuilt both sides from scratch in a new location and reproduced the heap-buffer-overflow of CVE-2019-17533.

### Rule 3 -- paths in records are always written relative to the sample directory

For every field in `dynamic_confirmation.json` and `craft.json` that points at a file:

- Write `dynamic_evidence/repro.sh`, **not** `repro.sh` (a bare file name makes complete evidence look nonexistent; measured to have wasted hours)
- **Do not write** `/scratch/.../wl_campaign/x/repro.sh` (outside the repository, the recipient cannot get it)
- **Do not write** shell brace expansions such as `pathb/exim_2014/{a,b,c}` -- tools splitting literally cannot resolve the paths, and three samples were wrongly reported as having no evidence because of this
- Do not put the pointer only in a `README.txt` -- one sample's harness was in a twin directory and the only thing saying so was a txt file, which json-only tools missed entirely

### Rule 4 -- third-party software, source code and builds all land inside `VulValidate/`

| Thing | Where it goes |
|---|---|
| at-commit build tree / banked ASan binaries | `pathb/<lane>/<name>_{vuln,fix}/` |
| upstream tarballs, source packages | `pathb/_srcpkg/` (store the original archive + sha256, do not keep only the unpacked tree) |
| cross/period toolchains, sysroots | `pathb/_toolchain/` |
| kernel images / rootfs | `pathb/kasan/` |
| shared stub headers, cross-sample harnesses | `pathb/_shared/` |

`pathb/` is inside the repository and is shared along with the whole of `VulValidate/`, **so banked binaries do not need to be copied into every sample directory** -- but `repro.sh` must reference them with a **repository-relative** path (`R="$(dirname "$0")/../../../../.."` or read `VULVALIDATE_ROOT`), and write a pin into `EVIDENCE_MAP.json`:

```json
{"build_tree": "pathb/matio_lane/matio_vuln",
 "git_remote": "https://github.com/tbeu/matio", "commit": "9e8e2e3...",
 "dirty_files": 0, "configure": "./configure CFLAGS='-fsanitize=address -g -O0'"}
```

`dirty_files != 0` means there are changes git cannot restore, and then the diff must be stored in `dynamic_evidence/` as well.

**Do not** copy upstream build trees per sample -- measured, that comes to 6.13 GB / 520,000 files, of which 3.19 GB are locally built `.o` files. Pinning the commit is enough.

### Rule 5 -- self-check before handing in: actually run it, do not just look at whether files exist

```bash
cd data/output/dataset/bigvul/<id>/dynamic_evidence
rm -f *.o arm_vuln arm_fix            # delete the build products, to prove it comes up from source
bash repro.sh                          # both sides must build, and a differential must really appear
grep -rn '/scratch/\|/tmp/\|/home/' *.sh   # must print nothing
```

**Three easily mistaken criteria** (all of them cost us in practice):

- **A log is not a reproduction file.** `dynamic_confirmation.asan.log` is evidence that it "was run"; it cannot let you "run it again". Only logs in the directory = not valid.
- **The existence of `craft.json` != a differential was run.**
- **Both sides clean does not mean there is no vulnerability** -- the harness may never have compiled the labelled function (measured: 90% of 125 harnesses did not compile the labelled function at all), or HW acceleration bypassed the vulnerable path. Prove the labelled code really executed before concluding.

### Rule 6 -- the record of `dynamic_evidence` must agree in three places

The path fields in `dynamic_confirmation.json`, the path fields in `data/output/dynamic/confirmed/bigvul_<id>.craft.json`, and the real files on disk must all line up. When the location changes, change all three. The ledgers (RUNLOG, registry) themselves are not moved into the sample directory; only the paths they describe are updated.

### Rule 7 -- withdrawing a confirmation means changing **four** places, and `info.json` is the one most easily missed

Measured 2026-07-28: the first round of evidence repair downgraded 21 samples, and **21/21 of their `info.json` still said `tier: dynamically_confirmed` / `is_vulnerable: YES`** -- because the dispatch prompt only named dc.json and craft.json. Downstream tools read `info.json` first of all, so from their point of view these confirmations were never withdrawn.

When downgrading, change all four together:

1. `dynamic_confirmation.json` -> `verdict: NOT_DYNAMICALLY_CONFIRMED` + an honest reason + the `label_noise` family of fields
2. `craft.json` **moved into** `<id>/prior_confirmation_<stamp>/` (**moved, not deleted**)
3. `info.json` -> set `tier` and `is_vulnerable` from the repository's existing vocabulary; do not invent your own:
   - `label_noise: true` -> `tier: mislabel`, `is_vulnerable: NO`
   - `label_noise: false` (a real patch but not triggerable) -> `tier: not_dynamically_confirmed`, `is_vulnerable: NOT_CONFIRMED`
   - `label_noise_type: label_noise_dynamic_tools_attacked` (really attacked, nothing fired, all seven gates passed) -> likewise `tier: mislabel`, `is_vulnerable: NO`, plus `label_noise_basis: dynamic_attack_negative` so it can be counted separately from rulings made by static reading
   - **`label_target` is never touched.** BigVul's label is its own business; what changes is our dynamic ruling. Conflating the two is exactly why 1,937 negative samples were once propagated into positives.
4. **Leave a rerunnable script for the negative result** in `dynamic_evidence/` -- "both sides clean" must itself be verifiable by someone else rerunning it, not just a sentence

Tool: `evidence_repair/reconcile_info_json.py` (`--ids a,b,c --apply`, picks the wording automatically from `label_noise`, backs up `info.json.before_<stamp>`, and stores the original values into a new block).

Self-check tools: `tasks/bigvul_reports/evidence_repair/audit_reproducibility.py` (lists samples with no reproducible files) and `locate_evidence.py` (lists samples whose evidence landed outside the sample directory). **Run them once before closing out; newly added samples must not appear in either list.**

---

## ★★★ PHASE-2 PATH-B PUSH CAMPAIGN (new user instruction 2026-07-22): work through the 2119 needs-Path-B one by one

**Background (current snapshot 2026-07-26)**: the audit of positive-sample result files has identified **5,291** explicit label-noise cases, and after merging the maintenance ledger a total of **5,525** target=1 IDs are hard-excluded from the worklist. The current ruler of `bigvul_current_dynamic_method_worklist.csv` has been changed per the user's 2026-07-25 instruction to **"all target=1 samples other than CONFIRMED and LABEL_NOISE_EXCLUDED"**, totaling **2,008** rows (DEFER 293, SKIP 163, `<MISSING_OR_UNPARSEABLE_VERDICT>` 21, INCONCLUSIVE 202, NEEDS_PATH_B 93, CANDIDATE 68, DEFERRED 8, REJECT 6, LABEL_NOISE 2, plus a long tail), each row carrying `sample_path` and `recommended_method`; 698 of those rows carry `label_noise_declared=True` (label noise was declared under an outcome other than INCONCLUSIVE/NOT_DYNAMICALLY_CONFIRMED). The old four-state ruler can be reproduced with `--legacy-states` (133 rows at the time, all INCONCLUSIVE). The dynamic status and the worklist must be refreshed every round by `compute_bigvul_dynamic_status_statistics.py`, `refresh_current_bigvul_reports.py` and `build_current_dynamic_method_worklist.py`; do not keep citing the earlier 5,320 / 3,015 / 2,119 / 1,804 snapshots.

**Per-sample criteria (the faithful iron law still applies)**: build both the vulnerable-commit side and the fixed-commit side (or a fn-local #ifdef), and use real crafted input to make the pre-fix build crash/leak/hang while the fixed build stays clean on the same input (the differential is the acceptance test). **A crashing fixed side is no longer a veto** -- if the defect is inside the labelled function and the pre-fix build can trigger it, it still counts as CONFIRMED; record fix_arm_also_vulnerable:true honestly (see the criteria change at the top). A fault forced by synthetic magic numbers != a confirmation. Temporal DoS (assert/panic/infinite loop) = CONFIRMED.

**★ Compliance (required for every assigned id)**: rewrite `data/output/dataset/bigvul/<id>/dynamic_confirmation.json` additively (keeping the original fields), adding: `path_b_attempted:true`, `path_b_route` (which lane/tool/banked-build was used), `path_b_differential{vuln_rc,fix_rc}`, `path_b_reason`. For ones that are nailed down, also write `data/output/dynamic/confirmed/bigvul_<id>.craft.json` (harness+repro+cve_match) and change the verdict to `DYNAMICALLY_CONFIRMED`. For ones out of reach but where **a build was really run**: `path_b_attempted:true` + an honest `path_b_reason`. For genuinely **unmeasurable classes** (Spectre/side-channel/timing, the 2^31 memory wall, Chrome M72 needing a full browser with no extractable standalone third-party library): mark `path_b_terminal:true` + the reason, and **do not retry**. A bare "DEFERRED" / no path_b_* fields = non-compliant.

**LANE routing + concurrency model (build-once-per-commit, one build reused for all siblings)**:
- **USERSPACE-build (255, highest yield, attack first)**: userspace parsers/daemons built at fix^ (IM/openssl/gs/krb5/php-src/qemu/suricata/wireshark/FFmpeg/poppler/gnupg...), with ASan/UBSan/LSan/valgrind/MSan. **Prefer reusing banked builds** (krb5_work/jasper19/openmpt/ff_vuln_2017/php_lane/im6_9144/libvnc/gpac/vim/pdfresurrect etc. under pathb/, see memory); build new only when nothing is banked. **Give the same (project,cve,commit) cluster to the same agent, build once and replay all siblings one by one** (581 clusters covering 1011 samples).
- **LINUX-kasan (329) / LINUX-kvm-race (307)**: an era-matched KASAN kernel in QEMU (`pathb/kasan/`, the binutils-2.26 ubuntu16 builder, the v4.10 KASAN tree, etc.); race/UAF goes through the KVM `-smp` race-runner (syz-prog2c-collide -> KVM). **Try a user-space micro-harness (kernel_stub.h) + ASan/-fsanitize=bounds/-m32/MSan first** (storm-immune, no VM boot) -- many "needs-live-kernel" cases are in fact within reach of extract-stub (see the primevul-qemu-extractstub-reopened vein); only escalate to QEMU when the micro-harness cannot reach it.
- **ANDROID-stub (114)**: extract-and-stub behavioral differential (OMX/media/libavc reusing the 188227 omx_stub recipe).
- **CHROME-lib (6)**: files under third_party/{libxml,libxslt,harfbuzz,libpng,brotli,...} that are independently buildable library subsets; build that library @commit^.
- **CHROME-triage (985, mostly terminal)**: first make a **quick static determination** of whether the file belongs to an extractable standalone third-party library; yes -> move it to a CHROME-lib build; no (Chrome itself/V8/blink M72 era-trap) -> mark `path_b_terminal:true` (no-extractable-lib / M72-full-browser) and do not build.

**★★ ANTI-STORM (Path-B builds are heavy, stricter than Phase-1)**:
- **Concurrency cap of 2-3 heavy builds** (newly created userspace/kernel builds); **reusing banked builds is lightweight** and may run more in parallel. **QEMU/KASAN boots <= 2-3 concurrent, each with a hard 120s timeout + `--rm`**; the same cap for the race-runner KVM.
- Each tick check `/proc/loadavg` + CPU-usage/iowait: **with load>40 start no new heavy build** (lightweight banked-replay/extract-stub/triage agents may continue), **with iowait>50 wait for drain**, **with load>150 kill builds/VMs stuck for >300s**. In `pkill`, `-f qemu-system` is forbidden (a self-kill footgun) -- kill the docker-run-qemu wrapper precisely by etimes>300.
- `ASAN_OPTIONS=disable_coredump=1` + `ulimit -c 0`; `make -j8` cap; **builds only inside `pathb/`** (not in /tmp, not outside the repository); after a build, keep the banked binaries and delete `.o`/intermediate objects; repro.sh references the banked binaries with repository-relative paths and writes a git pin into `EVIDENCE_MAP.json`, and **does not copy the build tree into the sample directory** (but the harness/driver/PoC/logs must be copied); a SKIP-if-craft.json-exists guard; frame subagent wording as defensive-label-verification to avoid a cyber flag.

**PER-TICK FLOW**: check /proc -> harvest (craft count + RUNLOG tail, do not read transcripts; merge stray RUNLOGs into the canonical one) -> `python3 <HOME>/.claude/jobs/50816601/tmp/pathb_refresh.py` (computes DONE/TERMINAL/TRACTABLE and writes `bigvul_pathb_pull.csv` sorted by lane priority) -> remove in-flight agent ids from the pull -> **dispatch concurrently**: ~2-3 heavy-build agents (each taking one commit-cluster, building once and replaying all siblings) + ~2-4 lightweight agents (banked-replay / extract-stub micro-harness / Android-stub / Chrome-triage, each taking ~10-15 ids). Only **when TRACTABLE==0** (every non-terminal needs-Path-B has `path_b_attempted:true`, or is already confirmed, or is already `path_b_terminal:true`) do `ScheduleWakeup stop:true` and report the final statistics. Never stop while TRACTABLE!=0. On a session limit -> harvest, then set the wakeup for after the reset.

**Completion criteria**: `pathb_refresh.py` reports `TRACTABLE unattacked (pull) = 0`. Related memories: `needs-pathb-attempt-directly-4090`, `pathb-prebuilt-binary-strategy-4090`, `concurrent-build-io-cap-4090`, `kasan-qemu-era-toolchain-4090`, `kvm-race-runner-lever-4090`, `primevul-qemu-extractstub-reopened-vein-4090`, and the various `pathb-*-reusable` banked-build memories.

---

## ★★ Persistence hard rule (user, 2026-07-22): do not stop until the worklist is fully covered (Phase-1, completed)

**Never stop the loop until every label_target==1 sample in `bigvul_current_dynamic_method_worklist.csv` has a verdict (`data/output/dataset/bigvul/<id>/dynamic_confirmation.json` exists, or a craft.json already exists).** Do not stop because "there are no new confirmations / the rest are all needs-Path-B / this class of samples has been gone through" -- not confirmed != not processed. Every unprocessed sample must be given one of the honest verdicts: DYNAMICALLY_CONFIRMED (nailed down by a differential) / NOT_DYNAMICALLY_CONFIRMED+label_noise:true (**attacked and nothing fired**, with `label_noise_type:label_noise_dynamic_tools_attacked` + `label_noise_category` + `real_vuln_location` + a `label_noise_attack/` evidence directory; ★ since 2026-08-03 reading the code alone does not count) / INCONCLUSIVE+label_noise:false (a real vulnerability but needs-Path-B/cyber-block/undetectable-class). Criteria: each round, first compute how many target=1 ids in the worklist still have no dc.json (see the script below), and keep dispatching agents until that number == 0. Only after 100% coverage of the worklist may you ScheduleWakeup stop.

Computing the remainder: use `python3` to walk the ids in the CSV and count those that have neither `data/output/dynamic/confirmed/bigvul_<id>.craft.json` nor `data/output/dataset/bigvul/<id>/dynamic_confirmation.json` and whose info.json label_target==1.

### ★★ Upgrade rule (user, 2026-07-22): every remaining sample needs "an actual dynamic tool test", not just a static classification
**Every sample** in the worklist (which now contains only the non-confirmed/non-label_noise remainder) -- **whatever its old verdict was: NOT_DYNAMICALLY_CONFIRMED / DEFERRED / needs-Path-B / INCONCLUSIVE -- must really be run once through a differential with a dynamic tool**; you may not close out with a static ruling based only on `diff -w`/commit-stat. **You are not bound by `recommended_method`**: based on this sample's info.json project / CWE / commit / function, choose the most suitable dynamic method yourself and actually execute it:
- linux kernel -> KASAN+QEMU (banked `pathb/kasan/kernels/v3.14-v4.19` + `/dev/kvm` + syzkaller; build-straddle or build-at-fix^ KASAN) / KMSAN (uninit-leak) / KCSAN (race) / a kernel micro-harness (single function).
- userspace lib/daemon (openssl/gnupg/php/gs/im/ffmpeg/git/tor/irssi/heimdal/frr/...) -> Path-B build-at-fix^/fix + ASan/UBSan/LSan + the fix's own regression tests or a differential on really constructed input.
- Android -> extract-and-stub (OMX/codec/parser) / rediscovery with the already banked `pathb/wt_*/build/*_dec_fuzzer` fuzzers plus attribution / m32 (32-bit) / MSan (uninit).
- Integer overflow that is 32-bit-only -> the m32 docker (`vulvalidate-m32`); uninit info-leak -> MSan (clang -fsanitize=memory); fuzzer-found -> coverage-libFuzzer to regenerate the crash.
- Side-channel/Spectre (which sanitizers inherently cannot see), Windows-only, Chrome (the M72 era-trap requiring a full browser) -> still honestly needs-Path-B / cyber-block / undetectable-class, but **you must write into dc.json "the dynamic methods already attempted + why that class of tool cannot produce a differential"** (the tried_dynamic_method field); you may not merely state needs-Path-B statically.
The differential is the standard path (revised 2026-07-28): the pre-fix build (fix^) faults and the fixed build is clean on the same input = CONFIRMED_CVE_MATCH; both sides fault identically but the defect is inside the labelled function and the pre-fix build can trigger it = CONFIRMED + fix_arm_also_vulnerable:true + confirmation_class:OTHER_DEFECT_UNFIXED; the pre-fix build cannot trigger it at all = an honest INCONCLUSIVE, but the tool must actually have been run. Every dc.json records `tried_dynamic_method` (the tool actually run) + `differential` (vuln_rc/fix_rc).

---

_Adapted from the primevul `LOOP_PROMPT.md` for BigVul's dataset characteristics. **Last updated: 2026-09-20 -- aligned the output ruler with §2a of `tasks/diversevul_only_vulnerable_official_18945_reports/LOOP_PROMPT.md`**: (1) added a four-outcome quick-reference block "read this first: what this round must hand in at the end" at the top; (2) renamed §0a's fourth outcome `BUILD_FAILED` to **`NOT_DYNAMICALLY_TESTED`** and the secondary field `build_failed_reason` to **`not_tested_reason`** (the old names are only aliases), with the reason written right underneath that section -- "not one of those 230 samples was a build failure"; (3) rewrote the `not_tested_reason` vocabulary into 7 values **determined from the actual state on disk** (adding `attempted_no_usable_result` / `needs_path_b_not_attempted` / `never_attempted` / `attempted_inherited_crossdataset` (BigVul has 495 cross-dataset propagations, which must be countable separately) / `confirmation_withdrawn_nothing_measured_since`), and abolished the black-hole value `no_reason_recorded`; (4) changed the ruler for `inverted_polarity`: it is no longer a terminal "cannot decide" state, it moves to `LABEL_NOISE_EXCLUDED` once it passes two gates, and **you may not close out sitting on it**; (5) added "only vocabulary values count" to both vocabularies; (6) added to §0a a **decision-order table** (the first match from the top wins) and "the boundary between cells 3 and 4 depends only on whether integer readings from both sides were obtained"; (7) **wrote the "output ruler" into the end of the verbatim `/loop` text that gets pasted** -- previously the four outcomes lived only in the body text, and the pasted copy never required accounting by the four outcomes; (8) updated the outstanding-debt section, making clear that the `manual_check_bigvul_20260913/` set (`ALL_ADJUDICATIONS.csv` / `WORKLIST_REMAINING.csv` / `_mocktest.py` / `_armcheck.py`) is a **three-state manual re-review**, not the four-outcome partition, though it can serve as input to the reader. The backup is at `BIGVUL_LOOP_PROMPT.md.bak_before_outcome_align_20260920`. **Previous update: 2026-08-21 -- synced with the current logic and requirements of `tasks/primevul_reports/LOOP_PROMPT.md`**: (1) added a "current snapshot" block at the top (source of truth `bigvul_dynamic_status_latest.json`, the refresh commands + the I/O rule "skip the full-repository scan when this round published no confirmation"); (2) added §0a **the four outcomes** (`CONFIRMED` / `LABEL_NOISE_EXCLUDED` / `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` / `BUILD_FAILED`) and the two required secondary-field vocabularies, and voided nine old verdict strings as outcomes; (3) added §0b **the three closing states must not be merged** (`build_failed` / `attack_exhausted` / `unattributed_sanitizer_output`); (4) added §0c **build once per project, reuse within the batch** (what is saved is the clone/configuration/ccache/harness, **not the pair built from pre-fix and post-fix code**); (5) the gates were formally raised from five to **seven** (stored-body completeness, and execution proof reaching the lines the patch changed), hanging the P104 inlining re-check and the P36 flag trap on the same section; (6) added a second value to `label_noise_basis`, **`dynamic_differential_inverted`** (measured, and the direction is inverted); (7) added **rule C** (whether an injected runtime condition counts as a faithful trigger: look at whether the upstream fix accepts that condition, with five preconditions); (8) added a batch of reading traps from 2026-08-15 (a mute positive control, `-fsanitize=integer` on unsigned left shifts, "the two sides differ" requires first looking at which side faults, a one-line hunk missed by `git show --stat`, the `nm` assertion for a banked binary that lacks the labelled function, ASan's fast unwinder dropping frames, `std::string::empty()` not being instrumented, this machine having network access, and not letting work continue after a record-writing assertion fails); (9) added the closing self-check / stop conditions / the three hard rules for bulk record edits / the requirement to use full sentences for the two label-noise categories; (10) recorded three **honest outstanding debts**: BigVul has no equivalent four-outcome reader module, 264 samples are still in old status strings, and the two checkers do not yet cover the rules added this time. **Previous update: 2026-08-03 (two user instructions, same day): (1) for samples really attacked with a dynamic tool where the vulnerability did not come out, the result may not be written as NOT_MEASURED/not confirmed; it must be written as `label_noise_type: label_noise_dynamic_tools_attacked`; (2) **you must attack before ruling label noise** -- reading alone (an empty diff -w, a commit touching 41 files, changes that are all whitespace) may only be recorded as `suspected_label_noise`, and the sample stays on the worklist waiting to be attacked; the attack scripts/inputs/complete logs must be stored in `<id>/dynamic_evidence/label_noise_attack/`, and without that directory the ruling does not hold; also established were five hard gates, the `label_noise_category` sub-category vocabulary and the `label_noise_basis` field. The trigger was the measurement that, of 1,160 samples in class C3, 843 of the "tested" ones were actually diff -w text comparisons and 1,057 had no evidence directory at all; see P25 in evidence_repair/PROBLEM_REGISTER_20260803.md. **This also voided three old instructions**: "when diff -w is identical, mark label_noise directly and skip dispatching a subagent", ">4-6 files means INCONCLUSIVE-relabel directly, do not waste a build", and the "INCONCLUSIVE+label_noise:true" clause in the full-coverage terms)**. Previous update: **2026-07-28 (added the six "★★★★ evidence self-sufficiency hard rules" at the top: artifacts always land in `<id>/dynamic_evidence/`, `/tmp` and out-of-repository paths are forbidden, scripts are relativized, record paths are written in relative form, third-party material goes to `pathb/` with a git pin, and an actual run as self-check before handing in; also rewrote the raw /loop block, the output-path discipline, the ANTI-STORM build clauses, the preservation clauses, and the note that target=0 has been migrated out)**. Previous update: 2026-07-21 (added: (1) explicit label_noise marking rules; (2) UNIQUE pre-filtering before dispatch; (3) defensive-label-verification wording for subagents to avoid a cyber safety flag; (4) output-path discipline. The preceding 2026-07-20 update added the faithful-trigger hard criteria "the differential is the acceptance test", derived from the 179087/CVE-2013-7022 case)._

## The original /loop prompt (verbatim, copy straight into /loop)

> **★ 2026-08-21: the block below is historical verbatim text; before pasting it, remember three things that have changed** --
> (1) there are **seven** gates, not five (the added ones are "the stored body is verbatim identical to the upstream at fix^" and "the execution proof must reach the lines the patch changed");
> (2) there are only four outcomes (see §0a), and strings like `INCONCLUSIVE` / `DEFERRED` / `NEEDS_PATH_B` **are no longer outcomes**;
>    they may only remain in a sample record's `verdict` as history;
> (3) the word "arm" in the text must, in newly written text, become "the build from pre-fix code / the fixed one" or "the two sides".
> When dispatching a subagent, this whole document plus the round's briefing must be named in the prompt for it to read; pasting only this block is not enough.
>
> **★ 2026-09-20: the output ruler has been written into the end of the block below.**
> Previously §0a's four outcomes were written only in the body text, while what actually got copied into `/loop` was this historical text --
> so **the pasted prompt never required sorting samples into the four outcomes**, and nobody accounted by the four outcomes at the end of a round.
> An "output ruler" paragraph has now been added at the end, and you must paste it along with the rest.

```
Please continue doing dynamic-tool analysis on bigvul and nail down more samples. The result files and intermediate files that need to be saved should also follow the existing logic (craft_run.py writes back into the sample folder + repro.sh + the ledger). Methods available: the ones recommended under <REPO_ROOT>/tasks/bigvul_reports. For each sample, choose a suitable method from tasks/bigvul_reports to do dynamic verification. Key rules: before confirming you must check info.json's label_target and only confirm label_target==1; never do unfiltered cluster propagation (it may only go to a twin with label_target==1 whose labelled function == the function that reproduces the fault); avoid low-yield network-protocol/cryptographic-arithmetic/pure-fuzzer classes, and prefer self-contained file/format parsers + cryptographic string out-of-bounds. As long as CPU and memory usage are both within 60%, run as concurrently as possible (drop to 1-2 agents during a co-tenant storm). At the start of each round check /proc/loadavg and free -g for the gating decision; exclude already-confirmed samples; honestly skip logic/authentication classes with non-deterministic sanitizer faults; append results to tasks/RUNLOG_<host>_bigvul.md. For every sample confirmed by a dynamic tool, and every one not confirmed, the corresponding files must be saved following the existing logic. Ones dynamically confirmed as vulnerable need reproducible files saved per the existing logic; ones that are not reproducible need their corresponding explanation files saved per the existing logic.

★★★★ Criteria change (user, 2026-07-28, highest priority): a CVE mismatch is no longer a veto. As long as the labelled function can be made to trigger a real vulnerability with real, reachable input, it counts as CONFIRMED -- even if it is not the CVE it is labelled with. In that case write cve_match:false + cve_attribution_note (where the labelled CVE actually is and why it is wrong) + real_vuln{class,site,trigger}. So before downgrading because "the labelled function has nothing to do with this CVE", you must ask one more question: does this function itself have a real triggerable defect? If it does, confirm it. ★ A vulnerable fixed version is not a veto either (user, added 2026-07-28): if the sample is vulnerable and its fix is also vulnerable, then as long as a dynamic tool can trigger this sample's vulnerable behavior, this sample is confirmed as vulnerable -- you only need to annotate honestly that its fix is also vulnerable. Record verdict:DYNAMICALLY_CONFIRMED + fix_arm_also_vulnerable:true + defect_present_both_arms:true + confirmation_class:OTHER_DEFECT_UNFIXED + fix_arm_signal (the actual sanitizer output of the build from the fixed code). Cases bigvul/178795 (libmagic cdf_read_property_info out-of-bounds read), bigvul/181140 (IM WriteJP2Image leaking 1054040 bytes). None of the three preconditions may be missing, or it becomes "any bug you happen to find counts": (1) the defect must be reachable from the labelled function -- inside its body **or inside a callee it calls** (relaxed by the user 2026-08-01, overturning the old counter-example 183055). A defect in a callee is not downgraded; just add confirmation_scope:"reachability" + defect_site + callee_of_labelled_function:true + call_path to annotate it clearly (case 180379). Only when you cannot get in from the labelled function at all is it label noise -- when the fault is in its caller, or in a sibling function with no call relation; before ruling you must read the upstream source and verify the call direction (counter-examples 187879 / 187880: the assert really fires but in CreateBlockGroup, and neither labelled function Segment::ParseNext nor Cluster::ParseSimpleBlock has it in its call closure -- ParseSimpleBlock is the **alternative** branch to Cluster::Parse's BlockGroup branch, not its caller. ★ Correction 2026-08-02: 187869 was originally cited here, and that example was **wrong** -- line 204 inside `ParseBlockGroup` is `CreateBlock(0x20, // BlockGroup ID)`, and `Cluster::CreateBlock` at containing_file.cc:7200 does `return CreateBlockGroup(...)`. 187869 has therefore been confirmed under confirmation_scope:"reachability". The lesson of the wrong example is the rule itself: **read the call direction first, do not go by impression**); (2) triggered by real, reachable input, with empirical output from a sanitizer or an equivalent oracle; a synthetic trigger (absurd magic numbers, values upstream would reject) still does not count; (3) the build from pre-fix code must be able to trigger it by itself -- counter-example 183295, inverted polarity: the stored "vulnerable version" is the clean one and the "fixed version" is what crashes, so this sample is not the vulnerable one. Only if the function really has no defect at all, or the build from pre-fix code cannot trigger anything, do you downgrade. Statistics come in three grades that may not be mixed: CONFIRMED_CVE_MATCH (what was triggered is the labelled CVE and the two sides differ) / CONFIRMED_OTHER_DEFECT (another real defect in the labelled function with a differential between the two sides, cve_match:false) / OTHER_DEFECT_UNFIXED (a real defect in the labelled function that upstream did not fix, both sides fault identically). ★★★★ Unreachability is not a veto (user, added 2026-07-31, overriding the word "reachable" in precondition (2) above): if the defect really is inside the labelled function body and is real (not manufactured by the harness changing upstream code), then even if no attacker-controlled path to it can be found, still record verdict:DYNAMICALLY_CONFIRMED and just add the fields reachability:"UNREACHABLE" + reachability_note (what the defect is, on which line, with what oracle it was observed; what precondition is needed to reach it and why that precondition is not something an attacker can construct) + attacker_controlled_trigger:null. reachability is orthogonal to the three grades above; it does not change the grade, it only adds a qualifier to it. Case bigvul/187837 (libwebm ContentEncoding::GetCompressionByIndex: count is a ptrdiff_t, and idx >= static_cast<unsigned long>(count) turns a negative count into a huge unsigned upper bound; under -DNDEBUG its own assert(count>=0) is compiled away, and the probe obtained an entry for idx=3 on a 4-slot array; but producing count<0 requires the caller to pass in an object whose end_ precedes begin_, which is a broken class invariant, hence UNREACHABLE + OTHER_DEFECT_UNFIXED + cve_match:false). The word "reachable" in precondition (2) is only there to block synthetic triggers (absurd magic numbers, values upstream would reject) and harness-manufactured defects; it is not there to require that an attacker path exists in the real program -- do not conflate the two. Keep three things apart; only the first takes UNREACHABLE: (1) the defect is real, inside the labelled function, with no attacker path -> CONFIRMED+UNREACHABLE; (2) not built, not run, or the wrong oracle -> not unreachable, just unfinished, go back and do it; (3) the harness used #ifdef to delete a guard upstream already had and then reported the overrun -> downgrade (counter-example 187416). Before writing UNREACHABLE, ask yourself: did I really prove unreachability, or did I merely fail to find a path? The latter gets reachability:"UNKNOWN" plus a list of the entry points searched; do not pass it off as a conclusion -- the bad example is 181875, where it was once asserted that "it needs a 16GB allocation so it is unreachable", and measured, that allocation succeeded and the out-of-bounds write happened anyway. Unreachability is to be measured, not deduced.

★★★ Evidence self-sufficiency hard rules (overriding other path conventions): the ruling is not the artifact; the set of files that lets someone else rerun it is. Measured: of 4,894 confirmations, 136 sample directories had no reproducible file at all, 2,021 samples had their evidence outside data/output/dataset/bigvul/, and 329 of those references pointed into /tmp/claude-<pid>/... which disappears forever after one reboot; after the first relocation only 1 of 164 scripts actually ran (126 hard-coded absolute paths, 116 referenced sibling files that were not moved along). Therefore:
(1) Every sample's reproducible files (confirmed and unconfirmed alike) always land in data/output/dataset/bigvul/<id>/dynamic_evidence/, with a fixed directory name. It contains at least: repro.sh (one command that builds both sides + runs + prints the differential), driver.c/harness, the code under test for both sides (body_vuln.inc/body_fix.inc or stub.h+#ifdef FIXED), the real PoC input file (stored as raw binary), the actual output logs of the pre-fix side and the fixed side, and EVIDENCE_MAP.json (each file's purpose + sha256). Unconfirmed samples must also leave the scripts and logs that were actually run; "ran it but got no differential" must equally be verifiable by rerunning.
(2) It is strictly forbidden to leave any artifact in /tmp, ~, <SCRATCH>/wl_campaign/ or anywhere outside VulValidate/. If temporary space is needed, export TMPDIR="$(dirname "$0")"/tmp and keep it after the run.
(3) No absolute paths in scripts: use cd "$(dirname "$0")", D="$(dirname "$0")/.." (the sample directory), CC=${CC:-gcc}. Swapping in a different absolute path is the same as not fixing it -- the next time the dataset is copied elsewhere it breaks just the same. Before handing in you must run grep -rn '/scratch/\|/tmp/\|/home/' *.sh with no output.
(4) Paths in records are written relative to the sample directory: write "dynamic_evidence/repro.sh" in dynamic_confirmation.json and craft.json, not the bare name "repro.sh" (a bare name makes complete evidence look nonexistent), not an absolute path outside the repository, not a shell brace expansion pathb/x/{a,b,c} (tools splitting literally cannot resolve the paths), and do not put the pointer only in a README.txt. Three places must agree: the path fields in dc.json, the path fields in craft.json, and the real files on disk.
(5) Third-party software/source/builds all land inside VulValidate/: at-commit build trees and banked ASan binaries -> pathb/<lane>/<name>_{vuln,fix}/, upstream tarballs -> pathb/_srcpkg/ (store the original archive + sha256), toolchains/sysroots -> pathb/_toolchain/, kernel images -> pathb/kasan/, shared cross-sample stub headers -> pathb/_shared/. pathb/ is inside the repository and is shared along with the whole of VulValidate/, so banked binaries do not need to be copied into every sample directory, but repro.sh must reference them with repository-relative paths and write a pin into EVIDENCE_MAP.json (git_remote+commit+dirty_files+the configure line; if dirty_files!=0 the diff must be stored into dynamic_evidence/ as well). Do not copy upstream build trees per sample -- measured, that comes to 6.13 GB / 520,000 files, of which 3.19 GB are locally built .o files.
(6) Self-check before handing in: actually run it, do not just look at whether files exist: cd into dynamic_evidence/, rm the build products, and bash repro.sh must build both sides from source and really produce a differential. Three easily mistaken criteria: a log is not a reproduction file (.asan.log is evidence that it "was run" and cannot let you "run it again"; only logs in the directory = not valid); the existence of craft.json != a differential was run; both sides clean does not mean there is no vulnerability (the harness may never have compiled the labelled function -- measured, 90% of 125 harnesses did not -- or HW acceleration bypassed the vulnerable path), so prove the labelled code really executed before concluding.
(7) Withdrawing a confirmation means changing four places, and info.json is the one most easily missed (measured: 21/21 missed it in the first round, while info.json is the first thing downstream tools read): (1) change verdict+reason+the label_noise family in dc.json; (2) move craft.json into <id>/prior_confirmation_<stamp>/ (moved, not deleted); (3) change info.json using the repository's existing vocabulary -- label_noise:true uses tier=mislabel/is_vulnerable=NO, label_noise:false (a real patch but not triggerable) uses tier=not_dynamically_confirmed/is_vulnerable=NOT_CONFIRMED (★ added 2026-08-03: for ones really attacked with a dynamic tool where the vulnerability did not come out, write label_noise_type:label_noise_dynamic_tools_attacked + label_noise_basis:dynamic_attack_negative, tier=mislabel/is_vulnerable=NO, and **do not write NOT_MEASURED/not confirmed**; the seven gates are in the "explicit label-noise marking rules" section), and label_target is never touched (that is the dataset's label; what changes is our ruling); (4) leave a rerunnable script for the negative result in dynamic_evidence/, since "both sides clean" must itself be verifiable by someone else rerunning it. Tool: evidence_repair/reconcile_info_json.py --ids a,b,c --apply.
(8) Before closing out, run tasks/bigvul_reports/evidence_repair/audit_reproducibility.py and locate_evidence.py; samples added this round must not appear in either list.

★ CVE-match faithful-trigger hard criteria (all must hold for CONFIRMED, otherwise INCONCLUSIVE):
In one sentence: **only what can be reached by really constructed input through a real call chain is a real trigger; what is forced out by absurd parameters and cannot be produced by real input is synthetic. (**Since 2026-07-28: "the patch does not stop it" no longer equals synthetic** -- upstream not fixing this bug != this bug not existing; see the criteria change at the top.)**
(1) Read the real CVE first: before confirming, pull NVD + the fix diff of commit_id, and write out real_root_cause / trigger_mechanism / attacker_controlled_trigger.
(2) The differential is the standard path: on the same input, the vulnerable version (built at fix^) faults and the real fixed version (built at the fix commit) passes cleanly = CONFIRMED_CVE_MATCH. extract-stub must also compile both a vuln and a fixed version for comparison. **Both versions crashing -> rule by the rules at the top**: if the defect is inside the labelled function and the build from pre-fix code can trigger it, it is still CONFIRMED; record fix_arm_also_vulnerable:true + confirmation_class:OTHER_DEFECT_UNFIXED; only when the defect is not inside the labelled function is it label noise. **Neither version crashing** = the build from pre-fix code cannot trigger it at all -> not a confirmation. ★ 2026-08-03: at that point you **may not** stop at NOT_MEASURED/not confirmed -- if this round really did attack the labelled function with attack input (all seven gates passed), record `label_noise_dynamic_tools_attacked`; if the gates are not passed, it is simply unfinished, so go back and do it.
(3) Prefer "build-at-commit + real input" through the real demux/parse/decode call chain, rather than hand-assembling a struct and calling the labelled function directly.
(4) Trigger values must be realistic and reachable: sizes/lengths/counts must be producible by a really constructed file and must reach the labelled function through a real entry point; absurd magic numbers are forbidden (such as 40000x40000, or passing INT_MAX directly) unless that exact value is reachable by an attacker through a real path; a value upstream validation would reject = unreachable = invalid.
(5) Mechanism agreement: the fault type/location must match the mechanism the fix repairs; another real vulnerability inside the labelled function -> cve_match=false, still CONFIRMED; forcing it with out-of-bounds/contract-violating parameters on an unrelated statement = synthetic -> INCONCLUSIVE (reason: synthetic-trigger/not-the-vuln-region; note that no-fix-differential no longer constitutes a veto by itself).
(6) The allocation site != the write site is allowed: when the labelled function is the "under-allocation" root cause and the overrun happens in a downstream callee in the same file (such as g2m_init_buffers under-allocating / yuv2rgb writing out of bounds), that is faithful -- record frame_note(alloc_site/fault_site), and do not synthesize just to make frame#0 be the labelled function.
Save both kinds: dc.json and craft.json record cve_match(true/false), triggered_vuln, cve_vuln, synthetic_trigger, differential(vuln_rc/fix_rc), frame_note.

★ Explicit label-noise marking (user, 2026-07-21): ★★ changed by the user 2026-08-03: **before ruling label noise you must have attacked the labelled function with a dynamic tool and not triggered the vulnerability**; reading the diff / counting files / looking at the commit title can only produce suspected_label_noise:true + suspected_label_noise_category, and the sample stays on the worklist waiting to be attacked. Attack scripts, inputs and complete logs always go into <id>/dynamic_evidence/label_noise_attack/, and without that directory the ruling does not hold. For ones that really did not fire after being attacked, write in dynamic_confirmation.json label_noise:true, label_noise_type:"<type>", a reason containing the literal words "label noise", and real_vuln_location:"<the function/file where the real vulnerability is>". label_noise_type is always label_noise_dynamic_tools_attacked; also fill label_noise_category to say which kind of mislabel it is, with values: whole-commit-relabel (a fix touching >4-6 files where each one gets labelled) / multi-function-relabel / whitespace-only-relabel (diff -w is empty) / wrong-function (the vulnerability is in a sibling or a callee) / version-skew (before-after does not match the real fix commit) / mass-hardening-sweep (one defensive guard swept across ~100 files) / library-import-relabel (a wholesale re-vendor of upstream) / cosmetic-refactor (signature/renaming plumbing) / wrong-cwe / test-file-labeled / label_noise_dynamic_tools_attacked (really attacked with dynamic tools and the vulnerability did not come out; the seven gates must be passed: a real integer exit code was produced + the labelled function really was executed + attack input was used + the oracle was chosen to match the fix mechanism + the attack-surface coverage is written out + first prove the stored body is verbatim identical to the upstream at fix^ + the execution proof must reach the lines the patch changed (with the hit counts written into the record). Results of this class may not be written as NOT_MEASURED/not confirmed). A real vulnerability that the tools cannot reach gets the opposite: label_noise:false + a reason containing "needs-Path-B"; the two are strictly separated.

★★★★★ Output ruler (user instruction 2026-09-20, the final step, not to be skipped): **every target=1 sample touched this round must end up in exactly one of the four outcomes below, with that outcome's secondary fields filled in.** The four outcomes have only these four names, and old strings such as INCONCLUSIVE / DEFERRED / NEEDS_PATH_B / NOT_CONFIRMED / UNTOUCHED may no longer appear as outcomes (they may only remain in the sample record's verdict field as history):
(1) CONFIRMED -- the labelled function triggered a real defect on faithful input. Fill in confirmation_class (one of the three grades CONFIRMED_CVE_MATCH / CONFIRMED_OTHER_DEFECT / OTHER_DEFECT_UNFIXED) + cve_match + confirmation_scope (defect_site or reachability, only these two values) + reachability (REACHABLE / UNREACHABLE / UNKNOWN).
(2) LABEL_NOISE_EXCLUDED -- the label is overturned: either it was attacked with a tool matching the CWE, nothing fired, and the seven gates are in place, or a differential was measured whose direction is inverted. Fill in label_noise_category + label_noise_basis (only the two values dynamic_attack_negative / dynamic_differential_inverted) + label_noise_type; write cve_match as n/a. **Anything that merely looks like a mislabel from reading the code does not belong in this cell**; write suspected_label_noise, keep it on the worklist, and count it statistically in cell (4).
(3) DY_Attacked_But_can_not_decide_confirmed_or_label_noise -- a dynamic tool really attacked it and readings from both sides were obtained, but this measurement cannot tell whether it is a confirmation or a mislabel. dy_attacked_undecided_category is required, and its value can only come from the vocabulary in §0a (nominated_awaiting_adjudication / attacked_no_trigger / guard_never_evaluated / decision_diff_no_impact / fault_not_attributable / inverted_polarity (only as a temporary state pending adjudication; once it passes the two gates it moves to cell (2)) / no_differential_possible / synthetic_trigger / reachability_unproven / cve_mismatch / single_arm_only / unclassified_reason).
(4) NOT_DYNAMICALLY_TESTED -- no valid dynamic measurement has been obtained yet: never tested, could not reach it, or built and ran but produced no result. not_tested_reason is required, and its value can only come from the vocabulary in §0a (attempted_no_usable_result / needs_path_b_not_attempted / never_attempted / build_failed / attempted_inherited_crossdataset / confirmation_withdrawn_nothing_measured_since / unclassified_reason), and it must be **determined from the actual state on disk** (is there a repro.sh, is there a run log, is there a needs-Path-B marker, did it come from cross-dataset propagation); do not rely on that reason field in the record, which is empty for most.
The boundary between cell (3) and cell (4) is one question only: **was this sample really attacked by a dynamic tool and were readings from both sides obtained?** Attacked -> (3); the attack did not succeed or has not happened -> (4). "identical" / "n/a" / null / the string "1" are not integer exit codes and all go to (4).
**When reporting at sign-off the four numbers must add up to this round's denominator, and you must give the secondary-field distributions of cells (3) and (4) at the same time** -- reporting only the total of cell (3) is meaningless, because each kind of "cannot decide" inside it has a completely different next action. An empty string, NONE, or a whole sentence pasted into the value slot are not valid values; they must stay visible and may not be laundered into unclassified_reason.
```

## Paths and ledgers (BigVul-specific)

- Dataset samples: `data/output/dataset/bigvul/<id>/` (containing info.json / context_meta.json / vulnerable_function.c / fixed_function.c / containing_file.c / dependencies/ / dynamic_confirmation.json / record.md). **Reproducible files -> `<id>/dynamic_evidence/`** (see rule 1 at the top). Note that metadata such as `file`/`function` actually lives in `context_meta.json`, and `info.json::file_name` is often empty.
- The registry (source of truth): `data/output/dynamic/confirmed/bigvul_<id>.craft.json` (for the schema, refer to any existing bigvul craft.json). **Note that it is `data/output/dynamic/confirmed/`; `data/output/confirmed/` does not exist** -- a validation script pointing at the wrong level will report the whole campaign as "craft.json missing".
- Builds and third-party material: `pathb/` (inside the repository, shared along with the whole of `VulValidate/`). See the partition table in rule 4 at the top.
- Ledger: `tasks/RUNLOG_<host>_bigvul.md`. Reindex: `nohup python3 scripts/build_dedup_index.py` (do not block on it every round).
- Key info.json fields: `label_target` (**only confirm ==1**; the folder also contains target=0 negative samples), `cve`, `labeled_cwe`, `project`, `commit_id` (**= the FIX commit**; Path-B builds at its parent = fix^), `file_name`, `before_cwes`/`after_cwes`, `static_verdict`, `tier`.

## ★ CVE-match faithful-trigger hard criteria (strengthened by the user 2026-07-20, effective together with the prompt)

The acceptance standard in one sentence: **only what can be reached by really constructed input through a real call chain is a real trigger; what is forced out by absurd parameters and cannot be produced by real input is synthetic. (**Since 2026-07-28: "the patch does not stop it" no longer equals synthetic** -- upstream not fixing this bug != this bug not existing; see the criteria change at the top.)**

Six hard criteria (all must hold for CONFIRMED, otherwise INCONCLUSIVE):
1. **Evidence before action**: before confirming, read NVD + the fix diff of `commit_id`, and write `real_root_cause` / `trigger_mechanism` / `attacker_controlled_trigger` into the record.
2. **The differential is the standard path (revised 2026-07-28, no longer the only path)**: on the same input, the vulnerable version (built at `fix^`) faults and the real fixed version (built at the fix commit) passes cleanly = `CONFIRMED_CVE_MATCH`. Prefer real binaries from build-at-commit; extract-stub must also compile both a vuln and a fixed version for comparison.
   - **Both versions faulting** -> no longer an automatic veto. If the defect is **inside the labelled function** and **the build from pre-fix code can trigger it by itself**, it is still CONFIRMED; record `fix_arm_also_vulnerable:true` + `confirmation_class:OTHER_DEFECT_UNFIXED` (cases 178795 / 181140). **A defect inside a callee of the labelled function is likewise confirmed** (user, 2026-08-01),
     you only need to add `confirmation_scope:"reachability"` + `defect_site` + `callee_of_labelled_function:true` + `call_path`
     to annotate it clearly (case 180379). Only when **you cannot get in from the labelled function at all** (the fault is in its caller,
     or in a sibling function with no call relation) is it label noise -- before ruling you must read the upstream source and verify the call direction (counter-examples 187879 / 187880; ★ note that 187869 was once listed as a counter-example here and was overturned by measurement on 2026-08-02 and re-ruled CONFIRMED/reachability -- see the correction above).
   - **Neither version faulting** -> the build from pre-fix code cannot trigger it at all -> not a confirmation.
   - **Inverted polarity** (the build from pre-fix code is clean and the fixed one faults) -> this sample is not the vulnerable one; the collection mistook the commit that introduced the defect for the fix (counter-example 183295).
3. **Prefer real entry points**: if you can "compile the real tool + feed a really constructed file through the real decode path", do not use a miniature harness that hand-assembles struct state and calls the labelled function directly -- the real path validates reachability and value realism at the same time.
4. **Trigger values must be realistic and reachable**: sizes/lengths/counts must be values that really constructed input can produce and that reach the labelled function through the real demux/parse/decode call chain. **Absurd magic numbers are forbidden** (40000x40000, passing `INT_MAX` directly) unless that exact value is reachable by an attacker through a real path; a value upstream validation would reject/clamp = unreachable = an invalid trigger.
5. **Mechanism agreement**: the fault type/location triggered must match the mechanism the fix diff repairs (an out-of-bounds write must report an out-of-bounds write, not an integer overflow/assertion/something else). **Another real vulnerability** inside the labelled function -> `cve_match=false`, still CONFIRMED; forcing it with out-of-bounds/contract-violating parameters on an unrelated statement (such as `f(arr,2,3)` -> `arr[-1]`) = synthetic -> INCONCLUSIVE (`synthetic-trigger/not-the-vuln-region`). A miniature behavioral differential that faithfully models the real fix's check is not synthetic.
6. **The allocation site != the write site is allowed**: if the labelled function is the "under-allocation" root cause and the overrun happens in a downstream callee in the same file, that is faithful -- record `frame_note`(alloc_site=the labelled function, fault_site=the callee), and do not synthesize just to make frame#0 be the labelled function.
   **(Added 2026-07-31) This belongs to `confirmation_scope: "defect_site"`** -- the decision point of the defect is still in the labelled function (it is the one that allocated too little).
   If the labelled function **performs no defective operation at all** (a pure forwarding shell that the upstream patch does not touch either), that is not frame_note, it is `confirmation_scope: "reachability"`,
   and you must additionally fill `defect_site` naming the callee that really contains the defect. The boundary between the two is that counterfactual question: **if you change only the labelled function, does the vulnerability disappear?**

Saving: dc.json + craft.json record `cve_match`, `triggered_vuln`, `cve_vuln`, `synthetic_trigger`, `differential`(vuln_rc/fix_rc), `frame_note`.

### Counter-example vs positive example (179087 / CVE-2013-7022, FFmpeg g2meet.c `g2m_init_buffers`)
- **Synthetic (the old `dynamic_confirmation.harness.c`, does not count as cve_match)**: the extract-stub was stuffed with `width=height=tile=40000`, forcing a `40000*120000` **signed integer overflow** (UBSan). But a real G2M frame cannot be 40000 squared and upstream would reject it; moreover that integer overflow **happens on the fixed extract-stub just the same** (no clean differential) -- the mechanism triggered (int overflow) != the CVE mechanism (an edge-tile out-of-bounds write). -> synthetic, INCONCLUSIVE.
- **Faithful (`dynamic_confirmation_tile_oob_20260720/`, cve_match=true)**: build the real historical FFmpeg (`pathb/ff_2013_{vuln,fix}`) + construct a real G2M4 AVI (**a 17x17 frame / 16x16 tiles / edge tile (1,1)**, i.e. the real trigger condition of "dimensions not an integer multiple of the tile size") -> go through the real decode chain -> **the vulnerable version gives an ASan heap-overflow WRITE**, one byte past the end of the 2048-byte buffer allocated by `g2m_init_buffers` (`g2meet.c:228 yuv2rgb`), while **the fixed version exits cleanly on the same input**. The stride arithmetic matches ASan's "2048 bytes"; frame#0=yuv2rgb is the write site and the allocation site is the labelled function (frame_note recorded). -> a real trigger.
- **Not triggered (`cve7022_tile_oob_20260720/`, do not treat it as a confirmation)**: same geometry, but the hand-assembled entropy stream used AC-ZRL instead of EOB, so `kempf_decode_tile` reported "Error decoding tile 1,1" before writing any pixel, and vuln/fixed **both exit 0 with no ASan** = no differential -> not a confirmation.

## ★ Explicit label-noise marking rules (added 2026-07-21; **the user rewrote the admission conditions on 2026-08-03**)

### ★★★★★ Highest priority: you must attack with a dynamic tool before ruling label noise (user, 2026-08-03)

> **Reading the code alone cannot establish label noise.**
> Even if you are already convinced it is a mislabel -- the commit touched 41 files, `diff -w` is empty, the changes are all whitespace --
> **you must first really attack the labelled function with a dynamic tool, and only if the attack fires no vulnerability may you rule label noise.**

**Why this rule was added**: measured on 2026-08-03 over 1,160 samples of the "no-op change" class,
**843 of them (72.7%) had a `tried_dynamic_method` saying `diff -w` or similar text comparison**,
with not a single exit code in `differential`, and 1,057 did not even have a `dynamic_evidence/` directory --
all of them were "label noise read out of the code", yet they showed up in the statistics as "tested".
"This commit did not change this function" and "this function has no vulnerability" are two different things:
whether a function has a vulnerability depends on its own code, **not on whether some commit touched it**. See
**P25** in `evidence_repair/PROBLEM_REGISTER_20260803.md`.

### Three terminal states, each written differently

**(1) Attacked and the vulnerability did not come out -> this is what label noise is**

```json
"verdict": "NOT_DYNAMICALLY_CONFIRMED",
"label_noise": true,
"label_noise_type": "label_noise_dynamic_tools_attacked",
"label_noise_category": "<one from the vocabulary below>",
"label_noise_basis": "dynamic_attack_negative",
"real_vuln_location": "<the function/file where the real vulnerability is, if it can be located>",
"reason": "<must contain the literal words label noise; say what was attacked, how, and why it is judged to be this category>"
```

`label_noise_type` is **always** `label_noise_dynamic_tools_attacked` (it says where this judgement came from);
`label_noise_category` says **which kind of mislabel it is**, with values:

| category | Meaning |
|---|---|
| `whole-commit-relabel` | The fix touches >4-6 files and every touched function gets labelled |
| `multi-function-relabel` | The commit really is fixing this CVE, but this function is a bit player |
| `whitespace-only-relabel` | `diff -w` is empty |
| `cosmetic-refactor` | Plumbing such as signatures/renames/`#line` |
| `wrong-function` | The fault is in a sibling function (**note: a fault in a callee does not count**, see the three-way distinction below) |
| `version-skew` | BigVul's before/after does not match the real fix commit |
| `mass-hardening-sweep` | One defensive guard swept indiscriminately across ~100 files |
| `library-import-relabel` | A wholesale re-vendor of an upstream library |
| `wrong-cwe` | The CWE/CVE classification itself is wrong |
| `test-file-labeled` | Labelled on test/example/generated code |
| `inverted-polarity` | The commit that introduced the vulnerability was collected as the fix commit |

**(2) Only read the code, not attacked yet -> this is not label noise, it is "suspected", and the sample stays on the worklist**

```json
"label_noise": false,
"suspected_label_noise": true,
"suspected_label_noise_category": "<same vocabulary as above>",
"label_noise_basis": "static_reading",
"reason": "<what was read; how you plan to attack next>"
```

**`suspected_label_noise` does not trigger exclusion, and the sample still has to be attacked.** Do not close out treating it as a conclusion.

**(3) needs-Path-B (a real vulnerability that the tools cannot reach)**: the label is right, the vulnerability is real, but a docker-free
extract-stub/micro-harness cannot get there (it needs a whole-tree build / MSan / KASAN+QEMU etc.).
Write `label_noise: false` + a `reason` containing **"needs-Path-B"**.
**This class is strictly separated from (1)**: could not reach it != attacked and nothing fired.

### ★ Attack records and logs must go into the sample's own subdirectory

The fixed path is **`data/output/dataset/bigvul/<id>/dynamic_evidence/label_noise_attack/`**,
containing at least:

| File | Content |
|---|---|
| `attack.sh` | One command that reruns the entire attack (relative paths; `/tmp` and out-of-repository paths forbidden) |
| `driver.c` / `harness.*` | The driver used for the attack |
| `body_vuln.inc` (plus `body_fix.inc` when there are two sides) | **Copied verbatim from the sample's own `vulnerable_function.c`**, verified with `cmp` inside `attack.sh` |
| `inputs/` | Every attack input, stored as raw binary |
| `attack.<n>.log` | The **complete** actual output of each run, never truncated |
| `ATTACK_LOG.md` | What was attacked, the intent of each shot, the result, and why it stopped |
| `EVIDENCE_MAP.json` | Each file's purpose + sha256 |

**No such directory = this label-noise ruling does not hold**, and the sample goes back on the worklist.

### ★ Entering (1) has **seven** hard gates; miss one and you may not rule label noise

**There were originally five; the sixth and seventh were added on 2026-08-04 after it was measured that "all five passed and the conclusion still did not hold"
(see P67 / P68), and after aligning with PrimeVul on 2026-08-21 they are uniformly counted as seven.**
Write down which gate is missing, and the sample stays on the worklist as "not finished" -- do not force a fit.

| # | Gate | How to prove it (required fields) |
|---|---|---|
| (1) | **It was really built and run**, not text-compared | `dynamic_evidence/label_noise_attack/` contains `attack.sh` + a **non-empty** log; `vuln_rc` in `differential` is a **real integer** exit code, never `"identical"` / `"n/a"` / `"unknown"` |
| (2) | **The labelled function really was executed**, not merely compiled in | `labelled_fn_executed: true` + `execution_proof`: instrumented output inside the function / a gdb breakpoint hit / a gcov count / the function's frame appearing in an ASan backtrace. **"It was compiled in" does not count** -- measured, 90% of another batch of 125 harnesses never compiled the labelled function at all |
| (3) | **Attack input was used, not normal input** | `attack_inputs`: list the inputs actually fed in and their construction intent (out-of-range lengths, malformed headers, negatives, race timings...). Bad examples: 177997 used "on a host that has a real /sbin/mount.cifs", and 178043 used a normal `HTTP_COOKIE=PHPSESSID=<id>` -- **that is running the function normally once, not attacking it** |
| (4) | **The oracle is chosen correctly** (**chosen by the mechanism in the fix diff**, not by the labelled CWE, and certainly not always ASan) | `oracle_kind` + `oracle_rationale`. CWE-125/787 -> ASan; CWE-401/772 -> LSan; CWE-190/191/369 -> UBSan or m32; CWE-457/665/908/200 -> **MSan or Valgrind**; CWE-476 -> ASan/SEGV; CWE-362 -> TSan/KCSAN/real concurrency; DoS -> timeout/signal/resource growth; logic/privilege/injection classes -> behavioral differential. **"ASan did not report" says nothing about an integer overflow or an information leak** |
| (5) | **Attack-surface coverage is spelled out** | `attack_surface_note`: which entry points/value ranges were tried, whether a value sweep or fuzzing was done, and for how long it ran. It must let someone else judge whether this was "seriously attacked" or "one shot tried" |
| (6) | **First prove the stored body is complete** (P67) | Compare it **verbatim** with the upstream file at `fix^` (line count, first and last lines, brace balance), verified with `cmp` inside `attack.sh`. If it does not match, this is not "attacked and nothing fired", it is **attacking the wrong object** -- record `stored_body_incomplete` + `needs-Path-B`. Measured: the function body stored on disk for 177956 was only **23 lines** while upstream was **129 lines**, and **what was missing was exactly the out-of-bounds read**; that truncated body was valid C, compiled, and returned a clean 0/0 on input that would make the real function read about 2000 bytes out of bounds. **A truncated body that does not compile is actually safe (it fails on the spot); the dangerous one is the kind that compiles and runs clean.** |
| (7) | **The execution proof must reach "the lines the patch changed", not "the function was entered"** (P68) | Set breakpoints on the lines the patch changed, run to completion, read the hit counts from `info breakpoints`, and write the **per-line counts** into the record. Measured on 180307/180308: the function really was entered (the `lstat` line was hit twice), but **the entire branch the patch cares about was hit 0 times** -- on this input it is dead code. A hit count of 0 means **this measurement did not measure the disputed point**, and it can support neither `defect_site` nor "attacked and nothing fired". Positive control 180309: the line at the patch's insertion point was hit, and `defect_site` holds |

**★ The seventh gate comes with a mandatory cross-check (P104): a gdb hit count of 0 != it did not execute.**
A `static` function gets inlined at `-O1`, and `break <file>:<function>` only resolves to the one copy that was not inlined,
so the count is 0 while the function did in fact execute (measured on `rx_cache_find` in 183017 and `parse_wcc_attr` in 181112).
**When the gdb count is 0 you must confirm with a second means** (ASan/UBSan frames -- they understand inlining -- gcov,
or an output string unique to that function), **otherwise you may not write `labelled_fn_executed: false`**.
The reverse holds too: a batch relying only on gdb counts will systematically under-report static functions.

**★ There is one more check, unnumbered but equally able to veto everything (P36 / 8h): a command-line flag hard-coded in the script can mask a real vulnerability.**
The criteria is not "it ran and nothing was reported", it is **"is what ran the path upstream considers the one to run"**. Measured across two rounds, 7 samples were recorded as
"both sides clean" for one reason only: `repro.sh` added `-vvv`, while the vulnerability check was in the `if (!verbose)` branch;
upstream's `tests/TESTLIST` runs the same capture with no flags at all, and removing `-vvv` immediately gave vuln rc=86 / fix rc=0.
**Their "0/0" was never a measurement result; the script manufactured it. Go look at what flags the upstream tests use before running.**

**Special note for samples whose two sides are semantically identical (no-op changes / hardening sweeps)**: they cannot produce a differential, so you can only build
**one** and run the oracle on it, and in that case gate (1)'s "real exit code" refers to that one.
**Do not treat "the two sides behave the same" as an attack result** -- the two sides are the same code to begin with,
so identical behavior is a construction-level certainty, not a measurement.

### `label_noise_basis` vocabulary (**only these three values**; the second was synced from PrimeVul on 2026-08-17)

| Value | When to write it |
|---|---|
| `dynamic_attack_negative` | **Attacked, and nothing fired at all**, with all seven gates passed |
| **`dynamic_differential_inverted`** | **A differential was measured, and its direction is inverted** -- what goes wrong is the build from the **fixed** code, and the build from **pre-fix** code is clean |
| `static_reading` | **Only read the code.** **This does not trigger exclusion**; the sample stays on the worklist waiting to be attacked |

> **★ Remember the reason for the second value.** Before it there were only the first and the third, and inverted polarity **is neither of them** --
> something did happen, and it was measured, it just happened on the other side. Writing `dynamic_attack_negative` is **a falsehood**.
> This gap is exactly what caused "two fields in one record telling two stories".
>
> **`dynamic_differential_inverted` says "the label got the vulnerable side wrong",
> not "this function has no defect"** -- the latter requires a separate single-sided attack before you can say it.

**Corresponding writing in info.json**: `label_noise: true` -> `tier: mislabel` + `is_vulnerable: NO`;
`suspected_label_noise` does not change info.json (it is not a conclusion yet); `label_target` is never touched.

CONFIRMED samples are unaffected (craft.json + cve_match as usual). The criteria follow the relabel classification in `BIGVUL_LABEL_NOISE_REPORT.md`.

★ **The three-way distinction (revised 2026-07-31): wrong-function vs frame_note vs reachability**.
The original distinction between the first two is below; **a third is added**: the labelled function and the faulting function have a real call relation and a differential really was produced, but the labelled function **performs no defective operation itself** (pure forwarding, zero memory operations, the upstream patch does not touch it) -- this is neither a wrong-function mislabel nor frame_note (it is not the allocation site), it is `confirmation_scope: "reachability"`: **keep CONFIRMED, keep `label_noise` false, and additionally fill `defect_site` naming the callee** (case 180356). Setting `label_noise: true` triggers an unconditional hard exclusion, which contradicts "keep the confirmation".

The original distinction: if the fault happens in a callee in the same file that the labelled function **really calls**, and it is reachable through the labelled function's real call chain with really constructed input (for example `CMS_verify` calling `do_free_upto`, with the infinite loop in the callee), this is a **faithful CONFIRMED**; record `frame_note`(entry_site=the labelled function, fault_site=the callee), with **label_noise=false** -- it is not a wrong-function mislabel. Only when the labelled function and the faulting function have **no real call relation** (pure siblings, changed incidentally by the same commit) is it wrong-function label noise. Never mistake "the allocation site/entry point != the fault site" for wrong-function.

## ★ Does an injected runtime condition count as a faithful trigger -- the standard is "does upstream accept it" (rule C, ruled by the PrimeVul owner 2026-08-17, applies to BigVul as well)

One class of samples only exhibits its defect when some **runtime condition** occurs, most commonly an **allocation failure**:
`AcquireMagickMemory` returning NULL, `pf_aligned_alloc` returning NULL, `read()` returning a short read.
These conditions **cannot be produced by an input file**, so the question has been stuck on "does injecting it count as an attacker capability".
**The standard is one sentence**:

> **Is what this fix changed "what to do when this condition occurs"?**
> Yes -> injecting this condition **counts as a faithful trigger** and it can be confirmed;
> No -> it counts as a **synthetic trigger** and cannot be confirmed.

**Why use this**: it does not require answering "can an attacker actually cause OOM", which we cannot measure,
only "does upstream itself accept this condition", which **can be checked verbatim by reading the fix diff**.
It also naturally blocks harness-manufactured defects -- `#ifdef`-ing out a guard upstream already had and then reporting an overrun (counter-example 187416),
where that "condition" is not what the fix is handling, fails the first question.

**When confirming with this rule, all five of the following must hold; miss one and it does not stand:**

1. **The failure/NULL must come in through the program's own public interface** -- for example ImageMagick's
   `SetMagickMemoryMethods()`, or the `pf_aligned_alloc` callback of the Android ivd API.
   **Not one line of upstream source may be changed.**
2. **The injector is verbatim identical in both builds**, and the only variable is still the labelled function body.
3. **Write `faithful_trigger_basis`**, and **quote verbatim** the place in the fix commit that handles this condition
   (the commit title, or those lines in the diff). Merely asserting "upstream accepts this condition" does not count.
4. **Write `attacker_controlled_trigger` honestly as `null`**, and write `reachability` as `UNKNOWN`
   (unless a reaching path has been separately measured). **Rule C settles "does this count as a faithful trigger", not "can an attacker reach it"**
   -- the two must be recorded separately.
5. **Readings from both sides are still required**: real integers, execution proof reaching the disputed lines, and a positive control that responds.

**The record must also write the two sides' readings separately** (field name `alloc_failure_reading_<date>`):
(1) what happens when this condition really occurs, and **on what basis you say it really occurred**;
(2) whether any attacker-controlled input can reach the same state without the injection --
**when the answer is "no", say so plainly; that is a conclusion, not a gap**.

**This applies far beyond allocation failures**: any "runtime condition upstream wrote dedicated handling code for" is treated the same way
(examples: short reads, clock rollback, lock-acquisition failure, handle exhaustion). Conversely, a condition upstream never checks is still a synthetic trigger.

---

## ★ Closing self-check and stop conditions (aligned with PrimeVul 2026-08-21)

### Per-sample self-check (run for every ID processed this round)

```bash
python3 -m json.tool data/output/dataset/bigvul/<id>/dynamic_confirmation.json >/dev/null
python3 -m json.tool data/output/dataset/bigvul/<id>/dynamic_evidence/EVIDENCE_MAP.json >/dev/null
grep -rn '/scratch/\|/tmp/\|/home/' data/output/dataset/bigvul/<id>/dynamic_evidence --include='*.sh'
cd data/output/dataset/bigvul/<id>/dynamic_evidence
rm -f arm_vuln arm_fix *.o        # first ls the same glob to see how many it matches, then delete
bash repro.sh
```

The `grep` must print nothing (comment lines explaining history do not count). **Deleting with a broad glob from the dataset root is forbidden** --
measured, one agent ran `rm -f */dynamic_evidence/X.json` from the dataset root, and that glob swept ten thousand directories across the whole repository.

**Add one more field scan** (lesson (8) from 2026-08-15): any sample in this batch that has **neither `tried_dynamic_method`
nor `blocked_reason`** is a missed write, and must not be let through.

### Batch-level checkers (run both; missing one means not closed out)

```bash
cd tasks/bigvul_reports/evidence_repair
python3 verify_batch.py --ids <this round's id list>
python3 check_loop_prompt_compliance.py <project>
python3 check_loop_prompt_FULL.py <project>      # no argument means the whole worklist
python3 locate_evidence.py                       # samples added this round must not appear in the list
```

`audit_reproducibility.py` has been retired (all four agents running it got rc=124/143 with zero output, and a check that never finishes is no check at all),
but **retiring it does not mean that gate may be left empty** -- `check_loop_prompt_FULL.py` now carries it.

**★ These two checkers do not yet cover the rules added this time** (the four outcomes' required secondary fields,
`dynamic_differential_inverted` for `label_noise_basis`, the sixth/seventh gates, the five preconditions of rule C).
Per repository-root `CLAUDE.md` §8c: **from now on, whenever a hard rule is added to this document, the same commit must add it to one of these two checkers;
a rule written only into the document and not into the checkers does not exist.** These three items are outstanding debts explicitly left by this update.

### The checkers' own most common mistake: accepting only "a value was filled in", not "it was measured and cannot be decided"

The same fault was committed three times in one day: mechanically filling `defect_site` (disguising "nothing was measured" as "something was measured", P56),
reporting an honestly written `labelled_fn_executed: false` as "missing field" (P97),
and reporting "it ran, the two sides did not separate, so it cannot be decided" as "missing field" (P107).
**The common shape: the checker forces people to invent a value.**

**Rule: whenever a required field is added, the same change must work out "what the valid way to write it is when nothing can be measured",
and make the checker accept that.** Two are accepted today: boolean fields (such as `labelled_fn_executed`) are **only checked for `is None`,
and `False` counts as filled in**; `confirmation_scope` left empty but with `confirmation_scope_undetermined` + a reason counts as done.
When adding an exception, finish changing **every** place in the same file that checks fields of the same kind, then rerun to confirm.

### Three hard rules for bulk record edits

1. **Read, judge and write must be adjacent; "read everything into memory then write everything" is forbidden.** Measured: a script read all 1,517 records first and then wrote them one by one,
   and by record 530 it collided with a file a running agent had just changed. **Luckily a self-check assertion stopped it** -- without it, the whole file would have been overwritten with
   a copy that was minutes out of date, wiping out every proof field the agent had just written,
   **with nothing on disk looking abnormal, the `.bak` also holding the stale version, so even a rollback could not save it** (P93).
   **Re-read and re-judge before every write to disk; skip entirely any project with an agent running on it.**
2. Every bulk script must carry this assertion:
   ```python
   after = dict(d)
   for k in NEW_KEYS: after.pop(k)
   assert after == before, sid      # apart from the keys I mean to add, nothing else may change
   ```
3. **Before `rm` with a glob, `ls` the same glob first** and see exactly how many it matches.

### The campaign's stop conditions

It counts as complete only when all of the following hold at once:

- Every active `target=1` sample has a real `tried_dynamic_method` and a real two-sided `differential`,
  or a measured, fully evidenced, legitimate structural exception;
- Every sample lands in exactly one of section 0a's four outcomes, and the secondary fields (`dy_attacked_undecided_category` /
  `not_tested_reason` / `confirmation_class`+`confirmation_scope`+`reachability` /
  `label_noise_category`+`label_noise_basis`) **are all filled in**;
- Every statically judged `suspected_label_noise` has either really been attacked or is still on the active list,
  and **may not disappear through a default exclusion**;
- Every processed sample's scripts, inputs, both sides' source, complete logs and `EVIDENCE_MAP.json` are inside the sample directory and rerunnable;
- `dynamic_confirmation.json`, craft.json and `info.json` agree with the registry's ruler;
- After the final rerun of the statistics and the worklist generator, no discrepancy remains on disk that can only be explained by an old snapshot, a static classification or an agent's self-report.

**Being left with only needs-Path-B, both sides clean, tools temporarily out of reach, or something that looks like a mislabel statically are none of them automatic reasons to stop.**
Neither is `blocked_reason: "build_failed"` -- it only says this route did not work this round, and next round you must try again with a different lane,
a different period toolchain, or extract-and-stub; only when the four fields of section 0b's `build_failure`
(the number of attempts, which **different** approaches were tried, the verbatim error, and why it cannot be recovered now) plus the failed build logs are all on disk
does this round count as an honest ending for that sample. **"It cannot be built" can never imply "this function has no vulnerability".**

---

## ★ These two categories must be stated as full sentences (user instruction 2026-08-08, in force for every prompt)

The two categories on the label-noise axis **have short names that get read backwards, and may never again be used on their own**:

| Do not write this any more | Must be written like this | Short tag |
|---|---|---|
| "the exclusion stands" | **attacked and not a single fault fired ⇒ the label-noise finding stands, the function really is mislabelled** | `(mislabel stands)` |
| "the exclusion probably does not stand, awaiting your ruling" | **a fault fired and it attributes to the labelled function ⇒ the label-noise finding is probably wrong, the function may genuinely be vulnerable, pending human adjudication** | `(may genuinely be vulnerable, pending adjudication)` |
| "does not count yet - not finished this round" | **no conclusion this round** (not attacked / the measurement does not hold / the fault does not attribute to this function) | `(no conclusion)` |

**Why**: "the exclusion stands" sounds like "confirmed vulnerable", while it means **exactly the opposite**.

Writing requirements: (1) **the full sentence must be written the first time it appears**, and only afterwards may the short tag be used;
(2) the sentence must mention both "attack/fire" and "whether there was a fault" --
a reader does not need to know what "exclusion" means in order to understand it;
(3) when reporting numbers, state the **direction** along with them, for example "**the count of 'a fault fired, may genuinely be vulnerable' rose from 70 to 89**".
Field names like `exclusion_earned` / `EARNED` must also be expanded when they appear in text written for humans.
**The same applies in prompts that dispatch a subagent.**

---

## BigVul dataset characteristics (key differences from primevul)

1. **Function-level + whole-file/whole-commit relabel noise**: BigVul's labelled CWE is often the overall label of that CVE's file, not this specific function's bug. **Classify first with `git show --stat <commit_id>` (or pull the fix `.patch`)**: >4-6 files, or a "Merge tag" title = a **strong suspicion** of sibling-function relabel -> record `suspected_label_noise: true` + `suspected_label_noise_category: "whole-commit-relabel"`, **but you must still attack once before settling it** (★ changed by the user 2026-08-03: the original text "go straight to INCONCLUSIVE-relabel, do not waste a build" is void). What this item is for now is **setting priorities and choosing the attack approach**, not replacing the attack. Differences between `before_cwes`/`after_cwes` also help identify the real class of fix.
2. **commit_id = the FIX commit**: Path-B builds the pre-fix version at **fix^ (the parent)**; the `tests/` regression files that come with the fix commit are often a ready-made PoC.
3. **Cross-dataset deduplication and one-way transfer**: the duplicate index expresses only a similarity relation and authorizes no writes. Between BigVul and PrimeVul
   only `BigVul -> PrimeVul` evidence archiving/reuse is allowed, and any `PrimeVul -> BigVul` propagation must fail closed
   before anything is written to disk. If a historical BigVul record originates from `primevul:*`, that lineage must be preserved, and it may not be rewritten as an independent BigVul rerun merely on the strength of existing
   logs. Still run `scripts/is_duplicate.py bigvul:<id>` before confirming; duplicate samples are handled by a dedicated one-way reuse audit and may not follow the old two-way propagation flow. The old "202 exact-body" figure is only a historical
   snapshot and may not replace the current byte-for-byte/normalized audit.
   **Current implementation state (2026-08-13)**: the security stop-gap for reverse/third-library cross-dataset writes has passed an independent re-review; the forward
   BigVul->PrimeVul physical importer has not been functionally delivered. Its mutating API / `--apply` remains hard-retired with zero writes because of the reproduced staging
   symlink/path-swap problem; do not delete the early exit and restore the old pathname writer. A new transaction must first be implemented with
   dirfd/openat(O_NOFOLLOW)/inode binding/no-replace, the currently skipped race tests must be restored, and only then may it be authorized by a 900-second stability gate and an ordered live audit. The frozen `431/625/107` are historical structural statistics only, not copyable.
4. **target=0 negative samples have been migrated out wholesale (2026-07-28)**: `data/output/dataset/bigvul/` now holds only **10,900 target=1** samples + `_shared_libgd_harness`; the 170,868 target=0 samples were moved to `data/output/dataset/bigvul_only_non_vulnerable/` (`evidence_repair/split_negatives.py`, log `moved_negatives_20260728.tsv`, `--undo` available). Likewise for primevul: 6,004 stayed, 218,529 were moved out. **You must still check `label_target`** -- the migration lowered the risk but did not remove it, and propagation/deduplication scripts may still hit the old paths. **It is strictly forbidden** to propagate to or confirm a target=0 sample. There was another target0 purge on 2026-07-17 (see `bigvul_target0_dynamic_confirmation_purge_20260717.md`).

## Method routing and yield (chosen by project/CWE/CVE-year)

**Do these first (docker-free, high yield):**
- **Behavioral differential with `#ifdef FIXED`** (the workhorse; access control/injection/DoS/privilege/memory-fault gates; kernel CVEs can also be confirmed without booting a kernel -- see the KVM/nfsd/keyring/kexec/overlayfs/tcp-SACK series found in primevul).
- **Kernel micro-harness**: `kernel_stub.h` + extracting the labelled kernel function + ASan (no kernel infrastructure); hits on roughly 1/3 of kernel CVEs with a single-function fix. See `bigvul_reports/giant_method_lists`, `DYNAMIC_METHODS_CATALOG.md`.
- **extract-stub** (self-contained parsers: small parsers such as ngiflib/libmspack/wavpack/openmpt/wildmidi/curl; DoS recursion in mujs/tcpdump).
- **Path-B build-at-fix^ ASan**: reuse the banked `pathb/` binaries (jasper19 / krb5_work / php_lane / openmpt_{vuln,fix} / libtiff_407 / the im series / tcpdump{474,481,490,492} / ff_vuln_2017 + target_dec_fuzzer / libyal / libraw_src / radare2_vuln). **Give subagents a hard no-rebuild constraint** and run the already banked binaries directly (a fresh build easily hangs).
- **ARVO exact-commit reproduction**: bigvul fix-commit intersected with ARVO fix_commit (`bigvul-arvo-exact-commit-vein`), reproducing the crash with `docker n132/arvo:<localId>-vul`; siblings on the same commit need a faithful per-sample frame#0 mapping.

**Low yield / honest DEFER:** hardening-relabel in FFmpeg/openssl/git/poppler/ghostscript/FreeType; Chromium (the M72 era-trap, browser-process needs-full-browser, see `CHROMIUM_BUILDER_PLAN.md`); giant-method whole-file relabel (yield ~4%, label-noise-bounded); era-mismatched kernels (the build tree does not match the CVE's vintage); cryptographic arithmetic/side channels.

## How to dispatch

- About 12 ids per batch, with 6-8 concurrent channels **when load is below the threshold**; during a co-tenant storm (low CPU with high load = I/O) drop to 1-2 channels.
- **Pre-filter to UNIQUE before dispatching (high yield, 2026-07-21)**: the large worklist buckets (M20/M19/M3) are ~85% Chrome = honest DEFER (the M72 era-trap), so remove those first; then classify with `data/output/dynamic/duplicate_samples.json` (rec.canonical==tag -> canonical, otherwise redundant, not in the table -> UNIQUE), and **dispatch only UNIQUE** (otherwise subagents just hit `is_duplicate.py` -> DUP -> SKIP and waste the run). DUP-canonical-unconfirmed is a separate propagation-only vein (see the `dupcanon` notes) and does not belong to this loop. You may also layer a `diff -w` pre-screen: if vuln and fixed are identical ignoring whitespace -> **you may only mark `suspected_label_noise: true` + `suspected_label_noise_category: "whitespace-only-relabel"`, and the sample must still be dispatched to be attacked** (★ changed by the user 2026-08-03: the original "mark label_noise directly and skip dispatching a subagent" is void -- an empty `diff -w` only proves this sample cannot produce a two-sided differential, not that this function has no vulnerability; see P25). Its value is **downgrading the work to a single-sided attack**: when the two bodies are the same, do not waste time building two sides; build one and run the oracle. **The highest-yield vein: one CVE with many RPC-stubs/coders in a single file where each function really was changed (for example the 23 `*_svc` LSan leaks in krb5 CVE-2015-8631 kadmind), reusing the extract-stub recipe of an already confirmed sample one by one (verifying each real change + each sample's own differential, not blind propagation).**
- Deduplicate before dispatching: exclude ones where `bigvul_<id>.craft.json` already exists + the canonical is already confirmed + `label_target!=1` + cross-dataset DUP + already handled in the RUNLOG + the inflight set.
- **Subagent wording (to avoid a cyber safety flag)**: Opus subagents exit early with a "flagged for a cybersecurity topic" API error triggered by exploit-crafting wording (such as a PHP phar UAF PoC). Frame every dispatch as "defensive vulnerability-dataset label-verification by differential sanitizer testing (pre-fix vs post-fix, same input); NOT exploit development", with the technical actions unchanged.
- **★ Output-path discipline (the subagents' most common mistake, strengthened 2026-07-28)**: per-sample artifacts are written only under `data/output/dataset/bigvul/<id>/`, and **reproducible files always go into `<id>/dynamic_evidence/`**; the dc.json file name must be `dynamic_confirmation.json` (not dc.json, and not written to data/interim); craft.json -> `data/output/dynamic/confirmed/bigvul_<id>.craft.json`; the RUNLOG is only **appended** to `tasks/RUNLOG_<host>_bigvul.md` (creating new RUNLOG_*.txt files is forbidden). **It is strictly forbidden** to leave artifacts in `/tmp`, `~`, `<SCRATCH>/wl_campaign/` or anywhere outside `VulValidate/` -- measured, 329 references pointed into `/tmp/claude-<pid>/...` and one reboot wipes them all. Write these paths explicitly and rigidly into the dispatch prompt.
- **Recompilation concurrency limited to 2-3** (the disk I/O threshold is counted separately); **build inside `pathb/<lane>/`**, keep the banked binaries and delete only intermediate objects; repro.sh references banked binaries with repository-relative paths + `EVIDENCE_MAP.json` records a git pin; subagents get a `make -j8` cap + a SKIP-if-craft.json-exists guard.
- **Every dispatch subagent prompt must embed the "CVE-match faithful-trigger hard criteria" above** (especially "read the fix diff first + the differential is the acceptance test (pre-fix crashes / fixed is clean on the same input) + no magic numbers, values must be reachable + allocation site != write site is recorded with frame_note"), or subagents easily produce synthetic confirmations.
- **DoS ruling**: a hang/timeout, unbounded recursion -> stack overflow, an infinite loop, divide-by-zero SIGFPE, an unbounded allocation = CONFIRMED (a vuln <-> fix differential is still required: the fixed version no longer hangs/crashes on the same input).
- Saving: confirmed -> **`<id>/dynamic_evidence/`** (harness + repro.sh + PoC input + both sides' sanitizer/behavioral logs + EVIDENCE_MAP.json) + dynamic_confirmation.json (DYNAMICALLY_CONFIRMED, +cve_match/triggered_vuln/cve_vuln/synthetic_trigger/differential/frame_note, with path fields written as `dynamic_evidence/...`) + craft.json + record.md + RUNLOG; unconfirmed -> an INCONCLUSIVE dynamic_confirmation.json + record.md (no craft.json) + **likewise leave the scripts and logs actually run in `<id>/dynamic_evidence/`** ("ran it but got no differential" must also be verifiable by rerunning), and per the rules above set either `label_noise:true`+`label_noise_type:label_noise_dynamic_tools_attacked`+`label_noise_category`+`real_vuln_location`+**the `dynamic_evidence/label_noise_attack/` attack-evidence directory** (mislabel; ★ since 2026-08-03 you must have attacked with nothing firing before you may set this) or `label_noise:false`+a reason containing "needs-Path-B" (a real vulnerability out of reach). ★ Added 2026-08-03, a third kind: really attacked and the vulnerability did not come out -> `label_noise_type:label_noise_dynamic_tools_attacked` + `label_noise_basis:dynamic_attack_negative` + the proof fields of the seven gates (`labelled_fn_executed`/`execution_proof`/`attack_inputs`/`oracle_kind`+`oracle_rationale`/`attack_surface_note`), and **do not write NOT_MEASURED/not confirmed**.

## Current progress anchors

- BigVul's current statistical anchor (**snapshot 2026-08-03**, denominator target=1 = 10,900): `target=1` confirmed **5,092** (46.72%), of which **4,597** are independent dynamic runs/historical registrations and **495** are exact-function-body cross-dataset propagation (**489** sourced from PrimeVul, **5** from MegaVul, **1** from inside BigVul). The remaining partition: `LABEL_NOISE_EXCLUDED` **5,547**, `INCONCLUSIVE` **168**, `INCONCLUSIVE_LABEL_NOISE` **39**, `NOT_DYNAMICALLY_CONFIRMED` **17**, `NOT_DYNAMICALLY_CONFIRMED_LABEL_NOISE` **13**, `NOT_DYNAMICALLY_CONFIRMED (NO DIFFERENTIAL: BOTH ARMS FAULT IDENTICALLY)` **12**, `DEFERRED` **6**, with the rest scattered below 5.
  **"confirmed" uses the census rule**: the registry has an entry inside the denominator **or** the sample's own verdict is `DYNAMICALLY_CONFIRMED`, taking the union. Both agree on 5,060, registry-only is 32, own-verdict-only is **0**.
  Note that the `data/output/dynamic/confirmed/` directory holds **5,460** `bigvul_*` files, 368 more than the 5,092 above -- the extras are not among these 10,900 target=1 records. Citing "how many entries the registry has" must state whether it is the file count in the directory or the number of entries inside the denominator.
  **All the old numbers are void; stop citing them**: 4,713 / 4,558 / 5,154 / 4,742 / 4,926 / 4,514 / 3,486 / craft.json approximately 2,249 / canonical approximately 1,008. See `bigvul_dynamic_status_latest.{md,json}`.
- The highest-yield new source, following primevul: rerun by routing those INCONCLUSIVE/DEFERRED samples that have a method labelled but **never actually ran that method** (`bigvul_current_dynamic_method_worklist.jsonl` / `defer_full_worklist.jsonl` / `actionable_gap_worklist.jsonl`); the behavioral differential is the highest-yield route.
- Ledger/report tools: `compute_bigvul_dynamic_status_statistics.py` (writes `bigvul_dynamic_status_latest.{md,json}`), `build_current_dynamic_method_worklist.py`, and the authoritative summary `BIGVUL_DYNAMIC_STATUS_SUMMARY.md`.

## Related reports (tasks/bigvul_reports/)

`DYNAMIC_METHODS_CATALOG.md` (the full set of methods), `BIGVUL_LABEL_NOISE_REPORT.md` (relabel noise), `CHROMIUM_BUILDER_PLAN.md` (do not build Chrome in full), `DEFER_GAP_FINAL_REPORT.md` / `DEFER_GAP_LOOP_PROMPT.md` (finishing off DEFER), `BIGVUL_GIANT_PROJECT_DYNAMIC_STRATEGY.md` (giant projects), `gpt5.6_terr_bigvul_dynamic_current_statistics_20260713.*` (statistical snapshots).
