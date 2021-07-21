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


    def move_front_punch(self, landmark_list):
        return self._move_punch(
            wrist=landmark_list[LandmarkIndexEnum.LEFT_WRIST],
            elbow=landmark_list[LandmarkIndexEnum.LEFT_ELBOW],
            shoulder=landmark_list[LandmarkIndexEnum.LEFT_SHOULDER]
        )

    def move_back_punch(self, landmark_list):
        return self._move_punch(
            wrist=landmark_list[LandmarkIndexEnum.RIGHT_WRIST],
            elbow=landmark_list[LandmarkIndexEnum.RIGHT_ELBOW],
            shoulder=landmark_list[LandmarkIndexEnum.RIGHT_SHOULDER]
        )

    def _move_punch(self, wrist, elbow, shoulder):
        if np.average([
            elbow.visibility + wrist.visibility + shoulder.visibility
        ]) < 0.9:
            return False

        elbow_to_wrist = np.complex(wrist.x - elbow.x, wrist.y - elbow.y)
        elbow_to_shoulder = np.complex(shoulder.x - elbow.x , shoulder.y - elbow.y)

        wrist_to_shoulder = np.complex(shoulder.x - wrist.x , shoulder.y - wrist.y)

        if abs(np.angle(elbow_to_wrist) + np.angle(elbow_to_shoulder)) > 2.8:
            if abs(np.angle(wrist_to_shoulder) > 2.8):
                return True
        return False
