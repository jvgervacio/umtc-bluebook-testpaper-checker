import numpy as np
import utils.utils as util

class Student:
    def __init__(self, signature_imgpath: str, eval_imgpath: str, eval: list, score: int):
        self.signature_imgpath = signature_imgpath
        self.eval_imgpath = eval_imgpath
        self.eval = eval
        self.score = score

    def serialize(self) -> dict:
        student = self.__dict__
        return student

    