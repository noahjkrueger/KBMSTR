import argparse
import eel
import os
import multiprocessing as mp
from math import inf
from sys import argv
from json import load, dump
from random import sample, random, choices, getrandbits, randint
from zipfile import ZipFile
from datetime import datetime
from tqdm import tqdm


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# TODO: allow different finger pos -> .config see line 68
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
    def __init__(self, dataset, valid_chars):
        self.__kb_tools = {}
        self.__finger_duty = None
        self.__cost_matrix = None

        self.__dataset = dataset
        self.__chars = 0
        self.__uncounted = 0
        self.__zips = list()
        self.__filenames = list()
        self.__dataset_names = list()
        self._init_dataset(valid_chars)

        if self.__zips == list():
            raise Exception(f"No .zip files found in directory {self.__dataset}. Please provide the -dataset arg with a"
                            f" directory that contains .zip compressed archives of .txt files.")

    def update_keyboards(self, keyboards):
        self.__kb_tools = {}
        for keyboard in keyboards:
            tool = _KeyboardTool()
            tool.set_layout(keyboard)
            self.__kb_tools[keyboard] = tool

    #TODO: create one gian list() -> can ommit uncounted chars, add some character to indicate eof
    def _init_dataset(self, valid_chars):
        for root, direct, files in os.walk(self.__dataset):
            for file in files:
                if '.zip' in file:
                    self.__zips.append(os.path.join(root, file))
        for zip_path in self.__zips:
            with ZipFile(zip_path, 'r') as zipObj:
                filenamelist = zipObj.namelist()
                print(f"Initializing datasets from {zip_path}")
                with tqdm(total=len(filenamelist)) as pbar:
                    for file in filenamelist:
                        if '.txt' in file:
                            self.__filenames.append(file)
                            with zipObj.open(file) as dataset:
                                while line := dataset.readline():
                                    for char in line.decode()[:-1].lower():
                                        self.__chars += 1
                                        if char not in valid_chars:
                                            self.__uncounted += 1
                        pbar.update(1)
        cls()

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

    def _process_line(self, string, kb):
        for char in string:
            self.__chars += 1
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

    def _analyze_thread(self, tool, out_queue, distance_limit):
        for zip_path in self.__zips:
            with ZipFile(zip_path, 'r') as zipObj:
                filenamelist = zipObj.namelist()
                for file in filenamelist:
                    with zipObj.open(file) as dataset:
                        while line := dataset.readline():
                            self._process_line(line.decode()[:-1].lower(), tool)
                            if tool.accumulated_cost > distance_limit:  # TODO: maybe make better heuristic - check every n chars if doing better or nah (within some ratio)
                                tool.accumulated_cost = inf
                                break
        out_queue.put((tool.layout, tool.accumulated_cost))

    def _listener(self, q):
        pbar = tqdm(total=len(self.__kb_tools))#*len(self.__filenames)) TODO: make this work
        last_size = 0
        while (size := q.qsize()) < len(self.__kb_tools):#*len(self.__filenames):
            pbar.update(size - last_size)
            last_size = size

    def preform_analysis(self, distance_limit):
        print(f"Using distance limit {distance_limit} to speed things up")
        self._init_finger_duty()
        self._init_cost_matrix()
        if not self.__kb_tools:
            raise Exception("no keyboards initialized. use AnalyzeKeyboards.update_keyboards(list)")
        out_queue = mp.Queue()
        proc = mp.Process(target=self._listener, args=(out_queue, ))
        proc.start()
        workers = []
        for kb in self.__kb_tools.keys():
            workers.append(mp.Process(target=self._analyze_thread, args=(self.__kb_tools[kb], out_queue, distance_limit)))
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        proc.join()
        print("Dumping Results")
        for i in tqdm(range(0, len(self.__kb_tools))):
            res = out_queue.get()
            if res[1] == inf:
                self.__kb_tools[res[0]].accumulated_cost = inf
            else:
                self.__kb_tools[res[0]].accumulated_cost = res[1]
        cls()

    def get_results(self):
        keyboards = list()
        total_distances = list()
        efficiencies = list()
        for kb in self.__kb_tools.values():
            layout, total_cost = kb.get_info()
            keyboards.append(layout)
            total_distances.append(total_cost)
            efficiencies.append(total_cost / (self.__chars - self.__uncounted))
        return {
            'keyboards': keyboards,
            'total_distances': total_distances,
            'total_chars': self.__chars,
            'total_uncounted': self.__uncounted,
            'efficiencies': efficiencies,
            'dataset_names': self.__dataset_names,
            'last_analysis': datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        }


