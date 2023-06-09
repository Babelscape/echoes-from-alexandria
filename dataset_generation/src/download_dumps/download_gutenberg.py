import os
import subprocess


def download_gutenberg(output_path: str):
    script_path = "src/scripts/download_gutenberg.sh"
    if not os.path.exists(output_path):
        cmd = ["bash", script_path, output_path]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for line in p.stdout:
            print(line)
        p.wait()
        # # files are renamed to follow a unified standard
        rename_files(output_path)


def rename_files(output_path):
    files = os.listdir(output_path)
    for file in files:
        old_filepath = os.path.join(output_path, file)
        new_filename = None
        if "-" in file:
            new_filename = f'{file.split("-")[0]}.txt'
        elif "pg" in file:
            new_filename = f'{file.split(".")[0].replace("pg", "")}.txt'
        if new_filename is not None:
            new_filepath = os.path.join(output_path, new_filename)
            os.rename(old_filepath, new_filepath)
