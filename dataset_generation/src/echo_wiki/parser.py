import json
import os.path
import re
from typing import List

import mwparserfromhell
from tqdm import tqdm
from dataset_generation.src.book_classification.book_classifier import BookClassifier
from dataset_generation.src.metrics.edit_similarity import EditSimilarity
from dataset_generation.src.metrics.filter import Filter
from dataset_generation.src.parsers.gutenberg_parser import GutenbergParser
from dataset_generation.src.parsers.wikisource_parser import WikisourceParser
from dataset_generation.src.utils.constants import (
    PLOT_TAGS_PATH,
    WIKI_DUMP_PATH,
    WIKI_DUMP_DATE,
)
from dataset_generation.src.utils.utils import parse_introduction, EnhancedJSONEncoder


SECTION_PATTERN = "={2,}.*={2,}"
REDIRECTION_TAG = "WIKI_RED:"
FILM_PATTERN = "~?FILM"


def iter(wiki_path, limit=None):
    count = 0
    with open(wiki_path) as f:
        for line in f:
            count += 1
            if limit is None or count < limit:
                yield line
            else:
                return


class EchoWikiParser:
    def parse(
        self,
        languages: List[str] = None,
        debug: bool = True,
        outpath: str = None,
        debug_title: str = None,
        debug_synset: str = None,
        limit: int = None,
        edit_similarity_treshold: int = 0.7,
        title_translations_path: str = "data/wiki_title_translations/wiki_title_translations.jsonl",
    ):
        if debug_title is not None:
            outpath = f"{debug_title}.jsonl"
        if debug_synset is not None:
            outpath = f"{debug_synset}.jsonl"
        out_dir = "/".join(outpath.split("/")[:-1])
        if not "." in out_dir and out_dir != "" and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if not os.path.exists(outpath):
            parse_introductions = True
            book_classifier = BookClassifier()
            # similarity threshold to discard uncorrectly mapped titles ->  wiki pages
            title_translations = self._load_translations(
                languages, title_translations_path
            )
            synset2book = {}
            summ_id = "summ:00000000"
            with open(outpath, "w") as dataset_f:
                for i, lang in enumerate(languages):
                    metric = EditSimilarity(lang)
                    filter = Filter(
                        metric,
                        edit_similarity_treshold,
                        report_path=outpath.replace(
                            ".jsonl", f"_{metric.get_name()}.tsv"
                        ),
                    )
                    parsers = [
                        GutenbergParser(lang, filter),
                        WikisourceParser(lang, languages),
                    ]
                    wiki_dump = f"{WIKI_DUMP_PATH}/{lang}_{WIKI_DUMP_DATE}.jsonl"
                    plot_tags_path = os.path.join(PLOT_TAGS_PATH, f"{lang}.txt")
                    bn_title2synset = self._get_title2synset(title_translations)
                    with open(plot_tags_path) as f:
                        plot_tags = [l.strip() for l in f.readlines()]
                        for p in tqdm(
                            iter(wiki_dump, limit), f"generating {lang} dataset"
                        ):
                            page_json = json.loads(p)
                            if page_json["raw_text"] is None:
                                continue
                            content = page_json["raw_text"]
                            title = page_json["title"]
                            if not (
                                debug
                                and debug_title is not None
                                and title != debug_title
                            ):
                                book_synset = self._get_synset(
                                    title, bn_title2synset, REDIRECTION_TAG
                                )
                                if not (
                                    debug
                                    and debug_synset is not None
                                    and book_synset != debug_synset
                                ):
                                    versions = []
                                    for parser in parsers:
                                        versions.extend(
                                            parser.get_links(
                                                content, title, book_synset=book_synset
                                            )
                                        )
                                    has_versions = len(versions) > 0
                                    raw_content = content
                                    content = content.lower()
                                    lines = content.split("\n")
                                    page_sections = [
                                        l.lower()
                                        for l in lines
                                        if re.search(SECTION_PATTERN, l)
                                    ]
                                    summary_sections = self._get_summary_sections(
                                        page_sections, plot_tags
                                    )
                                    if has_versions or len(summary_sections) > 0:
                                        if book_synset is None:
                                            book_synset = self._increment_id(summ_id)
                                            summ_id = book_synset
                                        categories = book_classifier.get(book_synset)
                                        if categories is not None and any(
                                            [
                                                re.search(FILM_PATTERN, c)
                                                for c in categories
                                            ]
                                        ):
                                            continue
                                        # whether to create a new instance for the book or associate it with a previous one (based on translations)
                                        book = synset2book.get(book_synset, {})
                                        book = self._build_book(
                                            book,
                                            book_synset,
                                            lang,
                                            versions,
                                            summary_sections,
                                            title,
                                            title_translations,
                                            categories,
                                        )
                                        summaries = self._parse_summaries(
                                            raw_content, summary_sections
                                        )
                                        if summaries:
                                            book = self._set_book_field(
                                                book, lang, "summaries", summaries
                                            )
                                        if parse_introductions:
                                            try:
                                                intro = parse_introduction(raw_content)
                                                book = self._set_book_field(
                                                    book, lang, "introduction", intro
                                                )
                                            except:
                                                print(f"Parsing error: {title}")
                                        synset2book[book_synset] = book
                    filter.report_file.close()
                grouping = {}
                for _, book in synset2book.items():
                    for lang in languages:
                        if "title" in book and lang in book["title"]:
                            book_title = book["title"][lang]
                            # key = f"{lang}_{book_title}"
                            title_books = grouping.get(book_title, [])
                            title_books.append(book["synset"])
                            grouping[book_title] = title_books
                            # grouping[key] = title_books
                grouping = {k: v for k, v in grouping.items() if len(v) > 1}
                synset_blacklist = {"bn:01293529n"}
                # resolve title conflicts by removing low quality synset based on wikidata categorization
                for key, synsets in grouping.items():
                    LQ_synsets = [
                        s
                        for s in synsets
                        if "categories" not in synset2book[s]
                        or not s.startswith("bn:")
                        or all(
                            [
                                cat.startswith("~")
                                for cat in synset2book[s]["categories"]
                            ]
                        )
                    ]
                    if len(LQ_synsets) == len(synsets):
                        LQ_synsets = []
                    synset_blacklist.update(set(LQ_synsets))
                for syn, book in synset2book.items():
                    if syn not in synset_blacklist:
                        if "categories" in book:
                            book["categories"] = [
                                cat.replace("~", "").strip()
                                for cat in book["categories"]
                            ]
                        dataset_f.write(
                            json.dumps(book, cls=EnhancedJSONEncoder) + "\n"
                        )

    def _get_summary_sections(self, sections, summary_tags):
        sec_toks = [re.sub("={2,}", "", s.lower()).strip().split(" ") for s in sections]
        matched = []
        for s_tag in summary_tags:
            # exact match if summary tag is a multiword or startswith '!' marker, otherwise soft match (summary tag contained in section)
            matched = (
                # contain-like match
                [
                    sections[i]
                    for i, toks in enumerate(sec_toks)
                    if self._contain_tokens(s_tag.replace("~", "").strip(), toks)
                ]
                if s_tag.startswith("~")
                # exact match
                else [
                    s
                    for s in sections
                    if re.sub("={2,}", "", s.lower()).strip() == s_tag
                ]
            )
            if matched:
                break
        return matched

    def _contain_tokens(self, summary_tag: str, tokens: List[str]):
        summary_tokens = summary_tag.split(" ")
        return all([tok in summary_tokens for tok in tokens])

    def _load_books(self, books_path: str):
        with open(books_path) as f:
            books = [json.loads(l.strip()) for l in f.readlines()]
        return {b["synset"]: b for b in books if "synset" in b}

    def _get_title2synset(self, wiki_translations):
        langtitle2synset = {}
        for synset, translations in wiki_translations.items():
            titles = []
            for _, names in translations.items():
                titles.extend(names)
            for lang_title in titles:
                langtitle2synset[lang_title] = synset
        return langtitle2synset

    def _check_book(self, title, langtitle_2synset, redirection_tag):
        redirection_title = f"{redirection_tag}{title}"
        return title in langtitle_2synset or redirection_title in langtitle_2synset

    def _get_synset(self, title, langtitle_2synset, redirection_tag):
        redirection_title = f"{redirection_tag}{title}"
        synset = langtitle_2synset.get(
            title, langtitle_2synset.get(redirection_title, None)
        )
        if synset is None:
            synset = langtitle_2synset.get(
                title.lower(), langtitle_2synset.get(redirection_title.lower(), None)
            )
        return synset

    def _load_translations(self, languages, wiki_title_translations_path):
        langs_tag = "".join(sorted(languages))
        filtered_translations_path = wiki_title_translations_path.replace(
            ".json", f"_{langs_tag}_filtered.json"
        )
        translations_path = (
            wiki_title_translations_path
            if not os.path.exists(filtered_translations_path)
            else filtered_translations_path
        )
        with open(translations_path) as f:
            translations = [
                json.loads(l.strip())
                for l in tqdm(f.readlines(), desc="loading wiki titles translations")
            ]
        translations = {
            page["synset"]: {
                lan: links
                for lan, links in page["links"].items()
                if lan.lower() in languages
            }
            for page in tqdm(translations, desc="filtering wiki titles translations")
        }
        if not os.path.exists(filtered_translations_path):
            with open(filtered_translations_path, "w") as f:
                for synset, transl in translations.items():
                    if len(transl) > 0:
                        f.write(json.dumps({"synset": synset, "links": transl}) + "\n")
        return {
            synset: transl for synset, transl in translations.items() if len(transl) > 0
        }

    def _build_book(
        self,
        book,
        book_synset,
        language,
        versions,
        summary_sections,
        title,
        translations,
        categories,
    ):
        cleaned_sections = [re.sub("={2,}", "", s).strip() for s in summary_sections]
        # removes parenthesis from title
        title = re.sub("\(.*\)", "", title).strip()
        book = self._set_book_field(book, language, "title", title)
        book["synset"] = book_synset
        if categories is not None:
            book["categories"] = categories
        book = self._set_book_field(book, language, "sections", cleaned_sections)
        for lang in set([v.language for v in versions]):
            lang_versions = [v for v in versions if v.language == lang]
            book_versions = book.get("versions", [])
            book_versions.extend(lang_versions)
            final_versions = []
            seen = set()
            for v in book_versions:
                if not any([path in seen for path in v.filepaths]):
                    final_versions.append(v)
                    seen.update(v.filepaths)
            book["versions"] = final_versions

        book_translations = translations.get(book_synset, None)
        if book_translations is not None:
            book["translations"] = {
                **book.get("translations", {}),
                **translations[book_synset],
            }
        return book

    def _set_book_field(self, book, language, field_name, field_value):
        field = book.get(field_name, {})
        ## updates existing info
        if language in field and isinstance(field[language], list):
            field_value = list(set(field_value + field[language]))
        field[language] = field_value
        if field_value:
            book[field_name] = field
        return book

    def _get_lang_translations(self, synset2book, lang):
        books = [v for _, v in synset2book.items()]
        lang_titles2book = {b["translations"][lang.upper()]: b for b in books}
        lang_title2book = {}
        for titles, book in lang_titles2book.items():
            for t in titles:
                lang_title2book[t] = book
        return lang_title2book

    def _parse_summaries(self, content, summary_sections):
        summaries = []
        for section in summary_sections:
            indent = int(len(re.findall("=", section)) / 2)
            content_after_section_title = content[
                content.lower().index(section) + len(section) :
            ]
            marker_pattern = "[^=]={\d}[^=]".replace("\d", str(indent))
            end_offset = re.search(marker_pattern, content_after_section_title)
            # summary section is the last one
            if end_offset is None:
                end_offset = -1
            # if end_offset is not None and end_offset.regs:
            else:
                end_offset = end_offset.regs[0][0]
            summary = content_after_section_title[:end_offset]
            summary = mwparserfromhell.parse(summary).strip_code()
            summary = re.sub(".*\|", "", summary)
            if summary.strip() != "" and len(summary.strip()) > 50:
                summaries.append(summary)

        return summaries

    def _increment_id(self, previous_id: str):
        prefix = "summ:"
        _, id = previous_id.split(prefix)
        new_id = int(id) + 1
        return f"{prefix}{str(new_id).zfill(8)}"
