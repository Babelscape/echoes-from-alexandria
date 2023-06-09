import json
import os
import pickle
import subprocess
import sys
import xml.sax
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
import regex as re
import wget
from tqdm import tqdm

from dataset_generation.src.utils.constants import (
    WIKISOURCE_DUMP_PATH,
    WIKISOURCE_DUMP_DATE, WIKI_DUMP_DATE,
)
from dataset_generation.src.utils.utils import EnhancedJSONEncoder, unique

MAIN_NS = "0"
REGEXP_SKIP = re.compile("^(#REDIRECT|redirect)")


@dataclass
class RawWikiPage:
    """
    Represents a Wikipedia Page
    """

    title: str
    id: str
    raw_text: str
    namespace: str


def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (
        current / total * 100,
        current,
        total,
    )
    # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()


class SplitWikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data_classes using SAX"""

    def __init__(self, language, outpath: str, corpus: str):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self.corpus = corpus
        self.progress_bar = tqdm(desc=f"Parsing {corpus}")
        self.output = open(outpath, "w")
        self.language = language

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.output.close()
        self.progress_bar.close()

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ("title", "text", "ns", "id"):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = "".join(self._buffer)

        if (
            name == "page"
            and (
                not REGEXP_SKIP.match(self._values["text"])
                or self.corpus == "wikisource"
            )
            and (self._values["ns"] == MAIN_NS or self.corpus == "wikisource")
        ):
            self.output.write(
                json.dumps(
                    RawWikiPage(
                        self._values["title"],
                        self._values["id"],
                        self._values["text"],
                        self._values["ns"],
                    ),
                    cls=EnhancedJSONEncoder,
                )
            )
            self.output.write("\n")
            self.progress_bar.update(1)


def download(language: str, dump_path: str, date: str, corpus: str = "wiki"):
    """download wikipedia"""
    url = f"https://dumps.wikimedia.org/{language}{corpus}/{date}/{language}{corpus}-{date}-pages-articles-multistream.xml.bz2"
    print(url)
    Path(dump_path).parent.mkdir(exist_ok=True, parents=True)
    wget.download(url, dump_path, bar=bar_progress)


def generate_dump(language: str, wiki_dump_path: str, date: str, corpus: str):
    """Creates small chunks of Wikipedia. Downloads the dump automatically if is not present"""
    output_path = wiki_dump_path.replace(".bz2", ".jsonl")
    if not os.path.exists(output_path):
        download(language, wiki_dump_path, date, corpus)
        # Object for handling xml
        with SplitWikiXmlHandler(language, output_path, corpus) as handler:
            # Parsing object
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            # Iteratively process file
            for line in subprocess.Popen(
                ["bzcat"],
                stdin=open(wiki_dump_path, "r"),
                stdout=subprocess.PIPE,
            ).stdout:
                parser.feed(line)
            handler.output.close()


def download_wiki(corpus: str, output_path: str, date: str, languages: List[str]):
    for language in languages:
        dump_path = os.path.join(output_path.rstrip('/'), f"{language}_{date}.bz2")
        generate_dump(language, dump_path, date, corpus)


def organize_texts(
    wikisource_dump: str,
    wikisource_date: str,
    languages: List[str],
    debug_title: str = None,
):
    for language in languages:
        language_dump_path = os.path.join(
            wikisource_dump, f"{language}_{wikisource_date}"
        )
        trie_path = (
            f"{language_dump_path}.pkl" if debug_title is None else f"{debug_title}.pkl"
        )
        title2id, title2text, titles = {}, {}, []
        if not os.path.exists(trie_path) or not os.path.exists(language_dump_path):
            title2id, title2text = parse_wikisource_indices(language_dump_path)
            titles = [k for k, _ in title2id.items()]
        if not os.path.exists(trie_path):
            build_wikisource_trie(
                debug_title, title2id, title2text, titles, trie_path, language
            )
        if not os.path.exists(language_dump_path):
            Path(language_dump_path).mkdir(parents=True, exist_ok=True)
            dump_texts(language_dump_path, title2text, language, title2id=title2id)


def parse_wikisource_indices(language_dump_path):
    title2text = {}
    title2id = {}
    with open(f"{language_dump_path}.jsonl") as f:
        for line in tqdm(f, desc="parsing wikisource dump"):
            book = json.loads(line.strip())
            id = book["id"]
            title = book["title"]
            raw_text = book["raw_text"]
            title2text[title] = raw_text
            title2id[title] = id
    return title2id, title2text


def build_wikisource_trie(
    debug_title, title2id, title2text, titles, trie_path, language
):
    trie = {}
    for title in tqdm(titles, desc="generating wikisource trie"):
        if debug_title is None or title == debug_title:
            title = title.replace("_", " ")
            text = title2text[title]
            # links are parsed if the page is an index
            links = get_links(title, text, title2id, language, title2text)
            level = trie
            path = title.split("/")
            for i, chunk in enumerate(path):
                parent_page = "/".join(path[:-1])
                parent_text = title2text.get(parent_page, "")
                is_parent_index = (
                    parent_page.strip() == ""
                    or parent_text == ""
                    or len(
                        get_links(
                            parent_page,
                            title2text[parent_page],
                            title2id,
                            language=language,
                            title2text=title2text,
                        )
                    )
                    > 0
                )
                # path is followed only if the parent is an index page
                if is_parent_index:
                    index = f"/{chunk}" if i > 0 else chunk
                    index = index.rstrip("/")
                    if index not in level:
                        level[index] = OrderedDict()
                    level = level.get(chunk, level.get(f"/{chunk}", None))
                    if level is None:
                        raise Exception(f"Error in trie visit for {title}")
                    if i == len(path) - 1:
                        if all(
                            [
                                l.startswith(page_translate("Page:", language))
                                for l in links
                            ]
                        ):
                            book_titles = set([l.split("/")[0] for l in links])
                            for t in book_titles:
                                level[t] = OrderedDict()
                        else:
                            for link in links:
                                no_redir_link = link.replace("#REDI:", "")
                                found = no_redir_link in title2id
                                if not found:
                                    multi_s_pattern = "\s{2,}"
                                    found = (
                                        re.sub(multi_s_pattern, " ", no_redir_link)
                                        in title2id
                                    )
                                    if found:
                                        link = re.sub(multi_s_pattern, " ", link)
                                link = link.replace(title + "/", "/")
                                # removes non existing links, e.g. the ones in underlined in red in https://en.wikisource.org/wiki/Theogony
                                if link.strip() != "" and (
                                    link.startswith("/") or found
                                ):
                                    link = link.rstrip("/")
                                    level[link] = OrderedDict()
    with open(trie_path, "wb") as f:
        pickle.dump(trie, f)


def page_translate(page, language):
    translation = {"es": "Página:", "it": "Pagina:", "de": "Seite:"}.get(
        language, "Page:"
    )
    return page.replace("Page:", translation)


def dump_texts(
    language_dump_path, title2text, language: str, title2id, page_limit: int = 5000
):
    blacklist = get_blacklist(language)
    author_marker = get_author_marker(language)
    for title, text in tqdm(title2text.items(), "cleaning wikisource texts"):
        if not any([dir in title for dir in blacklist]):
            if author_marker is None or not author_marker in title2text.get(title, ""):
                dump_text(
                    language=language,
                    language_dump_path=language_dump_path,
                    text=text,
                    title=title,
                    title2text=title2text,
                    title2id=title2id,
                )


def get_blacklist(language: str):
    # these titles are discarded since their texts are huge
    return {
        "en": [
            "1911 Encyclopædia Britannica",
            "Dictionary of National Biography, 1885-1900",
            "Popular Science Monthly",
            "Appletons' Cyclopædia of American Biography",
            "Catholic Encyclopedia (1913)",
            "Dictionary of Christian Biography and Literature to the End of the Sixth Century",
        ]
    }.get(language, [])


def dump_text(
    language,
    language_dump_path,
    text,
    title,
    title2text,
    title2id,
    sec_sep: str = "-sec=",
):
    filepath = os.path.join(language_dump_path, f"{title[:200]}.txt")
    links = get_links(title, text, title2id, language, title2text)
    pages_links = [
        l
        for l in links
        if l.startswith("Page:") or l.startswith(page_translate("Page:", language))
    ]
    has_pages = len(pages_links) > 0
    has_content = len(links) == 0 or has_pages and "Author:" not in title
    if has_content:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if has_pages:
            pages_texts = [
                title2text.get(p.split(sec_sep)[0], "")
                for p in pages_links
                if p.split(sec_sep)[0] in title2text
            ]
            # discards sections from text, according to fromsection, tosection tags
            if re.search(f"{sec_sep}\d+$", pages_links[0]):
                beginning_section = "s" + pages_links[0].split(sec_sep)[-1].strip()
                cropped_page = re.split(
                    f"<\s?section begin={beginning_section}\s?/>", pages_texts[0]
                )[-1]
                if cropped_page.strip() != "":
                    pages_texts[-1] = cropped_page
            if re.search(f"{sec_sep}\d+$", pages_links[-1]):
                ending_section = "s" + pages_links[-1].split(sec_sep)[-1].strip()
                cropped_page = re.split(
                    f"<\s?section end={ending_section}\s?/>", pages_texts[-1]
                )[0]
                if cropped_page.strip() != "":
                    pages_texts[-1] = cropped_page
            if pages_texts:
                text = "\n".join(pages_texts)
            else:
                return
        if text.strip() != "" and len(text) > 1000:
            with open(filepath, "w") as f:
                f.write(text)


def get_all_pages_files(page, page_limit, title2id):
    pages = [
        f"{page}/{str(num)}"
        for num in range(page_limit)
        if f"{page}/{str(num)}" in title2id
    ]
    return pages


def get_links(title, raw_text, title2id, language, title2text, extensions=None):
    if extensions is None:
        extensions = ["djvu", "pdf", "jpg"]
    # # removes content in header table to avoid prev and next chapter links which causes loops
    raw_text = re.sub(" \\| .*", "", raw_text)
    section_pattern = re.compile("={2,}")
    hyperlinks = []
    if re.search(section_pattern, raw_text):
        first_section = re.split(section_pattern, raw_text)[0]
        hyperlinks = get_hyperlinks(title, first_section, title2text, language)
    if not hyperlinks:
        hyperlinks = get_hyperlinks(title, raw_text, title2text, language)
    pages_files = []
    for ext in extensions:
        pages_files = get_pages_files(
            raw_text, ext, title2id=title2id, language=language
        )
        if pages_files:
            break
    path_hyperlinks = [h for h in hyperlinks if h.startswith("/") or f"{title}/" in h]
    if path_hyperlinks:
        hyperlinks = path_hyperlinks
    elif pages_files:
        hyperlinks = pages_files
    elif len(raw_text) > 4000:
        hyperlinks = []
    # redirection handling
    if len(hyperlinks) == 1 and re.search("# ?RED.*\[\[", raw_text) is not None:
        hyperlinks[0] = f"#REDI:{hyperlinks[0]}"
    for i, link in enumerate(hyperlinks):
        hyperlinks[i] = link.replace("{{PAGENAME}}", title)
    return unique(hyperlinks)


def get_author_marker(lang):
    return {
        "es": "{{Biocitas",
        "en": "{{author",
        "de": "{{Personendaten",
        "fr": "{{Auteur",
    }.get(lang, None)


def get_hyperlinks(title, raw_text, title2text, lang):
    hyperlinks = []
    for line in raw_text.split("\n"):
        # header line
        if line.startswith("|"):
            continue
        link = None
        version_link = re.findall("\[\[(.+?)\]\]", line)
        author_marker = get_author_marker(lang)
        version_link = [
            v
            for v in version_link
            if not re.search(":\w", v) and ("|" in v or re.search("# ?RED", line))
        ]
        # discards links to author pages
        if author_marker is not None:
            version_link = [
                v
                for v in version_link
                if not author_marker in title2text.get(v.split("|")[0], "")
            ]
        if version_link:
            # if multiple links in line, choose the one containing the page title
            matched_links = [l for l in version_link if title.lower() in l.lower()]
            if matched_links:
                links = [l.split("|")[0].strip() for l in matched_links]
                hyperlinks.extend(links)
                continue
            else:
                link = version_link[0].split("|")[0].strip()
        else:
            path_link = re.findall("\{\{(.+?)\}\}", line)
            if (
                path_link
                and re.search("\\|\s*/", path_link[0])
                and not re.search(":\w", path_link[0])
                and not re.search("similar ?\\|", path_link[0])
            ):
                link = path_link[0].split("|")[1]
        if link is not None:
            hyperlinks.append(link)
    return hyperlinks


def get_pages_files(raw_text, extension: str, title2id: Dict[str, str], language: str):
    pages_links = re.findall(f"<pages.* index.*{extension}.*>?", raw_text)
    if pages_links:
        pages_hyperlinks = extract_pages_numbers_from_tags(
            extension, pages_links, title2id, language
        )
    else:
        pages_hyperlinks = []
        extension_tags = re.findall("\\|.*" + extension + ".*}}", raw_text)
        for ext_tag in extension_tags:
            hyperlink = [chunk.replace('}}', '').strip() for chunk in ext_tag.split('|') if extension in chunk]
            if hyperlink:
                pages_hyperlinks.append(hyperlink[0])
    return pages_hyperlinks


def extract_pages_numbers_from_tags(
    extension, pages_links, title2id, language, page_limit=5000, section_sep="-sec="
):
    page_hyperlinks = []
    for page_link in pages_links:
        if len(page_link) > 200:
            continue
        book_filename = re.split("index\s*=", page_link)
        if len(book_filename) < 2:
            continue
        book_filename = book_filename[1].split(f".{extension}")
        if not book_filename:
            continue
        book_filename = book_filename[0]
        pages_numbers_tags = {}
        for tag in {"from", "to", "exclude", "include", "fromsection", "tosection"}:
            found_tag = re.findall(f'{tag}\s?=["\s]*s?\d+', page_link)
            if not found_tag:
                continue
            found_tag = found_tag[0]
            page_number = re.sub(f'{tag}\s?=["\s]*s?', "", found_tag).strip()
            pages_numbers_tags[tag] = page_number
        page_file = f"Page:{book_filename}.{extension}".replace('"', "")
        if pages_numbers_tags == {}:
            pages_files = get_all_pages_files(
                page_file, title2id=title2id, page_limit=page_limit
            )
            if not pages_files:
                page_file = page_translate(page_file, language)
                pages_files = get_all_pages_files(
                    page_file, title2id=title2id, page_limit=page_limit
                )
            if pages_files:
                page_hyperlinks.extend(pages_files)
        else:
            pages_to_exclude = single_pages_tags(pages_numbers_tags, "exclude")
            pages_to_include = single_pages_tags(pages_numbers_tags, "include")
            page_numbers = []
            if "from" in pages_numbers_tags and "to" in pages_numbers_tags:
                page_numbers = [
                    f"Page:{book_filename}.{extension}/{page_num}".replace('"', "")
                    for page_num in range(
                        int(pages_numbers_tags["from"]),
                        int(pages_numbers_tags["to"]) + 1,
                    )
                    if page_num not in pages_to_exclude
                ]
            elif "from" in pages_numbers_tags:
                page_num = int(pages_numbers_tags["from"])
                wikisource_page = (
                    f"Page:{book_filename}.{extension}/{page_num}".replace('"', "")
                )
                while wikisource_page in title2id:
                    if page_num not in pages_to_exclude:
                        page_numbers.append(wikisource_page)
                    wikisource_page = (
                        f"Page:{book_filename}.{extension}/{page_num}".replace('"', "")
                    )
                    page_num += 1
            elif "to" in pages_numbers_tags:
                page_numbers = [
                    f"Page:{book_filename}.{extension}/{page_num}".replace('"', "")
                    for page_num in range(
                        0,
                        int(pages_numbers_tags["to"]) + 1,
                    )
                    if page_num not in pages_to_exclude
                ]
                page_numbers = [p for p in page_numbers if p in title2id]
            page_numbers += [
                f"Page:{book_filename}.{extension}/{page_num}".replace('"', "")
                for page_num in pages_to_include
            ]
            if page_numbers:
                if "fromsection" in pages_numbers_tags:
                    page_numbers[
                        0
                    ] += f"{section_sep}{pages_numbers_tags['fromsection']}"
                if "tosection" in pages_numbers_tags:
                    page_numbers[
                        -1
                    ] += f"{section_sep}{pages_numbers_tags['tosection']}"
                page_hyperlinks.extend(page_numbers)
            else:
                print("WARNING: page number not extracted for:")
                print(page_link)
    filtered_page_hyperlinks = [
        h for h in page_hyperlinks if h.split(section_sep)[0] in title2id
    ]
    if len(page_hyperlinks) > 0 and len(filtered_page_hyperlinks) == 0:
        page_hyperlinks = [page_translate(p, language) for p in page_hyperlinks]
        filtered_page_hyperlinks = [
            h for h in page_hyperlinks if h.split(section_sep)[0] in title2id
        ]
    page_hyperlinks = sorted(
        filtered_page_hyperlinks,
        key=lambda x: int(x.split("/")[-1].split(section_sep)[0]),
    )
    return page_hyperlinks


def single_pages_tags(from_to, tag):
    pages_to_exclude = []
    exclude = from_to.get(tag, "")
    if exclude != "":
        pages_to_exclude = [int(p.replace('"', "")) for p in re.split("[,-]", exclude)]
    return pages_to_exclude


def test_dump(wikisource_page: str, language: str):
    language_dump_path = os.path.join(
        WIKISOURCE_DUMP_PATH, f"{language}_{WIKISOURCE_DUMP_DATE}"
    )
    title2id, title2text = parse_wikisource_indices(language_dump_path)
    dump_text(
        language,
        language_dump_path,
        title=wikisource_page,
        title2text=title2text,
        text=title2text[wikisource_page],
        title2id=title2id,
    )

