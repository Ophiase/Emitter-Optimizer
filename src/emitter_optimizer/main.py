import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import matplotlib

matplotlib.use("Agg")

import tensorflow as tf

from emitter_optimizer.gui.application import Application


def main() -> None:
    tf.get_logger().setLevel("ERROR")
    Application()
