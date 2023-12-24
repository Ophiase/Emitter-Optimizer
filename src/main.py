import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

import json
import matplotlib

import dearpygui.dearpygui as dpg
import engine.solver as solver
from gui.application import Application

def main() :
    tf.get_logger().setLevel("ERROR")
    matplotlib.use('Agg')
    app = Application()

if __name__ == '__main__':
    main()