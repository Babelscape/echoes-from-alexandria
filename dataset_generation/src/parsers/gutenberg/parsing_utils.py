import re

import pandas as pd

from dataset_generation.src.utils.utils import clean_title


def parse_gut_index(index_path: str = "data/gutenberg_indices/pg_catalog.csv"):
    df = pd.read_csv(
        index_path, header=0, usecols=["Text#", "Type", "Language", "Authors"]
    )
    # removes audio files
    df = df[df["Type"] == "Text"]
    df.rename(columns={"Text#": "id"}, inplace=True)
    index = df.set_index("id").to_dict("index")
    id2lan = {str(k): v["Language"] for k, v in index.items()}
    for id, lan in id2lan.items():
        if ";" in lan:
            lan = lan.split(";")[1].strip()
            id2lan[id] = lan
    id2aut = {str(k): v["Authors"] for k, v in index.items()}
    authors_to_discard = {"unknown", "anonymous", "various", "project gutenberg"}
    for separator in [",", "(", ";"]:
        id2aut = {
            k: v.split(separator)[0].strip()
            for k, v in id2aut.items()
            if isinstance(v, str) and v.lower() not in authors_to_discard
        }
    id2title, title2id, id2subtitle = parse_title2id(id2aut)
    return id2lan, id2title, title2id, id2aut, id2subtitle


def parse_title2id(id2aut):
    index_path = "data/gutenberg_indices/GUTINDEX.ALL.txt"
    END_MARKER = "<==End of GUTINDEX.ALL==>"
    with open(index_path) as f:
        index_lines = [l.strip() for l in f.readlines()[252:]]
    end_index = index_lines.index(END_MARKER)
    index_lines = index_lines[:end_index]
    title_lines = [
        line
        for line in index_lines
        if re.search("\d[A-Z]?$", line.strip())
        or re.search("\[[Ss]ubtitle.*", line.strip())
    ]
    id2title = {}
    title2ids = {}
    id2subtitle = {}
    book_id = None
    for line in title_lines:
        id = re.findall("\d+[A-Z]?$", line)
        subtitle = re.findall("\[[Ss]ubtitle.*", line.strip())
        # second conditions is to discard previously discarded elements, e.g. items that are not of type Text
        if len(id) > 0 and id[0] in id2aut:
            book_id = id[0]
            title = line.replace(book_id, "").strip()
            title = clean_title(title)
            if title.lower() == "not used":
                continue
            if " by " in title:
                title = title.split(" by ")[0].strip()
            if re.search("[A-Z]$", book_id):
                book_id = book_id[:-1]
            id2title[book_id] = title
            ids = title2ids.get(title, set())
            ids.add(book_id)
            title2ids[title] = ids
        if subtitle:
            id2subtitle[book_id] = re.sub("\[[Ss]ubtitle *: *", "", subtitle[0]).rstrip(
                "]"
            )

    return id2title, title2ids, id2subtitle

def parse_author_index():
    author_index_path = "data/gutenberg_indices/id2author.tsv"
    import csv
    with open(author_index_path, 'w') as w:
        with open('data/gutenberg_indices/pg_catalog.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count +=1
                    continue
                else:
                    id = row[0]
                    author_surname = row[5].split(",")[0].strip()
                    if author_surname != '':
                        w.write(f'{id}\t{author_surname}\n')
