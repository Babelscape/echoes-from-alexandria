import json
import os
import pickle
from copy import deepcopy
from tqdm import tqdm
import re
from typing import List, Set, Optional
from dataset_generation.src.metrics.filter import Filter
from dataset_generation.src.parsers.base_parser import Parser
from dataset_generation.src.utils.constants import (
    WIKISOURCE_DUMP_PATH,
    WIKISOURCE_DUMP_DATE,
)
from dataset_generation.src.utils.utils import Version, Source, unique


class WikisourceParser(Parser):
    def __init__(
        self,
        language: str,
        languages: List[str],
        filter: Optional[Filter] = None,
    ):
        super().__init__(language, filter)
        index_path = os.path.join(
            WIKISOURCE_DUMP_PATH, f"{self.language}_{WIKISOURCE_DUMP_DATE}.jsonl"
        )
        self.languages = languages
        self.parse_wikisource_tries(languages)
        self.manual_sources = {}
        self.titles = self.parse_titles(index_path)
        self.tag_patterns = self.get_patterns()
        self.full_text_pattern = {"fr": "Texte entier"}.get(language, None)

    def parse_wikisource_tries(self, languages):
        self.tries = {}
        for lang in languages:
            trie_path = os.path.join(
                WIKISOURCE_DUMP_PATH, f"{lang}_{WIKISOURCE_DUMP_DATE}.pkl"
            )
            with open(trie_path, "rb") as f:
                self.tries[lang] = pickle.load(f)

    def parse_titles(self, wikisource_dump):
        titles = []
        with open(wikisource_dump) as f:
            for line in tqdm(f, desc="parsing wikisource dump"):
                book = json.loads(line.strip())
                title = book["title"]
                titles.append(title)
        return titles

    def get_links(self, content: str, page_title: str, **kwargs) -> List[Version]:
        book_synset = kwargs["book_synset"]
        metatags = []
        self.parse_metatags(content, metatags)
        urls = []
        project_markers = self.get_markers()
        for tag in metatags:
            # parsing_fun = self.get_parsing_fun()
            link = self.title_tag_parsing(tag, page_title, project_markers)
            if link is not None:
                urls.append(link)
        if book_synset in self.manual_sources:
            book_manual_annotations = self.manual_sources[book_synset]
            for url in book_manual_annotations["versions"]:
                urls.append(Source(title=page_title, url=url))
        versions = {}
        for url in urls:
            final_urls = []
            wikisource_title = url.url.split("wiki/")[-1]
            try:
                self.get_files(final_urls, url, wikisource_title)
            except:
                print()
            if len(final_urls) < 1000:
                for source in final_urls:
                    language = url.url.split(".")[0]
                    base_path = os.path.join(
                        f"{WIKISOURCE_DUMP_PATH.split('/')[-1]}",
                        f"{language}_{WIKISOURCE_DUMP_DATE}/",
                    )
                    filepath = source.url.replace(base_path, "").replace(".txt", "")
                    # removes full text files when there are chapter files also (to avoid duplication of text)
                    if (
                        self.full_text_pattern is not None
                        and self.full_text_pattern in filepath
                        and len(final_urls) > 1
                    ):
                        continue
                    if "/" in filepath:
                        # version = "/".join(filepath.split("/")[:-1])
                        version = filepath.split("/")[0]
                    elif ":" in filepath:
                        version = filepath.split(":")[0].strip()
                    else:
                        version = filepath
                    group = versions.get(version, [])
                    group.append(source)
                    versions[version] = group
        if versions != {} and len(versions.values()) < 1000:
            final_versions = [
                Version(
                    title=t,
                    filepaths=unique([p.url for p in paths]),
                    language=paths[0].url.split("/")[1].split("_")[0],
                )
                for t, paths in versions.items()
            ]
            if self.filter is not None:
                final_versions = self.filter.filter_versions(page_title, final_versions)
            return final_versions
        else:
            return []

    def parse_metatags(self, content, metatags):
        for pattern in self.tag_patterns:
            metatags.extend(
                re.findall(pattern, content)
                + re.findall(self.get_patterns("en")[0], content)
            )
        if not metatags:
            for pattern in self.tag_patterns:
                content = content.replace("\n", " ")
                chunks = re.findall(pattern, content) + re.findall(
                    self.get_patterns("en")[0], content
                )
                metatags.extend([c.split("}}")[0] for c in chunks])
                # for chunk in chunks:
                #     metatags.extend([c for c in chunk.split("}}")[0] if c != ""])

    def get_files(
        self,
        final_urls: List[Source],
        url: Source,
        wikisource_title,
        seen: Set[str] = None,
    ):
        language = url.url.split(".")[0]
        wikisource_title = wikisource_title.replace("_", " ")
        if seen is None:
            seen = set()
        path = wikisource_title.split("/")
        title_trie = self.tries.get(language, None)
        for chunk in path:
            if title_trie is not None:
                level = title_trie.get(chunk, None)
                if level is None:
                    level = title_trie.get(f"/{chunk}", None)
                title_trie = level
        if title_trie is not None:
            if title_trie == {} or all(
                [k.startswith(self.get_page_translation(language)) for k in title_trie]
            ):
                title_url = deepcopy(url)
                language = title_url.url.split(".")[0]
                title_url.url = f"{wikisource_title}.txt"
                if os.path.exists(
                    os.path.join(
                        WIKISOURCE_DUMP_PATH,
                        f"{language}_{WIKISOURCE_DUMP_DATE}",
                        title_url.url,
                    )
                ):
                    title_url.url = os.path.join(
                        f"{WIKISOURCE_DUMP_PATH.split('/')[-1]}",
                        f"{language}_{WIKISOURCE_DUMP_DATE}",
                        title_url.url,
                    )
                    final_urls.append(title_url)
            elif list(title_trie.keys())[0].startswith("#REDI:"):
                red_title = list(title_trie.keys())[0].replace("#REDI:", "")
                if red_title not in seen:
                    seen.add(red_title)
                    self.get_files(final_urls, url, red_title, seen)
            else:
                uris = [
                    f"{wikisource_title}{u}" for u in title_trie if u.startswith("/")
                ]
                if not uris:
                    uris = [k for k in title_trie]
                for uri in uris:
                    if uri not in seen:
                        seen.add(uri)
                        self.get_files(final_urls, url, wikisource_title=uri, seen=seen)

    def get_parsing_fun(self):
        return {"it": self.title_tag_parsing, "fr": self.title_tag_parsing}.get(
            self.language, self.default_parsing_fun
        )

    def get_markers(self):
        return {"it": ["wikisource", "s", "testo", "text"]}.get(
            self.language, ["wikisource", "s", "text"]
        )

    def get_page_translation(self, language):
        return {"es": "Página:", "it": "Pagina:", "de": "Seite:"}.get(language, "Page:")

    def get_patterns(self, lang: Optional[str] = None):
        if lang is None:
            lang = self.language
        return {
            "en": [
                re.compile("{{[Ww]ikisource\\|.*}}"),
                re.compile("{{[Ss]isterlinks\\|.*}}"),
            ],
            "it": [
                re.compile("{{[iI]nterprogetto.*\\|s=?.*\\|?}}"),
                "{{[iI]nterprogetto.*\\|testo=?.*\\|?}}",
            ],
            "fr": [re.compile("{{[Aa]utres projets.*[wW]ikisource.*=.*}}")],
        }.get(lang, ["{{[Ww]ikisource\\|.*}}"])

    def parse_interproject_link(
        self, tag: str, page_title: str, project_marker: Optional[str] = "s"
    ):
        chunks = tag.split("|")
        marker_pattern = f"^{project_marker}\s*="
        tag_chunks = [
            chunk for chunk in chunks if re.search(marker_pattern, chunk.strip())
        ]
        tag_chunks = [
            t
            for t in tag_chunks
            if ":" not in t or any([f"{l}:" in t for l in self.languages])
        ]
        if tag_chunks:
            language = self.language
            title = tag_chunks[0]
            if ":" in title:
                language = re.findall("\w{2}:", title)[0][:-1]
                title = title.replace(f"{language}:", "")
            title = re.sub(marker_pattern, "", title).strip()
            return Source(
                url=f"{language}.wikisource.org/wiki/{title}",
                title=page_title,
            )
        elif len([chunk for chunk in chunks if chunk.strip() == project_marker]) > 0:
            return Source(
                url=f"{self.language}.wikisource.org/wiki/{page_title}",
                title=page_title,
            )

    def default_parsing_fun(
        self, tag: str, page_title: str, **kwargs
    ) -> Optional[Source]:
        chunks = tag.replace("}}", "").split("|")
        tag_chunks = [chunk for chunk in chunks[1:] if "=" not in chunk]
        if not tag_chunks:
            source = Source(
                url=f"{self.language}.wikisource.org/wiki/{page_title}",
                title=page_title,
            )
            return source

        title = self.get_title(tag_chunks)
        ## e.g. idioma=, lang=
        lang_tags = self.get_lang_tags()
        language = self.language
        matched_tags = [lang_tag for lang_tag in lang_tags if lang_tag in tag]
        if matched_tags:
            matched_tag = matched_tags[0]
            lang_chunk = [chunk for chunk in chunks if matched_tag in chunk][0]
            language = lang_chunk.replace(matched_tag, "")
        else:
            lang_chunk = [chunk for chunk in chunks if re.search("\w{2}:", chunk)]
            if lang_chunk:
                lang_chunk = lang_chunk[0]
                lang = re.findall("\w{2}:", lang_chunk)[0]
                title = lang_chunk.replace(lang, "")
                language = lang[:-1]
        return Source(
            url=f"{language}.wikisource.org/wiki/{title}",
            title=page_title,
        )

    def title_tag_parsing(
        self, tag: str, page_title: str, markers: List[str]
    ) -> Optional[Source]:
        for marker in markers:
            source = self.parse_interproject_link(
                tag, page_title, project_marker=marker
            )
            if source is not None:
                return source
        return self.default_parsing_fun(tag, page_title)

    def get_title(self, tag_chunks):
        # select the correct chunk according to wikisource index matching
        matched_title = [t for t in tag_chunks if t in self.titles]
        title = tag_chunks[0] if not matched_title else matched_title[0]
        return title

    def get_lang_tags(self):
        return {
            "en": ["language="],
            "es": ["idioma="],
            "fr": ["langue="],
            "it": ["lingua="],
            "de": ["sprache="],
        }.get(self.language, []) + ["lang="]

    def get_title_tag(self):
        return {
            "en": "title=",
            "es": "titulo=",
            "fr": "titre=",
            "it": "titolo=",
            "de": "titel=",
        }.get(self.language, "title")


# if __name__ == "__main__":
#     final_urls = []
#     WikisourceParser(languages=["en"], language="en").get_files(
#         final_urls=final_urls,
#         wikisource_title="Fairy_tales_and_stories_(Andersen,_Tegner)",
#         url=Source(
#             title="Fairy_tales_and_stories_(Andersen,_Tegner)",
#             url="en.wikisource.org/wiki/Fairy_tales_and_stories_(Andersen,_Tegner)",
#         ),
#     )
    print()
