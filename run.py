from logging import log
import os
import time
import argparse

import pyautogui
from dotenv import load_dotenv

from translate import translate


if __name__ == "__main__":

    load_dotenv()

    pyautogui.PAUSE = float(os.getenv('PYAUTO_PAUSE', 0.1))
    pyautogui.MINIMUM_DURATION = float(os.getenv('PYAUTO_MINIMUM_DURATION', 0.1))
    pyautogui.MINIMUM_SLEEP = float(os.getenv('PYAUTO_MINIMUM_SLEEP', 0))

    parser = argparse.ArgumentParser(
        prog="Pose2Input-MKKE",
        description="Translate the Video Input to Keystrokes"
    )
    parser.add_argument(
        '-d', '--debug_level', type=int, metavar='', default=0,
        help='[0, 1, 2, 3] set different levels of information for logs or live feed'
    )
    parser.add_argument(
        '-l', '--log_flag', action='store_true',
        help='stores the video_log in "logs" folder'
    )
    parser.add_argument(
        '-L', '--live_flag', action='store_true',
        help='displays the captured video'
    )
    args = parser.parse_args()

    time.sleep(int(os.getenv('DELAY_TIME', 0)))

    live_flag = args.live_flag
    log_flag = args.log_flag
    debug_level = args.debug_level

    if (debug_level > 0) and not (log_flag or live_flag):
        log_flag = True

    if not os.path.exists('logs'):
        os.mkdir('logs')

    translate(
        log_flag=log_flag,
        live_flag=live_flag,
        debug_level=debug_level,
        log_fps=int(os.getenv('LOG_FPS', 20)),
        camera_port=os.getenv('CAMERA_PORT', '0'),
        motion_threshold_invese_factor=int(
            os.getenv('MOTION_THRESHOLD_INVESE_FACTOR', 48)
        ),
    )
