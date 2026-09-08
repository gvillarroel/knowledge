"""Auditable three-consecutive-miss schedule; Harbor owns all measured scores."""
from __future__ import annotations

import copy
import hashlib
import json
import math


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


class Sweep:
    """One family, a finite operator catalog, and an append-only attempt ledger."""
    def __init__(self, strategies, baseline_id, baseline_score, profile):
        if not math.isfinite(baseline_score):
            raise ValueError("A finite evaluated baseline is mandatory")
        self.strategies = copy.deepcopy(strategies)
        self.best_id, self.best_score, self.profile = baseline_id, baseline_score, copy.deepcopy(profile)
        self.operator = self.variant = self.failures = 0
        self.events = []
        self.seen = {digest(profile)}

    def next(self):
        while self.operator < len(self.strategies):
            item = self.strategies[self.operator]
            if self.failures >= 3 or self.variant >= len(item["variants"]):
                self.events.append({"event": "strategy-finished", "strategy": item["id"], "reason": "three-consecutive-failures" if self.failures >= 3 else "catalog-exhausted", "failures": self.failures, "unused_variants": len(item["variants"])-self.variant})
                self.operator += 1
                self.variant = self.failures = 0
                continue
            variant = item["variants"][self.variant]
            self.variant += 1
            return item, variant
        return None

    def claim(self, profile):
        key = digest(profile)
        if key in self.seen:
            self.events.append({"event": "duplicate-skipped", "profile_sha256": key})
            return False
        self.seen.add(key)
        return True

    def observe(self, candidate_id, profile, score, *, evaluable=True, qualified=True):
        if score is not None and (type(score) not in (float, int) or not math.isfinite(score)):
            raise ValueError("Invalid native score")
        if not evaluable:
            self.events.append({"event": "unavailable", "candidate": candidate_id, "score": None})
            raise RuntimeError("Non-evaluable execution stops the campaign without semantic fitness")
        if qualified and score is None:
            raise ValueError("Qualified candidate has no native score")
        improved = qualified and score > self.best_score + 1e-12
        previous = self.best_score
        if improved:
            self.best_id, self.best_score, self.profile = candidate_id, score, copy.deepcopy(profile)
            self.failures = 0
        else:
            self.failures += 1
        self.events.append({"event": "attempt", "candidate": candidate_id, "score": score, "qualified": qualified, "improved": improved, "incumbent_before": previous, "incumbent_after": self.best_score, "consecutive_failures": self.failures})
        return improved
