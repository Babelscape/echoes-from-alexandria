from typing import List, Optional

from dataset_generation.src.metrics.filter import Filter
from dataset_generation.src.utils.utils import Version


class Parser:
    def __init__(self, language, filter: Optional[Filter]):
        self.language = language
        self.filter = filter

    def get_links(self, content: str, page_title: str, **kwargs) -> List[Version]:
        raise NotImplementedError
