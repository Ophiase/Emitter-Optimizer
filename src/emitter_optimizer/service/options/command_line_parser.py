import argparse
import math
import sys
from pathlib import Path
from typing import NoReturn, override

EXIT_BAD_INPUT = 2


class CommandLineParser(argparse.ArgumentParser):
    """A parser that refuses bad input in one line, and the types that detect it."""

    @override
    def error(self, message: str) -> NoReturn:
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(EXIT_BAD_INPUT)

    @staticmethod
    def positive_int(text: str) -> int:
        value = int(text)
        if value <= 0:
            message = f"must be a positive integer, not {text}"
            raise argparse.ArgumentTypeError(message)
        return value

    @staticmethod
    def positive_float(text: str) -> float:
        value = float(text)
        if not (math.isfinite(value) and value > 0):
            message = f"must be a positive number, not {text}"
            raise argparse.ArgumentTypeError(message)
        return value

    @staticmethod
    def existing_file(text: str) -> Path:
        path = Path(text)
        if not path.is_file():
            message = f"no such file: {text}"
            raise argparse.ArgumentTypeError(message)
        return path
