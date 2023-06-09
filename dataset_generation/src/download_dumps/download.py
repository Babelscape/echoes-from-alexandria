from typing import List
from dataset_generation.src.download_dumps.download_gutenberg import download_gutenberg
from dataset_generation.src.download_dumps.download_wiki import download_wiki, organize_texts
from dataset_generation.src.utils.constants import WIKI_DUMP_PATH, WIKI_DUMP_DATE, WIKISOURCE_DUMP_PATH, \
    GUTENBERG_DATASET_PATH


def download(languages: List[str], debug_title: str = None):
    # downloads and parses wikipedia
    download_wiki("wiki", WIKI_DUMP_PATH, WIKI_DUMP_DATE, languages)
    # downloads and parses wikisource
    download_wiki("wikisource", WIKISOURCE_DUMP_PATH, WIKI_DUMP_DATE, languages)
    # cleans and organizes wikisource book texts
    organize_texts(
        WIKISOURCE_DUMP_PATH, WIKI_DUMP_DATE, languages, debug_title=debug_title
    )
    # download and parse gutenberg
    download_gutenberg(GUTENBERG_DATASET_PATH)