class GeneticKeyboards:
    def __init__(self, original, dataset, produce_simple, gen_size,
                 epsilon, steps_to_converge, mutation_rate, save_stats):
        self.__original = original
        self.__produce_simple = produce_simple
        self.__mutate_rate = mutation_rate
        self.__save_stats = save_stats  # TODO
        self.__gen_size = gen_size
        self.__delta = inf
        self.__epsilon = epsilon
        self.__steps_to_converge = steps_to_converge
        self.__num_steps = 0
        self.__gen_number = 0
        self.__current_gen_top_performance = inf
        self.__current_gen = [original]
        self.__current_results = None
        self.__judge = AnalyzeKeyboards(dataset, original)
        for i in range(1, gen_size):
            self.__current_gen.append(''.join(sample(original, len(original))))
        self.__best_keyboard = None
        self._print_status()
        self._calculate_fitness()
        self.__gen_number = 1

    def _print_status(self):
        print(f"-------------------GENERATION {self.__gen_number:>4}\n"
              f"Best Efficiency:{self.__current_gen_top_performance:>18}\n"
              f"Δ:{self.__delta:>32}\n"
              f"ε:{self.__epsilon:>32}\n"
              f"Steps:{self.__num_steps:>26}/{self.__steps_to_converge}\n"
              f"Generation Size: {self.__gen_size:>17}\n"
              f"Mutation Rate:{self.__mutate_rate:>20}\n")

    def generate(self):
        while self.__delta > self.__epsilon or self.__steps_to_converge != self.__num_steps:
            self._print_status()
            new_gen = [self.__best_keyboard]
            weights = list()
            for i in range(0, self.__gen_size):
                if self.__current_results['efficiencies'][i] == inf:
                    weights.append(0)
                else:
                    weights.append((self.__gen_size - i)**2)
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
                   'layout': self.__best_keyboard,
                   'total_distance': self.__current_results['total_distances'][0],
                   'total_chars': self.__current_results['total_chars'],
                   'total_uncounted': self.__current_results['total_uncounted'],
                   'efficiency': self.__current_results['efficiencies'][0],
                   'dataset_names': self.__current_results['dataset_names'],
                   'last_analysis': self.__current_results['last_analysis']
               }, simple

    def _mutate(self, keyboard):
        length = len(keyboard)
        for i in range(0, len(self.__original)):
            if random() <= self.__mutate_rate:
                i1, i2 = randint(0, length - 1), randint(0, length - 1)
                old = keyboard[i1]
                keyboard[i1] = keyboard[i2]
                keyboard[i2] = old
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
        print(F"Calculating fitness...")
        self.__judge.update_keyboards(self.__current_gen)
        try:
            self.__judge.preform_analysis(min(self.__current_results['total_distances']))
        except TypeError:
            self.__judge.preform_analysis(inf)
        self.__current_results = self.__judge.get_results()
        self.__current_gen = [x for _, x in sorted(zip(self.__current_results['efficiencies'],
                                                       self.__current_results['keyboards']), key=lambda pair: pair[0])]
        self.__best_keyboard = self.__current_gen[0]
        top_preform = min(self.__current_results['efficiencies'])
        self.__delta = min(abs(self.__current_gen_top_performance - top_preform), top_preform)
        if self.__delta <= self.__epsilon:
            self.__num_steps += 1
        else:
            self.__num_steps = 0
        self.__current_gen_top_performance = top_preform


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
             "Directories of multiple .zip collections are allowed."
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
        help="Change the rate at which mutations occur. (Default: 0.25) "
    )
    parser.add_argument(
        "-epsilon",
        metavar="EPSILON",
        type=float,
        default=0.005,
        help="Change the threshold of convergence. (Default: 0.005)"
    )
    parser.add_argument(
        "-steps_to_converge",
        metavar="STEPS",
        type=int,
        default=5,
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
    cls()
    args = parser.parse_args(argv)
    with open(args.keyboard, "r") as json_file:
        keyboard = load(json_file)
    if args.display:
        show_keyboards(keyboard)
        exit()
    if not args.dataset:
        raise Exception("A dataset is required for this action.")
    if args.analyze:
        analysis = AnalyzeKeyboards(args.dataset)
        analysis.update_keyboards([keyboard['layout']])
        analysis.preform_analysis(inf)
        results = analysis.get_results()
        keyboard['total_distance'] = results['total_distances'][0]
        keyboard['total_chars'] = results['total_chars']
        keyboard['total_uncounted'] = results['total_uncounted']
        keyboard['efficiency'] = results['efficiencies'][0]
        keyboard['dataset_names'] = results['dataset_names']
        keyboard['last_analysis'] = results['last_analysis']
        with open(args.keyboard, "w") as json_file:
            dump(keyboard, json_file)
        exit()
    generator = GeneticKeyboards(keyboard['layout'], args.dataset, args.simplify, args.gen_size,
                                 args.epsilon, args.steps_to_converge, args.mutation_rate, args.save_stats)
    raw, simplified = generator.generate()
    with open(f"keyboards/{args.name if args.name else raw['last_analysis']}.raw.json", "w") as json_file:
        raw['name'] = f"keyboards/{args.name if args.name else raw['last_analysis']}"
        dump(raw, json_file)
    if simplified:
        with open(f"keyboards/{args.name}.simplified.json", "w") as json_file:
            simplified['name'] = f"keyboards/{args.name if args.name else raw['last_analysis']}"
            dump(simplified, json_file)
    cls()
    print(f"Finished running KBMSTR with args:\n\n\tkeyboard={args.keyboard}\n\tdataset={args.dataset}\n\t"
          f"name={args.name}\n\tsimplify={args.simplify}\n\tgen_size={args.gen_size}\n\t"
          f"mutation_rate={args.mutation_rate}\n\tepsilon={args.epsilon}\n\tsteps_to_converge={args.steps_to_converge}"
          f"\n\tsave_stats={args.save_stats}\n\tanalyze={args.analyze}\n\tdisplay={args.display}\n")


if __name__ == "__main__":
    main(argv[1:])
