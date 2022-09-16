import numpy as np
import utils.utils as util

class Student:
    def __init__(self, id, eval: list, score: int):
        self.id = id
        self.eval = eval
        self.score = score

    def serialize(self) -> dict:
        student = self.__dict__
        return student

    