# Finishing the FULL_WORKLIST project by project — the general agent brief

You have been given one **project** (for example `tcpdump`, `jasper`), and you must finish **all of that project's samples** in `FULL_WORKLIST_20260803.csv`. Samples from the same project share one
build tree and one harness recipe, so doing them together is far cheaper than splitting them up — that is why work is dispatched per project.

Your sample list is in `overlap361_batches/proj_<project name>_ALL.json`; each entry carries
`{id, class, task, cve, cwe, file, func, commit, detail, scripts}`.

**Read these two first; they are rules, not reference material**:
- `tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md` (the general criteria)
- **§1b "Why every sample needs a two-sided differential"** in `tasks/bigvul_reports/evidence_repair/README.md`

**Cross-dataset write gate (user, 2026-08-12)**: the only permitted cross-dataset transfer is
`bigvul:<id> -> primevul:<id>`; every other cross-dataset direction fails closed before anything is
written to disk, and operations inside one dataset are unaffected. If a historical BigVul record carries a PrimeVul origin, that lineage must be kept; the mere presence
of logs in the directory does not license rewriting it to `independent_rerun:true`. Once old BigVul logs are imported into PrimeVul they serve only as an archive and do not count as a PrimeVul
measurement.

**Current execution status (2026-08-13)**: the safety stop-gap forbidding PrimeVul→BigVul/third-library
detours is GO; full forward copying is still NO-GO. The canonical `import_bigvul_reuse.py --apply` / `copy_one()` stay hard-retired with zero writes because of the reproduced staging symlink/path-swap
arbitrary-target write. No agent may remove the early return or call the old pinned import/restore/rerun scripts; first implement a dirfd/openat(O_NOFOLLOW)/inode-bound/no-replace
importer and pass the independent race negative tests, then wait for the 900-second writer-free
stability gate and the ordered live audit. The frozen `431/625/107` are only for historical planning and are not the current copy list.

---

## ★ Added 2026-08-29: six lessons from practice (skip them and they will recur; each has a concrete sample)

For the full background see `RESUME_PLAN_20260903.md` and P-20260829-47..66 in
`PROBLEM_REGISTER_20260803.md`.

1. **Read `repro.sh` first and see how many experiments it runs.** In `181507`'s script, case A is the one the patch targets, while case B's comment says explicitly "the patch does NOT address this one,
   both arms expected to fault". Reading the two experiments' logs mixed together produces
   "both sides faulted" — the opposite of the truth.
2. **The comment at the top of an evidence file is part of the evidence; read it first.** The first seven lines of `188040`'s `body_fix.inc` explain why the first line of the stored body was removed:
   BigVul stored the pre-fix and post-fix signatures side by side, and it does not compile as-is. Without reading it you would report "the fix side is not using the fixed version the sample stores".
3. **Attribute with qualified function names; do not drop the class name.** Dropping the class name
   turns `EBMLHeader::Parse` into `Parse`, which matches the other 10 `Parse` overloads in mkvparser
   (`Block::Parse`, `Cluster::Parse`, …). Use `evidence_lib.qualified_name()` and compare with `==`, not `in`.
4. **A simplified/single-user mode may be unable to measure the fix.** `177853` crashes on both sides
   under `postgres --single`, because `SET max_stack_depth` has no effect in that mode while the fix depends on it to raise an error; only in server mode does the vuln side crash and the fix side stay
   clean. **Before running, confirm that this path is the one upstream considers the one to run.**
5. **Equal exit codes on both sides does not mean there is no differential.** Across the whole dataset
   901 confirmations have equal rc on both sides, and 864 of them correctly record the differential in an observation (peak RSS, output byte count, whether an assert fired, filesystem effects).
   **Do not score by rc.**
6. **`import evidence_lib`; do not rewrite the regexes yourself.** `tasks/bigvul_reports/evidence_repair/evidence_lib.py` collects the fault signatures (MSan/TSan
   print `WARNING:`, not `ERROR:`), fault-stack parsing (not mixing in the freed-by stack, merging
   inlined chains by pc, recognizing sanitizer-internal frames by file path), stored-body comparison, and the §2 legal single-side ruling.
   27 self-tests: `python3 test_evidence_lib.py`, to be run both before and after changing criteria.

