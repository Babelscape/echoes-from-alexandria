import os.path
from typing import List
from dataset_generation.src.utils.constants import BOOK_CLASSIFICATIONS


class BookClassifier:
    def __init__(self):
        self.book_classifications = {}
        if os.path.exists(BOOK_CLASSIFICATIONS):
            with open(BOOK_CLASSIFICATIONS) as f:
                lines = [l.split("\t") for l in f.readlines()]
                self.book_classifications = {l[0]: l[2:-1] for l in lines}

    def get(self, synset: str) -> List[str]:
        return self.book_classifications.get(synset, None)
