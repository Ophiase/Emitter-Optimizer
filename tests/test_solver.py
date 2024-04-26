import unittest
from .utils import describe_test
from src.engine.solver import Solver
from src.gui import configuration

class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        describe_test("Solver")

    def test_something(self):
        print("Test work !!")