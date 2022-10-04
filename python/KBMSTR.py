import argparse
import sys
import json
import eel
import os
from zipfile import ZipFile
from datetime import datetime


def measure_vs_dataset(keyboard_mapping, finger_duty, cost, dataset):
    dist, chars, uncounted = 0, 0, 0
    finger_pos = {"l_p": 10, "l_r": 11, "l_m": 12, "l_i": 13, "r_i": 16, "r_m": 17, "r_r": 18, "r_p": 19}
    while line := dataset.readline():
        # TODO: make better>
        tokens = line.decode()[:-1].lower().split(" ")
        for token in tokens:
            for char in token:
                if char in keyboard_mapping.keys():
                    chars += 1
                    trans_dest = keyboard_mapping[char]
                    duty = finger_duty[trans_dest]
                    transition = finger_pos[duty], trans_dest
                    transition_i = trans_dest, finger_pos[duty]
                    if transition[0] == transition_i[0]:
                        pass
                    elif transition in cost.keys():
                        dist += cost[transition]
                    else:
                        dist += cost[transition_i]
                    finger_pos[duty] = trans_dest
                else:
                    uncounted += 1
    return dist, chars, uncounted


def get_keyboard_maps(keyboard_layout):
    i = 0
    keyboard_mapping = {}
    for char in keyboard_layout:
        keyboard_mapping[char] = i
        i += 1

    # TODO: check these
    finger_duty = dict.fromkeys([0, 10], "l_p")
    finger_duty.update(dict.fromkeys([1, 11, 21], "l_r"))
    finger_duty.update(dict.fromkeys([2, 12, 22], "l_m"))
    finger_duty.update(dict.fromkeys([3, 13, 23, 4, 14, 24, 25], "l_i"))
    finger_duty.update(dict.fromkeys([5, 6, 15, 16, 26, 27], "r_i"))
    finger_duty.update(dict.fromkeys([7, 17, 28], "r_m"))
    finger_duty.update(dict.fromkeys([8, 18, 29], "r_r"))
    finger_duty.update(dict.fromkeys([9, 19, 20, 30], "r_p"))

    # TODO: check these
    a, b, c, d, e, f, g, h, i, r = 1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 2.3, 2.5, 2.75, 0.0
    cost = dict.fromkeys([(3, 4), (23, 24), (24, 25), (5, 6), (26, 27), (19, 20)], a)
    cost.update(dict.fromkeys([(0, 10), (1, 11), (2, 12), (3, 13), (4, 14), (6, 16), (7, 17), (8, 18), (9, 19)], b))
    cost.update(dict.fromkeys([(11, 21), (12, 22), (13, 23), (13, 24), (15, 26), (16, 26), (16, 27),
                                (17, 28), (18, 29), (19, 30), (20, 30)], c))
    cost.update(dict.fromkeys([(4, 13)], d))
    cost.update(dict.fromkeys([(13, 25), (9, 20), (3, 14)], e))
    cost.update(dict.fromkeys([(1, 21), (2, 22), (3, 23), (4, 24), (6, 26)], f))
    cost.update(dict.fromkeys([(3, 24), (4, 25), (5, 26), (6, 27), (9, 30)], g))
    cost.update(dict.fromkeys([(4, 23), (5, 27)], h))
    cost.update(dict.fromkeys([(3, 25)], h))
    return keyboard_mapping, finger_duty, cost


def analyze_keyboard(keyboard, datasets):
    zips = []
    for root, direct, files in os.walk(datasets):
        for file in files:
            if '.zip' in file:
                zips.append(os.path.join(root, file))
    total_distance, total_chars, total_uncounted, dataset_names = 0, 0, 0, []
    keyboard_mapping, finger_duty, cost = get_keyboard_maps(keyboard['layout'])
    for zip_path in zips:
        with ZipFile(zip_path, 'r') as zipObj:
            for file in zipObj.namelist():
                if '.txt' in file:
                    dataset_names.append(f"{zip_path.split('/')[-1]}/{file}")
                    with zipObj.open(file) as dataset:
                        dist, chars, uncounted = measure_vs_dataset(keyboard_mapping, finger_duty, cost, dataset)
                        total_distance += dist
                        total_chars += chars
                        total_uncounted += uncounted
    keyboard['total_distance'] = total_distance
    keyboard['total_chars'] = total_chars
    keyboard['total_uncounted'] = total_uncounted
    keyboard['efficiency'] = total_chars / total_distance
    keyboard['dataset_names'] = dataset_names
    keyboard['last_analysis'] = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return keyboard


def show_keyboards(keyboard):
    eel.init('display')

    def load_json_to_html(name, layout, last_analysis, efficiency, datasets):
        eel.read_data(name, layout, last_analysis, efficiency, datasets)
    load_json_to_html(keyboard['name'], keyboard['layout'], keyboard['last_analysis'], keyboard['efficiency'], keyboard['dataset_names'])
    eel.start('index.html', size=(1000, 700))


def main(argv):
    parser = argparse.ArgumentParser(
        prog="python3 KBMSTR.py",
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
    with open(args.keyboard, "r") as json_file:
        keyboard = json.load(json_file)
    if args.display:
        show_keyboards(keyboard)
        exit()
    if args.analyze:
        keyboard = analyze_keyboard(keyboard, args.dataset)
    else:
        pass # TODO
        # generate_keyboard(keyboard, )
    with open(args.keyboard, "w") as json_file:
        json.dump(keyboard, json_file)


if __name__ == "__main__":
    main(sys.argv[1:])
