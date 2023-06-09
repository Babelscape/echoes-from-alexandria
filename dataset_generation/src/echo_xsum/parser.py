import json

from tqdm import tqdm

from dataset_generation.src.utils.constants import ECHO_XSUM_PATH


class EchoXSumParser:
    def __init__(self):
        self.index_path = ECHO_XSUM_PATH

    def parse(self, output_path):
        with open(output_path) as f:
            books = [json.loads(l.strip()) for l in f.readlines()]
        synset2book = {b['synset']: b for b in books}
        with open(self.index_path) as f:
            novel_xsum_books = [json.loads(l.strip()) for l in f.readlines()]
        for b in tqdm(novel_xsum_books, 'merging with Echo-XSum'):
            synset = b['synset']
            if synset.startswith('bn:'):
                proj_alex_book = synset2book.get(synset, {})
                # synset, xsummaries, title
                proj_alex_book['xsummaries'] = b['xsummaries']
                proj_alex_book['synset'] = synset
                proj_alex_book['title'] = proj_alex_book.get('title', {})
                for lan in b['title']:
                    if lan not in proj_alex_book['title']:
                        proj_alex_book['title'][lan] = b['title'][lan]
                synset2book['synset'] = proj_alex_book
        with open(output_path, 'w') as w:
            for _, b in synset2book.items():
                w.write(json.dumps(b) + "\n")