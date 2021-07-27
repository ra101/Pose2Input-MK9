import pyautogui
import numpy as np

from constants import InputConfig
from mediapipe.python.solutions.pose import (
    PoseLandmark as LandmarkIndexEnum
)

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
        r_ankle = landmark_list[LandmarkIndexEnum.RIGHT_ANKLE]
        l_ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE]
        r_knee = landmark_list[LandmarkIndexEnum.RIGHT_KNEE]
        l_knee=landmark_list[LandmarkIndexEnum.LEFT_KNEE]

        if np.average([
            l_ankle.visibility, r_ankle.visibility,
            l_knee.visibility, r_knee.visibility
        ]) < 0.95:
            return False

        if  (l_ankle.y + r_ankle.y) < (r_knee.y + l_knee.y):
            return True
        return False

    def move_down(self, landmark_list):
        r_hip = landmark_list[LandmarkIndexEnum.RIGHT_HIP]
        l_hip=landmark_list[LandmarkIndexEnum.LEFT_HIP]
        r_knee = landmark_list[LandmarkIndexEnum.RIGHT_KNEE]
        l_knee=landmark_list[LandmarkIndexEnum.LEFT_KNEE]
        nose=landmark_list[LandmarkIndexEnum.NOSE]

        if np.average([
            r_hip.visibility, l_hip.visibility, r_knee.visibility,
            l_knee.visibility, nose.visibility
        ]) < 0.95:
            return False

        hip = np.complex(0, (r_hip.y + l_hip.y)/2)
        knee = np.complex(0, (r_knee.y + l_knee.y)/2)
        nose = np.complex(0, nose.y)

        knee_to_nose = knee - nose
        hip_to_nose = hip - nose

        if abs(hip_to_nose)/abs(knee_to_nose) > 0.7:
            return True
        return False

    def move_left(self, landmark_list):
        return self._move_x_direction(
            r_ankle=landmark_list[LandmarkIndexEnum.RIGHT_ANKLE],
            l_ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE],
            hip=landmark_list[LandmarkIndexEnum.RIGHT_HIP],
            right=False
        )

    def move_right(self, landmark_list):
        return self._move_x_direction(
            r_ankle=landmark_list[LandmarkIndexEnum.RIGHT_ANKLE],
            l_ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE],
            hip=landmark_list[LandmarkIndexEnum.LEFT_HIP],
            right=True
        )

    def _move_x_direction(
        self, r_ankle, l_ankle, hip, right=True):
        if np.average([
            r_ankle.visibility, l_ankle.visibility, hip.visibility
        ]) < 0.95:
            return False

        median_of_body_x = (r_ankle.x + l_ankle.x)/2

        l_ankle_to_hip = np.complex(hip.x - l_ankle.x, hip.y - l_ankle.y)
        r_ankle_to_hip = np.complex(hip.x - r_ankle.x, hip.y - r_ankle.y)

        if np.average(np.abs([
            np.sin(np.angle(l_ankle_to_hip)) , np.sin(np.angle(r_ankle_to_hip))
        ])) > 0.95:
            if right and median_of_body_x > hip.x:
                return True
            if not right and median_of_body_x < hip.x:
                return True
        return False

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
            elbow.visibility, wrist.visibility, shoulder.visibility
        ]) < 0.95:
            return False

        elbow_to_wrist = np.complex(wrist.x - elbow.x, wrist.y - elbow.y)
        elbow_to_shoulder = np.complex(shoulder.x - elbow.x , shoulder.y - elbow.y)
        wrist_to_shoulder = np.complex(shoulder.x - wrist.x , shoulder.y - wrist.y)

        if abs(np.sin(
            np.angle(elbow_to_wrist) + np.angle(elbow_to_shoulder)
        )) < 0.18:
            if abs(np.sin(np.angle(wrist_to_shoulder))) < 0.18:
                return True
        return False

    def move_front_kick(self, landmark_list):
        return self._move_kick(
            hip=landmark_list[LandmarkIndexEnum.LEFT_HIP],
            ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE],
        )

    def move_back_kick(self, landmark_list):
        return self._move_kick(
            hip=landmark_list[LandmarkIndexEnum.RIGHT_HIP],
            ankle=landmark_list[LandmarkIndexEnum.RIGHT_ANKLE],
        )

    def _move_kick(self, hip, ankle):
        if np.average([hip.visibility, ankle.visibility]) < 0.95:
            return False

        ankle_to_hip = np.complex(hip.x - ankle.x, hip.y - ankle.y)

        if abs(np.sin(np.angle(ankle_to_hip))) < 0.7:
            return True
        return False

    def move_throw(self, landmark_list):
        nose = landmark_list[LandmarkIndexEnum.NOSE]
        if nose.visibility < 0.95:
            return False

        r_wrist = landmark_list[LandmarkIndexEnum.RIGHT_WRIST]
        r_elbow = landmark_list[LandmarkIndexEnum.RIGHT_ELBOW]
        l_wrist = landmark_list[LandmarkIndexEnum.LEFT_WRIST]
        l_elbow = landmark_list[LandmarkIndexEnum.LEFT_ELBOW]

        if np.average([r_wrist.visibility, r_elbow.visibility]) > 0.95:
            if r_wrist.y < r_elbow.y < nose.y:
                return True

        if np.average([l_wrist.visibility, l_elbow.visibility]) > 0.95:
            if l_wrist.y < l_elbow.y < nose.y :
                return True

    def move_tag(self, landmark_list):
        r_wrist = landmark_list[LandmarkIndexEnum.RIGHT_WRIST]
        r_elbow = landmark_list[LandmarkIndexEnum.RIGHT_ELBOW]
        l_wrist = landmark_list[LandmarkIndexEnum.LEFT_WRIST]
        l_elbow = landmark_list[LandmarkIndexEnum.LEFT_ELBOW]

        if np.average([
            r_wrist.visibility, l_wrist.visibility,
            r_elbow.visibility, l_elbow.visibility
        ]) < 0.95:
            return False

        wrist_to_wrist = np.complex(r_wrist.x - l_wrist.x , r_wrist.y - l_wrist.y)

        if abs(np.sin(np.angle(wrist_to_wrist))) < 0.18:
            if abs(r_wrist.x - l_wrist.x) / abs(r_elbow.x - l_elbow.x) < 0.3:
                return True

    def move_block(self, landmark_list):
        nose = landmark_list[LandmarkIndexEnum.NOSE]
        if nose.visibility < 0.95:
            return False

        r_wrist = landmark_list[LandmarkIndexEnum.RIGHT_WRIST]
        r_elbow = landmark_list[LandmarkIndexEnum.RIGHT_ELBOW]
        l_wrist = landmark_list[LandmarkIndexEnum.LEFT_WRIST]
        l_elbow = landmark_list[LandmarkIndexEnum.LEFT_ELBOW]

        if np.average([r_wrist.visibility, r_elbow.visibility]) > 0.95:
            if r_wrist.y < nose.y < r_elbow.y:
                return True

        if np.average([l_wrist.visibility, l_elbow.visibility]) > 0.95:
            if l_wrist.y < nose.y < l_elbow.y:
                return True