**And one meta-lesson**: during the downtime I wrote 17 versions of the statistics, and every version's reported "outstanding debt" deviated from the facts, always because the criteria were narrower than
what was actually written on disk. **Before reporting numbers, open 3 samples judged "problematic" at
random and read their complete records.** The times I did this it converged on the spot (16→1, 222→0); the times I did not, false reports went into the report.

---

## What counts as a sample being finished

Only two things (these are the two fields the whole-dataset statistics actually check):

1. **`tried_dynamic_method` has a value** in `dynamic_confirmation.json` — the record really did run
   some tool;
2. **`differential` has a value** — the measured result of the two sides on the same input.

Both present = finished. **Note that the two fields have different gates**: `tried_dynamic_method` can be filled from a real oracle log of one side;
`differential` **requires both sides** — one side cannot produce a differential; that is a one-sided
observation.

**Finished ≠ confirmed.** If it was run properly and no differential came out, honestly record `NOT_MEASURED` plus a specific reason of at least 40 characters, and it still counts as finished.
**Inventing a differential is what is unacceptable.**

---

## What each of the six classes requires

| Class | What is on disk now | What you must do |
|---|---|---|
| **A** | Oracle logs for both sides exist and are non-empty | **Only transcribe, do not run tools** — copy the observation lines of both sides word for word into `differential` |
| **B** | Only one side has an oracle log | **Add the fix side** — the vuln side was run; build the fix side and run it again on the same input |
| **C** | A `.sh` script exists but there are no oracle logs on disk | **First re-run it as-is** to locate where it is stuck, then fix that point |
| **D** | No logs, no script | Build the harness/input from scratch from the fix diff (prefer extract-and-stub) |
| **E** | The PoC / build tree / headers the script reads are no longer on disk | Find them again or rebuild them from the fix diff, **then actually run it** |
| **F** | The script writes its products to the shared `/tmp` | Change it to the sample's own `dynamic_evidence/`, **then actually run it again** |

The order is **A → B → E → C → F → D**: pick the ready ones first and leave the ones that need a new build tree for later, so that even if you stop midway the most is finished.

---

## The two-sided differential: there may be only one variable

`arm_vuln = the same driver + vulnerable_function.c`,
`arm_fix  = the same driver + fixed_function.c`.
The input, compilation flags, machine and environment variables are all the same; **the only variable is the labelled function's body being switched from pre-fix to post-fix**.

All three rulings rest on "nothing but this function changed", so this rule cannot be skipped:

| Ruling | When to use it |
|---|---|
| `CONFIRMED_CVE_MATCH` | What was triggered is the labelled CVE, and the two sides differ |
| `CONFIRMED_OTHER_DEFECT` | Another real defect inside the labelled function, the two sides differ, plus `cve_match:false` |
| `OTHER_DEFECT_UNFIXED` | Upstream did not fix it, and both sides fault the same way |

**Only three situations allow not building the second side**:
(1) both sides fault the same way (that is `OTHER_DEFECT_UNFIXED`; record `fix_arm_also_vulnerable:true` honestly);
(2) the fix^ side does not exist structurally (e.g. the fix commit is purely additive and the labelled
function does not exist at fix^ at all); (3) the two sides' compiled products are completely identical (`CODEGEN_IDENTICAL`) — but that only
settles "is there a differential", not "does it crash", so you **still have to build one side and run an oracle once**.

### After building both sides you must verify once

```bash
md5sum arm_vuln arm_fix    # the two md5s must differ
```

If they are the same you never built two sides at all. **Observed in practice**: an agent let 5
`make`s write the same FFmpeg tree concurrently, and the 5 "fix" binaries came out byte-identical to
the vuln one, so every differential was fake. The root cause is that `setsid` without `--wait` silently detaches and the script runs on before the
build has finished. **Every `setsid` must be written as `setsid --wait`.**

