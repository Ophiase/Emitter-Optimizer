import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from emitter_optimizer.kernel.placement.exact import Certificate, Instance


@dataclass(frozen=True, slots=True)
class ExactReport:
    """A certificate, written where a person can read it and check it."""

    instance: Instance
    certificate: Certificate

    def summary(self, plan: Path | None) -> dict[str, object]:
        lower, upper = self.certificate.lower, self.certificate.upper
        summary: dict[str, object] = {
            "covered_weight": lower,
            "total_weight": int(self.instance.weights.sum()),
            "upper_bound": upper,
            "proved_optimal": self.certificate.proved,
            "candidates_examined": self.certificate.vertices,
            "seconds": round(self.certificate.seconds, 3),
        }
        if plan is not None:
            covered = self.instance.covered_weight(
                np.loadtxt(plan, delimiter=",", ndmin=2, comments="#")
            )
            summary["your_plan"] = {
                "covered_weight": covered,
                "percent_below_the_bound": round(100.0 * (upper - covered) / upper, 3),
            }
        return summary

    def write(self, directory: Path, plan: Path | None) -> dict[str, object]:
        directory.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            directory / "positions.csv", self.certificate.positions, delimiter=","
        )
        summary = self.summary(plan)
        (directory / "certificate.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        return summary
