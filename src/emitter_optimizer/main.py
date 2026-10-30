import matplotlib

matplotlib.use("Agg")

from emitter_optimizer.gui.application import Application


def main() -> None:
    Application()