---

## Hard prohibitions

- **Do not change any sample's `verdict`, and do not change `confirmation_class` either.**
  Your job is to supply evidence, not to re-rule — **the tier is part of the ruling**.
  (In practice an agent saw that `info.json`'s `cve` was null and changed three entries from `CONFIRMED_CVE_MATCH` to `CONFIRMED_OTHER_DEFECT` on its own. The direction was right, but that is
  an adjudication and is not yours to make. Write it into the report and let me rule.) If you think a confirmation does not stand → write it into the report and let me adjudicate;
  **you do not touch it**.
- **No downgrading.** A downgrade requires changing four places (dc.json / moving craft.json away /
  info.json / leaving a negative-result script), must strictly follow the loop prompt's procedure, and is not yours to do.
- **Do not touch `data/output/dynamic/confirmed/`** (the registry).
- **Do not change `vulnerable_function.c` / `fixed_function.c`** (the stored function bodies).
- `make -j8` maximum; at most 2-3 rebuilds at a time.
- **`pkill -f` / `killall` are forbidden** — they kill other people's work and your own as well.
  To kill something, start it with `setsid --wait`, note the PGID, and `kill -- -$PGID`.
- Run every binary with `timeout`, `ulimit -c 0`, `ASAN_OPTIONS=disable_coredump=1`, and `unset LD_LIBRARY_PATH` (in practice a crossed LD_LIBRARY_PATH makes both sides look identical).

## Where things land on disk

- Every sample's reproducible files go into `data/output/dataset/bigvul/<id>/dynamic_evidence/`.
  Writing to `/tmp`, `~` or anywhere outside `VulValidate/` is **forbidden**.
- **No absolute paths may appear in scripts.** Swapping one absolute path for another = not fixed.
  Before delivery, `grep -rn '/scratch/\|/tmp/\|/home/' *.sh` must produce no output.

  ★ **Making paths relative has a trap I fell into today, which once destroyed three samples' evidence.** It is **6 levels** up from `dynamic_evidence/` to the repository root. But **the order matters**:

  ```bash
  cd "$(dirname "$0")"                        # cd first
  R="$(cd ../../../../../.. && pwd)"          # ✅ already in the script's directory, so go up relatively
  ```
  ```bash
  cd "$(dirname "$0")"
  R="$(cd "$(dirname "$0")"/../../../../../.. && pwd)"   # ❌ wrong
  ```
  The wrong form: `$0` is the relative path **at call time** and becomes invalid after the `cd`, so the
  `cd` in the subshell fails, `$()` returns an **empty string**, the binary path becomes `/pathb/...` and `rc=127`.
  Worse, this failure **overwrites the good logs with failure output**.

  **So: before re-running after editing a script, back up the existing logs first**
  (`cp x.log x.log.bak`), and delete the backup only after confirming the new run is fine. I re-ran directly without a backup, which is exactly what happened.
- ★ **After fixing things, always go back and deal with the old `<id>/repro.sh` in the sample root.**
  A sample often has two scripts: the one in the root is the old one and still writes to `/tmp`, while the one in `dynamic_evidence/` is the clean one you just fixed. **Fixing only the latter does not
  count as finished** — in practice 739 samples are stuck in this shape, and it keeps finished samples
  from leaving the worklist. Handle it one of two ways:
  (1) change the root script into a one-line forwarder `exec "$(dirname "$0")/dynamic_evidence/repro.sh" "$@"`;
  (2) delete it, and note in `EVIDENCE_MAP.json` that it "has been superseded by dynamic_evidence/".
  **Read the root script before deleting it** and confirm it does not reference something that exists only in the root directory (one sample's root script referenced a `#ifdef FIXED` harness that lived
  only in the root, and deleting it outright lost that).
- Upstream build trees and banked binaries stay inside `pathb/<lane>/`; **do not copy them per sample**; write the git pin (remote + commit + configure line) in `EVIDENCE_MAP.json`.
- Paths in records are written in the relative form `dynamic_evidence/repro.sh`, not as a bare file name.

