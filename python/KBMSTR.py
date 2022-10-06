import argparse
import eel
import os

from math import inf
from sys import argv
from json import load, dump
from random import sample, random, choice, getrandbits, randint
from zipfile import ZipFile
from datetime import datetime


class _KeyboardTool:
    def __init__(self):
        self.layout = None
        self.mapping = None
        self.finger_pos = None
        self.accumulated_cost = 0

    def get_info(self):
        return self.layout, self.accumulated_cost

    def set_layout(self, layout):
        self.layout = layout
        self._init_mapping(layout)
        self._init_finger_pos()

    def _init_finger_pos(self):
        self.finger_pos = {"l_p": 10, "l_r": 11, "l_m": 12, "l_i": 13, "r_i": 16, "r_m": 17, "r_r": 18, "r_p": 19}

    def _init_mapping(self, layout):
        i = 0
        mapping = {}
        for char in layout:
            mapping[char] = i
            i += 1
        self.mapping = mapping


class AnalyzeKeyboards:
    def __init__(self):
        self.__kb_tools = list()
        self.__chars = 0
        self.__uncounted = 0
        self.__dataset_names = list()
        self.__finger_duty = None
        self.__cost_matrix = None
        self.__dataset = None

    def init(self, keyboards, dataset):
        self.__chars = 0
        self.__uncounted = 0
        self.__dataset = dataset
        self.update_keyboards(keyboards)

    def update_keyboards(self, keyboards):
        self.__kb_tools = list()
        for keyboard in keyboards:
            tool = _KeyboardTool()
            tool.set_layout(keyboard)
            self.__kb_tools.append(tool)

    def _init_finger_duty(self):
        finger_duty = dict.fromkeys([0, 10, 21], "l_p")
        finger_duty.update(dict.fromkeys([1, 11, 22], "l_r"))
        finger_duty.update(dict.fromkeys([2, 12, 23], "l_m"))
        finger_duty.update(dict.fromkeys([3, 4, 13, 14, 24, 25], "l_i"))
        finger_duty.update(dict.fromkeys([5, 6, 15, 16, 26, 27], "r_i"))
        finger_duty.update(dict.fromkeys([7, 17, 28], "r_m"))
        finger_duty.update(dict.fromkeys([8, 18, 29], "r_r"))
        finger_duty.update(dict.fromkeys([9, 19, 20, 30], "r_p"))
        self.__finger_duty = finger_duty

    def _init_cost_matrix(self):
        a, b, c, d, e, f, g = 1.0, 1.031, 2.062, 2.016, 1.118, 1.6, 2.5
        cost = dict.fromkeys([(3, 4), (13, 14), (24, 25), (5, 6), (15, 16), (26, 27), (19, 20)], a)
        cost.update(dict.fromkeys([(0, 10), (1, 11), (2, 12), (3, 13), (4, 14), (5, 15), (6, 16),
                                   (7, 17), (8, 18), (9, 19), (10, 21), (11, 22), (12, 23), (13, 24),
                                   (14, 25), (15, 26), (16, 27), (17, 28), (18, 29), (19, 30)], b))
        cost.update(dict.fromkeys([(0, 21), (1, 22), (2, 23), (3, 24), (4, 25), (5, 26), (6, 27),
                                   (7, 28), (8, 29), (9, 30)], c))
        cost.update(dict.fromkeys([(4, 24), (6, 26)], d))
        cost.update(dict.fromkeys([(4, 13), (6, 15), (14, 24), (16, 26), (20, 30)], e))
        cost.update(dict.fromkeys([(3, 14), (13, 25), (5, 16), (15, 27), (9, 20)], f))
        cost.update(dict.fromkeys([(3, 25), (5, 27)], g))
        self.__cost_matrix = cost

    def _process_line(self, string):
        for char in string:
            self.__chars += 1
            for kb in self.__kb_tools:
                try:
                    destination = kb.mapping[char]
                except KeyError:
                    self.__uncounted += 1
                    continue
                responsible_finger = self.__finger_duty[destination]
                transition = (kb.finger_pos[responsible_finger], destination)
                if transition[0] == transition[1]:
                    continue
                kb.finger_pos[responsible_finger] = destination
                try:
                    kb.accumulated_cost += self.__cost_matrix[transition]
                except KeyError:
                    kb.accumulated_cost += self.__cost_matrix[(transition[1], transition[0])]

    # TODO: remove need for os.walk every time: move to init
    def preform_analysis(self, store_dataset_names=True):
        self._init_finger_duty()
        self._init_cost_matrix()
        if not self.__kb_tools:
            raise Exception("no keyboards initialized. use AnalyzeKeyboards.init_keyboards(list)")
        zips = []
        for root, direct, files in os.walk(self.__dataset):
            for file in files:
                if '.zip' in file:
                    zips.append(os.path.join(root, file))
        for zip_path in zips:
            with ZipFile(zip_path, 'r') as zipObj:
                for file in zipObj.namelist():
                    if '.txt' in file:
                        if store_dataset_names:
                            self.__dataset_names.append(f"{zip_path.split('/')[-1]}/{file}")
                        with zipObj.open(file) as dataset:
                            while line := dataset.readline():
                                self._process_line(line.decode()[:-1].lower())

    def get_results(self):
        keyboards = {}
        efficiencies = {}
        for kb in self.__kb_tools:
            layout, total_cost = kb.get_info()
            keyboards[layout] = total_cost
            efficiencies[layout] = total_cost / (self.__chars - self.__uncounted)
        return {
            'keyboards': keyboards,
            'total_chars': self.__chars,
            'total_uncounted': self.__uncounted,
            'efficiencies': efficiencies,
            'dataset_names': self.__dataset_names,
            'last_analysis': datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        }


