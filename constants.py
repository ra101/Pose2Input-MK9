import os
import enum

from dotenv import load_dotenv


load_dotenv()


@enum.unique
class InputConfig(enum.Enum):
    UP = os.getenv('UP', 'up').lower()
    DOWN = os.getenv('DOWN', 'down').lower()
    LEFT = os.getenv('LEFT', 'left').lower()
    RIGHT = os.getenv('RIGHT', 'right').lower()
    FRONT_PUNCH = os.getenv('FRONT_PUNCH', 'a').lower()
    BACK_PUNCH = os.getenv('BACK_PUNCH', 's').lower()
    FRONT_KICK = os.getenv('FRONT_KICK', 'z').lower()
    BACK_KICK = os.getenv('BACK_KICK', 'x').lower()
    THROW = os.getenv('THROW', 'd').lower()
    TAG = os.getenv('TAG', 'c').lower()
    BLOCK = os.getenv('BLOCK', 'space').lower()
    FLIP_STANCE = os.getenv('FLIP_STANCE', 'ctrlright').lower()
    PAUSE = os.getenv('PAUSE', 'tab').lower()
    BACK = os.getenv('BACK', 'backspace').lower()
