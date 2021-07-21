from constants import InputConfig, LandmarkIndexEnum


def moves_to_input(movelist):
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
