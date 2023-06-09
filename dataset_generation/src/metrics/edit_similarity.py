from datasets import load_metric
from nltk.corpus import stopwords


class Metric:
    def __init__(self, language: str):
        self.language = language

    def compute(self, s1: str, s2: str):
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError


lan2nltk = {
    "en": "english",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "es": "spanish",
}


class EditSimilarity(Metric):
    def __init__(self, language: str, remove_stopwords: bool = True):
        super().__init__(language)
        language = lan2nltk[language]
        self.remove_stopwords = remove_stopwords
        if remove_stopwords:
            self.stopwords = set(stopwords.words(language))

    def compute(self, s1, s2):
        if self.remove_stopwords:
            s1 = self.delete_stopwords(s1)
            s2 = self.delete_stopwords(s2)

        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(
                        1 + min((distances[i1], distances[i1 + 1], distances_[-1]))
                    )
            distances = distances_
        levenshtein = distances[-1]
        return 1 - float(levenshtein) / max(len(s1), len(s2))

    def delete_stopwords(self, s1):
        cleaned_string = " ".join(
            [tok for tok in s1.split(" ") if tok.lower() not in self.stopwords]
        )
        if cleaned_string.strip() != "":
            return cleaned_string
        else:
            return s1

    def get_name(self) -> str:
        return "edit"


class BertScore(Metric):
    def __init__(self, language: str):
        super().__init__(language)
        self.metric = load_metric("bertscore")

    def compute(self, s1, s2):
        if s1.lower() == s2.lower():
            return 1.0
        return self.metric.compute(
            predictions=[s1], references=[s2], lang=self.language
        )["f1"][0]

    def get_name(self) -> str:
        return "bertscore"
