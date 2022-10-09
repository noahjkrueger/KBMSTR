import argparse
import eel
import os

from math import inf
from sys import argv
from json import load, dump
from random import sample, random, choices, getrandbits, randint
from zipfile import ZipFile
from datetime import datetime


# TODO: allow different finger pos
class _KeyboardTool:
    def __init__(self):
        self.layout = None
        self.mapping = {}
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
        for char in layout:
            self.mapping[char] = i
            i += 1


# TODO: allow for other mappings and distances. etc. probably with config file (command line arg?).
class AnalyzeKeyboards:
    def __init__(self, dataset):
        self.__chars = 0
        self.__uncounted = 0

        self.__kb_tools = list()
        self.__finger_duty = None
        self.__cost_matrix = None

        self.__dataset = dataset
        self.__zips = list()
        self.__dataset_names = list()
        self._init_zip_list()
        if self.__zips == list():
            raise Exception(f"No .zip files found in directory {self.__dataset}. Please provide the -dataset arg with a"
                            f" directory that contains .zip compressed archives of .txt files.")
        self.__store_dataset_names = True

    def update_keyboards(self, keyboards):
        self.__kb_tools = list()
        for keyboard in keyboards:
            tool = _KeyboardTool()
            tool.set_layout(keyboard)
            self.__kb_tools.append(tool)

    def _init_zip_list(self):
        for root, direct, files in os.walk(self.__dataset):
            for file in files:
                if '.zip' in file:
                    self.__zips.append(os.path.join(root, file))

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

    # TODO: find better way to get char and uncounted ONCE
    def _process_line(self, string):
        for char in string:
            if self.__store_dataset_names:
                self.__chars += 1
            for kb in self.__kb_tools:
                try:
                    destination = kb.mapping[char]
                except KeyError:
                    if self.__store_dataset_names:
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

    def preform_analysis(self):
        self._init_finger_duty()
        self._init_cost_matrix()
        if not self.__kb_tools:
            raise Exception("no keyboards initialized. use AnalyzeKeyboards.update_keyboards(list)")
        for zip_path in self.__zips:
            with ZipFile(zip_path, 'r') as zipObj:
                for file in zipObj.namelist():
                    if '.txt' in file:
                        if self.__store_dataset_names:
                            self.__dataset_names.append(f"{zip_path.split('/')[-1]}/{file}")
                        with zipObj.open(file) as dataset:
                            while line := dataset.readline():
                                self._process_line(line.decode()[:-1].lower())
        if self.__store_dataset_names:
            self.__uncounted = int(self.__uncounted / len(self.__kb_tools))
            self.__store_dataset_names = False

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