## Committing

Use `tasks/bigvul_reports/evidence_repair/overlap_commit.py`; for the arguments see the
"## Committing" section of `OVERLAP361_AGENT_BRIEF.md` (that is the authoritative version and includes
the mandatory `--confirmation-class` and the branches for both sides faulting / both sides clean).

`--not-measured --why '<a specific reason of at least 40 characters>'` is a **legal result**, not a failure.

---

## Self-check before delivery (all three have gone wrong in practice)

```bash
python3 tasks/bigvul_reports/evidence_repair/verify_batch.py --ids <all the ids you handled>
```

It prints one line per sample, and only the abnormal ones need expanding. **Delivery only counts once
it reaches 0 problems.**

What it checks corresponds to three easy mistakes:

1. **Logs are not reproduction files.** Only `.log` files in the directory = not acceptable — nobody else can "run it again".
2. **Both sides clean does not mean there is no vulnerability.** It may be that the harness never
   compiled the labelled function in at all (in practice 90% of 125 harnesses did not). Before drawing
   a conclusion, prove that the labelled code really executed.
3. **Compare stack frames with line numbers.** A patch pushes code downwards, so the same call site has a different line number on the fix side. Grepping a bare file name will show a pile of hits on the
   fix side and lead to the wrong conclusion that "the defect was not fixed". In practice: 181139's 6 frames at `cals.c:561` really are gone on the fix side, while the 17 frames
   at `cals.c:570` were merely pushed to 571.

**Also: do not truncate logs being checked with `grep -m2` or `head`** — sanitizer errors are often in
the second half of the file. I myself misjudged two good samples as fabrications because of `-m2`, and corrected it on the spot.

---

## What to hand back

**All per-sample detail goes into the JSON on disk**:
`tasks/bigvul_reports/evidence_repair/proj_<project name>_RESULT.json`, each entry being `{id, outcome, class, what_was_broken, oracle_kind, vuln_rc, fix_rc, one_line_evidence, committed}`.

**The reply you send me may contain only these four lines** (I will open the JSON for the detail
myself — every word you write has to pass through my context, and since I do not trust self-reports
anyway and will verify against the disk, writing more means paying twice for the same thing):

```
1. Result file path + how many handled / how many in total
2. How many of each outcome (one line of counts)
3. If not finished, which id it stopped at and why
4. Anything needing my adjudication: id plus one sentence only, at most 5 entries
```

Exceptions — the following three **must be named explicitly in the reply**, because they contaminate other samples and I will not see them unless I go looking:
- You found a tautological harness (the harness manufactures the defect and then reports the consequence)
- You found two samples sharing the same evidence, or a piece of "evidence" copied from elsewhere
- You touched any file outside this project

**Do not write anything in the report that you have not verified on disk. I will open the files one by
one and check.**

Anything odd outside those three that you are unsure about also goes into `proj_<project name>_RESULT.json` (add an `oddity` field with the phenomenon plus the exact lines you
saw on disk).
I will file it into `PROBLEM_REGISTER_20260803.md` — that is the standing problem register where all discovered difficulties and the sample ids involved are collected; **do not edit it yourself**.

---

## ★ Three items added on the afternoon of 2026-08-03 (all found in practice that day)

### 1. When ruling NOT_MEASURED, **the old `differential` block must be cleared along with it**

In practice with 179436 / 179927 / 179930 / 179931: the agent honestly recorded NOT_MEASURED, but
**the ASan text written in a previous round was not deleted** from the record (for example `heap-buffer-overflow WRITE size 512 (ceph_x_decrypt)`), while that sentence cannot be found in any log
on disk. The record then looks as if it "still has a measured value", which is **fake cleanliness**.

When clearing it, move the original text into a **history field explicitly marked with a date**, such
as `prior_differential_<date>`; do not simply delete it — that is the basis for tracing things later.

### 2. **The rc a record claims must match what the vuln side's log says**

