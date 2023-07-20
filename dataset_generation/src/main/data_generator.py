import json
import os.path
import random
from copy import deepcopy
from typing import List, Optional
from dataset_generation.src.echo_wiki.parser import EchoWikiParser
from dataset_generation.src.echo_xsum.parser import EchoXSumParser
from dataset_generation.src.main.clean_books import clean_books
from dataset_generation.src.main.organize_books import organize_books
from dataset_generation.src.utils import constants


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
    out_dir = '/'.join(output_path.split('/')[:-1])
    dump_datasets(out_dir, output_path)
    splits = {'train', 'val', 'test'}
    for dataset_name in {'echo-wiki', 'echo-xsum'}:
        with open(os.path.join(out_dir, dataset_name + '.jsonl')) as f:
            dataset = [json.loads(l.strip()) for l in f.readlines()]
        shuffle = not all([os.path.exists(os.path.join(constants.BASE_PATH, split + '-' + dataset_name + '-ids.tsv')) for split in splits])
        if shuffle:
            random_splits(dataset, dataset_name, out_dir)
        else:
            split_as_in_paper(dataset, dataset_name, out_dir, splits)


def split_as_in_paper(dataset, dataset_name, out_dir, splits):
    for split in splits:
        with open(os.path.join(constants.BASE_PATH, split + '-' + dataset_name + '-ids.tsv')) as f:
            split_ids = [l.strip() for l in f.readlines()]
            split_dataset = [s for s in dataset if s['synset'] in split_ids]
            with open(os.path.join(out_dir, f'{split}_' + dataset_name + '.jsonl'), 'w') as w:
                w.write('\n'.join([json.dumps(s) for s in split_dataset]))




def random_splits(dataset, dataset_name, out_dir):
    train_perc, val_perc, test_perc = 0.8, 0.1, 0.1
    random.shuffle(dataset)
    train_len = len(dataset) * train_perc
    val_len = len(dataset) * val_perc
    train_dataset = dataset[:train_len]
    val_dataset = dataset[train_len: train_len + val_len]
    test_dataset = dataset[train_len + val_len:]
    train_ids = set([l['synset'] for l in train_dataset])
    val_ids = set([l['synset'] for l in val_dataset])
    test_ids = set([l['synset'] for l in test_dataset])
    assert len(train_ids.intersection(val_ids)) == 0
    assert len(train_ids.intersection(test_ids)) == 0
    assert len(val_ids.intersection(test_ids)) == 0
    with open(os.path.join(out_dir, 'train_' + dataset_name + '.jsonl'), 'w') as w:
        w.write('\n'.join([json.dumps(s) for s in train_dataset]))
    with open(os.path.join(out_dir, 'validation_' + dataset_name + '.jsonl'), 'w') as w:
        w.write('\n'.join([json.dumps(s) for s in val_dataset]))
    with open(os.path.join(out_dir, 'test_' + dataset_name + '.jsonl'), 'w') as w:
        w.write('\n'.join([json.dumps(s) for s in test_dataset]))


def dump_datasets(out_dir, output_path):
    index_output_path = output_path.replace(".jsonl", "_index.jsonl")
    echo_wiki_path = os.path.join(out_dir, 'echo-wiki.jsonl')
    echo_xsum_path = os.path.join(out_dir, 'echo-xsum.jsonl')
    with open(index_output_path) as f:
        books = [json.loads(l.strip()) for l in f.readlines()]
        echo_wiki_books = [b for b in books if 'summaries' in b]
        echo_xsum_books = [b for b in books if 'xsummaries' in b]
    fields_to_delete = ['introduction', 'translations', 'xsummaries']
    with open(echo_wiki_path, 'w') as ew:
        for b in deepcopy(echo_wiki_books):
            delete_fields(b, fields_to_delete)
            ew.write(json.dumps(b) + '\n')
    fields_to_delete = ['introduction', 'translations', 'summaries', 'sections']
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
