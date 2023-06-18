# ./translate.py

import time
from datetime import datetime

import cv2
import mediapipe.python.solutions as mp

from utils import TranslatePose, moves_to_keystroke, input_keys, UNUSED_LANDMARKS


def translate(
    log_flag=True, live_flag=False, debug_level=0, log_fps=20,
    camera_port="0", motion_threshold_factor=48
):
    """
    function translate input settings for camera, captures frames accordingly,
    process the captured frame and types the associated keystroke.

    log_flag <bool>: if True, it stores the video_log in "logs" folder
    live_flag <bool>: if True, it displays the captured video
    log_fps <int>: FPS Setting for video_log
    camera_port <str>: select the port, can be url address or port number in str
    motion_threshold_factor <int>: More the value is, More the Motion is Captured
    debug_level <int> -> <0 | 1 | 2 | 3>:
        - 0: Raw Video Footage
        - 1: 0 + FPS and Output Moves
        - 2: 1 + Virtual Exoskeleton of Body Parts Found
        - 3: 2 + Black Screen if no motion found
    """

    camera_port = int(camera_port) if camera_port.isdigit() else camera_port

    translate_pose = TranslatePose()

    camera = cv2.VideoCapture(camera_port, cv2.CAP_DSHOW)
    success, prv_img = camera.read()

    if not success:
        raise cv2.error("Invalid Video Source")

    height, width, channel = prv_img.shape

    # More the value is, More the Motion is Captured
    motion_theshold = height * width * channel * 255 // motion_threshold_factor

    # MediaPipe Pose
    pose = mp.pose.Pose()

    if log_flag:
        # Intialise VideoWriter for logs in `./logs/` folder
        video_log = cv2.VideoWriter(
            f"logs/log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.avi",
            cv2.VideoWriter_fourcc(*"XVID"), log_fps, (width, height)
        )
        video_log.write(prv_img)

    if debug_level > 0:
        # FPS and Output Moves setting
        cur_time = 0
        cv_font_vars_outline = (cv2.FONT_HERSHEY_PLAIN, 1.7, (192, 44, 44), 3)
        cv_font_vars = (cv2.FONT_HERSHEY_PLAIN, 1.7, (245,66,66), 2)
        fps_coord = (width - 100, 50)
        movelist_coord = (50, height - 50)


    while cv2.waitKey(1) & 0xFF != 27:
        if debug_level > 0:
            # Update prv_time for FPS
            prv_time = cur_time

        # Set to false for Each Frame
        motion_detected = False

        # Grabs image form Capturing Device
        _, img = camera.read()

        # Frame differencing for motion detection
        diff_img = cv2.absdiff(img, prv_img)

        # Compare the sum of pixel after differencing with initalized theshold
        if diff_img.flatten().sum() > motion_theshold:
            motion_detected = True

        # same img for next comparsion
        prv_img = img.copy()

        if motion_detected:
            # MediaPipe finds marker for all body parts
            pose_landmarks = pose.process(
                cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ).pose_landmarks

        movelist = []
        if motion_detected and pose_landmarks:

            # removing lankmarks that will not be used futher:
            for mark in UNUSED_LANDMARKS:
                pose_landmarks.landmark[mark].visibility = 0

            # Using Coordinates, Deduces the Move(s)
            movelist = translate_pose.process(pose_landmarks.landmark)

            # Using Move(s), returns the associated key
            inputs = moves_to_keystroke(movelist)

            # Uses pyAutoGUI to input the key(s)
            input_keys(inputs)

        if debug_level > 0:
            cur_time = time.time()

            if debug_level > 1 and motion_detected and pose_landmarks:
                mp.drawing_utils.draw_landmarks(
                    img, pose_landmarks, mp.pose.POSE_CONNECTIONS,
                    mp.drawing_utils.DrawingSpec(color=(66,66,245)),
                    mp.drawing_utils.DrawingSpec(color=(66,245,66))
                )

            if debug_level > 2 and not motion_detected:
                img = diff_img

            # FPS: 1 frame  / time taken to process a whole frame
            fps = 1/(cur_time - prv_time)  if (cur_time - prv_time) !=0 else 0

            # FPS and Output Moves Output
            cv2.putText(img, f"{fps:.2f}", fps_coord, *cv_font_vars_outline)
            cv2.putText(img, f"{fps:.2f}", fps_coord, *cv_font_vars)

            cv2.putText(img, f"{list(movelist)}", movelist_coord, *cv_font_vars_outline)
            cv2.putText(img, f"{list(movelist)}", movelist_coord, *cv_font_vars)

        # live_flag is set to True, Display the captured image
        if live_flag:
            cv2.imshow("Pose2Input-MK9", img)

        # log_flag is set to True, Store the captured image
        if log_flag:
            video_log.write(img)

    # Closes Capturing Device
    camera.release()

    if log_flag:
        # Closes Video Writer
        video_log.release()

    # Closes all the frames
    cv2.destroyAllWindows()
