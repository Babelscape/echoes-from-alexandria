import json
import os
from typing import List, Optional

from pytz import unicode
from tqdm import tqdm

from dataset_generation.src.utils.constants import (
    GUTENBERG_DATASET_PATH,
    WIKISOURCE_DUMP_PATH,
)


def organize_books(
    output_path: str,
    books_outpath: Optional[str] = None,
    sources_dump_paths: List[str] = None,
    debug_title: str = None,
    debug_synset: str = None,
):
    if debug_title is not None or debug_synset is not None:
        return
    if sources_dump_paths is None:
        sources_dump_paths = [GUTENBERG_DATASET_PATH, WIKISOURCE_DUMP_PATH]
    path2source_name = {
        GUTENBERG_DATASET_PATH: "gutenberg",
        WIKISOURCE_DUMP_PATH: "wikisource",
    }
    out_dir = "/".join(output_path.split("/")[:-1])
    if "." in out_dir:
        out_dir = "."
    index = []
    index_output_path = output_path.replace(".jsonl", "_index.jsonl")
    if not os.path.exists(index_output_path):
        books_out_path = (
            os.path.join(out_dir, "books") if books_outpath is None else books_outpath
        )
        if not os.path.exists(books_out_path):
            os.makedirs(books_out_path)
        with open(output_path) as f:
            books = [json.loads(l.strip()) for l in f.readlines()]
        for book in tqdm(
            books,
            desc=f"Copying books from dump dirs to dataset dir: {books_out_path}",
        ):
            if "versions" in book and ("summaries" in book or "xsummaries" in book):
                versions = book["versions"]
                final_versions = []
                seen_files = set()
                for version in versions:
                    for source_dump in sources_dump_paths:
                        source_dir_name = os.path.join(source_dump.split("/")[-1])
                        dump_base_dir = source_dump.replace(source_dir_name, "")

                        if not any(
                            [source_dir_name in p for p in version["filepaths"]]
                        ):
                            continue
                        text = ""
                        for filepath in version["filepaths"]:
                            dump_book_filepath = os.path.join(
                                dump_base_dir, filepath.lstrip("/")
                            )
                            if os.path.exists(dump_book_filepath):
                                try:
                                    with open(dump_book_filepath, "rb") as f:
                                        file_text = f.read()
                                        file_text = unicode(file_text, errors="replace")
                                        text += file_text + "\n"
                                except:
                                    print(dump_book_filepath)
                        # discards undesired languages
                        if version["language"] in book["title"]:
                            title = (
                                book["title"][version["language"]]
                                + "_"
                                + version["title"]
                            )
                            filename = (version["language"] + "_" + title).replace(
                                "/", " "
                            )[:100]
                            book_filename = filename + ".jsonl"
                            book_file = os.path.join(books_out_path, book_filename)
                            version["filepath"] = book_file
                            # deduplication: gutenberg may contain the same book text associated with different ids.
                            if book_file not in seen_files:
                                final_versions.append(version)
                                source = path2source_name[source_dump]
                                with open(book_file, "w") as w:
                                    w.write(
                                        json.dumps(
                                            {
                                                "title": version["title"],
                                                "wikipedia_page": book["title"][
                                                    version["language"]
                                                ],
                                                "language": version["language"],
                                                "source": source,
                                                "raw_text": text,
                                            }
                                        )
                                    )
                            seen_files.add(book_file)
                for v in final_versions:
                    del v['filepaths']
                book['versions'] = final_versions
                index.append(book)
    with open(index_output_path, "w") as f:
        for b in index:
            f.write(json.dumps(b) + "\n")
