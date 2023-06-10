import os
import shutil
import argparse


def main():
    read_path, write_path = get_args()
    flatten(read_path, write_path)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read_path", type=str)
    parser.add_argument("-w", "--write_path", type=str)
    args = parser.parse_args()
    read_path = args.read_path
    write_path = args.write_path
    return read_path, write_path


def flatten(read_path, write_path):
    all_files = []
    for path, subdirs, files in os.walk(read_path):
        for name in files:
            all_files.append(os.path.join(path, name))
    for filename in all_files:
        print(f"copy {filename} to {write_path}")
        shutil.copy(filename, write_path)


if __name__ == "__main__":
    main()
