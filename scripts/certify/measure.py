from emitter_optimizer.kernel.placement.exact import ExactPlacement, Instance
from scripts.certify.runs.discrete import Discrete
from scripts.certify.runs.engine_runs import EngineRuns
from scripts.certify.scores import Scores

EXACT_SECONDS = 600.0


def measure(instance: Instance) -> tuple[Scores, dict[str, object]]:
    certificate = ExactPlacement(instance, EXACT_SECONDS).solve()
    discrete = Discrete(instance)
    engine = EngineRuns(instance).run()
    scores = Scores(
        name=instance.name,
        points=instance.points.shape[0],
        emitters=instance.emitters,
        walls=instance.walls.shape[0],
        lower=certificate.lower,
        upper=certificate.upper,
        vertices=certificate.vertices,
        columns=certificate.columns,
        exact_seconds=certificate.seconds,
        random=discrete.random(),
        demand_sites=discrete.on_demand_sites(),
        grid_16=discrete.on_grid(16),
        grid_32=discrete.on_grid(32),
        grid_64=discrete.on_grid(64),
        greedy=engine.greedy,
        descent=engine.descent,
        relocation=engine.relocation,
        engine_seconds=engine.seconds,
    )
    record = instance.record() | {
        "optimum": certificate.upper if certificate.proved else None,
        "lower": certificate.lower,
        "upper": certificate.upper,
        "placement": certificate.positions.tolist(),
    }
    print(scores, flush=True)
    return scores, record


def measure_scale(instance: Instance) -> str:
    """A row of the scale table: the solver alone, with nothing else running."""
    certificate = ExactPlacement(instance, EXACT_SECONDS).solve()
    proved = "yes" if certificate.proved else f"no, {certificate.upper} at most"
    row = (
        f"| {instance.points.shape[0]} | {instance.emitters} "
        f"| {instance.walls.shape[0]} | {certificate.vertices} | {certificate.columns} "
        f"| {proved} | {certificate.seconds:.0f} |"
    )
    print(row, flush=True)
    return row