# TODO: make is so while a keyboard is being analyzed if the distance is greater than previous best, stop -> save a
#  bunch of time this will require some other things to be done. mostly index stuff. and changing parameters. maybe
#  put process line (above in analyize and do one at time. change bias weights. anything to reduce time analyzing.
class GeneticKeyboards:
    def __init__(self, original, dataset, produce_simple, gen_size, epsilon, mutation_rate, save_stats):
        self.__original = original
        self.__produce_simple = produce_simple
        self.__mutate_rate = mutation_rate
        self.__save_stats = save_stats  # TODO
        self.__gen_size = gen_size
        self.__delta = inf
        self.__epsilon = epsilon
        self.__gen_number = 0
        self.__current_gen_top_performance = 0
        self.__current_gen = [original]
        self.__current_results = None
        for i in range(1, gen_size):
            self.__current_gen.append(''.join(sample(original, len(original))))
        self.__judge = AnalyzeKeyboards(dataset)
        self._calculate_fitness()
        self.__gen_number = 1

    def generate(self):
        while self.__delta > self.__epsilon:
            new_gen = list()
            length = len(self.__original)
            weights = [length - i for i in range(0, self.__gen_size)]
            while len(new_gen) < self.__gen_size:
                parent_a, parent_b = choices(self.__current_gen, weights, k=2)
                new_gen.append(self._crossover(parent_a, parent_b))
            self.__current_gen = new_gen
            self._calculate_fitness()
            self.__gen_number += 1
        simple = None
        if self.__produce_simple:
            pass  # TODO: produce a simplified version of the best one. probably another method.
        return {
                   'layout': self.__current_gen[0],
                   'total_distance': self.__current_results['keyboards'][self.__current_gen[0]],
                   'total_chars': self.__current_results['total_chars'],
                   'total_uncounted': self.__current_results['total_uncounted'],
                   'efficiency': self.__current_results['efficiencies'][self.__current_gen[0]],
                   'dataset_names': self.__current_results['dataset_names'],
                   'last_analysis': self.__current_results['last_analysis']
               }, simple

    def _mutate(self, keyboard):
        length = len(keyboard)
        mutation = True
        while mutation:
            i1, i2 = randint(0, length - 1), randint(0, length - 1)
            old = keyboard[i1]
            keyboard[i1] = keyboard[i2]
            keyboard[i2] = old
            mutation = random() <= self.__mutate_rate
        return keyboard

    def _crossover(self, parent_a, parent_b):
        index_a, index_b = 0, 0
        used = set()
        child = []
        length = len(self.__original)
        while len(used) < length:
            if index_b == len or (bool(getrandbits(1)) and index_a < length):
                if parent_a[index_a] not in used:
                    child.append(parent_a[index_a])
                    used.add(parent_a[index_a])
                index_a += 1
            elif index_b < length:
                if parent_b[index_b] not in used:
                    child.append(parent_b[index_b])
                    used.add(parent_b[index_b])
                index_b += 1
        return "".join(self._mutate(child))

    def _calculate_fitness(self):
        print(F"Calculating fitness for generation {self.__gen_number}")
        self.__judge.update_keyboards(self.__current_gen)
        self.__judge.preform_analysis()
        self.__current_results = self.__judge.get_results()
        self.__current_gen = [x for _, x in sorted(zip(self.__current_results['efficiencies'],
                                                       self.__current_results['keyboards']), key=lambda pair: pair[0])]
        top_preform = self.__current_results['efficiencies'][self.__current_gen[0]]
        self.__delta = abs(self.__current_gen_top_performance - top_preform)
        self.__current_gen_top_performance = top_preform
        print(f"Top preform efficiency: {self.__current_gen_top_performance} delta {self.__delta}")


def show_keyboards(keyboard):
    eel.init('display')

    def load_json_to_html(name, layout, last_analysis, efficiency, datasets):
        eel.read_data(name, layout, last_analysis, efficiency, datasets)

    load_json_to_html(keyboard['name'].split("/")[-1], keyboard['layout'], keyboard['last_analysis'],
                      keyboard['efficiency'],
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
        "-mutation_rate",
        metavar="RATE",
        type=float,
        default=0.25,
        help="Change the rate at which mutations occur. Each child will always mutate at least once, even if set to "
             "0.0 to preserve diversity and avoid early convergence. (Default: 0.25) "
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
        analysis = AnalyzeKeyboards([keyboard['layout']], args.dataset)
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
    generator = GeneticKeyboards(keyboard['layout'], args.dataset, args.simplify, args.gen_size,
                                 args.epsilon, args.mutation_rate, args.save_stats)
    raw, simplified = generator.generate()
    with open(f"keyboards/{args.name if args.name else raw['last_analysis']}.raw.json", "w") as json_file:
        raw['name'] = f"keyboards/{args.name if args.name else raw['last_analysis']}"
        dump(raw, json_file)
    if simplified:
        with open(f"keyboards/{args.name}.simplified.json", "w") as json_file:
            simplified['name'] = f"keyboards/{args.name if args.name else raw['last_analysis']}"
            dump(simplified, json_file)


if __name__ == "__main__":
    main(argv[1:])
