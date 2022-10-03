import argparse
import sys
import json
import eel
import os
from zipfile import ZipFile
from datetime import datetime


def calc_distance(key_a, key_b):
    transition = key_a, key_b
    transition_i = key_b, key_a
    a, b, c, d, e, f, g, h, i, r = 1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 2.3, 2.5, 2.75, 0.0
    if key_a == key_b:
        return r
    a_trans = {(3, 4), (23, 24), (24, 25), (5, 6), (26, 27), (19, 20)}
    if transition in a_trans or transition_i in a_trans:
        return a
    b_trans = {(0, 10), (1, 11), (2, 12), (3, 13), (4, 14), (6, 16), (7, 17), (8, 18), (9, 19)}
    if transition in b_trans or transition_i in b_trans:
        return b
    c_trans = {(11, 21), (12, 22), (13, 23), (13, 24), (15, 26), (16, 26), (16, 27),
               (17, 28), (18, 29), (19, 30), (20, 30)}
    if transition in c_trans or transition_i in c_trans:
        return c
    if transition == (4, 13) or transition_i == (4, 13):
        return d
    e_trans = {(13, 25), (9, 20), (3, 14)}
    if transition in e_trans or transition_i in e_trans:
        return e
    f_trans = {(1, 21), (2, 22), (3, 23), (4, 24), (6, 26)}
    if transition in f_trans or transition_i in f_trans:
        return f
    g_trans = {(3, 24), (4, 25), (5, 26), (6, 27), (9, 30)}
    if transition in g_trans or transition_i in g_trans:
        return g
    h_trans = {(4, 23), (5, 27)}
    if transition in h_trans or transition_i in h_trans:
        return h
    if transition == (3, 25) or transition_i == (2, 25):
        return i
    return -1


def measure_vs_dataset(keyboard_mapping, dataset):
    dist, words, chars, uncounted = 0, 0, 0, 0
    finger_pos = {"l_p": 10, "l_r": 11, "l_m": 12, "l_i": 13, "r_p": 16, "r_r": 17, "r_m": 18, "r_i": 19}
    while line := dataset.readline():
        tokens = line.decode()[:-1].lower().split(" ")
        words += len(tokens)
        for token in tokens:
            for char in token:
                chars += 1
                if char in keyboard_mapping.keys():
                    trans_dest = keyboard_mapping[char]
                    for finger in finger_pos:
                        if result := calc_distance(finger_pos[finger], trans_dest) != -1:
                            dist += result
                            finger_pos[finger] = trans_dest
                            break
                else:
                    uncounted += 1
    return dist, words, chars, uncounted


def get_keyboard_map(keyboard_layout):
    i = 0
    keyboard_mapping = {}
    for char in keyboard_layout:
        keyboard_mapping[char] = i
        i += 1
    return keyboard_mapping


def analyze_keyboard(keyboard, datasets):
    zips = []
    for root, direct, files in os.walk(datasets):
        for file in files:
            if '.zip' in file:
                zips.append(os.path.join(root, file))
    total_distance, total_words, total_chars, total_uncounted, dataset_names = 0, 0, 0, 0, []
    for zip_path in zips:
        with ZipFile(zip_path, 'r') as zipObj:
            for file in zipObj.namelist():
                if '.txt' in file:
                    dataset_names.append(f"{zip_path.split('/')[-1]}/{file}")
                    with zipObj.open(file) as dataset:
                        dist, words, chars, uncounted = measure_vs_dataset(get_keyboard_map(keyboard['layout']),
                                                                           dataset)
                        total_distance += dist
                        total_words += words
                        total_chars += chars
                        total_uncounted += uncounted
    keyboard['total_distance'] = total_distance
    keyboard['total_words'] = total_words
    keyboard['total_chars'] = total_chars
    keyboard['total_uncounted'] = total_uncounted
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
