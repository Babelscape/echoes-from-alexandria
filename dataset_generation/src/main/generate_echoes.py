from dataset_generation.src.download_dumps.download import download
from dataset_generation.src.main.data_generator import generate_dataset

if __name__ == "__main__":
    languages = ["en", "de", "es", "fr", "it"]
    output_path = "echoes_from_alexandria/echoes.jsonl"
    download(languages)
    generate_dataset(output_path, languages)
