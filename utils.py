import pyautogui
import numpy as np

from constants import InputConfig, LandmarkIndexEnum

def input_keys(inputs):
    for key in inputs:
        pyautogui.keyDown(key)
    for key in reversed(inputs):
        pyautogui.keyUp(key)

def moves_to_keystroke(movelist):
    return [
        getattr(InputConfig, move).value for move in movelist
    ]

class TranslatePose:

    def __init__(self):
        self.all_transaltion_funcs = [
            getattr(self, i) for i in dir(self) if i.startswith('move_')
        ]

    def process(self, landmark_list):
        return set([
            func.__name__[5:].upper()
                for func in self.all_transaltion_funcs if func(landmark_list)
        ])

    def move_up(self, landmark_list):
        return True
