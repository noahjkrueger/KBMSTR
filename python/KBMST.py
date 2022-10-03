import argparse
import sys
import json
import eel
import os
from zipfile import ZipFile
from datetime import datetime


def calc_distance(key_a, key_b):
    # finger on key
    if key_a == key_b:
        return 0.0
    # top row transitions TODO
    elif 0 < key_a < 10:
        if key_b < 4:
            return 1.1
        elif 5 < key_a < 10:
            return


def measuere_agianst_dataset(keyboard_layout, dataset):
    dist, words, chars = 0, 0, 0
    return dist, words, chars


def analyze_keyboard(keyboard, datasets):
    zips = []
    for root, direct, files in os.walk(datasets):
        for file in files:
            if '.zip' in file:
                zips.append(os.path.join(root, file))
    total_distance = 0
    total_words = 0
    total_chars = 0
    dataset_names = []
    for zip_path in zips:
        with ZipFile(zip_path, 'r') as zipObj:
            for file in zipObj.namelist():
                if file[-4:] == ".txt":
                    dataset_names.append(f"{zip_path.split('/')[-1]}/{file}")
                    with zipObj.open(file) as dataset:
                        dist, words, chars = measuere_agianst_dataset(keyboard['layout'], dataset)
                        total_distance += dist
                        total_words += words
                        total_chars += chars
    keyboard['total_distance'] = total_distance
    keyboard['total_words'] = total_words
    keyboard['total_chars'] = total_chars
    if total_distance == 0 or total_words == 0 or total_chars == 0:
        keyboard['efficiency'] = 0
    else:
        keyboard['efficiency'] = 2 / ((total_distance / total_words) + (total_distance / total_chars))
    keyboard['dataset_names'] = dataset_names
    keyboard['last_analysis'] = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return keyboard


def load_json_to_html(keyboard):
    eel.read_data(keyboard.split("/")[1])


def show_keyboards(keyboard):
    eel.init('keyboards')
    load_json_to_html(keyboard)
    eel.start('index.html', mode='chrome-app', port=8080, cmdline_args=['--start-fullscreen'])


def main(argv):
    parser = argparse.ArgumentParser(
        prog="python3 KBMST.py",
        description="KBMSTR: Keyboard Master - Find the best keyboard for an input dataset using a genetic algorithm.",
        prefix_chars="-",
        epilog="Generates a 31 key keyboard, see https://github.com/noahjkrueger/Keyboard-Layout for more info."
    )
    parser.add_argument(
        "keyboard",
        type=str,
        help="Name of the keyboard layout to improve upon, stored in /keyboards."
    )
    parser.add_argument(
        "-dataset",
        metavar="DATASET",
        type=str,
        default="",
        help="A single or a collection of (.zip) of datasets (.txt) to be used in the generation. Enter a directory "
             "or a single .zip compressed file. Only .txt files within a .zip file are used to rank the keyboards. "
             "Directories of multiple .zip collections are allowed. "
    )
    parser.add_argument(
        "-result_type",
        choices=['raw', 'simplified', 'both'],
        default='both',
        help="Select the type of result to output.\nraw: the most efficient keyboard in terms of distance for the "
             "dataset\nsimplified: Not as effect as raw, but closer to the keyboard specified in the 'improve'"
             " argument; selecting this will lessen the learning curve to adapt to a new keyboard layout\nboth: create "
             "both\nResults are stored in /keyboards."
    )
    parser.add_argument(
        "-name",
        metavar="NAME",
        type=str,
        default="",
        help="Name the keyboard being generated. (.raw/.simplified) are added with respect to result_type. Default "
             "naming scheme: yyyy/mm/dd:hh:mm:ss.(raw/simplified)"
    )
    parser.add_argument(
        "-gen_size",
        metavar="SIZE",
        type=int,
        default=100,
        help="Chose the number of members for each generation. (Default: 100)"
    )
    parser.add_argument(
        "-epsilon",
        metavar="EPSILON",
        type=float,
        default=0.05,
        help="Change the threshold of convergence. (Default: 0.05)"
    )
    parser.add_argument(
        "-save_stats",
        action="store_true",
        help="Create 2 files in run_stats: a visual plot and a file that reflects that data in the plot."
    )
    parser.add_argument(
        "-analyze",
        action="store_true",
        help="Analyze the efficiency of the inputted keyboard against dataset(s) provided in -dataset and places "
             "results in /keyboards. Ignores all other options."
    )
    parser.add_argument(
        "-display",
        action="store_true",
        help="Create a visual display of the keyboard inputted. Ignores all other options."
    )

    args = parser.parse_args(argv)

    if args.display:
        show_keyboards(args.keyboard)
        exit()

    with open(args.keyboard, "r") as json_file:
        keyboard = json.load(json_file)
    if args.analyze:
        keyboard = analyze_keyboard(keyboard, args.dataset)
    with open(args.keyboard, "w") as json_file:
        json.dump(keyboard, json_file)


if __name__ == "__main__":
    main(sys.argv[1:])