In practice 9 samples' records said `vuln_rc=134` / `=7` / `=1`, while the last line of their own `vuln.log` said in black and white `vuln exit=0` with no sanitizer error anywhere.
Among them, 179623's log VERDICT line **itself says** "see the record for why this is not a differential", and 179293's log says that the race "never reproduced even once".

`verify_batch.py` now catches this. **Delivery must reach 0 problems**; do not just look at how many
the agent counted itself.

### 3. `differential` has more than one set of key names

`vuln_signal`/`fix_signal`, `vuln`/`fix`, `vuln_observed`/`fix_observed`, and a `detail` that writes
both sides together — all four exist on disk. **When you write, use `vuln_signal`/`fix_signal` uniformly**; when reading old records, recognize all
four.

---

## User instruction, 2026-08-03: "really attacked and nothing fired" has its own category; do not write NOT_MEASURED

The old way was: ran it, no differential → `NOT_MEASURED` / not confirmed. **This has changed.**

As long as you **really attacked the labelled function with attack inputs** and the vulnerability did not come out, write the result as:

```json
"verdict": "NOT_DYNAMICALLY_CONFIRMED",
"label_noise": true,
"label_noise_type": "label_noise_dynamic_tools_attacked",
"label_noise_basis": "dynamic_attack_negative",
"reason": "...containing the literal words label noise, stating what was attacked and how..."
```

**There are five hard gates for entering this category; miss one and you may not enter — write down
which one is missing and keep treating it as "not finished":**

1. **Really ran**: `differential.vuln_rc` is an **integer** exit code. Writing `"identical"` / `"n/a"` /
   `"unknown (build needed)"` never counts, and `dynamic_evidence/` must contain `repro.sh` plus non-empty logs.
2. **The labelled function really was executed**: `labelled_fn_executed: true` + `execution_proof`
   (in-function instrumentation / a gdb breakpoint / a gcov count / a frame for that function in the ASan backtrace). **Being compiled in does not count.**
3. **Attack inputs were used**: `attack_inputs` lists the inputs and the intent behind their
   construction. Running the function once normally **is not an attack**.
4. **The oracle is chosen correctly by CWE**: `oracle_kind` + `oracle_rationale`.
   Integer overflow needs UBSan, leaks need LSan, uninitialized memory needs MSan/Valgrind — "ASan reported nothing" says nothing whatsoever about those.
5. **The attack surface is stated clearly**: `attack_surface_note` — which entry points were tried,
   whether value ranges were scanned, how long it ran.

**Samples whose two sides are semantically identical** (no-op changes / hardening sweeps) may build only **one side** and run an oracle.
**Do not take "both sides behave the same" as an attack result** — both sides are the same code to
begin with, so identical behaviour is inevitable and is not a measurement.

**Label noise ruled from static reading** (reading the diff, counting files, looking at the commit title) always fills in `"label_noise_basis": "static_reading"`. The two evidence strengths differ by
orders of magnitude and must be countable separately.

**Why these five gates were added**: on 2026-08-03 the 1,160 samples of class C3 "no-op change" were measured, and **843 of them (72.7%) had `diff -w` textual comparison written in
`tried_dynamic_method` and not a single exit code in `differential`**, yet because the field is called
"tried_dynamic_method" they showed up in the statistics as "measured"; 1,057 did not even have a `dynamic_evidence/` directory.
Without gates, a new category just becomes the same rubbish bin. See **P25** in `PROBLEM_REGISTER_20260803.md`.

**Note**: you still **may not change any sample's `verdict` or `confirmation_class`**.
This new rule governs how you record the samples you newly work on; it does not authorize you to
re-rule old samples.

---

## Second user instruction, 2026-08-03: before ruling label noise you must attack first

**Reading the code alone cannot rule label noise.** Even if you are already convinced it is a mislabel — the commit touched 41 files, `diff -w` is empty,
everything changed is whitespace — **you must first really attack the labelled function with a dynamic tool, and only if the attack fires no vulnerability may you rule label noise.**

The reason: "this commit did not change this function" and "this function has no vulnerability" are
two different things.
Whether a function has a vulnerability depends on its own code, not on whether some commit touched it.

