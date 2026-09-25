#!/usr/bin/env python3
# NOTE (translated reference copy, 2026-09-25): comments, docstrings and human-facing strings were translated
# from the Chinese original; the regex alternatives that matched Chinese-language reason text were replaced by
# English glosses, so this copy documents the vocabulary but is not a drop-in classifier for records written in Chinese.
"""Single source of truth for how a PrimeVul sample's dynamic-analysis outcome is named.

Why this file exists
--------------------
The campaign used to report three outcomes -- confirmed / label noise /
build_failed -- and everything else fell into an unnamed remainder. On
2026-08-13 that remainder was 286 of 318 freshly classified samples, i.e. the
*majority*. Calling it "other" hid the fact that it is not one thing: a sample
whose fix arm is the one that crashes needs a completely different follow-up
from a sample whose two arms are byte-identical by construction.

So the taxonomy below names every outcome, and every name says what to do next.
Rules the categories encode (see route_campaign/ROUTE_AGENT_RULES.md):

  * label noise may only be concluded after a CWE-appropriate dynamic tool has
    actually attacked the labelled function and failed to trigger it. Reading the
    code supports `suspected_label_noise` only.
  * `build_failed` means "could not build, so could not attack". It is mutually
    exclusive with a real differential.
  * inverted polarity (the FIX arm is the one that faults) is never a confirmation.
  * a fault that lands in a sibling function, a caller, or harness-authored stub
    code is not attributable to the labelled function.

Used by:
  compute_blank_reason_statistics.py   (writes the JSON + Markdown breakdown)
  refresh_current_primevul_reports.py  (renders the section into the reports)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ----------------------------------------------------------------- top level

# User instruction 2026-08-14: only three categories may appear outwards; everything else is demoted to a secondary field.
# Every target=1 sample falls in exactly one of them, and the three numbers add up to the denominator.
DY_UNDECIDED = "DY_Attacked_But_can_not_decide_confirmed_or_label_noise"

TOP_LEVEL = {
    "CONFIRMED":            "Confirmed: the labelled function triggered a real defect on a faithful input",
    "LABEL_NOISE_EXCLUDED": "The mislabel stands: attacked with a tool matching the CWE, nothing triggered, all seven gates in place",
    DY_UNDECIDED:           "**A dynamic tool really did attack it and readings from both sides were obtained, but this measurement cannot decide whether it is a confirmation or a mislabel**"
                            " (for the specific reason it cannot be decided, see the secondary field dy_attacked_undecided_category)",
    "BUILD_FAILED":         "**Not measured**: cannot be built, cannot be reached, or simply has not been tested yet (for why it was not measured, see the secondary field build_failed_reason)",
}

# User instruction 2026-08-17: add the fourth outcome.
#
# Before this, "measured but not a confirmation" had no box of its own, so it was stuffed into a
# field literally named `build_failed_reason` (build failure reason) -- and not one of those 230 samples was a build failure.
# The consequence is concrete: anyone reading by the field name will read it wrong, and it directly
# violates §2b (`build_failed` and `attack_exhausted` are strictly separate). Today the same record
# told two different stories in two fields twice in a row (214365, 201328).
#
# There is only one dividing line, easy to remember and easy to check: **was this sample really attacked by a dynamic tool, and were readings from both sides obtained?**
#   attacked -> DY_Attacked_But_can_not_decide_confirmed_or_label_noise
#   the attack did not succeed / has not been attempted -> BUILD_FAILED

# The fourth outcome's secondary field (`dy_attacked_undecided_category`).
# Every entry must say which kind of "cannot decide" it is -- reporting only the total of the fourth outcome is meaningless.
DY_ATTACKED_UNDECIDED_CATEGORIES = {
    "attacked_no_trigger":    "Both sides really built and run, attacked with a matching tool, nothing fired, "
                              "but one or more of the seven gates is still missing -- once the gates are filled it should turn into LABEL_NOISE_EXCLUDED",
    "fault_not_attributable": "A fault fired, but it cannot be attributed to the labelled function (sibling function / caller / the harness's own code)",
    "decision_diff_no_impact": "There is a clean two-sided decision differential at the patch point, but no security consequence fired",
    "no_security_consequence": "There is a real behavioural difference, but no security consequence",
    "inverted_polarity":      "Inverted polarity: the one that faults is the build from the post-fix code, while the build from the pre-fix code is clean",
    "no_differential_possible": "By construction both sides are the same code, so a differential cannot exist; "
                                "**one of them must be attacked on its own to judge whether this function has a defect**",
    "synthetic_trigger":      "The trigger condition is manufactured by the harness and a real input cannot produce it",
    "reachability_unproven":  "The fault is inside the function body, but it was not proved that an attacker can reach it",
    "guard_never_evaluated":  "The disputed lines were never executed at all -- clean is not a conclusion about this function",
    "cve_mismatch":           "The labelled CVE does not belong to this commit or this function",
    "single_arm_only":        "Only one of them could be built and run; the second does not exist structurally",
    "unclassified_reason":    "A reason was written but the existing matching rules do not recognize it (the rules need extending; it is not the sample's problem)",
    "nominated_awaiting_adjudication": "Readings from both sides were obtained, **and a legal confirmation class has already been nominated** -- "
                              "what it owes is neither a measurement nor a write-up, but an adjudication. Added 2026-08-17: before this, such samples "
                              "were counted into `no_reason_recorded`, because the matcher looked only at the single field `confirmation_class_suggested_note` "
                              "while the rules require that note only **when the class is left empty**. So a record carrying a nominated class, "
                              "a real integer two-sided differential, execution proof and a positive control was still counted as having written no reason.",
    "no_reason_recorded":     "Readings from both sides were obtained, but the record does not say at all why it stopped here -- "
                              "**this value can only occur on the branch where the measurement holds**, so it belongs here, "
                              "not to BUILD_FAILED (it was put in the wrong place at the first split on 2026-08-17 and corrected the same day)",
}

# BUILD_FAILED's secondary field -- it now holds only the genuinely "not measured" ones.
BUILD_FAILED_REASONS = {
    "could_not_build":        "Repeated attempts still cannot build or reach it, so no attack succeeded at all -- our capability is insufficient, "
                              "**and no conclusion whatsoever about this function follows**",
    "suspected_only_never_attacked": "Only the code was read and it looked like a mislabel; not a single tool was ever run -- **it stays on the worklist waiting to be attacked**",
    "not_measured_yet":       "Not yet measured",
}

# Only the two tables together are all the values `build_failed_reason()` could historically return.
ALL_SECONDARY = {**DY_ATTACKED_UNDECIDED_CATEGORIES, **BUILD_FAILED_REASONS}


def top_level_for_reason(reason: str | None) -> str:
    """Which outcome a secondary value hangs under. **This is the only dispatch point; do not write it again elsewhere.**"""
    if reason in DY_ATTACKED_UNDECIDED_CATEGORIES:
        return DY_UNDECIDED
    return "BUILD_FAILED"

# Old top-level categories -> the new three plus a secondary field. Kept so the numbers in old reports can be reconciled.
LEGACY_TOP_LEVEL_MAP = {
    "LABEL_NOISE": ("LABEL_NOISE_EXCLUDED", None),
    "SUSPECTED_LABEL_NOISE": ("BUILD_FAILED", "suspected_only_never_attacked"),
    "ATTACK_EXHAUSTED": (DY_UNDECIDED, "attacked_no_trigger"),
    "SINGLE_ARM_ONLY": (DY_UNDECIDED, "single_arm_only"),
    "MEASURED_NO_VERDICT": (DY_UNDECIDED, None),
    "NOT_MEASURED": ("BUILD_FAILED", "not_measured_yet"),
}

# MEASURED_NO_VERDICT's sub-keys -> secondary field values.
# The name keeps `..._TO_BUILD_FAILED` only so existing callers are not broken; since 2026-08-17
# almost all of these values land under the fourth outcome, dispatched by top_level_for_reason().
BLANK_REASON_TO_BUILD_FAILED = {
    "INVERTED_POLARITY": "inverted_polarity",
    "NO_DIFFERENTIAL_POSSIBLE": "no_differential_possible",
    "ATTACKED_NO_TRIGGER": "attacked_no_trigger",
    "NOT_ATTRIBUTABLE": "fault_not_attributable",
    "DECISION_DIFF_NO_IMPACT": "decision_diff_no_impact",
    "NO_SECURITY_CONSEQUENCE": "no_security_consequence",
    "CVE_MISMATCH": "cve_mismatch",
    "SYNTHETIC_TRIGGER": "synthetic_trigger",
    "REACHABILITY_UNPROVEN": "reachability_unproven",
    "GUARD_NEVER_EVALUATED": "guard_never_evaluated",
    "NO_REASON_RECORDED": "no_reason_recorded",
    "UNCLASSIFIED_REASON": "unclassified_reason",
}

# ------------------------------------------------- the sub-classes of MEASURED_NO_VERDICT
#
# Every entry carries an `action` saying what to do next for that sub-class. The order is the matching priority.
BLANK_REASONS: list[dict] = [
    {
        "key": "INVERTED_POLARITY",
        "label": "Inverted polarity: the one that faults is the fix side, while the sample side is clean",
        "action": "Close the case. Unless the labelled function is redefined, no other result is possible.",
        "terminal": True,
        # Deliberately narrow: only explicit polarity language counts. A loose
        # "fix arm ... fault" pattern misfiled 210099, where fix_rc=1 merely means
        # the fixed code REJECTED the bad input -- that is correct behaviour and
        # the normal polarity, not a fault in the fix arm.
        "patterns": [r"invert(ed)? polarit", r"polarity is invert", r"polarity reversed",
                     r"the reason is polarity", r"runs the wrong way",
                     r"polarity is (the )?wrong"],
    },
    {
        "key": "NO_DIFFERENTIAL_POSSIBLE",
        "label": "By construction both sides are the same code, so a differential cannot exist",
        "action": "Close the case. The two sides compile to the same code (byte-identical, the same generated machine code, "
                  "or the patched lines are not compiled on this platform at all), so no amount of further attacking can produce a differential.",
        "terminal": True,
        # Only *construction* evidence belongs here. "both arms ran and nothing
        # fired" is a completely different situation -- there the two arms really
        # are different code and the attack came back negative, which is the entry
        # condition for label noise. That goes to ATTACKED_NO_TRIGGER.
        "patterns": [r"identical_by_construction", r"identical by construction",
                     r"byte-identical [^ ]{0,6} ?(assembly|binar|code|bodies|source)",
                     r"the two arms are byte-identical because",
                     r"codegen-identical", r"agree by construction",
                     r"(is|are) not compiled", r"browser-test-only",
                     r"expands to the literal", r"identical by construction"],
    },
    {
        "key": "ATTACKED_NO_TRIGGER",
        "label": "Both sides really were built and run, attacked with a matching tool, and no fault of any kind fired",
        "action": "This is precisely the entry condition for ruling a mislabel, not a terminal state. Next step: check that the oracle used matches "
                  "(out-of-bounds needs ASan, uninitialized needs MSan, integers need UBSan), that the positive control is alive, "
                  "and that the attack evidence (inputs plus run traces under label_noise_attack/) is complete. Only then should label_noise be ruled.",
        "terminal": False,
        "patterns": [
            r"attacked dynamically and (nothing|no defect) came out",
            r"nothing fired in either arm", r"neither arm produce[sd]",
            r"no fault (of any kind )?was produced,? in either",
            r"no fault was produced in either arm", r"nothing was triggered",
            r"both arms .{0,30}(clean|no asan|the same)",
            r"no (uninitialized disclosure|defect|fault) .{0,40}(across|in either)",
            r"rc 0/0", r"same checksum and no asan", r"measured neg",
            r"found no differential and no independently attributable fault",
            r"byte-identical (output|behaviou?r)", r"identical signature counts on both arms",
            r"nothing triggered in either arm", r"exit 0 with no sanitizer output",
            r"produce[sd]? byte-identical", r"no sanitizer fired in either arm",
        ],
    },
    {
        "key": "NOT_ATTRIBUTABLE",
        "label": "A fault fired, but it cannot be attributed to the labelled function (sibling function / caller / the harness's own code)",
        "action": "Still salvageable: change the entry point, supply the real call path, or build a third side for a counterfactual.",
        "terminal": False,
        "patterns": [r"not independently attributable", r"not attributable", r"cannot be attributed|attributed to",
                     r"sibling", r"zero frames", r"harness-authored", r"in (my|the) stub",
                     r"scaffold", r"belongs to the vulnerable .{0,20}assembly",
                     r"every frame in .{0,40}(allocator|operators)", r"harness'?s (own )?(model|modell?ed)", r"self-written stub", r"stub_[a-z]+\.h", r"harness-constructed", r"outside (this|the) harness", r"outside the labelled (body|function)", r"is a test client"],
    },
    {
        "key": "DECISION_DIFF_NO_IMPACT",
        # ★ After the owner's ruling on 2026-08-21, this entry also covers the former `no_security_consequence`.
        # Both ask the same thing: a real difference was measured, but it has no security consequence.
        "label": "A real difference was measured, but it has no security consequence -- covering two wordings: "
                 "(1) there is a clean two-sided decision differential at the patch point, yet no sanitizer fault, no out-of-bounds/leak; "
                 "(2) there is a real behavioural difference (a rendering difference, by design), but it does not reach a security boundary",
        "action": "Two steps. First ask whether it can still be salvaged: wire up the real downstream consumer, or switch to an oracle that can see this kind of consequence "
                  "(out-of-bounds needs ASan, uninitialized needs MSan, integers need UBSan, leaks compare byte counts) -- "
                  "this class is the most likely to flip to a confirmation. Only when it cannot be salvaged and the difference really stops at the behavioural level "
                  "does it become a human adjudication of how large a behavioural difference has to be to count as a vulnerability.",
        "terminal": False,
        "patterns": [
            r"clean,? (and )?(reproducible )?two-arm (decision )?differential",
            r"decision differential", r"differ by a real integer exit code",
            r"guard-bypass differential", r"separates cleanly",
            r"real,? attributable behavioural difference",
            r"(asan|msan|ubsan|sanitizer)s? remains? silent",
            r"but (nothing|no) .{0,40}(defect|fault|consequence) .{0,20}(was )?(measured|observed|produced)",
            r"real,? (and )?(reproducible|deterministic|repeatable)?,? ?two-arm (behaviou?ral )?differential", r"behaviou?r(al)? differential", r"count differential", r"the differential is real", r"no independently attributable fault", r"a behavior difference alone is not", r"real two-arm", r"two arms (really )?do differ", r"differ only in"],
    },
    {
        "key": "NO_SECURITY_CONSEQUENCE",
        "label": "There is a real behavioural difference, but no security consequence (a rendering difference, by design)",
        "action": "Needs human adjudication: how large a behavioural difference has to be to count as a vulnerability.",
        "terminal": False,
        "patterns": [r"no security (consequence|impact|boundary)", r"not a security",
                     r"rendering", r"cosmetic", r"by design", r"by design|no security impact",
                     r"wrong (mac|prf|output|message)", r"only a wrong", r"hardening step,? not a demonstrated", r"is a hardening", r"nothing that was measured is a defect", r"no availability, authoriz", r"writer regression"],
    },
    {
        "key": "CVE_MISMATCH",
        "label": "The labelled CVE does not belong to this commit or this function",
        "action": "Needs human adjudication: under the current rules a CVE mismatch does not veto a confirmation; if the function has a real defect of its own it should be recorded as CONFIRMED_OTHER_DEFECT + cve_match:false.",
        "terminal": False,
        "patterns": [r"cve does not belong", r"labelled cve .{0,40}(not|another|different)",
                     r"wrong component", r"belongs to (another|a different)", r"the CVE belongs to", r"(is |it is )?not the .{0,60}described by CVE", r"not the .{0,40}CVE-\d"],
    },
    {
        "key": "SYNTHETIC_TRIGGER",
        "label": "The trigger condition is manufactured by the harness and is not one a real input can produce",
        "action": "Still salvageable: find a value a real entry point can produce.",
        "terminal": False,
        "patterns": [r"synthetic", r"harness[- ]suppl(y|ied|ies)", r"manufactured",
                     r"harness creates a .{0,30}skew", r"synthetic"],
    },
    {
        "key": "REACHABILITY_UNPROVEN",
        "label": "Reachability proof missing: the fault is inside the function body, but it was not proved that an attacker can reach it",
        "action": "Still salvageable: supply a reachable path from a real entry point; if it cannot be proved, write UNKNOWN and list the entry points searched.",
        "terminal": False,
        "patterns": [r"reachab", r"unreachable", r"no upstream caller", r"cannot be reached",
                     r"the code that would have to run .{0,30}did not"],
    },
    {
        "key": "GUARD_NEVER_EVALUATED",
        "label": "The disputed lines were never executed at all (the guard was evaluated but never entered, or the whole block is dead code)",
        "action": "Still salvageable: change the input so the disputed lines really execute; this must be kept separate from \"it was reached and nothing happened\".",
        "terminal": False,
        "patterns": [r"never (reached|executed|taken)", r"did not (execute|run)",
                     r"neither aborts nor produces", r"(contested|patched|guard(ed)?|disputed)[^.]{0,60}0 times|0 times[^.]{0,60}(contested|patched|guard|disputed)", r"never hit", r"(contested|patched|disputed|that branch|the branch)[^.]{0,50}dead code|dead code[^.]{0,50}(branch|line|path)(?![^.]{0,30}from )", r"hit zero times", r"never executes it", r"is a guard (that|which) (never|was never)"],
    },
]

# 2026-08-15: `unclassified_reason` once reached 82. Reading those notes one by one showed they
# **all did write a reason**, the wording just was not in the vocabulary -- a gap in the matching rules, not samples without a reason.
# The following are supplementary wordings taken from real notes, **without touching the original list above** (the last time
# those inline lists were edited directly, the insertion point hit a `]` inside a regex character class and cut a string in half).
# **The residue still lands in `unclassified_reason` and stays visible** -- a positive vocabulary inherently produces silent misses,
# so the gap must stay on the report instead of being swallowed by a catch-all category.
EXTRA_PATTERNS = {
    "DECISION_DIFF_NO_IMPACT": [
        r"no in-tree consumer",
        r"nothing in the (client|caller)'?s own",
        r"downstream[^.]{0,60}was not (repro|observed|demonstrated)",
        r"different .{0,40}decisions? at the patched",
        r"byte-level difference",
        r"different integer exit codes on the same faithful",
        r"limit of what was observed, not doubt about the code",
    ],
    "NO_DIFFERENTIAL_POSSIBLE": [
        r"compiled away",
        r"identical rc histogram",
        r"the only comparable schedule is clean",
    ],
    "NOT_ATTRIBUTABLE": [
        r"fault site is harness\.",
        r"faults? occur[^.]{0,40}(harness|sweep)",
        r"stop on harness-model behaviour",
    ],
    "GUARD_NEVER_EVALUATED": [
        r"condition the patch guards never held",
        r"never held during the run",
    ],
    "NO_SECURITY_CONSEQUENCE": [
        r"benign error path",
        r"perf-accounting",
        r"dying cleanly",
    ],
    "ATTACKED_NO_TRIGGER": [
        r"nothing faulted on either arm",
        r"made to fail, in both arms, with an oracle proven",
        r"both arms were built and driven[^.]{0,60}live positive control",
    ],
}
for _r in BLANK_REASONS:
    _r["patterns"] = list(_r["patterns"]) + EXTRA_PATTERNS.get(_r["key"], [])

# ---------------------------------------------------------------- 2026-08-17 matcher corrections
# The owner said "the three buckets do not match their names; find out why, then fix the way the statistics are computed".
# The diagnosis and the measured numbers are in evidence_repair/MATCHER_DIAGNOSIS_20260817.md. The essentials:
# of the 285 samples in the fourth outcome that have reason text, **135 (47%) hit 2 or more categories at once**
# and were silently classified first-come-first-served; another 17 had their first hit in a negated context, meaning exactly the opposite.
# In other words, nearly half of the secondary categories were decided by the **ordering** of the patterns, not by the content of the record.

# (1) These bare words hit "mentioned in passing", not "asserted". Measured: /reachab/ hit 73 times while that bucket holds only
#     16 (it ranks 9th, so most were taken by earlier entries); /sibling/ 24 times; /synthetic/ 12 times.
#     A value of None = delete the entry entirely; otherwise replace it with a context-bearing expression.
_RETIRED_PATTERNS = {
    r"reachab": (r"(attacker|entry ?point|caller|input|attack surface)[^.]{0,80}reachab"
                 r"|reachab[^.]{0,80}(attacker|entry ?point|input|attack surface)"
                 r"|reachability (is |was )?(unproven|not (shown|demonstrated|established|proven))"),
    r"sibling": r"sibling (function|overload|frame|symbol)",
    r"synthetic": r"synthetic (trigger|input|condition|geometry|value|magic)",
    r"scaffold": r"(harness|test|driver) scaffold",
    r"cosmetic": r"cosmetic (only|change|difference|refactor)",
    r"rendering": None,
    r"by design": None,
    # Measured 2026-08-17, second pass: neither of these two hits means "an attacker cannot reach it".
    # /cannot be reached/ hit 9213's "the disputed branch cannot be reached at all" -- that is guard_never_evaluated,
    #   so it was moved to that category (see _ADDED_PATTERNS) rather than deleted.
    # /unreachable/ hit 207223's "the upstream out-of-bounds consumer has been dead code since 5.4"
    #   and 5534's "the fix explicitly asserts that scenario is unreachable" -- both describe the code,
    #   not a shortfall in our own evidence. Kept, but must carry attacker context.
    r"cannot be reached": None,
    r"unreachable": (r"(attacker|entry ?point|attack surface|input)[^.]{0,60}unreachable"
                     r"|unreachable[^.]{0,60}(attacker|entry ?point|attack surface)"),
}

# Expressions moved in from elsewhere (not newly invented criteria, but existing criteria put back in the category they belong to).
_ADDED_PATTERNS = {
    "GUARD_NEVER_EVALUATED": [r"cannot be reached", r"could not be reached",
                              r"was never reached", r"contested (branch|line)s? .{0,30}not"],
}

def _apply_retirements(pats):
    out = []
    for pat in pats:
        if pat in _RETIRED_PATTERNS:
            repl = _RETIRED_PATTERNS[pat]
            if repl is None:
                continue
            out.append(repl)
        else:
            out.append(pat)
    return out

_COMPILED = [(r["key"],
              [re.compile(p, re.I)
               for p in _apply_retirements(r["patterns"]) + _ADDED_PATTERNS.get(r["key"], [])])
             for r in BLANK_REASONS]

# (2) Negation guard. /invert(ed)? polarit/ will hit "so this is NOT inverted polarity"
#     -- that is how 210884 got swept into inverted_polarity. If a negator appears within 60 characters
#     to the left of the hit, the hit is void. This corresponds to the "CONFIRM substring-match gotcha" in memory.
# ★ 2026-08-17, third pass: the first version of the guard used a 60-character window and **got more wrong than the problem it fixed**.
# Of the 18 hits it killed in practice, only 3 deserved killing. The reason is that these categories are **semantically negative by nature**
# ("nothing fired in either arm", "no fault was produced"), so a negator in the preceding clause is the norm:
#   202263 "no FAULT was observed in either arm and <<no security consequence>>"   <- wrongly killed
#   210125 "no fault was produced, so this is a <<decision differential>>"          <- wrongly killed
#   4281   "it is not 'attacked_no_trigger' either, because <<the differential is real>>" <- wrongly killed
#   210379 "line 162 is <<never reached>>"                                          <- wrongly killed
# The correct criterion is that the negator is **immediately adjacent to the matched phrase** ("is not <<inverted polarity>>"),
# with only a few function words allowed in between. The window is tightened from 60 characters to "immediately adjacent".
_NEGATOR = re.compile(
    r"\b(?:not|never|isn'?t|wasn'?t|aren'?t|weren'?t|no longer|hardly|"
    r"by no means|nothing like|far from|anything but)\s+"
    r"(?:a |an |the |really |actually |simply |merely |strictly |truly )?$",
    re.I)


def _affirmative_hit(pat, note):
    """True only when this expression hits in an **affirmative** context. A hit in a negated context is always void."""
    for m in pat.finditer(note):
        left = note[max(0, m.start() - 60):m.start()]
        if not _NEGATOR.search(left):
            return True
    return False


# ★ Owner's ruling 2026-08-21: merge `no_security_consequence` into `decision_diff_no_impact`.
#
# The two ask the same thing: **a real difference was measured, but it has no security consequence.**
# Writing them separately is just two wordings -- the first starts from "there is a clean two-sided decision differential at the patch point",
# the second from "there is a real behavioural difference", and they land in exactly the same place.
#
# The cost is concrete and countable: **27** samples pending adjudication hit both entries at once,
# and since the matcher by design "may not resolve ambiguity by ordering", it sent them into `unclassified_reason`.
# In other words those 27 did not fail to write a reason; **we ourselves split one question into two rules** and caused it.
# After the merge they disambiguate on the spot.
#
# `no_security_consequence` is kept as an **alias** (`_MERGED_KEYS` folds only at the hit-set level),
# because records already on disk carry that value and deleting it would make them unreadable.
# Both patterns in the vocabulary remain in force; they just fold into the same canonical value.
_MERGED_KEYS = {"NO_SECURITY_CONSEQUENCE": "DECISION_DIFF_NO_IMPACT"}


def matching_blank_reasons(note):
    """Which categories this reason text hits affirmatively -- order-independent, all returned.

    The hit set is folded by `_MERGED_KEYS` and then deduplicated, so hitting both of the merged
    entries at once no longer counts as ambiguity. The folding is here rather than at the call sites
    so that the rule in `classify_blank_reason` that multiple hits = cannot decide benefits automatically,
    without having to be written again at each call site (private copies cause number drift).
    """
    hits = [key for key, pats in _COMPILED
            if any(_affirmative_hit(p, note) for p in pats)]
    seen = set()
    out = []
    for k in hits:
        k = _MERGED_KEYS.get(k, k)
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out
REASON_BY_KEY = {r["key"]: r for r in BLANK_REASONS}


def classify_blank_reason(note: str | None) -> str:
    """Map a `confirmation_class_suggested_note` to one of BLANK_REASONS.

    Returns "UNCLASSIFIED_REASON" when no pattern matches. That is deliberately a
    *visible* bucket, not a silent default: an earlier version of this matcher used
    Chinese-only patterns against English notes and dropped 63% into "other",
    which looked like the records were vague when in fact the matcher was.
    Anything landing here means this file needs another pattern, not that the
    sample lacks a reason.
    """
    if not note or not note.strip():
        # Not the same thing as "the matcher missed it": the record itself never
        # said why. Keeping these apart is the difference between "fix this file"
        # and "go back to that sample and write down what stopped it".
        return "NO_REASON_RECORDED"
    hits = matching_blank_reasons(note)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        # (3) Ambiguity may not be resolved by ordering. This used to be first-come-first-served, so 135 samples'
        # categories were decided by the ordering of _COMPILED. Now it says honestly "our rules cannot decide" --
        # the vocabulary's definition of UNCLASSIFIED_REASON is already "the rules need extending; it is not the sample's problem".
        # This makes the bucket visibly larger; that is what fixed looks like, not what broken looks like,
        # and it is the same principle as "if you cannot count it, write cannot be read, never 0".
        return "UNCLASSIFIED_REASON"
    return "UNCLASSIFIED_REASON"


LEGAL_CLASSES = {"CONFIRMED_CVE_MATCH", "CONFIRMED_OTHER_DEFECT", "OTHER_DEFECT_UNFIXED"}


def _class_value(rec: dict) -> str:
    """The sample's class, or a visible marker for anything that is not one.

    Measured 2026-08-15: 188 records carry a `confirmation_class_suggested` that
    is not one of the three legal values -- 153 empty strings, 31 the literal
    string "NONE", and 4 whole sentences (one of which BEGINS with a real class
    name and is therefore a nomination the publish gate drops on the floor).
    "NONE" is truthy, so `x or y or "<not written>"` passes it straight through and it
    lands in the report as if it were a class.  Anything illegal is bucketed
    visibly instead: a wrong value that looks wrong gets fixed, one that looks
    like a class does not.
    """
    for value in (rec.get("confirmation_class"), rec.get("confirmation_class_suggested")):
        if value in LEGAL_CLASSES:
            return value
        if isinstance(value, str) and value.strip() and value not in LEGAL_CLASSES:
            return f"<illegal value: {value.strip()[:30]}>"
    return "<not written>"


def confirmed_detail(rec: dict) -> dict:
    """Secondary fields for a CONFIRMED sample, read straight off the record."""
    return {
        "confirmation_class": _class_value(rec),
        "cve_match": rec.get("cve_match") if isinstance(rec.get("cve_match"), bool) else "<not written>",
        "confirmation_scope": rec.get("confirmation_scope")
                              or rec.get("confirmation_scope_suggested") or "<not written>",
        "reachability": rec.get("reachability") or rec.get("reachability_suggested") or "<not written>",
    }


def label_noise_detail(rec: dict) -> dict:
    """Secondary fields for a LABEL_NOISE_EXCLUDED sample."""
    return {
        "label_noise_category": rec.get("label_noise_category") or "<not written>",
        "label_noise_basis": rec.get("label_noise_basis") or "<not written>",
        "label_noise_type": rec.get("label_noise_type") or "<not written>",
        # A mislabel claim says nothing about a CVE, so this is deliberately not
        # a true/false: writing false here would read as "the CVE does not match",
        # which is a different and stronger statement than "not applicable".
        "cve_match": "n/a (a mislabel conclusion has nothing to do with CVE matching)",
    }



# ★ The ninth hole (2026-08-17, caught by an agent): GUARD_NEVER_EVALUATED's three expressions are too loose
# and pull samples into this box by **wording** rather than by **measurement**:
#   `dead code` hit a **commit title**, "Removing dead code from NetworkActionPredictor" (5531);
#   `0 times`   hit 988's sentence saying BUG_ON "was hit 0 times", while its own gate accounting says gate 7 PASS
#               -- that 0 says the **fix side** did not crash, not that the disputed lines did not run;
#   `is a guard` hit 206966's "...is a guard decision", which is talking about a **decision differential**.
# All three now carry a context requirement. The structured `_gate7_failed()` judges all four of these samples correctly;
# **what was wrong all along was the free-text fallback.**
_GATE7_FAIL_RE = re.compile(r"\bFAIL(?:S|ED)?\b|\bNOT_HIT\b", re.I)


def _gate7_failed(rec):
    """Whether the record **explicitly** says gate 7 (the disputed lines were executed) failed.

    It reads only the conclusion fields, and requires the conclusion to **start with FAIL/NOT_HIT** -- measured 2026-08-17:
    `\bFAIL\b` does not match `FAILS`, while "hit 1 time" in a sibling field falsely matches `\bHIT\b`,
    which is how 210669 was read as passing (its own record says FAILS_CONTESTED_LINES_NEVER_RAN).
    If no conclusion can be read, return False -- **do not infer "failed" from "I could not read it".**
    """
    fails, passes = [], []
    for key, val in rec.items():
        if not isinstance(val, dict):
            continue
        # The conclusion may hang on the **outer** key (`gate7_check_20260817`'s `result`),
        # or on the **inner** key (`gate6_gate7_status.gate_7_...`). Both must be looked at --
        # looking only at the inner one misses 197499, looking only at the outer one misses 210669.
        if re.search(r"gate[_\- ]?7", key, re.I):
            for rk in ("result", "verdict", "status", "conclusion", "pass"):
                if rk in val:
                    rv = val[rk]
                    if rv is False:
                        fails.append(key); break
                    head = str(rv).strip().upper()[:24]
                    if head.startswith(("FAIL", "NOT_HIT")):
                        fails.append(key); break
                    if head.startswith(("PASS", "HIT")):
                        passes.append(key); break
        for k2, v2 in val.items():
            if not re.search(r"gate[_\- ]?7", k2, re.I):
                continue
            # ★ The eleventh of the same shape (2026-08-17): this used to serialize the dict, strip '"{ ' and look at the start,
            # so `{"pass": false, ...}` stripped down to `PASS": FALSE` -- **and was read as PASS**.
            # That is how 283 fell from guard_never_evaluated into attacked_no_trigger (implying the negative result stands),
            # while its stored body was truncated in the first place. **Structured fields must be read structurally, not guessed by prefix after serializing.**
            if isinstance(v2, dict):
                verd = None
                for rk in ("pass", "result", "verdict", "status", "conclusion"):
                    if rk in v2:
                        rv = v2[rk]
                        if isinstance(rv, bool):
                            verd = "PASS" if rv else "FAIL"
                        else:
                            h = str(rv).strip().upper()[:24]
                            if h.startswith(("FAIL", "NOT_HIT", "N/A", "NOT_APPLICABLE")):
                                verd = "FAIL"
                            elif h.startswith(("PASS", "HIT")):
                                verd = "PASS"
                        break
                if verd == "FAIL":
                    fails.append(k2)
                elif verd == "PASS":
                    passes.append(k2)
                continue
            head = str(v2).strip().upper()[:24]
            if head.startswith(("FAIL", "NOT_HIT")):
                fails.append(k2)
            elif head.startswith(("PASS", "HIT")):
                passes.append(k2)
    # ★ The tenth of the same shape (2026-08-17): this used to "return True on the first FAIL hit",
    # so an **old** gate-7 FAIL would override a PASS/HIT measured later --
    # those five ImageMagick samples were re-measured, three of them were proved impossible by construction,
    # and one of the 0 counts was caused by gdb breakpoint slide, yet the classification did not budge.
    # **When the two conflict, do not silently file it under guard_never_evaluated**: that is choosing the older one on someone's behalf.
    if fails and passes:
        return False
    return bool(fails)

def secondary_reason(rec: dict) -> str:
    """The secondary value for this sample, whichever of the two outcomes it lands in.

    Order matters and is not arbitrary: the two states that must never be read as
    each other are checked first and separately.  "could not build" is about our
    capability and supports no conclusion about the function; "attacked and
    nothing fired" is about the function and is one gate away from label noise.

    Since 2026-08-17 those two no longer share a top level either -- call
    `top_level_for_reason()` on the result to find out which outcome it belongs to.
    """
    if (str(rec.get("blocked_reason") or "") == "build_failed"
            or isinstance(rec.get("build_failure"), dict)):
        return "could_not_build"
    # ★ The order matters: when gate 7 explicitly failed, it **must be judged first** and attack_exhausted must not jump ahead.
    # The sentence "attacked, attacked repeatedly, and nothing fired" presupposes that **the disputed lines really ran**;
    # when the disputed lines were hit 0 times, that "nothing fired" is not a conclusion about this function (P68),
    # and filing it under attacked_no_trigger pushes it towards "fill the gates and it turns into label noise" -- **exactly the wrong direction**.
    # ★ When the stored body is truncated, any "attacked and nothing fired" is attacking the **wrong object** (P67: 177956's truncated body
    # is legal C, compiles, and returns 0/0 perfectly cleanly on an input that makes the real function read 2000 bytes out of bounds).
    # §7's gate 6 says explicitly that this situation is `stored_body_incomplete + needs-Path-B`,
    # and **it must never land in a box that implies the negative result stands**.
    if rec.get("stored_body_incomplete") is True:
        return "no_differential_possible"
    if _gate7_failed(rec):
        return "guard_never_evaluated"
    # ★ The order (third adjustment, 2026-08-17): **a record that nominated a legal confirmation class cannot at the same time be
    # "attacked, attacked repeatedly, and nothing fired".** Measured on 197499: `attack_exhausted` was a stale marker left by that
    # MP4Box round (on that binary the patched call is a no-op anyway, so a differential cannot exist),
    # while after the gpac playback path was built, 343 x (vuln 1 leak / fix 0) was measured.
    # Letting a stale attack_exhausted jump ahead of the nomination would show a confirmation nomination as "close to a mislabel".
    if str(rec.get("confirmation_class_suggested") or "").strip() in LEGAL_CLASSES:
        return "nominated_awaiting_adjudication"
    if isinstance(rec.get("attack_exhausted"), dict) or rec.get("attack_exhausted") is True:
        return "attacked_no_trigger"
    if str(rec.get("blocked_reason") or "") == "single_arm_only":
        return "single_arm_only"

    diff = rec.get("differential")
    tdm = rec.get("tried_dynamic_method")
    measured = (isinstance(tdm, dict) and isinstance(diff, dict)
                and isinstance(diff.get("vuln_rc"), int)
                and isinstance(diff.get("fix_rc"), int))
    if measured:
        # A sample that nominated a LEGAL confirmation class is not "no reason
        # recorded" -- it said what it thinks it is and is waiting for a
        # dispatcher.  Checking this BEFORE the note keeps the two apart.  Only a
        # vocabulary value counts: "NONE", or a whole sentence pasted into the
        # slot, is a different defect and must stay visible rather than be
        # laundered into this bucket.
        # ★ Evening of 2026-08-17: for a sample whose gate 7 explicitly FAILED, its "clean" is not a conclusion about this function.
        # `guard_never_evaluated` in the vocabulary exists for exactly this case:
        # "the disputed lines were never executed at all -- exactly the opposite: that 'clean' is not a conclusion about this function".
        # They all used to land in `attacked_no_trigger` ("one or more gates still missing"),
        # whose next action is "fill the gates and it turns into label noise" -- **the wrong direction**;
        # what these samples need is **a different input so the disputed lines execute**.
        # The criterion only accepts a conclusion in the record explicitly stating gate 7 failed; if it cannot be read, leave it alone.
        if str(rec.get("confirmation_class_suggested") or "").strip() in LEGAL_CLASSES:
            return "nominated_awaiting_adjudication"
        key = classify_blank_reason(rec.get("confirmation_class_suggested_note"))
        return BLANK_REASON_TO_BUILD_FAILED.get(key, "unclassified_reason")
    if rec.get("suspected_label_noise") is True:
        return "suspected_only_never_attacked"
    return "not_measured_yet"


# Old name kept so nothing that imports it breaks.  It no longer means "this
# sample is in BUILD_FAILED" -- ask top_level_for_reason() for that.
build_failed_reason = secondary_reason


def classify_sample(rec: dict, in_registry: bool = False) -> tuple[str, str | None]:
    """Return (top_level, secondary) for one dynamic_confirmation.json.

    FOUR top-level values since the owner's 2026-08-17 instruction (three before
    that).  The fourth exists because "we attacked it and the measurement cannot
    decide" is not a build failure and never was -- 230 samples had been carrying
    that meaning inside a field literally named `build_failed_reason`.

    The old verdict strings (INCONCLUSIVE, NOT_DYNAMICALLY_CONFIRMED, DEFERRED,
    NEEDS_PATH_B, ...) are still not outcomes: they survive only inside the record
    as history.  What changed is where they land -- a sample that was really
    attacked now lands in DY_Attacked_But_can_not_decide_confirmed_or_label_noise,
    and only one that was never successfully measured lands in BUILD_FAILED.
    """
    verdict = str(rec.get("verdict") or "")
    if in_registry or verdict.startswith("DYNAMICALLY_CONFIRMED") or verdict == "CONFIRMED":
        return "CONFIRMED", None
    if rec.get("label_noise") is True:
        return "LABEL_NOISE_EXCLUDED", None
    reason = secondary_reason(rec)
    return top_level_for_reason(reason), reason


def terminal_keys() -> set[str]:
    """Blank-reason keys that cannot produce a different answer on a re-attack."""
    return {r["key"] for r in BLANK_REASONS if r["terminal"]}
