import dataclasses
from dataclasses import dataclass
import json
import re
import unicodedata
from typing import List
import mwparserfromhell


@dataclass
class Source:
    title: str
    url: str


# e.g. Odissey (Pope)
@dataclass
class Version:
    title: str
    filepaths: List[str]
    language: str


def strip_accents(text):
    try:
        text = unicode(text, "utf-8")
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def clean_title(title, remove_parenthesis_content=False):
    title = strip_accents(title)
    if remove_parenthesis_content:
        title = re.sub("\(.*\)", "", title)
    only_alnum = re.sub("[^a-zA-Z0-9()]", " ", title)
    no_extra_spaces = re.sub("\s{2,}", " ", only_alnum)
    return no_extra_spaces.lower().strip()


def flatten(list):
    return [item for sublist in list for item in sublist]


# let json encode python dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def parse_introduction(content) -> str:
    raw_intro = content[: content.index("==")]
    return mwparserfromhell.parse(raw_intro).strip_code()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
