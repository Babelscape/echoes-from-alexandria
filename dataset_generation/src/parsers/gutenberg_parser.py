import os.path
import re
from typing import List, Optional

from dataset_generation.src.metrics.filter import Filter
from dataset_generation.src.parsers.base_parser import Parser
from dataset_generation.src.parsers.gutenberg.parsing_utils import parse_gut_index
from dataset_generation.src.utils.constants import GUTENBERG_DATASET_PATH
from dataset_generation.src.utils.utils import clean_title, Version


class GutenbergParser(Parser):
    def __init__(self, language: str, filter: Optional[Filter] = None):
        super().__init__(language, filter)
        (
            self.id2language,
            self.id2title,
            self.title2id,
            self.id2aut,
            self.id2subtitle,
        ) = parse_gut_index()

    def get_links(self, content: str, page_title: str, **kwargs) -> List[Version]:
        page_title = clean_title(page_title, remove_parenthesis_content=True)
        content_to_match = content.lower()
        found_links = (
            re.findall("www\\.gutenberg\\.org/etext/[0-9]+", content_to_match)
            + re.findall("www\\.gutenberg\\.org/ebooks/[0-9]+", content_to_match)
            + self.metatags_to_links(
                re.findall("{{gutenberg *\\|no *= *[0-9]+", content_to_match)
            )
        )
        matched_ids = self.index_matching(content, page_title)
        id2title = {
            self.guten_link2id(l): self.id2title.get(self.guten_link2id(l), None)
            for l in found_links
        }
        matchedids2title = {id: self.id2title.get(id, None) for id in matched_ids}
        id2title = {**matchedids2title, **id2title}
        versions = [
            Version(
                title=t,
                filepaths=[
                    os.path.join(GUTENBERG_DATASET_PATH.split("/")[-1], f"{id}.txt")
                ],
                language=self.id2language.get(id, None),
            )
            for id, t in id2title.items()
            if id in self.id2title and t is not None
        ]
        # discards versions due to missing file
        versions = [
            v
            for v in versions
            if all(
                [
                    os.path.exists(
                        os.path.join(GUTENBERG_DATASET_PATH, p.split("/")[-1])
                    )
                    for p in v.filepaths
                ]
            )
        ]
        if self.filter is not None:
            filtered_versions = self.filter.filter_versions(page_title, versions)
            if not filtered_versions:
                for v in versions:
                    id = v.filepaths[0].split("/")[-1].replace(".txt", "").strip()
                    if id in self.id2subtitle:
                        subtitle = self.id2subtitle[id].lower()
                        v.title = (v.title + ": " + subtitle).strip()
                filtered_versions = self.filter.filter_versions(page_title, versions)
            versions = filtered_versions
        return versions

    def index_matching(self, content, page_title):
        matched_ids = []
        if page_title in self.title2id:
            for id in self.title2id[page_title]:
                matched_ids.append(id)
        if matched_ids:
            filtered_matched_ids = []
            for i, id in enumerate(matched_ids):
                aut = self.id2aut.get(id, "")
                # checks whether the author name is in the introduction of the wikipedia page
                intro = content[: content.index("==")] if "==" in content else content
                # removes see also... from header, may contain other authors
                intro = re.sub('{{.*}}', '', intro)
                if aut != "" and aut.lower() in intro.lower().split(" "):
                    filtered_matched_ids.append(id)
            matched_ids = filtered_matched_ids
        return matched_ids

    def metatags_to_links(self, metatags):
        links = []
        for m in metatags:
            id = re.findall("[0-9]+", m)[0]
            links.append(f"www.gutenberg.org/ebooks/{id}")
        return links

    @staticmethod
    def guten_link2id(link):
        return re.findall("\d+", link)[-1]
