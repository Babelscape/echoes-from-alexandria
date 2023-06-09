import json
import os
import re
from typing import Optional
import mwparserfromhell
from tqdm import tqdm

from dataset_generation.src.utils.utils import chunks


def clean_books(
    output_path: str,
    books_path: Optional[str] = None,
):
    if books_path is None:
        books_path = os.path.join("/".join(output_path.split("/")[:-1]), "books")
    for book in tqdm(os.listdir(books_path), desc='Cleaning books'):
        book_file = os.path.join(books_path, book)
        with open(book_file) as f:
            book_json = json.load(f)
            if 'raw_text' in book_json:
                book_text = book_json["raw_text"]
                source = book_json["source"]
                if source == "wikisource":
                    PARSER_MAX_LEN = 1_000_000
                    if len(book_text) < PARSER_MAX_LEN:
                        text = clean_wikisource_text(book_text)
                    else:
                        text = ''
                        text_chunks = chunks(book_text, PARSER_MAX_LEN)
                        for chunk in text_chunks:
                            text += clean_wikisource_text(chunk) + '\n'
                elif source == "gutenberg":
                    text = clean_text(book_text)
                else:
                    raise Exception(f"Cleaning not implemented for source: {source}")
        if 'raw_text' in book_json:
            book_json['text'] = text
            del book_json['raw_text']
            with open(book_file, "w") as w:
                w.write(json.dumps(book_json))


def clean_wikisource_text(book_text):
    text = misc_pre_cleaning(book_text)
    text = mwparserfromhell.parse(text).strip_code()
    text = misc_cleaning(text)
    return text


def misc_pre_cleaning(text):
    text = handle_initial_tags(text)
    text = re.sub("{{float center\\|{{smaller block\\|", "", text)
    text = text.replace("&nbsp;", "")
    text = remove_html_tag("noinclude", text)
    return text


def remove_html_tag(tag: str, text: str) -> str:
    return re.sub(rf"(?s)<{tag}>.*?</{tag}>", "", text)


def misc_cleaning(text):
    text = re.sub("\[\[File:.*\]\]", "", text)
    text = re.sub("\d{2,3}px", "", text)
    text = re.sub("frameless\|.*", "", text)
    text = re.sub("Category:.*", "", text)
    text = re.sub("\{\|.*", "", text)
    text = re.sub("\|\}.*", "", text)
    text = re.sub("}{2,}", "", text)
    characters = ["|", "<", "{", "}"]
    new_text = ""
    for line in text.split("\n"):
        if line.strip() != "":
            if not any([line.startswith(c) for c in characters]):
                new_text += line + "\n"
    return new_text.strip()


def handle_initial_tags(text):
    initial_tags = re.findall(
        "(\{\{[Dd]rop ?cap\|\w\}\})|(\{\{[Dd]rop ?initial\|\w\}\})|(\{\{[dD]i\|\w\}\})|(\{\{[Dd]rop ?initial\|\w\|.+\}\})|(\{\{[dD]i\|\w\|.+\}\})|(\{\{[us]c\|\w+\}\})|(\{\{[us]c\|.*\}\})|(\{{[Ss]mall-?caps\|.*\}\})",
        text,
    )
    initial_tags = [[item for item in list(t) if item != ""][0] for t in initial_tags]
    for tag in initial_tags:
        for chunk in tag.split("{{"):
            if chunk.strip() != "":
                if "|" in chunk:
                    actual_text = re.sub("}{2}", "", chunk.split("|")[1], count=1)
                    escaped_str = re.escape("{{" + chunk)
                    try:
                        text = re.sub(escaped_str, actual_text, text)
                    except:
                        continue
    return text


def clean_text(text: str) -> Optional[str]:
    start_patterns = [
        "\\*{3}\s?START OF.*[\r\n]?.*\\*{3}[\n\r]+",
    ]
    end_patterns = [
        "\\*{3}\s?END OF.*[\r\n]?.*\\*{3}[\n\r]+",
    ]
    note_patterns = {"Illustration", "Footnote"}
    new_text = None
    for pattern in note_patterns:
        text = re.sub("[\n\r]+", "@#@", text)
        text = re.sub(f"\[{pattern}:?.*?]", "", text)
        text = re.sub("@#@", "\n", text)
    start_offset = None
    end_offset = None
    for start_pattern in start_patterns:
        start_offset = [
            match.end() for match in re.finditer(re.compile(start_pattern), text)
        ]
        if start_offset:
            start_offset = start_offset[0]
            break
    if not start_offset:
        start_offset = None
    for end_pattern in end_patterns:
        end_offset = [match.start() for match in re.finditer(end_pattern, text)]
        if end_offset:
            end_offset = end_offset[0]
            break
    if not end_offset:
        end_offset = None
    if start_offset is not None:
        new_text = text[start_offset:]
    if end_offset is not None:
        if new_text is not None:
            new_text = new_text[:end_offset]
        else:
            new_text = text[:end_offset]
    return new_text if new_text is not None else text


if __name__ == "__main__":
    # clean_books(
    #     "project_alexandria_9_11/project_alexandria.jsonl",
    #     source_paths=[WIKISOURCE_DUMP_PATH],
    # )
    print(clean_text("/media/ssd/alessandro/project_alexandria/gutenberg/4637.txt"))