### Three terminal states

**(1) Attacked and nothing fired → this is what label noise is**

```json
"verdict": "NOT_DYNAMICALLY_CONFIRMED",
"label_noise": true,
"label_noise_type": "label_noise_dynamic_tools_attacked",
"label_noise_category": "<whole-commit-relabel | multi-function-relabel | whitespace-only-relabel |
                          cosmetic-refactor | wrong-function | version-skew | mass-hardening-sweep |
                          library-import-relabel | wrong-cwe | test-file-labeled | inverted-polarity>",
"label_noise_basis": "dynamic_attack_negative",
"real_vuln_location": "...",
"reason": "...containing the literal words label noise..."
```

**(2) Only the code was read, no attack yet → not a conclusion, a "suspicion"**

```json
"label_noise": false,
"suspected_label_noise": true,
"suspected_label_noise_category": "<the same vocabulary as above>",
"label_noise_basis": "static_reading"
```

**The sample stays on the worklist waiting to be attacked. Do not sign off on it as a conclusion.**

**(3) needs-Path-B (the tools cannot reach it)** is strictly distinguished from (1): cannot reach ≠ attacked and nothing fired.

### Where the attack evidence is stored (a hard requirement)

The fixed path **`<id>/dynamic_evidence/label_noise_attack/`**:

- `attack.sh` — one command that re-runs the whole attack, **with relative paths; `/tmp` and paths
  outside the repository are forbidden**
- driver / harness
- `body_vuln.inc` (plus `body_fix.inc` when there are two sides) — **copied word for word from the sample's own `vulnerable_function.c`**, verified with `cmp` inside `attack.sh`
- `inputs/` — every attack input, stored as binaries as-is
- `attack.<n>.log` — the **complete** output of every run, **no truncation**
- `ATTACK_LOG.md` — what was attacked, the intent of every shot, the result, why it stopped
- `EVIDENCE_MAP.json` — each file's purpose + sha256

**Without this directory the label-noise ruling does not stand**, and the sample goes back on the
worklist.

### The five hard gates (miss one and label noise may not be ruled)

1. **Really ran**: `differential.vuln_rc` is an **integer** exit code; `"identical"`/`"n/a"`/`"unknown"`
   are not allowed.
2. **The labelled function really was executed**: `labelled_fn_executed: true` + `execution_proof` (in-function instrumentation / a gdb breakpoint / a gcov count / a frame for that function in the
   ASan backtrace). **Being compiled in does not count.**
3. **Attack inputs were used**: `attack_inputs`. Running the function once normally **is not an attack**.
4. **The oracle is chosen correctly by CWE**: `oracle_kind` + `oracle_rationale`. Integer overflow needs UBSan, leaks need LSan, uninitialized memory needs MSan — "ASan reported
   nothing" says nothing whatsoever about those.
5. **The attack surface is stated clearly**: `attack_surface_note` — which entry points were tried,
   whether value ranges were scanned, how long it ran.

**Samples whose two sides are semantically identical** (no-op changes / hardening sweeps) may build only **one side** and run an oracle.
**Do not take "both sides behave the same" as an attack result** — both sides are the same code to begin with, so identical behaviour is inevitable.

### Three old instructions are void; do not follow them any more

- ~~If `diff -w` is identical, "mark label_noise directly and skip dispatching a subagent"~~ → now it
  may only be marked `suspected_label_noise` and must still be attacked. Its value becomes
  **downgrading to a single-side attack** (when the two bodies are identical, do not waste time building both sides).
- ~~">4-6 files means INCONCLUSIVE-relabel directly, do not waste a build"~~ → now used only to **set
  priority and choose the line of attack**.
- ~~The "INCONCLUSIVE+label_noise:true" in the full-coverage clause~~ → changed to `NOT_DYNAMICALLY_CONFIRMED + label_noise:true`, and it must come with an attack evidence directory.

**Note**: you still **may not change any sample's `verdict` or `confirmation_class`**.
This new rule governs how you record the samples you newly work on; it does not authorize you to
re-rule old samples.
