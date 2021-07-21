import os
import time
import argparse

from dotenv import load_dotenv

from translate import translate


if __name__ == "__main__":

    load_dotenv()

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

    time.sleep(int(os.getenv('DELAY_TIME', "0")))

    live_flag = args.live_flag
    log_flag = args.log_flag
    debug_level = args.debug_level

    if (debug_level > 0) and not (log_flag or live_flag):
        log_flag = True

    if not os.path.exists('logs'):
        os.mkdir('logs')

    translate(
        camera_port=os.getenv('CAMERA_PORT', '0'),
        debug_level=debug_level,
        live_flag=live_flag,
        log_flag=log_flag,
    )
