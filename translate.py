import time
from datetime import datetime

import cv2
import pyautogui
from mediapipe import solutions as mp_solns

from constants import landmarks_connections
from utils import TranslatePose, moves_to_input


pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_DURATION = 0

def translate(
    camera_port=0, debug_level=0, log_flag=False, live_flag=False
):
    camera_port = int(camera_port) if camera_port.isdigit() else camera_port

    translate_pose = TranslatePose()

    camera = cv2.VideoCapture(camera_port, cv2.CAP_DSHOW)
    success, prv_img = camera.read()

    if not success:
        raise cv2.error("Invalid Video Source")

    height, width, channel = prv_img.shape
    print(prv_img.shape)

    motion_theshold = height * width * channel * 255 // 32

    pose = mp_solns.pose.Pose()

    if log_flag:
        video_log = cv2.VideoWriter(
            f"logs/log_{datetime.now().strftime('%Y-%M-%d_%H-%m-%S')}.avi",
            cv2.VideoWriter_fourcc(*"XVID"), 24, (width, height)
        )

    if log_flag:
        video_log.write(prv_img)


    if debug_level > 0:
        cur_time = 0
        cv_font_vars = (cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 2)


    while cv2.waitKey(1) & 0xFF != 27:
        if debug_level > 0:
            prv_time = cur_time

        motion_detected = False

        _, img = camera.read()

        diff_img = cv2.absdiff(img, prv_img)

        if diff_img.flatten().sum() > motion_theshold:
            motion_detected = True

        prv_img = img.copy()

        pose_landmarks = pose.process(
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ).pose_landmarks

        movelist = []
        if motion_detected and pose_landmarks:
            movelist = translate_pose.process(pose_landmarks.landmark)
            inputs = moves_to_input(movelist)
            pyautogui.hotkey(*inputs, _pause=0)

        if debug_level > 0:
            cur_time = time.time()

        if debug_level > 1 and pose_landmarks:
            mp_solns.drawing_utils.draw_landmarks(
                img, pose_landmarks, landmarks_connections
            )

        if debug_level > 2 and not motion_detected:
            img = diff_img

        if debug_level > 0:
            fps = 1/(cur_time - prv_time)

            cv2.putText(
                img, f"{fps:.2f}", (width - 100, 50), *cv_font_vars
            )

            cv2.putText(
                img, f"{list(movelist)}", (50, height - 50), *cv_font_vars
            )


        if live_flag:
            cv2.imshow("Pose2Input-MKKE", img)

        if log_flag:
            video_log.write(img)

    camera.release()

    if log_flag:
        video_log.release()

    # Closes all the frames
    cv2.destroyAllWindows()
