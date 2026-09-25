# The two scopes of a confirmation: defect site vs reachability

**User adjudication, 2026-07-31.** A confirmation must declare which of the two it is, otherwise the two kinds of sample are mixed under one label and downstream nobody can tell "this function contains a
defect" from "this function can carry attacker input to the defect".

The fields go in the sample's main record:

```json
"confirmation_scope": "defect_site" | "reachability",
"defect_site": {                       // mandatory when scope is reachability
  "function": "<the function that really contains the defect>",
  "file": "<the file it is in>",
  "reached_via": "<the call chain from the labelled function to it>",
  "defect": "<the observed defect, including the sanitizer text>"
},
"reachability_note": "<why the labelled function is not itself the defect site>"
```

## The criteria for each

**`defect_site`** — the **deciding point** of the defect is inside the labelled function. The counterfactual test: **if only this labelled function is changed, does the vulnerability go away?**
Yes → it is the defect site, and it does not matter where the crash lands.

This subsumes the existing `frame_note(alloc_site / fault_site)` rule: the labelled function under-allocates and the out-of-bounds happens in a `memcpy` it calls or in a helper function in the
same file — the defect is still in the labelled function, and the callee is merely the scene of execution.

**`reachability`** — the labelled function performs no defective operation itself, but it delivers
attacker-controllable input to the defect. The typical form is a pure forwarding shell function.
The upstream patch does not touch it.

The model case: **180356**, whose labelled function is

```c
PHP_FUNCTION(locale_get_primary_language) {
    get_icu_value_src_php(LOC_LANG_TAG, INTERNAL_FUNCTION_PARAM_PASSTHRU);
}
```

Four lines, one forwarding call, zero memory operations, and `97eff7eb` indeed did not change it. But the differential in `dynamic_evidence/` really was run (vuln_rc=1 / fix_rc=0), and the out-of-bounds is
in the `strlen()` of the callee `get_icu_value_internal`. Ruled `reachability`, with `defect_site` pointing at `get_icu_value_internal`.

## Three boundaries that must be held

**1. `reachability` is not label noise; do not set `label_noise: true`.**
In this repository `label_noise: true` is an **unconditional hard exclusion**, and setting it makes the sample disappear from the worklist outright — keeping a confirmation and marking noise at the same time
is self-contradictory. To record the fact that "the upstream patch does not touch the labelled function", write it in `reachability_note`.

**2. Reachability is transitive, so it must be observed, not inferred.**
If "it called a function that has a defect" were enough, then every level up the call chain to `main()`
would count too. The precondition for ruling `reachability` is that **a differential really was run**: a real input reaches the defect through the labelled function and becomes clean under the real patch.
Not having run it does not count — this is not relaxed just because the reachability criterion is used.

**3. `defect_site` must name a concrete function.** "The defect is elsewhere" is not an annotation, it is a brush-off. Not being able to name a concrete
function means it has not been investigated properly yet.

## Situations where this does not apply (still downgraded)

| Situation | Example |
|---|---|
| Never measured at all | 180376: `differential` itself says "not measured -- no build attempted" |
| A defect manufactured by the harness | 187416: deleting a guard that existed upstream before the fix |
| Both sides fault identically, no differential | 187837: `arms.diff` is 0 bytes, the same ASan report on both sides |

These three are **not** reachability — reachability requires that a differential really was observed.

---

# The second dimension: the oracle must be chosen by defect type (added 2026-07-31)

The first half of this document is about **where the defect is** (`defect_site` vs `reachability`). This section is about **how it is judged to have triggered**.
The two are independent dimensions and both must be written down.

## Why this section was added

On 2026-07-31 I twice in a row used "exit codes `0/0` on both sides" as a disqualifying criterion and challenged conclusions that were correct. What actually happened was:

- **178365** (exim): on the input `Bob <bob@${run{/bin/sh -c "id > .../PWNED"}}example.com>`,
  the vulnerable side printed `ARBITRARY COMMAND EXECUTED. The marker file was CREATED`.
  **The command really executed and the marker file really landed on disk — while the process exited normally with rc=0.**
- **177998**: an unprivileged caller calls the mount helper directly, passing
  `mh_command = /path/to/evil.sh`. rc=0.
- **181554**: XMPP carbons forgery, where the attacker's `<message>` is taken as coming from `boss@...`. rc=0.

The command injection succeeded, so of course the process exited normally. **Judging this class of
vulnerability by exit code is using the wrong oracle and then declaring there is no defect** — exactly the mistake this campaign has already recorded 13 times ("not ASan-visible" was the wrong tool choice
13 times out of 13). I wrote that warning into the instructions and then reproduced the very same mistake with exit codes.

## Comparison table

| Defect type | The correct oracle | What must not be used to judge it |
|---|---|---|
| Out-of-bounds read/write, UAF, double-free | ASan | The exit code (it may still be 0 when ASan defaults to `abort_on_error=0`) |
| Memory leak | LSan (`detect_leaks=1`) | The main ASan report |
| Uninitialized read | MSan (`clang -fsanitize=memory -O0`) | ASan — **it cannot see it** |
| Out-of-bounds within a struct | UBSan `-fsanitize=bounds` | ASan (it does not report out-of-bounds within one allocation) |
| Integer overflow, out-of-range shift | UBSan `-fsanitize=integer,shift` | ASan |
| **Command injection, path traversal, permission bypass, message forgery, information leak** | **Behavioural output differential**: what each side prints / side-effect files / return values | **The exit code** — the process exits normally when the attack succeeds |
| A missing access-control gate | Behavioural output differential (e.g. `injections_performed=1` vs `-EPERM`) | A sanitizer |
| Resource exhaustion (CWE-400/770/835) | Wall-clock ratio, peak RSS curve, timeout | Sanitizers, the exit code |
| assert / panic / abort | **rc=134 is itself a confirmed DoS** | Do not downgrade it because "there is no sanitizer report" |
| Infinite loop | Timeout (rc=124) + an iteration count | A sanitizer |

## Three rules

**1. Determine the defect type first, then choose the oracle.** Read the fix diff to work out what the
patch changes, then decide what to observe. Doing it the other way round — run ASan first and declare
there is no defect when nothing is reported — is this campaign's most common source of false negatives.

**2. `rc=0/0` does not mean "did not trigger".** It only means **this oracle** did not see it. The correct reading for a behavioural vulnerability is to diff what the two sides actually printed and the
side effects they produced (files, return values, state). A real "did not trigger" is: the oracle was changed, the input was changed, and the two sides are still
completely identical — then rule `NOT_TRIGGERED_BY_THIS_HARNESS` and state which ones were tried.

**3. The converse holds too: the two sides' output being "different" is not automatically a differential.** Look at where the difference is.
If the difference is only the PID, an address, a timestamp, a `mktemp` name, or a **source line number** caused by the two function bodies having different lengths, that is noise, not signal — normalize
before comparing. One round of this campaign compared raw ASan text directly and judged every single
run as "different".

## The relationship to the first half

A confirmation has to answer two questions correctly at once:

| Dimension | Field | Question |
|---|---|---|
| Where the defect is | `confirmation_scope` + `defect_site` | Is the deciding point of the defect the labelled function? |
| How it was seen | `tried_dynamic_method.oracle_kind` | Does the oracle used match this defect type? |

Only when both are right is the confirmation one that stands.
