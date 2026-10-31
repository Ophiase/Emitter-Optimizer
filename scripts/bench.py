from emitter_optimizer.kernel import Coverage, HardOcclusion
from emitter_optimizer.render import MapImage
from emitter_optimizer.service.paths import PROJECT_ROOT
from scripts.situations import PHYSICS, measure, situations

OUTPUT = PROJECT_ROOT / "docs" / "benchmark" / "results.md"
FIGURES = PROJECT_ROOT / "docs" / "benchmark"


def main() -> None:
    results = [measure(situation) for situation in situations()]
    lines = [
        "# Benchmark",
        "",
        "| case | initial | final | gain | seconds |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| {result.situation.name} | {result.initial_gain:.4f} | "
            f"{result.gain:.4f} | {result.improvement:+.4f} | "
            f"{result.seconds:.2f} |"
        )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    FIGURES.mkdir(parents=True, exist_ok=True)
    for result in results:
        coverage = Coverage(result.situation.scene, HardOcclusion(), PHYSICS)
        image = MapImage(result.situation.scene, coverage, width=640).png(
            result.positions
        )
        (FIGURES / f"{result.situation.name}.png").write_bytes(image)
    print(OUTPUT)


if __name__ == "__main__":
    main()
