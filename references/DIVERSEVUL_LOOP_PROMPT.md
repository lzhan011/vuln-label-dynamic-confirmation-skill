# DiverseVul Dynamic Confirmation /loop Prompt

_Rewritten from the structure and style of BigVul's `BIGVUL_LOOP_PROMPT.md`, adapted to the reality of DiverseVul: no reliable CVE/CWE, with vulnerable/fixed function pairs as the ground truth.
**Extended on 2026-08-18 following the logic of `tasks/primevul_reports/LOOP_PROMPT.md`**: the four outcomes, the seven gates, the `dy_attacked_undecided_category` vocabulary, rule C,
judging scope from the stack shape. DiverseVul's own paths, sample keys, worklist ruler, per-project hit rates and Path-B recipes are unchanged._

> **Priority when things conflict**: repository-root `CLAUDE.md` > this file > `BIGVUL_LOOP_PROMPT.md`.
> Any general criteria not written here (attribution, log reading, resource limits, wording)
> follow `CLAUDE.md`.

<!-- CURRENT-SNAPSHOT-START -->
## Current auto-updated snapshot (2026-07-23)

True source of the statistics: `diversevul_dynamic_status_latest.json`. `target=1` **9,604**; `CONFIRMED` **733**; `INCONCLUSIVE` **2**; `UNTOUCHED` **8,867**; `LABEL_NOISE_EXCLUDED` **0**.

label-noise: explicitly **0** in the result files, **0** in the maintained ledger, **0** after merge and dedup. Historical body text is not used as the current count.
<!-- CURRENT-SNAPSHOT-END -->

---

# Part One · Highest-priority overriding rules (where later older wording conflicts with this part, this part wins)

## A. There are only four outcomes (introduced 2026-08-18 following PrimeVul's ruler)

When reporting outwards, writing records, or computing statistics, **only the following four outcomes
are allowed**. Every `target=1` sample falls in exactly one of them, and the four numbers add up to
the denominator **9,604**:

| Outcome | Meaning | Secondary fields |
|---|---|---|
| `CONFIRMED` | The labelled function triggered a real defect on a faithful input | `confirmation_class` (one of three tiers), `confirmation_scope`, `reachability`, `cwe`/`cwe_chain`/`cwe_basis`, `cve_match` (for DiverseVul always `undeterminable`) |
| `LABEL_NOISE_EXCLUDED` | The label is overturned: attacked with a matching tool and nothing fired while all gates are in place, **or** a differential was measured but its direction is inverted | `label_noise_category`, `label_noise_basis`, `label_noise_type`, `real_vuln_location` |
| `DY_Attacked_But_can_not_decide_confirmed_or_label_noise` | **A dynamic tool really did attack it and readings from both sides were obtained, but this measurement cannot decide between confirmation and mislabel** | `dy_attacked_undecided_category` |
| `BUILD_FAILED` | **Not measured**: cannot be built, cannot be reached, or simply has not been tested yet | `build_failed_reason` |

**The following strings are no longer outcomes**, and not one of them may appear in a results partition: `INCONCLUSIVE`, `UNTOUCHED`, `NOT_DYNAMICALLY_CONFIRMED`, `DEFERRED`, `NEEDS_PATH_B`,
`NOT_TRIGGERABLE_AS_LABELED`, `<MISSING_OR_UNPARSEABLE_VERDICT>`. They may stay in the `verdict` field of `dynamic_confirmation.json` / `inspection.json` as history.

**Whether a sample lands in the third or the fourth outcome turns on a single question:
was this sample really attacked by a dynamic tool, and were readings from both sides obtained?**

- **Attacked** → the third outcome, with `dy_attacked_undecided_category` saying which kind of
  "cannot decide" it is;
- **The attack did not succeed / has not been attempted** → `BUILD_FAILED`, with `build_failed_reason` saying which kind of "not measured" it is.

> **★ The word `UNTOUCHED` is especially dangerous in DiverseVul.** In the snapshot it is **8,867**,
> 92% of the total. It reads like a neutral "not its turn yet", but it is the same thing as
> `BUILD_FAILED`'s `not_measured_yet` — **these samples must stay on the worklist**; this is not a
> stable classification.

### `dy_attacked_undecided_category` vocabulary (**mandatory**, must not be left empty)

These samples have exactly one thing in common: **a dynamic tool really did attack them and readings
from both sides were obtained.** The reasons for "cannot decide" are completely different from each other, and so is the next action — **reporting only the total of the third outcome is meaningless;
the distribution of this table must be given alongside it.**

