import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

import json
import matplotlib

import dearpygui.dearpygui as dpg
import engine.solver as solver
from gui.application import Application

def lower_tf_warning():
    tf.get_logger().setLevel("ERROR")

def main() :
    lower_tf_warning()
    matplotlib.use('Agg')
    app = Application()

if __name__ == '__main__':
    main()