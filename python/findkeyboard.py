import argparse
import sys
import time


def analyze_keyboard(keyboard, datasets):
    pass


def show_keyboard(keyboard):
    pass


def main(argv):
    parser = argparse.ArgumentParser(
        prog="python3 findkeyboard.py",
        description="Find the best keyboard for an input dataset using a genetic algorithm.",
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
        help="A single or a collection (directory) of datasets to be used in the generation."
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
             "naming scheme: mm/dd/yyy:hh:mm:ss.(raw/simplified)"
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
        help="Analyze the efficiency of the inputted keyboard against dataset and places results in /keyboards. "
             "Ignores all other options."
    )
    parser.add_argument(
        "-display",
        action="store_true",
        help="Create a visual display of the keyboard inputted. Ignores all other options."
    )

    args = parser.parse_args(argv)

    if args.analyze:
        analyze_keyboard(args.keyboard, args.dataset)
    elif args.display:
        show_keyboard(args.keyboard)


if __name__ == "__main__":
    main(sys.argv[1:])