import numpy as np
import utils.utils as util

class Student:
    def __init__(self, id: int, signature_img: np.ndarray, eval_img: np.ndarray, eval: list, score: int):
        self.id = id
        self.signature_img = signature_img
        self.eval_img = eval_img
        self.eval = eval
        self.score = score

    def serialize(self) -> dict:
        student = self.__dict__
        student['signature_img'] = util.serialize_img(self.signature_img)
        student['eval_img'] = util.serialize_img(self.eval_img)
        return student

    