| Value | Meaning | What can be concluded about this function |
|---|---|---|
| `nominated_awaiting_adjudication` | Readings from both sides obtained, **and a legal confirmation class has already been nominated** | **What is owed is an adjudication, not a measurement** |
| `attacked_no_trigger` | Both sides really built and run, attacked with a matching tool, nothing fired, but one or more of the seven gates is still missing | **This is a conclusion about this function**; once the gates are filled it should turn into `LABEL_NOISE_EXCLUDED` |
| `guard_never_evaluated` | The disputed lines were never executed at all | **Exactly the opposite: that "clean" is not a conclusion about this function.** Change the input so they execute |
| `decision_diff_no_impact` | There is a clean two-sided decision differential at the patch point, but no security consequence fired | Most likely to flip to a confirmation after wiring up a real consumer or changing the oracle |
| `no_security_consequence` | There is a real behavioural difference, but no security consequence | Needs human adjudication |
| `fault_not_attributable` | A fault fired, but it cannot be attributed to the labelled function (sibling function / caller / the harness's own code) | Neither clean nor triggered |
| `inverted_polarity` | Inverted polarity: the side that faults is the `fixed_function.c` one | Terminal state |
| `no_differential_possible` | The two function bodies are semantically identical, so by construction both sides are the same code | Terminal state; **a single side must be attacked on its own to judge whether this function has a defect** |
| `synthetic_trigger` | The trigger condition is manufactured by the harness and a real input cannot produce it | Switch to a real input |
| `reachability_unproven` | The fault is inside the function body, but it was not proved that an attacker can reach it | Supply a real entry path |
| **`out_of_closure_sink`** | **Frequent in DiverseVul**: the defect is real, but the sink lies outside the labelled function's real call closure | **Not a mislabel**; move to Path-B |
| **`out_of_scope_for_differential_testing`** | The fix by definition produces no observable differential (constant-time hardening, entropy-source strengthening, revocation-state refresh) | **Neither a mislabel nor needs-Path-B**; see Part Two |
| `single_arm_only` | Only one side could be built and run; the second side does not exist structurally | Handle by the single-side route |
| `unclassified_reason` | A reason was written but the existing matching rules do not recognize it | **Fix the rules, not the sample** |

### `build_failed_reason` vocabulary (**mandatory**, must not be left empty)

**Not a single sample in this bucket has been measured successfully**, so it supports no conclusion whatsoever about these functions — it says **our capability or progress is insufficient**, and these
samples **must stay on the worklist**.

| Value | Meaning |
|---|---|
| `could_not_build` | Repeated attempts still cannot build or reach it (`attempts` ≥ 2, and **different** routes must be listed) |
| `dependency_closure_missing` | **Frequent in DiverseVul**: `dependencies/` lacks the real helper functions/types, so a faithful trigger cannot be constructed |
| `folder_not_materialized` | The sample folder was never materialized (about 5,139 positive samples); the source must be taken from the full JSONL |
| `suspected_only_never_attacked` | Only the code was read and it looked like a mislabel; not a single tool was ever run |
| `not_measured_yet` | Not yet measured (**essentially all of the current 8,867 `UNTOUCHED` belong here**) |
| `no_reason_recorded` | The record does not say at all why it stopped here |

**Do not write strings such as `differential.hv_rc: "build_failed"`.** Exit-code fields only ever hold
integers; if no integer came out then there was no differential this time, and the reason goes in the fields above.

## B. Before ruling label noise, a dynamic tool must really have attacked it

`diff -w` identical, a commit that only changes whitespace, a patch that did not touch the labelled
function, a suspected wrong-function — all of these can only be a **static suspicion** and cannot settle the case directly. At the static stage write:

```json
{
  "label_noise": false,
  "suspected_label_noise": true,
  "suspected_label_noise_category": "wrong-function",
  "label_noise_basis": "static_reading"
}
```

**Only when all seven of the following gates pass after a dynamic attack** may `label_noise:true` be
written:

1. Really built and run; the log is **non-empty and complete**, the exit code is an **actual integer**;
   a re-runnable script is on disk;
2. `labelled_fn_executed:true`, proved with in-function instrumentation, a gdb breakpoint, gcov or a sanitizer stack that the function **really executed** — **"it was compiled in" does not count**;
3. `attack_inputs` lists the malformed inputs and the attack intent of every shot; **running it once
   on a normal input is not an attack**;
4. `oracle_kind` and `oracle_rationale` **match the observed defect mechanism**: OOB→ASan, leak→LSan, integer UB→UBSan, uninitialized→MSan/Valgrind, logic/permission→behavioural
   oracle. **DiverseVul has no CWE to fall back on, so this gate can only go by mechanism**;
5. `attack_surface_note` states the entry point, the value ranges, the scanning/fuzzing duration and the reason for stopping;
6. **Stored-body integrity check**: compare `vulnerable_function.c` word for word with the upstream
   function at the same version (line count, first and last lines, brace balance). If they do not
   match then this is not "attacked and nothing fired", it is **attacking the wrong object** — record `stored_body_incomplete` + `BUILD_FAILED`;
7. **Prove execution reached the disputed line/branch of the diff**; merely entering the function
   while the disputed line is hit 0 times **does not support a negative conclusion**.

> **★ Gates 6 and 7 were imported from PrimeVul on 2026-08-18; remember why.**
> Gate 6: in practice a sample's stored function body on disk was truncated, and **what was missing
> was exactly the out-of-bounds part**, while that truncated body **was legal C, compiled fine, and
> returned 0 perfectly cleanly on inputs that would make the real function go out of bounds**.
> **Attacking a truncated stored body is guaranteed not to fire anything**, which produced a
> conclusion that passed all five gates and yet did not stand at all.
> **A truncated body that does not compile is actually safe** (it fails on the spot); the dangerous
> one is the kind that compiles and runs clean.
> Gate 7: in practice a sample's function **really was entered**, but **the whole branch the patch
> cares about was hit 0 times** — on that input it is dead code. **A gdb hit count of 0 must be
> double-checked with gcov or sanitizer inlined frames**, because a `static` function inlined at
> `-O1` makes the gdb count falsely report 0.
>
> **DiverseVul workaround**: gate 6 was originally "compare word for word with upstream at `fix^`".
> When upstream cannot be found, record `stored_body_verified: "no_upstream_reference"`, **and
> `label_noise:true` may not be written** — because a truncated stored body cannot be ruled out.
> When a `commit_id` exists, it must be checked against upstream.

Attack evidence always goes in `data/output/dataset/diversevul/<id>/dynamic_evidence/label_noise_attack/`:
`attack.sh` (relative paths), the driver/harness, the body copied word for word from
`vulnerable_function.c` and verified with `cmp`, `inputs/` (binaries as-is), **the complete log of every shot**, `ATTACK_LOG.md`, `EVIDENCE_MAP.json`.
**Without that directory the label-noise ruling does not stand**, and the sample must stay on the worklist.

A compliant negative dynamic-attack record:

```json
{
  "label_noise": true,
  "label_noise_type": "label_noise_dynamic_tools_attacked",
  "label_noise_category": "<one of the category vocabulary>",
  "label_noise_basis": "dynamic_attack_negative",
  "real_vuln_location": "<write it if it can be located>",
  "reason": "<must contain the literal words label noise; explain the attack and why it stopped>"
}
```

### `label_noise_basis` vocabulary (**only these three values**)

| Value | When to write it |
|---|---|
| `dynamic_attack_negative` | **Attacked, and nothing fired at all**, with all seven gates passed |
| **`dynamic_differential_inverted`** | **A differential was measured and its direction is inverted** — the one that fails is `fixed_function.c`, while `vulnerable_function.c` is clean |
| `static_reading` | **Only the code was read.** **This does not trigger exclusion**; the sample stays on the worklist waiting to be attacked |

> **★ The second value was introduced 2026-08-18.** Inverted polarity is **neither of the first two** —
> something did happen and it was measured, it just happened on the other side. Writing
> `dynamic_attack_negative` is **a lie**.
> **It says "the labelling got the wrong side", not "this function has no defect"** —
> the latter requires another single-side attack before it can be said.

Category vocabulary: `whole-commit-relabel`, `whitespace-only-relabel`, `cosmetic-refactor`,
`wrong-function`, `version-skew`, `mass-hardening-sweep`, `library-import-relabel`,
`wrong-cwe`, `test-file-labeled`, `multi-function-relabel`, `inverted-polarity`, `defensive-hardening-no-bug`.
**When DiverseVul has no reliable CWE, `wrong-cwe` usually does not apply.**

## C. The differential is the standard route, but not the only confirmation route

- The `vulnerable_function.c` side faults, the `fixed_function.c` side is clean: **standard confirmation**.
- Both sides can be made to trigger the same real defect on a faithful input: **still confirmable**, write `fix_arm_also_vulnerable:true`, `defect_present_both_arms:true`,
  `confirmation_class:"OTHER_DEFECT_UNFIXED"` and `fix_arm_signal`. The prerequisites are that the defect is entered from the labelled function (inside its body or in
  its real call closure), that it is demonstrated by a faithful input plus a sanitizer/equivalent
  oracle, and that the `vulnerable_function.c` side can trigger it **by itself**. A fault that occurs only in a caller, or in a sibling with no call relationship, does not count.
- Neither side faulting **cannot be a confirmation**.

> **★ Do not take "both sides behave the same" as a measurement result.** When the two function
> bodies are semantically identical (`diff -w` empty), both sides are the same code and identical
> behaviour is **inevitable by construction**, not something measured.
> Record `no_differential_possible` in this case, and **build only one side and hit it with attack inputs**.

**After building, `md5sum` both binaries; only different md5s** count as two sides really built —
identical means two sides were never built at all (observed in practice: concurrent makes writing the same tree, and 5 "fix" binaries were byte-identical to the vuln one).
**Every `setsid` must be written as `setsid --wait`**.

## D. `confirmation_scope` and `reachability` are both mandatory for CONFIRMED

The two fields are **orthogonal** and must not be conflated:

- `confirmation_scope` **can only be** `defect_site` or `reachability`;
- `reachability` **can only be** `REACHABLE`, `UNREACHABLE` or `UNKNOWN`.

**The criteria are the actual shape of the stack** (imported from PrimeVul 2026-08-18; the decision
logic of the tool `tasks/primevul_reports/route_campaign/check_scope_shape.py` can be reused directly):

| Stack shape | scope |
|---|---|
| The fault is inside the labelled function's body (frame #0) | `defect_site` |
| The fault is in a function the labelled function **really calls** | `reachability` + a `defect_site` object + `call_path` |
| The labelled function **writes a bad value into shared state**, and real upstream code only crashes when consuming it elsewhere (a sibling path, a later loop, another thread) | `reachability`, **provided the counterfactual is measured and holds and the consumer is real upstream code** |
| The fault is in a **caller**, or in a **sibling** with no call relationship | Only then does downgrading apply (`fault_not_attributable`) |

The counterfactual criterion: **if only the labelled function is changed, does the defect go away?** Yes → `defect_site`; no → `reachability`, and fill in
`defect_site.{function,file,reached_via,defect}` and `reachability_note`. **`reachability` is not label noise.**

If a real defect is indeed inside the labelled function but there is no attacker path, it is **still
CONFIRMED**: write `reachability:"UNREACHABLE"` + the measured basis + `attacker_controlled_trigger:null`.
If the path merely was not found, write `UNKNOWN` and list which entry points were searched.
**Not built, not run, or the wrong oracle is "not finished" and may not masquerade as UNREACHABLE.**

## E. Hard rules for evidence self-sufficiency

For every sample processed with a dynamic tool, confirmed or not, the reproducible evidence goes in `<id>/dynamic_evidence/`: `repro.sh`, the driver/harness, the code of both sides or an exact pin, the
real input, **complete logs for both sides**, `EVIDENCE_MAP.json` (purpose and sha256). **Unconfirmed "ran it but no fault / no differential" must also be re-runnable.**

- **Do not** leave evidence in `/tmp`, `~` or outside the repository; even temporary directories are
  created inside the evidence directory;
- Scripts use only relative paths and `${CC:-gcc}`, and **must not hard-code** `/scratch/`, `/tmp/`,
  `/home/`;
- Evidence paths in records are uniformly written in the **relative form** `dynamic_evidence/...`, never as a bare file name;
- Third-party source, toolchains and banked builds go in `pathb/` inside the repository, recording
  the remote, commit, configure command and dirty diff;
- **Before delivery really delete the build products and re-run** `bash dynamic_evidence/repro.sh` to confirm the labelled function really is compiled **and executed** — running without deleting
  proves nothing about whether it can still be built;
- **The log name must show which oracle was used** (`vuln.asan.log` / `vuln.msan.log` /
  `vuln.ubsan.log` / `vuln.valgrind.log`). **Names like `log.txt` / `out.log` that do not show the tool are not allowed**;
- When retracting a confirmation, keep the old craft file in the sample's own
  `prior_confirmation_<stamp>/` (**move it, do not delete it**), and correspondingly fix `dynamic_confirmation.json`, `info.json`, the RUNLOG and the dedup index;
  **`label_target` is never changed** — that is the dataset's label; what changes is our ruling.

---

# Part Two · The original /loop prompt (verbatim, copy straight into /loop)

```
Please continue on DiverseVul with defensive vulnerability-dataset label-verification by differential sanitizer testing (pre-fix vs post-fix, same input); NOT exploit development, and nail down more label_target==1 samples. Each round runs about 4 agents in parallel, each agent handling 1 sample and running the full pipeline: read vulnerable_function.c, fixed_function.c, info.json (plus dependencies/ and containing_file.c as needed) under data/output/dataset/diversevul/<id>/ → choose a method → faithful harness / real build → same-input differential between vuln and fix → write the product or the inspection. Sample ids look like 97208_<hash>; there is no function.c in the directory, and only the worklist CSV's function_file points to the correct vulnerable_function.c. Many rows have folder_materialized=False, so before dispatch you must filter with os.path.exists(vulnerable_function.c); source that was never materialized can be taken from the func field of data/output/full/diversevul.jsonl.

Each round, first check real CPU occupancy in /proc/stat, free -g, remaining disk and iowait; load average is only for reference; lower concurrency when iowait is high. Path-A micro-harnesses may exceed the old 2-channel cap; at most 1-2 heavy Path-B rebuilds at a time. Take candidates only from tasks/diversevul_reports/diversevul_current_dynamic_method_worklist.jsonl; already-triaged rows are in diversevul_triaged_worklist.jsonl, and those with needs_path_b=true go to Path-B. Before dispatch exclude: an existing data/output/dynamic/confirmed/diversevul_<id>.craft.json, canonical already confirmed, label_target!=1, inflight, already handled in the RUNLOG, cross-dataset DUP (for non-propagation tasks), folder_materialized=False; a semantically empty diff -w may only be marked suspected_label_noise and still requires a dynamic attack. Before confirming, run scripts/is_duplicate.py diversevul:<id>; no manual bulk copying — only call the existing propagation script and re-verify the normalized function-body hash. Agents must not write the RUNLOG themselves; they return a single RUNLOG_LINE, and the commander appends it serially to tasks/RUNLOG_<host>_diversevul.md.

★★ There are only four outcomes: CONFIRMED / LABEL_NOISE_EXCLUDED / DY_Attacked_But_can_not_decide_confirmed_or_label_noise / BUILD_FAILED, and the four numbers add up to 9,604. INCONCLUSIVE, UNTOUCHED, DEFERRED, NEEDS_PATH_B, NOT_TRIGGERABLE_AS_LABELED are no longer outcomes; they may only stay in the record's verdict as history. Landing in the third or the fourth turns on one thing only: whether a dynamic tool really attacked it and readings from both sides were obtained. If it was attacked, write dy_attacked_undecided_category; if the attack did not succeed, write build_failed_reason; both are mandatory and must not be left empty.

★ Hard criteria for a faithful trigger (all 6 must hold):
In one sentence: the standard confirmation is that on the same faithful input the vuln side faults and the fix side is clean; when the fix side also faults, check OTHER_DEFECT_UNFIXED per the highest-priority rules, and do not reject it merely because there is no differential.
(1) Evidence before action: first diff -w vulnerable_function.c fixed_function.c to understand the fix; when there is a commit_id, pull the upstream commit as corroboration. With no CVE/CWE it is forbidden to invent a CVE number or a fixed version, and cve_match is always written as "undeterminable (no CVE/CWE; ground truth=source diff)".
(2) Differential-first acceptance: record the complete results of both sides on the same input; vuln faults / fix clean is the standard confirmation. When both sides fault the same way, check the real defect and the call closure, and if the conditions hold it may be recorded as OTHER_DEFECT_UNFIXED; neither side faulting cannot be a confirmation. When the two function bodies are semantically identical, identical behaviour is inevitable by construction and not a measurement result: record no_differential_possible and build and attack only one side.
(3) Prefer real entry points: if a real tool can be built and fed a really constructed input through the real call chain, do not hand-assemble structs and call the labelled function directly; a micro-harness must likewise keep the labelled function's original text and the real helper functions in dependencies/ and containing_file.c, and must not bypass real checks.
(4) Trigger values must be faithful: do not remove an existing upstream guard or let the harness manufacture the defect. If the defect really exists in the labelled function but there is no attacker path, it is still CONFIRMED + reachability:UNREACHABLE; if the path merely was not found, write UNKNOWN, and passing off absurd magic numbers as a real input is forbidden.
(5) Mechanism agreement: the fault type/location must attribute to the mechanism the fix diff actually repairs; write mechanism_matches_diff. Allocation site ≠ fault site is allowed, recorded in frame_note (alloc_site/entry_site vs fault_site), but the fault site must lie within the labelled function's real call closure.
(6) Missing metadata ≠ confirmation: when CVE/CWE/commit is missing, prefer recording BUILD_FAILED or the third outcome; do not write a guessed vulnerability class, fixed version or trigger chain as fact.
Product fields must include cve_match, triggered_vuln, synthetic_trigger:false, differential (hv_rc/hf_rc as real integers), mechanism_matches_diff, frame_note where needed, plus label_noise + label_noise_type / needs-Path-B.
★ CWE must be written: cwe (an array), cwe_chain (root cause -> sink chain), cwe_basis (the actual observed evidence supporting that judgement, e.g. "ASan heap-buffer-overflow READ size 4, frame#1 vpc_open"). Derive the CWE from the observed mechanism, do not copy it from the commit message; when root cause and sink differ, write it as a chain (e.g. CWE-190 -> CWE-787); when it cannot be decided, write cwe:[] + cwe_basis:"not determinable from observed behaviour". Inventing a CVE is still forbidden; it may only be looked up upstream via commit_id. Add a cwe_chain column to the RUNLOG line.

★★★★★ The label-noise dynamic gate: any static conclusion may only be written as suspected_label_noise + label_noise_basis:"static_reading", does not trigger exclusion, and the sample stays on the worklist. Before a final label_noise:true, seven gates must pass: (1) a real integer exit code + a re-runnable script + non-empty complete logs (2) labelled_fn_executed with proof of execution ("compiled in" does not count) (3) the attack input is not a normal call (4) the oracle chosen matches the observed mechanism (5) attack_surface_note states the entry point / value ranges / duration (6) the stored body checked word for word against upstream (a truncated body = attacking the wrong object, record stored_body_incomplete) (7) proof that execution reached the disputed line of the diff (merely entering the function does not count; a gdb count of 0 must be double-checked with gcov). Evidence goes in <id>/dynamic_evidence/label_noise_attack/; without the evidence directory the ruling is void. For inverted polarity write label_noise_basis:"dynamic_differential_inverted", never dynamic_attack_negative.

★★★★★ Every CONFIRMED must fill in confirmation_scope:defect_site|reachability and reachability:REACHABLE|UNREACHABLE|UNKNOWN. Judge scope by the actual shape of the stack: fault inside the labelled function's body at frame#0 → defect_site; in a function it really calls → reachability + a defect_site object + call_path; in a caller or in a sibling with no call relationship → fault_not_attributable. When both sides fault the same way but a real defect inside the labelled function's call closure can be triggered faithfully, record OTHER_DEFECT_UNFIXED and do not reject it for lack of a differential.

Output path discipline: per-sample products are written only under data/output/dataset/diversevul/<id>/; all dynamic evidence goes into <id>/dynamic_evidence/, containing a repro.sh that can rebuild and run both sides from a clean state, the driver/harness, the real input, complete logs and an EVIDENCE_MAP.json with sha256. The log name must show which oracle was used. No absolute paths outside the repository may be left behind. On confirmation, save dynamic_confirmation.json and record.md, and register data/output/dynamic/confirmed/diversevul_<id>.craft.json. When not confirmed, still save dynamic_confirmation.json/inspection.json, record.md and the reproducible evidence that was actually run, but do not write craft.json. The RUNLOG is only appended to tasks/RUNLOG_<host>_diversevul.md; creating another RUNLOG is forbidden. Every dispatch prompt must embed the rules above.
```

---

# Part Three · What to do when there is no CVE / CWE (DiverseVul's central problem)

## 1. The ground truth is not a CVE, it is the diff between those two function bodies

The whole framework of BigVul / PrimeVul is anchored on the **fix commit**: read the CVE advisory, read the fix diff, build one side at `fix^` and one at `fix`. **DiverseVul does not have that anchor.**

**DiverseVul's anchor is the two function bodies in the sample directory themselves:**

```
data/output/dataset/diversevul/<id>/
├── vulnerable_function.c    ← the one labelled vulnerable
├── fixed_function.c         ← the one after the fix
├── info.json                ← commit_id is the FIX commit (VULN = <commit>^)
└── INFO.md
```

(**This is the layout of target=1 samples**; `function.c` appears only in target=0 samples, which
this campaign does not touch.)

So the first step is always **`diff -w vulnerable_function.c fixed_function.c`** —
it is at once the **cheapest sieve** and the **only reliable source of the mechanism**. `cve_match` is always written as `"undeterminable (no CVE/CWE; ground truth=source diff)"`.

## 2. A CWE may be written, a CVE may not — the two are different in nature

**This is the most important point in this section.** They are not in a "both missing, so write
neither" relationship:

| | CWE | CVE |
|---|---|---|
| What it is | The **type** of defect | The **number** a CNA assigns to a publicly disclosed vulnerability |
| Can it be derived from observation | **Yes** — the fault type and location the sanitizer reports are the evidence | **No** — it is the product of a social process |
| What to do | **Must be written**, derived from observation | Can only be looked up upstream via `commit_id` (OSV / NVD / GHSA); if it cannot be found, there is none |

**Under no circumstances may a CVE number be invented.**

Both CONFIRMED samples and unconfirmed samples whose mechanism has been located must write three fields in `dynamic_confirmation.json` / `craft.json`:

- `cwe`: an array, e.g. `["CWE-190","CWE-125"]`
- `cwe_chain`: a string, the root cause → sink chain, e.g.
  `"CWE-190 (32-bit size multiplication wraps) -> CWE-125 (OOB read in the BAT loop)"`
- `cwe_basis`: one sentence giving the **actual evidence** supporting that judgement, e.g.
  `"ASan heap-buffer-overflow READ size 4, frame#1 vpc_open"`

**Three hard rules:**

1. **Derive it from observation, do not copy it from the commit message.** The only admissible basis is the fault type/location the sanitizer reports, or a wrong decision observed in a behavioural
   differential (wrongly accepted, wrongly let through).
2. **When root cause and sink differ it must be written as a chain**, not squashed into a single id. An out-of-bounds write caused by an integer overflow is `CWE-190 -> CWE-787`, not one or the other.
3. **If it cannot be decided, leave it empty**: `cwe: []` +
   `cwe_basis: "not determinable from observed behaviour"`. **Leaving it empty is an honest value; inventing one is far worse than leaving it empty.**

Common mappings (**observation decides; do not force-fit**):

| Observation | CWE |
|---|---|
| heap/stack-buffer-overflow WRITE | CWE-787 (on the stack also tag CWE-121) |
| heap/stack-buffer-overflow READ | CWE-125 |
| Signed integer overflow / unsigned wraparound | CWE-190 / CWE-191 |
| Unbounded recursion → stack exhaustion | CWE-674 |
| use-after-free / double-free / leak | CWE-416 / CWE-415 / CWE-401 |
| NULL dereference / uninitialized read | CWE-476 / CWE-457 |
| Missing authorization / improper permission check | CWE-862 / CWE-863 |
| Improper signature verification / improper certificate validation | CWE-347 / CWE-295 |
| TOCTOU / race | CWE-367 / CWE-362 |

The RUNLOG line format gains a column accordingly:
`| <date> | <id> | <proj>/<fn> | <method> | <verdict> | <cwe_chain> | <evidence> |`

## 3. With no CWE you cannot route by CWE — route by code features instead

PrimeVul's fourth gate is "the oracle is chosen correctly by **CWE**". DiverseVul has no CWE, so this
gate becomes "the oracle is chosen correctly by the **observed mechanism**", and the mechanism is read out of `diff -w` and the code features:

| Code feature (read from the diff and the function body) | Preferred oracle |
|---|---|
| Array indices, pointer arithmetic, `memcpy`/`memmove`, controllable sizes | **M1 ASan** |
| Division, shifts, integer casts, accumulator overflow | **M6 UBSan** |
| `alloc`/`free` on error paths, reference counts | **M9 LSan / Valgrind** |
| Recursion, unbounded loops, unbounded allocation | **M15 DoS** |
| Uninitialized reads, information leaks | **M7 MSan** |
| Multithreading, locks | **M8 TSan** |
| Logic / permission / encoding strictness | **Behavioural differential** |

### ★ "ASan reported nothing" is not an empty value (this applies regardless of whether there is a CWE)

- **Uninitialized / information leak** → ASan **structurally cannot see it**; MSan is needed, and
  **it prints `WARNING:`, not `ERROR:`** — a checker that only matches `ERROR:` cannot see the entire MSan route;
- **Integer overflow / shifts** → UBSan, whose format is fixed as
  `<file>:<line>:<column>: runtime error:` (matching a bare `runtime error:` will hit diagnostic text
  the program prints itself); **UBSan by default "prints and keeps running", so the exit code is 0** — either add
  `-fno-sanitize-recover`, or **count the number of `runtime error:` lines** and do a count differential;
- **Leaks** → LSan **only reports at process exit**, and with `exitcode=0` the exit code is still 0, so **compare byte counts**;
- **Over-reads within the same object** → ASan cannot see them, memcheck can;
- **Over-allocation** → nothing can see it; read **the number of bytes requested**;
- **assert** → first confirm whether the build **has assertions enabled** (`NDEBUG`); if they are off,
  the assert channel is not quiet, it **does not exist**;
- **Time-based DoS** (recursion exhaustion, ReDoS) **counts as CONFIRMED in itself**, but take **counting evidence** (iteration count, recursion depth, allocation count) — **do not use the wall
  clock as evidence**.

## 4. Does an injected runtime condition count as a faithful trigger — rule C's DiverseVul workaround

One class of defect appears only when some **runtime condition** occurs (most commonly allocation
failure). The criterion:

> **Does this fix change "what to do when this condition occurs"?**
> Yes → injecting that condition **counts as a faithful trigger**; no → it counts as a **synthetic
> trigger** and cannot confirm.

When confirming by this rule, five things must hold at once: (1) the failure must come in through the program's **own public interface**, and **not one line of upstream source may be changed**;
(2) the injector is **word-for-word identical** on both sides, so the only variable is still the function body; (3) write `faithful_trigger_basis` and **quote word for word** the place in the fix
that handles this condition; (4) write `attacker_controlled_trigger` honestly as `null` and
`reachability` as `UNKNOWN`; (5) readings from both sides are still required as usual.

> **★ DiverseVul workaround**: this rule requires "reading the fix diff and checking it word for word".
> DiverseVul **does have** `diff -w vulnerable_function.c fixed_function.c` to check —
> **use that diff as the basis**; this is more direct than PrimeVul's situation.
> But if the diff does not show upstream handling this condition, then it is a synthetic trigger:
> record `synthetic_trigger`, and **do not let speculation replace a quotation**.

## 5. Out of scope for differential testing (neither a mislabel nor needs-Path-B)

Some fixes **by definition produce no observable differential**: the fix is real and the mechanism is clear, but building the historical version measures nothing either.
Judge it as `dy_attacked_undecided_category: "out_of_scope_for_differential_testing"` and state the method that would be needed:

- **Constant-time / cache-line access hardening** (side channel): e.g. openssl 177197
  `ssl3_cbc_copy_mac` changed to rotation-based access so the read pattern does not depend on the
  secret padding length — the two versions' output is byte-for-byte identical and rc is 0 on both. What is needed is a **timing/cache side-channel measurement**, not a sanitizer.
  During pre-screening, anything showing `constant time` / `cache line` / rotate-based access is classified here directly;
- **Randomness / entropy-source strengthening**, **certificate revocation-state refresh**: correctness
  depends on external state or statistical properties, which a single differential cannot observe.

**If the diff already shows before dispatch that a sample belongs here, archive it directly; there is no need to dispatch an agent.**

---

# Part Four · Paths, ledgers and dataset characteristics

## Paths and ledgers (DiverseVul-specific)

- **Sample directory**: `data/output/dataset/diversevul/<id>/`, with ids of the form `97208_<hash>`.
  **Inside a target=1 directory are** `vulnerable_function.c`, `fixed_function.c`, `info.json`,
  `INFO.md` — **there is no `function.c`** (`function.c` appears only in target=0 samples). The worklist CSV's `function_file` column points to the correct `vulnerable_function.c`.
- **DiverseVul has no reliable CVE/CWE**; the ground truth is the diff between those two function bodies.
  Many worklist rows have `folder_materialized=False` (about **5,139** positive samples have no materialized folder), so before choosing a sample you must filter with
  `os.path.exists(vulnerable_function.c)`;
  source that was never materialized can be taken from the `func` field of `data/output/full/diversevul.jsonl`.
- **Confirmation registration**: `data/output/dynamic/confirmed/diversevul_<id>.craft.json`.
  Confirmation products are written inside the sample directory: `dynamic_confirmation.json`, the harness/PoC, `repro.sh`, the sanitizer or behavioural logs, `record.md`.
- **Unconfirmed / static review**: `inspection.json` (`verdict` / `feasibility` / `analysis`) +
  `record.md`, **no craft.json**.
- **The ledger is only appended** to `tasks/RUNLOG_<host>_diversevul.md`; creating another RUNLOG file is forbidden. Rebuild the dedup index with
  `nohup python3 scripts/build_dedup_index.py` (do not block on it every round).
- **Path-B build workspace**: `<SCRATCH>/pathb_builds/`.

## DiverseVul dataset characteristics (key differences from BigVul/PrimeVul)

1. **No CVE/CWE metadata**: method selection can only go by code features, CWE routing cannot be
   applied; `cve_match` is always undeterminable; **but the CWE must be derived from observation and written out** (see Part Three).
2. **The before/after function pair is the ground truth**: `diff -w` is the first and cheapest sieve.
3. **`commit_id` = the FIX commit**: Path-B builds the vuln version at its parent (`<commit>^`).
4. **Cross-dataset dedup**: run `scripts/is_duplicate.py diversevul:<id>` before confirming;
   **469** entries already come from exact function-body propagation (466 from PrimeVul, 3 from BigVul). No manual bulk copying — only call the existing propagation script and **re-verify the normalized
   function-body hash**.
   > **★ Propagation is not measurement.** A propagated confirmation must permanently keep its
   > `propagated_from: <dataset>:<id>` lineage; **it is forbidden** to delete the source key or to
   > rewrite it as an independent confirmation merely because "there are already logs in the directory".
   > **The numbers must be split when reporting**: of the 733 confirmations, 469 were propagated and
   > only 250 were measured independently — reporting only the total makes people think 733
   > measurements were made.
5. **About 5,139 positive samples have no materialized folder**: you must check
   `folder_materialized` and whether `vulnerable_function.c` exists.

---

# Part Five · Method routing, per-project hit rates and Path-B

## Do these first (Path-A, docker-free, single-function micro-harness)

- **M1 ASan**: array indices, pointer arithmetic, `memcpy`/`memmove`, controllable sizes → highest yield;
- **M6 UBSan**: integer overflow in division/shifts/integer casts/accumulators;
- **M9 LSan/Valgrind**: alloc/free on error paths (leaks, double-free, UAF);
- **M15 DoS**: recursion, unbounded loops, unbounded allocation;
- **M7 MSan / M8 TSan / behavioural differential**: choose by feature;
- **32-bit ASan** (`clang -m32`, `/usr/lib32/libasan.so.6`): ILP32-only integer overflow; example: samba `read_nttrans_ea_list` 15232, where a single 32-bit next_offset cannot wrap on 64-bit.

## ★ Per-project hit rate (measured on 68 samples on 2026-07-25; the primary basis for sample selection)

| Project | Run | Confirmed | Hit rate | Notes |
|---|---:|---:|---:|---|
| qemu | 10 | 6 | **60%** | Device emulation, guest-controllable values → faults inside the closure; avoid the a4afa548 chardev family (all 5 are outside the closure) |
| samba | 6 | 3 | **50%** | File permissions (CWE-732) and parsing out-of-bounds; avoid the asn1 sticky-has_error defensive refactor |
| gpac | 2 | 1 | 50% | Parsers; the input proves reachability by itself |
| openssl | 15 | 5 | 33% | **All confirmations cluster in encoding strictness (DER/BIT STRING malleability) and trust decisions**; avoid constant-time hardening, application-mode feature gating, and paths already deleted in OpenSSL 3 |
| php-src | 3 | 1 | 33% | Signed/unsigned lengths passed into an allocator or a copy |
| **mysql-server** | 8 | **0** | **0%** | Systematically incomplete closure + Path-B needs the full build system → **skip on Path-A outright** |
| **envoy** | 3 | **0** | **0%** | Old function bodies cannot compile against the new API → **skip** |
| **mongo** | 2 | **0** | **0%** | The dependencies are version-mismatched auto-sliced layer files → **skip** |
| ImageMagick | 3 | 0 | 0% | The X11 widget family (font metrics outside the closure) is all wasted; but **image-parsing coders have never been tested and are worth trying separately** |
| node / curl | 2 each | 0 | 0% | The zone allocator / session cache are both outside the closure |

**How to use this**: filter by project first when selecting samples (skip projects at 0% whose reason
is the closure), then dedup by signature class and by commit. Take only one representative per commit — 873 commits have already been triaged, and sibling samples
are the main reason the hit rate declined later.
Ids pre-filtered by hand are recorded in `scratchpad/manually_prefiltered_ids.json` and excluded again on a rescan.

## ★ Verified high-yield veins (reuse the recipes directly)

- **radare2** `r_bin_java_*_attr_new` (missing `sz<8` check → OOB READ on a truncated .class attribute
  header): already confirmed 121238/121237/121234/121242/121239/121236/121230;
- **FreeRDP** `gdi_SurfaceToSurface` / `gdi_CacheToSurface` / `gdi_SurfaceToCache` (the fix adds `is_rect_valid` → out-of-bounds in `freerdp_image_copy`): already confirmed
  97209/97208/97210; the harness template is `data/output/dataset/diversevul/97208_*/work/harness.c`;
- **FreeRDP** Stream_Read channel handlers (the fix adds `Stream_GetRemainingLength(s) < N` /
  `Stream_CheckAndLogRequiredLength` → OOB READ on a truncated PDU; cliprdr/rdpdr/rail/rfx):
  already confirmed 183454 and others;
- **qemu** device emulation: fixed rx/tx buffers + guest-controllable lengths (tulip_receive, cursor_alloc, qcow2_snapshot_load_tmp);
- **Off-by-one index guards** (FreeRDP bitmap_cache_get 94261, gnutls dane_raw_tlsa).

## ★ Multi-signature scanning

Finishing one signature **≠** the pool is exhausted; scan class by class with `diff -w`:
(1) a newly added size/len guard; (2) an off-by-one comparison-operator flip; (3) the size or source argument of `memcpy`/`memmove`/`strncpy`/`snprintf` being changed; (4) integer-overflow accumulators/
allocations; (5) fixed-length array indices; (6) a newly added NULL check;
(7) bounds checks on returned pointers; (8) frees on error paths (leak/UAF/double-free); (9) unbounded string operations on buffers that are not NUL-terminated.
**Do not declare exhaustion on the strength of a single signature**; historically every new scanning angle has turned up another batch.

## Counterexamples vs positive examples

- **Positive example (faithful Path-A confirmation)**: `121237` radare2 `r_bin_java_*_attr_new` — the
  fix adds `if (sz < 8) return NULL;`; the harness uses the labelled function's original text plus a faithful `r_bin_java_default_attr_new`, and feeds an exactly sized small heap buffer with `sz=4` →
  the vuln version gets an ASan heap-buffer-overflow READ (reading a 6-byte attribute header), while
  the fix version exits cleanly on the same input.
- **Counterexample one (REDUNDANT guard)**: `121231` in the same family; the vuln version already has a dominating `sz<10` guard, so the newly added `sz<8` is dead code → not a confirmation.
- **Counterexample two (GUARD-SWAP)**: `121233`, where `buf_offset+8>sz` → `sz<8` is a correctness
  fix; the old guard is at least as safe on reachable inputs, and only an unreachable ut64 wraparound goes out of bounds → not a confirmation.
- **Static-suspicion examples**: FreeRDP `ber_read_*` samples 15006/15008/15011/15012/14997/15000 are
  merely `if(` → `if (` formatting; git `strdup` 131505 is merely strcpy→memcpy; libtorrent 40106 is
  merely a type substitution. A semantically empty `diff -w` may only be marked `suspected_label_noise`; **the case may only be
  settled after the single-side dynamic attack gate is completed**.

> **★ "The fix added a guard" ≠ "the vuln version can be triggered"**: you must confirm that the
> unguarded read/write **really executes before any existing guard**.

## The boundary between label noise and needs-Path-B

- **label noise (dataset mislabel)**: `diff -w` semantically empty / the function has no security-relevant change / existing guards were already sufficient (redundant) / guard replacement
  (guard-swap) / behaviour-preserving refactor (int→size_t, malloc→emalloc, struct-serialize→memcpy) / pure error-handling hardening / assertion-class changes (which only fire
  with NDEBUG off) / purely new functionality / the real vulnerability is in a sibling function
  (e.g. cmark-gfm 164398, whose real bug is in `try_opening_table_header`) / a logic DoS rather than a memory fault.
  **But all of these must pass the seven gates first** (see Part One, B).
- **needs-Path-B (not a mislabel)**: the label is right and the vulnerability is real, but the sink is outside the labelled function's closure, or it needs a whole-repository build / an old toolchain /
  a complete service runtime / KASAN+QEMU / MSan.
  Record `out_of_closure_sink`, `label_noise:false`, and a reason containing the literal `needs-Path-B`.
- **wrong-function vs frame_note**: when the fault happens in a downstream function the labelled
  function **really calls** and is reachable through a real input, it is a **faithful CONFIRMED** (`confirmation_scope:"reachability"`); record `frame_note`, `label_noise:false`, **this is not
  wrong-function**.
  Example: mbedtls 30594 labels `ssl_set_hostname`, while the fault is in the memcpy of the downstream `ssl_write_hostname_ext`.
  **Only when the labelled function has no real call relationship with the faulting function is it wrong-function.**
- DiverseVul currently has no local label-noise ledger; **the 0 in the statistics means "no ledger
  input", not "there is no noise".**

## Path-B (the main effort in the next phase)

Path-A's "small-diff single-function confirmable pool" has entered the long tail after 30+ rounds of scanning, so **the main effort in the next phase is Path-B**.

- The environment is verified: git / cmake / meson / ninja / make / gcc / clang / gcc-11 / autoconf /
  pkg-config are all present; the network is available; 32-bit ASan is at `/usr/lib32/libasan.so.6`;
- Build cache: `<SCRATCH>/pathb_builds/`, already containing libraw/openjpeg/libtiff/exiv2/zlib and
  others; the qemu environment is in `pathb_builds/qenv` + `diversevul_43483_qemu/`;
- **★★ When Codex executes Path-B it must not be given `<SCRATCH>/pathb_builds/` as the build root** (measured 2026-07-25): that path is outside codex-rescue's sandbox root
  (`data/output/dataset/diversevul`) and is **read-only** to it. Specifying it makes the build fail outright and return `hv_rc=125/hf_rc=125 "both required binaries unavailable"` — that is exactly how
  three samples in the mysqldump Path-B batch were wasted, and at the time it was **misjudged as
  "the mysql build system is too complex"**. **The correct approach**: when dispatching Path-B, specify `/tmp/diversevul_<id>_<proj>/` as the
  build root and require the evidence to state the real build path; if the commander wants to keep it afterwards, move it from /tmp to pathb_builds themselves.
- **Recipe**: `info.json`'s `commit_id` = FIX, VULN = `<commit>^`;
  clone → two checkouts → build each with `-fsanitize=address -g -O0` → construct a real attacker input → run both real binaries on the same input → the vuln version faults
  under ASan, the fix version is clean.
  The product's `path` field is written as `"Path-B (build@<commit>^ +ASan)"`;
- **Cost**: a single heavy Path-B takes about 25-40 minutes and 100-170k tokens (qemu/php scale). Prefer light builds with simple triggers (radare2/mbedtls/curl/openldap), and leave qemu/mysql/
  systemd-scale ones for later.

**Path-B results already achieved (usable as templates)**:

- **CONFIRMED**: mbedtls `ssl_set_hostname` 30594 (a 30KB SNI overflows the ClientHello buffer), radare2 `r_bin_ne` 123568 (ut16 size truncation under-allocates, `rabin2 -S` OOB READ),
  openldap `parseValuesReturnFilter` 104571 (real slapd + a ValuesReturnFilter control → UAF),
  qemu `qemu_chr_free_common` 43483 (a guest parallel port + QMP chardev-remove → UAF), systemd `iovw_put` 69492 (journal-export with a million fields → alloca stack overflow,
  CVE-2018-16865).
- **Not confirmed**: php `spl_autoload_unregister` 34347 (the fix commit 620ccc9b is a **partial fix**, the fix version has the same UAF, so no clean differential can be obtained; **the vulnerability is
  real, this is not label_noise**), qemu `virgl_cmd_set_scanout` 44378 (env-blocker),
  qemu `qemu_sendv_packet_async` 67874 (impossible-magic: needs a single packet larger than 2GiB).
- **BLOCKED**: curl `Curl_http_done` 130513 (the environment lacks the krb5/gssapi headers). **SKIP**: redis ziplist 115413 (needs an input larger than 4GB, unrealistic).

**Low-yield / honestly record `BUILD_FAILED`**: nondeterministic sanitizer faults; heavy dependence on
a complete runtime that cannot be faithfully reproduced; out-of-closure sinks (move to Path-B). With no CVE references, do not make M4 public-PoC replay or M19/M20 CWE triage the main route.

---

# Part Six · How to dispatch

- **Multiple agents in parallel each round**: about 4 agents, **each agent handling 1 sample**, running
  the full pipeline;
- **★ Agents must not write the RUNLOG themselves**: parallel appends corrupt the file on scratch/NFS. Agents return a single `RUNLOG_LINE` and the commander appends them **serially**;
- At the start of each round check real CPU occupancy (`/proc/stat`), `free -g`, remaining disk and
  **iowait**; load average is only for reference. Lower concurrency when iowait is high;
- On Path-A each agent only compiles a micro-harness, which may exceed the old 2-channel cap;
  **at most 1-2 heavy Path-B rebuilds at a time**;
- **★ The dependency closure is the strongest predictor of Path-A success** (measured 2026-07-25): prefer dispatching samples whose `dependencies/` is non-empty or that have a `containing_file.c`.
  Of that round's 7 CONFIRMED, all but the self-contained single functions had complete dependencies; **all** 5 needs-Path-B cases fell over on a missing closure.
  **This predicts the outcome better than the signature class, so sort by dependency count descending
  when screening**;
- Before dispatch, exclude those with an existing `diversevul_<id>.craft.json`, canonical already confirmed, `label_target!=1`, inflight, already handled in the RUNLOG, cross-dataset DUP (for
  non-propagation tasks), `folder_materialized=False`; then pre-screen with `diff -w`, and **when it is semantically empty only mark
  `suspected_label_noise` and move to a single-side dynamic attack; do not rule noise directly**;
- Every dispatch prompt must **embed** Part One's four outcomes, seven gates and six hard criteria for a faithful trigger;
- **★ The wording of a dispatch must separate "ruling fields" from "proof fields".**
  Saying only "do not change the verdict" will be understood as "do not touch a single word of the
  record" — in practice three batches of agents built the full attack evidence and wrote not one field into the record.
  The correct wording: "what is forbidden is `verdict` / `confirmation_class` / `confirmation_scope` / `reachability` / `label_noise*` / `real_vuln_location` / `cve_match` / `label_target` /
  `reason` / `status` / `info.json` / the craft registry; **the proof fields must be written**",
  listing the field names one by one;
- Frame the subagent's wording with "defensive vulnerability-dataset label-verification by differential sanitizer testing (pre-fix vs post-fix, same input); NOT exploit development";
- **★★ Codex sandbox-root limitation** (diagnosed 2026-07-25; cannot be corrected by prompting):
  codex-rescue's workspaceRoot is `data/output/dataset/diversevul`, and **the registration directory `data/output/dynamic/confirmed/` is outside that sandbox root, so Codex
  cannot write into it**. That is the real reason craft.json was repeatedly "forgotten" (5 of the first 6 confirmations missed
  it), **not laziness on its part**.
  It shows up in two ways: (1) craft.json is missing; (2) sometimes even `dynamic_confirmation.json` / `record.md` / `repro.sh` end up in the `work/` subdirectory as well.
  **Fixed commander follow-up actions**: (1) check `work/registration_payload.json`; (2) move `dynamic_confirmation.json` / `record.md` back from `work/` to the sample root;
  (3) put a thin wrapper `repro.sh` in the root directory
  (`exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/work/repro.sh" "$@"`) — **copying it directly breaks the script's `cd "$(dirname "$0")"` self-location**;
  (4) the commander writes craft.json.
- **DoS ruling**: a hang/timeout, unbounded recursion → stack overflow, an infinite loop, a divide-by-zero SIGFPE, unbounded allocation = CONFIRMED; the two-sided differential must still hold,
  and **counting evidence** rather than the wall clock must be taken.

---

# Part Seven · The field checklist for every CONFIRMED

| Field | Requirement |
|---|---|
| `differential.hv_rc` / `.hf_rc` | **Real integers**. No `"identical"` / `"n/a"` / `null` / strings |
| `tried_dynamic_method` | **Must be an object**, containing `oracle_kind` `why_this_oracle` `method` `trigger` `hv_rc` `hf_rc` `vuln_observed` `fix_observed` |
| `labelled_fn_executed` | Boolean. **`false` is an honest value** — writing false truthfully is far better than inventing a true |
| `execution_proof` | How it is proved that it **was executed**. "It was compiled in" does not count |
| `oracle_kind` + `oracle_rationale` | **Chosen by the observed mechanism** (DiverseVul has no CWE to fall back on) |
| `attack_inputs` / `attack_surface_note` | See the seven gates |
| `confirmation_scope` | **Only two legal values**: `defect_site` / `reachability` |
| `reachability` | **Mandatory**: `REACHABLE` / `UNREACHABLE` / `UNKNOWN` |
| `defect_site` object + `call_path` | **Mandatory** when scope is `reachability`; four sub-keys `function` `file` `reached_via` `defect` |
| `cwe` / `cwe_chain` / `cwe_basis` | **Mandatory**; if it cannot be decided write `cwe:[]` + `cwe_basis:"not determinable from observed behaviour"` |
| `cve_match` | Always `"undeterminable (no CVE/CWE; ground truth=source diff)"` |
| `mechanism_matches_diff` | The fault mechanism matches the mechanism `diff -w` actually fixes |
| `synthetic_trigger` | Must be marked honestly |
| `frame_note` | Mandatory when the allocation site ≠ the fault site (`alloc_site` / `entry_site` vs `fault_site`) |
| `craft.json` | Must be at `data/output/dynamic/confirmed/diversevul_<id>.craft.json` |

---

# Part Eight · Attribution, sign-off self-checks and resources

## Attribution: a fault appearing does not mean it belongs to the labelled function

- **Never match stack frames by a bare function name.** Sibling overloads will hit (measured:
  mkvparser has 11 `Parse`s, pngfix has 3 `main()`s). Use the **line range of the function body**; if the harness compiles the labelled function into its own body file, **attributing by file path is
  stronger** — but first confirm that the body file really holds only this one function;
- **C++ stack frames have spaces in the function names**, so **do not** use `\S+` to match the function name when parsing — it silently drops frames;
- When a sanitizer's output has no frame from the labelled function, write
  `unattributed_sanitizer_output` (count + signature + samples); **it may be treated neither as a clean log nor as a trigger**;
- **A single log may contain more than one fault; do not look only at the first one**;
- **If you cannot count it, write "cannot be read", never 0** — `0` and "not measured" look identical;
- **Do not truncate logs being checked with `head` / `grep -m2`** — sanitizer errors are often in the
  second half;
- **Always enumerate directories recursively** (`find` / `os.walk`), **not with a shell glob or
  `os.listdir`** — those look at only one level;
- **Skip foreign-library/historical archive directories** (`prior_evidence_from_*`, `.bak*`) — the logs there are not this round's run traces.

## Sign-off self-check

```bash
cd tasks/diversevul_reports
python3 compute_diversevul_dynamic_status_statistics.py     # recompute; do not cite the old snapshot
```

Sign-off requires:

1. The four outcomes add up **exactly** to 9,604;
2. Not one of Part Seven's fields is missing for any `CONFIRMED`;
3. Every sample in the third and fourth outcomes has a **non-empty** secondary field;
4. `grep -rn '/scratch/\|/tmp/\|/home/' <modified sample>/dynamic_evidence/*.sh` gives **no output**;
5. **Really delete the build products and then run `bash repro.sh`**, which must rebuild successfully
   from source;
6. **Numbers self-reported by an agent are all wrong until spot-checked against the files** — both the self-report and the on-disk verification **must be recorded**, disagreements flagged on the spot,
   and the choice not made on the owner's behalf.

**"Cannot be reached", "both sides clean" and "statically it looks like a mislabel" are none of them
reasons to stop.**

## Resources and safety boundaries

- `make -j4` maximum; at most 1-2 heavy Path-B rebuilds at a time; limit concurrency by **actual CPU occupancy** (not load-avg);
- Run any binary with `timeout` + `ulimit -c 0` + `ASAN_OPTIONS=disable_coredump=1` +
  `unset LD_LIBRARY_PATH` (a crossed LD_LIBRARY_PATH makes both sides look identical);
- **`pkill -f` / `killall` are forbidden** — they kill other people's work and your own as well; to kill something, start it with `setsid --wait`, record the PGID, and `kill -- -$PGID`;
- **Never use wildcards in `rm`**; before using a glob, `ls` the same glob first to see how many it
  matches;
- Before changing any script or log, `cp x x.bak` first;
- **Order for making a script relative**: compute the repository root **after** `cd "$(dirname "$0")"`; do not use `$0` after the cd — you get an empty string and rc=127, **and it
  will overwrite the good logs with failure output**.

## Wording

- **Do not use the word "predicate"**; say it plainly: "the decision rule", "the fields this code
  actually checks";
- **Do not use the word "prose" for narrative text**; just say "the explanatory text in the document";
- **Do not use the word "arm"** (including "the two arms", "cross-arm comparison", "the control arm") — say instead "the one built from `vulnerable_function.c` / the one built from `fixed_function.c`";
- When describing the three label-noise categories, the sentence must contain **both "attack" and
  "whether a fault fired"**:
  - "attacked and not a single fault fired ⇒ the label-noise finding stands, the function really is mislabelled"
  - "a fault fired and it attributes to the labelled function ⇒ the label-noise finding is probably
    wrong, the function may genuinely be vulnerable, pending human adjudication"
  - "no conclusion this round" (never attacked / the measurement does not hold / the fault cannot be
    attributed to this function).

---

# Related reports (tasks/diversevul_reports/)

`DIVERSEVUL_METHOD_SELECTION_GUIDE.md`, `DIVERSEVUL_STATUS_SUMMARY.md`, `LEDGER_STATUS.md`, `diversevul_dynamic_status_latest.{md,json}`, `diversevul_content_inventory.csv`,
`diversevul_current_dynamic_method_worklist.{jsonl,csv,md}`, `diversevul_triaged_worklist.{jsonl,csv}`;
scripts `compute_diversevul_dynamic_status_statistics.py`,
`build_diversevul_current_dynamic_method_worklist.py`.
