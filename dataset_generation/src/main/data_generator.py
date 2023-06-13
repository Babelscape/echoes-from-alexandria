import json
import os.path
from copy import deepcopy
from typing import List, Optional
from dataset_generation.src.echo_wiki.parser import EchoWikiParser
from dataset_generation.src.echo_xsum.parser import EchoXSumParser
from dataset_generation.src.main.clean_books import clean_books
from dataset_generation.src.main.organize_books import organize_books


def generate_dataset(
    output_path: str,
    languages: List[str],
    debug_title: Optional[str] = None,
    debug_synset: Optional[str] = None,
):
    # parse Echo-Wiki dataset (pairs book texts with Wikipedia summaries)
    EchoWikiParser().parse(
        languages=languages,
        outpath=output_path,
        debug_title=debug_title,
        debug_synset=debug_synset,
    )
    # parses Echo-XSum dataset (results from a manual annotation process)
    EchoXSumParser().parse(output_path)
    # creates files containing book texts
    organize_books(
        output_path,
        debug_title=debug_title,
        debug_synset=debug_synset,
    )
    clean_books(
        output_path
    )
    index_output_path = output_path.replace(".jsonl", "_index.jsonl")
    out_dir = '/'.join(output_path.split('/')[:-1])
    echo_wiki_path = os.path.join(out_dir, 'echo-wiki.jsonl')
    echo_xsum_path = os.path.join(out_dir, 'echo-xsum.jsonl')
    with open(index_output_path) as f:
        books = [json.loads(l.strip()) for l in f.readlines()]
        echo_wiki_books = [b for b in books if 'summaries' in b]
        echo_xsum_books = [b for b in books if 'xsummaries' in b]
    fields_to_delete = ['introduction', 'synset', 'translations', 'xsummaries']
    with open(echo_wiki_path, 'w') as ew:
        for b in deepcopy(echo_wiki_books):
            delete_fields(b, fields_to_delete)
            ew.write(json.dumps(b) + '\n')
    fields_to_delete = ['introduction', 'synset', 'translations', 'summaries', 'sections']
    with open(echo_xsum_path, 'w') as ex:
        for b in deepcopy(echo_xsum_books):
            delete_fields(b, fields_to_delete)
            summaries = b['xsummaries']
            b['summaries'] = summaries
            del b['xsummaries']
            ex.write(json.dumps(b) + '\n')

def delete_fields(b, fields_to_delete):
    for f in fields_to_delete:
        if f in b:
            del b[f]