def generate_keyboards(simplify, original, dataset, gen_size, epsilon, save_stats):
    parents = [original['layout']]
    for i in range(1, gen_size):
        parents.append(''.join(sample(original['layout'], len(original['layout']))))
    judge = AnalyzeKeyboards()
    judge.init(parents, dataset)
    judge.preform_analysis()
    results = judge.get_results()
    parents = [x for _, x in sorted(zip(results['efficiencies'], results['keyboards']), key=lambda pair: pair[0])]
    last_top_preform = results['efficiencies'][parents[0]]
    delta = inf
    og_len = len(original['layout'])
    while delta > epsilon:
        current_gen = []
        while len(current_gen) < gen_size:
            parent1 = choice(list(parents))
            parent2 = choice(list(parents))
            index_1, index_2 = 0, 0
            used = set()
            child_layout = []
            while len(used) < og_len:
                if index_2 == og_len or (bool(getrandbits(1)) and index_1 < og_len):
                    if parent1[index_1] not in used:
                        child_layout.append(parent1[index_1])
                        used.add(parent1[index_1])
                    index_1 += 1
                elif index_2 < og_len:
                    if parent2[index_2] not in used:
                        child_layout.append(parent2[index_2])
                        used.add(parent2[index_2])
                    index_2 += 1
            mutate = True
            while mutate:
                i1, i2 = randint(0, og_len - 1), randint(0, og_len - 1)
                old = child_layout[i1]
                child_layout[i1] = child_layout[i2]
                child_layout[i2] = old
                mutate = bool(getrandbits(1))
            current_gen.append(''.join(child_layout))
        judge.update_keyboards(current_gen)
        judge.preform_analysis(store_dataset_names=False)
        results = judge.get_results()
        parents = [p for _, p in sorted(zip(results['efficiencies'].values(), results['keyboards'].keys()))]
        print(results['efficiencies'][parents[0]], results['efficiencies'][parents[1]])
        top_preform = results['efficiencies'][parents[0]]
        delta = abs(last_top_preform - top_preform)
        last_top_preform = top_preform
    return {
        'layout': parents[0],
        'total_distance': results['keyboards'][parents[0]],
        'total_chars': results['total_chars'],
        'total_uncounted': results['total_uncounted'],
        'efficiency': results['efficiencies'][parents[0]],
        'dataset_names': results['dataset_names'],
        'last_analysis': results['last_analysis']
    }, None


def show_keyboards(keyboard):
    eel.init('display')

    def load_json_to_html(name, layout, last_analysis, efficiency, datasets):
        eel.read_data(name, layout, last_analysis, efficiency, datasets)

    load_json_to_html(keyboard['name'], keyboard['layout'], keyboard['last_analysis'], keyboard['efficiency'],
                      keyboard['dataset_names'])
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
        "-name",
        metavar="NAME",
        type=str,
        default="",
        help="Name the keyboard being generated. (.raw/.simplified) are added with respect to result_type. Default "
             "naming scheme: yyyy/mm/dd:hh:mm:ss.(raw/simplified)"
    )
    parser.add_argument(
        "-simplify",
        action='store_true',
        help="Include a simplified version of the generated keyboard- more closely resembles the inputted keyboard. ("
             "less efficiency metric, lower learning curver) "
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
        default=0.005,
        help="Change the threshold of convergence. (Default: 0.005)"
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
        keyboard = load(json_file)
    if args.display:
        show_keyboards(keyboard)
        exit()
    if not args.dataset:
        raise Exception("A dataset is required for this action.")
    if args.analyze:
        analysis = AnalyzeKeyboards()
        analysis.init([keyboard['layout']], args.dataset)
        analysis.preform_analysis()
        results = analysis.get_results()
        keyboard['total_distance'] = results['keyboards'][keyboard['layout']]
        keyboard['total_chars'] = results['total_chars']
        keyboard['total_uncounted'] = results['total_uncounted']
        keyboard['efficiency'] = results['efficiencies'][keyboard['layout']]
        keyboard['dataset_names'] = results['dataset_names']
        keyboard['last_analysis'] = results['last_analysis']
        with open(args.keyboard, "w") as json_file:
            dump(keyboard, json_file)
        exit()
    raw, simplified = generate_keyboards(args.simplify, keyboard, args.dataset, args.gen_size, args.epsilon,
                                         args.save_stats)
    with open(f"keyboards/{args.name if args.name else raw['last_analysis']}.raw.json", "w") as json_file:
        raw['name'] = f"keyboards/{args.name if args.name else raw['last_analysis']}"
        dump(raw, json_file)
    if simplified:
        with open(f"keyboards/{args.name}.simplified.json", "w") as json_file:
            simplified['name'] = f"keyboards/{args.name if args.name else raw['last_analysis']}"
            dump(simplified, json_file)


if __name__ == "__main__":
    main(argv[1:])
