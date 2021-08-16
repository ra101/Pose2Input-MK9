# ./utils.py

import pyautogui
import numpy as np

from constants import InputConfig
from mediapipe.python.solutions.pose import (
    PoseLandmark as LandmarkIndexEnum
)

def input_keys(inputs):
    '''
    press the given list of keys in ordered fashion
    pyautogui: uses keyDown and keyUp
    Not using pyautogui.hotkey as it not recognize by many applications

    input <list<str:PyAutoGUI recognizes key string>>
    '''
    for key in inputs:
        pyautogui.keyDown(key)
    for key in reversed(inputs):
        pyautogui.keyUp(key)

def moves_to_keystroke(movelist):
    '''
    Uses InputConfig to return list of keys from given moves in movelist

    movelist <list<str:move>>
    '''
    return [
        getattr(InputConfig, move, 'DEFAULT').value for move in movelist
    ]

class TranslatePose:
    '''
    Using Coordinates of body parts, this class can deduces the Move(s)/Pose(s)
    '''

    def __init__(self):
        '''
        Initalise a list of all the functions that starts with "move_"
        all these fuctions return bool for associated moves.
        functions and moves are associated in the format move_<move_name>
        help(TranslatePose.move_sample) to get how to make a move function
        '''
        self.all_transaltion_funcs = [
            getattr(self, i) for i in dir(self) if i.startswith('move_')
        ]
        self.all_transaltion_funcs.remove(self.move_sample)
        self.visibility_threshold = 0.9

    def process(self, landmark_list):
        '''
        pass landmark_list to all the functions in
        self.all_transaltion_funcs, and create a set of possible moves
        '''
        return set([
            func.__name__[5:].upper()
                for func in self.all_transaltion_funcs if func(landmark_list)
        ])

    def move_sample(self, landmark_list):
        '''
        sample function, bases for all `move_` functions

        # Input
        landmark_list <NamedTuple<NamedTuple>>: is a list of positional markers
            of each body part, Index for each body part can be found at
            mediapipe.python.solutions.pose.PoseLandmark
            which can be now used as nose = landmark_list[LandmarkIndexEnum.NOSE]
            this nose is also NamedTuple, which has `x`, `y`, and `visiblity` fields

        # Output
        <bool>: True or False, whether the `sample` move is portrayed by the
            given landmarks

        # Processing
            ## Initalizing
            initalize all the body parts required for the mathematical
                operations required to deduce the pose
            # Visibility Check
            check if the average of visiblity of all initialized body
                are greater than self.visibility_threshold
                eg: numpy.average([part_1.visibility, part_2.visibility]) < 0.9
            # Mathematics
            perform mathematical operations on x,y cordinates to determine pose
                always usew ratio or angles, as they are independent of camera distance
            # return True or False accordingly
        '''

    def move_up(self, landmark_list):
        '''
        ankles should be above knees
        '''
        r_ankle = landmark_list[LandmarkIndexEnum.RIGHT_ANKLE]
        l_ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE]
        r_knee = landmark_list[LandmarkIndexEnum.RIGHT_KNEE]
        l_knee=landmark_list[LandmarkIndexEnum.LEFT_KNEE]

        if np.average([
            l_ankle.visibility, r_ankle.visibility,
            l_knee.visibility, r_knee.visibility
        ]) < self.visibility_threshold:
            return False

        if  (l_ankle.y + r_ankle.y) < (r_knee.y + l_knee.y):
            return True
        return False

    def move_down(self, landmark_list):
        '''
        dist(hip->nose) : dist(hip->knee) > 7 : 10
        '''
        r_hip = landmark_list[LandmarkIndexEnum.RIGHT_HIP]
        l_hip=landmark_list[LandmarkIndexEnum.LEFT_HIP]
        r_knee = landmark_list[LandmarkIndexEnum.RIGHT_KNEE]
        l_knee=landmark_list[LandmarkIndexEnum.LEFT_KNEE]
        nose=landmark_list[LandmarkIndexEnum.NOSE]

        if np.average([
            r_hip.visibility, l_hip.visibility, r_knee.visibility,
            l_knee.visibility, nose.visibility
        ]) < self.visibility_threshold:
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
        '''
        (perpendicular of r_ankle->l_ankle) should be right of right hip
        slope(right_hip->ankle) for both ankles should be b/w -65° and -115°
        '''
        return self._move_x_direction(
            r_ankle=landmark_list[LandmarkIndexEnum.RIGHT_ANKLE],
            l_ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE],
            hip=landmark_list[LandmarkIndexEnum.RIGHT_HIP],
            right=False
        )

    def move_right(self, landmark_list):
        '''
        (perpendicular of r_ankle->l_ankle) should be left of left hip
        slope(left_hip->ankle) for both ankles should be b/w -65° and -115°
        '''
        return self._move_x_direction(
            r_ankle=landmark_list[LandmarkIndexEnum.RIGHT_ANKLE],
            l_ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE],
            hip=landmark_list[LandmarkIndexEnum.LEFT_HIP],
            right=True
        )

    def _move_x_direction(
        self, r_ankle, l_ankle, hip, right=True
    ):
        '''
        common implementation for move_left and move_right
        '''
        if np.average([
            r_ankle.visibility, l_ankle.visibility, hip.visibility
        ]) < self.visibility_threshold:
            return False

        median_of_body_x = (r_ankle.x + l_ankle.x)/2

        l_ankle_to_hip = np.complex(hip.x - l_ankle.x, hip.y - l_ankle.y)
        r_ankle_to_hip = np.complex(hip.x - r_ankle.x, hip.y - r_ankle.y)

        if np.average(np.abs([
            np.sin(np.angle(l_ankle_to_hip)) , np.sin(np.angle(r_ankle_to_hip))
        ])) > self.visibility_threshold:
            if right and median_of_body_x > hip.x:
                return True
            if not right and median_of_body_x < hip.x:
                return True
        return False

    def move_front_punch(self, landmark_list):
        '''
        slope(left_shoulder->left_wirst) should be b/w -10.5° and 10.5°
        angle(left_shoulder<-left_elbow->left_wirst) should be b/w 169.5° and 190.5°
        TLDR: arm should parallel to ground
        '''
        return self._move_punch(
            wrist=landmark_list[LandmarkIndexEnum.LEFT_WRIST],
            elbow=landmark_list[LandmarkIndexEnum.LEFT_ELBOW],
            shoulder=landmark_list[LandmarkIndexEnum.LEFT_SHOULDER]
        )

    def move_back_punch(self, landmark_list):
        '''
        slope(right_shoulder->right_wirst) should be b/w -10.5° and 10.5°
        angle(right_shoulder<-right_elbow->right_wirst) should be b/w 169.5° and 190.5°
        TLDR: arm should parallel to ground
        '''
        return self._move_punch(
            wrist=landmark_list[LandmarkIndexEnum.RIGHT_WRIST],
            elbow=landmark_list[LandmarkIndexEnum.RIGHT_ELBOW],
            shoulder=landmark_list[LandmarkIndexEnum.RIGHT_SHOULDER]
        )

    def _move_punch(self, wrist, elbow, shoulder):
        '''
        common implementation for move_front_punch and move_back_punch
        '''
        if np.average([
            elbow.visibility, wrist.visibility, shoulder.visibility
        ]) < self.visibility_threshold:
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
        '''
        slope(left_ankle->left_hip) should be b/w 45° and 135°
        '''
        return self._move_kick(
            hip=landmark_list[LandmarkIndexEnum.LEFT_HIP],
            ankle=landmark_list[LandmarkIndexEnum.LEFT_ANKLE],
        )

    def move_back_kick(self, landmark_list):
        '''
        slope(right_ankle->right_hip) should be b/w 45° and 135°
        '''
        return self._move_kick(
            hip=landmark_list[LandmarkIndexEnum.RIGHT_HIP],
            ankle=landmark_list[LandmarkIndexEnum.RIGHT_ANKLE],
        )

    def _move_kick(self, hip, ankle):
        '''
        common implementation for move_front_kick and move_back_kick
        '''
        if np.average([hip.visibility, ankle.visibility]) < self.visibility_threshold:
            return False

        ankle_to_hip = np.complex(hip.x - ankle.x, hip.y - ankle.y)

        if abs(np.sin(np.angle(ankle_to_hip))) < 0.7:
            return True
        return False

    def move_throw(self, landmark_list):
        '''
        wrist should be above elbow of same arm, they both should be above nose
        '''
        nose = landmark_list[LandmarkIndexEnum.NOSE]
        if nose.visibility < self.visibility_threshold:
            return False

        r_wrist = landmark_list[LandmarkIndexEnum.RIGHT_WRIST]
        r_elbow = landmark_list[LandmarkIndexEnum.RIGHT_ELBOW]
        l_wrist = landmark_list[LandmarkIndexEnum.LEFT_WRIST]
        l_elbow = landmark_list[LandmarkIndexEnum.LEFT_ELBOW]

        if np.average([r_wrist.visibility, r_elbow.visibility]) > self.visibility_threshold:
            if r_wrist.y < r_elbow.y < nose.y:
                return True

        if np.average([l_wrist.visibility, l_elbow.visibility]) > self.visibility_threshold:
            if l_wrist.y < l_elbow.y < nose.y :
                return True
        return False

    def move_tag(self, landmark_list):
        '''
        angle(left_elbow<-wirsts->right_elbow) should be b/w 169.5° and 190.5°
        TLDR: forearms should parallel to ground

        dist(wrists) : dist(elbows) < 3 : 10
        '''
        r_wrist = landmark_list[LandmarkIndexEnum.RIGHT_WRIST]
        r_elbow = landmark_list[LandmarkIndexEnum.RIGHT_ELBOW]
        l_wrist = landmark_list[LandmarkIndexEnum.LEFT_WRIST]
        l_elbow = landmark_list[LandmarkIndexEnum.LEFT_ELBOW]

        if np.average([
            r_wrist.visibility, l_wrist.visibility,
            r_elbow.visibility, l_elbow.visibility
        ]) < self.visibility_threshold:
            return False

        wirst_x = (l_wrist.x + r_wrist.x)/2
        wirst_y = (l_wrist.y + r_wrist.y)/2

        l_elbow_to_wrist = np.complex(wirst_x - l_elbow.x, wirst_y - l_elbow.y)
        r_elbow_to_wrist = np.complex(wirst_x - r_elbow.x, wirst_y - r_elbow.y)

        if abs(np.sin(
            np.angle(l_elbow_to_wrist) + np.angle(r_elbow_to_wrist)
        )) < 0.18:
            if abs(r_wrist.x - l_wrist.x) / abs(r_elbow.x - l_elbow.x) < 0.3:
                return True
        return False

    def move_block(self, landmark_list):
        '''
        wrist should be above nose, they both should be above elbow of same arm
        '''
        nose = landmark_list[LandmarkIndexEnum.NOSE]
        if nose.visibility < self.visibility_threshold:
            return False

        r_wrist = landmark_list[LandmarkIndexEnum.RIGHT_WRIST]
        r_elbow = landmark_list[LandmarkIndexEnum.RIGHT_ELBOW]
        l_wrist = landmark_list[LandmarkIndexEnum.LEFT_WRIST]
        l_elbow = landmark_list[LandmarkIndexEnum.LEFT_ELBOW]

        if np.average([r_wrist.visibility, r_elbow.visibility]) > self.visibility_threshold:
            if r_wrist.y < nose.y < r_elbow.y:
                return True

        if np.average([l_wrist.visibility, l_elbow.visibility]) > self.visibility_threshold:
            if l_wrist.y < nose.y < l_elbow.y:
                return True
        return False

    # def move_flip_stance(self, landmark_list):
    #     '''
    #     Not Gonna Implement
    #     '''
    #     return False

    # def move_pause(self, landmark_list):
    #     '''
    #     Not Gonna Implement
    #     '''
    #     return False

    # def move_back(self, landmark_list):
    #     '''
    #     Not Gonna Implement
    #     '''
    #     return False
