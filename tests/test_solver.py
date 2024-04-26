import unittest
from .utils import describe_test
from src.engine.solver import Solver
from src.gui.configuration import GuiConfig
from src.main import lower_tf_warning

class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lower_tf_warning()
        describe_test("Solver")

    def run(self, test):
        result = super().run(test)
        print("\n" + "=" * 30 + "\n")
        return result
    
    def test_cli(self):
        print("Make GuiConfig")
        config = GuiConfig()
        config.n_iteration = 20

        print("Make Solver")
        solver = config.to_solver()
        
        print("Solve")
        solver.solve()

        print("Done")

