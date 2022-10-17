import argparse
import eel
import os
import multiprocessing as mp
import matplotlib.pyplot as plot

from math import inf
from sys import argv
from json import load, dump
from random import sample, random, choices, getrandbits, randint
from zipfile import ZipFile
from datetime import datetime

import matplotlib.pyplot as plt
from tqdm import tqdm


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


class _KeyboardTool:
    def __init__(self, og_finger_pos):
        self.layout = None
        self.mapping = {}
        self.__og_finger_pos = og_finger_pos
        self.finger_pos = og_finger_pos
        self.accumulated_cost = 0

    def get_info(self):
        return self.layout, self.accumulated_cost

    def set_layout(self, layout):
        self.layout = layout
        i = 0
        for char in layout:
            self.mapping[char] = i
            i += 1

    def reset_finger_pos(self):
        self.finger_pos = self.__og_finger_pos


class AnalyzeKeyboards:
    def __init__(self, dataset, valid_chars, config):
        self.__kb_tools = {}
        self.__finger_duty = None
        self.__cost_matrix = None
        self.__og_finger_pos = None

        self.__dataset = dataset
        self.__chars = 0
        self.__uncounted = 0
        self.__zips = list()
        self.__filenames = list()
        self.__dataset_names = list()
        self.__dataset_chars = list()
        self._init_config(config)
        self._init_dataset(valid_chars)

        if self.__zips == list():
            raise Exception(f"No .zip files found in directory {self.__dataset}. Please provide the -dataset arg with a"
                            f" directory that contains .zip compressed archives of .txt files.")

    def update_keyboards(self, keyboards):
        self.__kb_tools = {}
        for keyboard in keyboards:
            tool = _KeyboardTool(self.__og_finger_pos)
            tool.set_layout(keyboard)
            self.__kb_tools[keyboard] = tool

    def _init_config(self, config):
        with open(config, 'r') as cfg:
            dic = eval(cfg.read())
            self.__finger_duty = eval(dic['finger_duty'])
            self.__cost_matrix = eval(dic['cost_matrix'])
            self.__og_finger_pos = eval(dic['finger_pos'])

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
                                        else:
                                            self.__dataset_chars.append(char)
                            self.__dataset_chars.append(None)
                        pbar.update(1)
        cls()

    # TODO: add char checkpoints -> create for each, save best -> distance_limits, nchars
    def _analyze_thread(self, tool, out_queue, distance_limit):
        for char in self.__dataset_chars:
            try:
                destination = tool.mapping[char]
            except KeyError:
                tool.reset_finger_pos()
                continue
            responsible_finger = self.__finger_duty[destination]
            transition = (tool.finger_pos[responsible_finger], destination)
            if transition[0] == transition[1]:
                continue
            tool.finger_pos[responsible_finger] = destination
            try:
                tool.accumulated_cost += self.__cost_matrix[transition]
            except KeyError:
                tool.accumulated_cost += self.__cost_matrix[(transition[1], transition[0])]
            if tool.accumulated_cost > distance_limit:
                tool.accumulated_cost = inf
                break
        out_queue.put((tool.layout, tool.accumulated_cost))

    def _listener(self, q):
        pbar = tqdm(total=len(self.__kb_tools))
        last_size = 0
        while (size := q.qsize()) < len(self.__kb_tools):
            pbar.update(size - last_size)
            last_size = size

    def preform_analysis(self, distance_limit):
        print(f"Using distance limit {distance_limit} to speed things up")
        if not self.__kb_tools:
            raise Exception("no keyboards initialized. use AnalyzeKeyboards.update_keyboards(list)")
        out_queue = mp.Queue()
        proc = mp.Process(target=self._listener, args=(out_queue,))
        proc.start()
        workers = []
        for kb in self.__kb_tools.keys():
            workers.append(
                mp.Process(target=self._analyze_thread, args=(self.__kb_tools[kb], out_queue, distance_limit)))
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
    def __init__(self, original, dataset, config, produce_simple, gen_size,
                 epsilon, steps_to_converge, mutation_rate, save_stats):
        self.__original = original
        self.__produce_simple = produce_simple
        self.__mutate_rate = mutation_rate
        self.__save_stats = save_stats
        if save_stats:
            self.__stats_best = []
        self.__gen_size = gen_size
        self.__epsilon = epsilon
        self.__steps_to_converge = steps_to_converge

        self.__delta = inf
        self.__num_steps = 0
        self.__gen_number = 0
        self.__current_gen_top_performance = inf
        self.__current_gen = [original]
        self.__current_results = None
        self.__judge = AnalyzeKeyboards(dataset, original, config)
        for i in range(1, gen_size):
            self.__current_gen.append(''.join(sample(original, len(original))))
        self.__best_keyboard = None
        self._print_status()
        self._calculate_fitness()
        self.__gen_number = 1

    def _print_status(self):
        print(f"---------------------GENERATION {self.__gen_number:>4}\n"
              f"Best Efficiency:{self.__current_gen_top_performance:>20}\n"
              f"Δ:{self.__delta:>34}\n"
              f"ε:{self.__epsilon:>34}\n"
              f"Steps:{self.__num_steps:>28}/{self.__steps_to_converge}\n"
              f"Generation Size: {self.__gen_size:>19}\n"
              f"Mutation Rate:{self.__mutate_rate:>22}\n")

    def generate(self):
        while self.__delta > self.__epsilon or self.__steps_to_converge != self.__num_steps:
            self._print_status()
            new_gen = [self.__best_keyboard]
            weights = list()
            for i in range(0, self.__gen_size):
                if self.__current_results['efficiencies'][i] == inf:
                    weights.append(0)
                else:
                    weights.append((self.__gen_size - i) ** 2)
            while len(new_gen) < self.__gen_size:
                parent_a, parent_b = choices(self.__current_gen, weights, k=2)
                new_gen.append(self._crossover(parent_a, parent_b))
            self.__current_gen = new_gen
            self._calculate_fitness()
            self.__gen_number += 1
        simple = None
        if self.__produce_simple:
            pass
            # TODO: produce a simplified version of the best one. Balance similarity and effeciency -> max(sim*eff) genetic? maybe swap keys around, sim = dist in keys?
        if self.__save_stats:
            plt.plot([i for i in range(0, self.__gen_number)], self.__stats_best, label='Raw')
            if self.__produce_simple:
                plt.plot(self.__gen_number - 1, self.__current_gen_top_performance, marker=".", # sTODO: change for simp
                         markersize=12, label='Simple')
            plt.text(0, self.__stats_best[0],
                        f"Best:{self.__current_gen_top_performance:>3f} "
                        f"ε:{self.__epsilon} "
                        f"Steps:{self.__num_steps} "
                        f"Gen Size: {self.__gen_size} "
                        f"Mutation Rate:{self.__mutate_rate}",
                        fontsize=8,
                        bbox={"facecolor": "white", "pad": 2})
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
        if self.__save_stats:
            self.__stats_best.append(top_preform)


def show_keyboards(keyboard):
    eel.init('display')

    def load_json_to_html(name, layout, last_analysis, efficiency, datasets):
        eel.read_data(name, layout, last_analysis, efficiency, datasets)

    load_json_to_html(keyboard['name'].split("/")[-1], keyboard['layout'], keyboard['last_analysis'],
                      keyboard['efficiency'],
                      keyboard['dataset_names'])
    eel.start('index.html', size=(1000, 700))


def main(args):
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
        "config",
        type=str,
        help="Name of the config JSON to initialize the cost matrix, finger responsibilities and initial finger "
             "positions. "
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

    args = parser.parse_args(args)
    with open(args.keyboard, "r") as json_file:
        keyboard = load(json_file)
    if args.display:
        show_keyboards(keyboard)
        exit()
    if not args.dataset:
        raise Exception("A dataset is required for this action.")
    if args.analyze:
        analysis = AnalyzeKeyboards(args.dataset, keyboard['layout'], args.config)
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
    generator = GeneticKeyboards(keyboard['layout'], args.dataset, args.config, args.simplify, args.gen_size,
                                 args.epsilon, args.steps_to_converge, args.mutation_rate, args.save_stats)
    raw, simplified = generator.generate()
    if args.save_stats:
        plt.title(f"Efficiency by Generation ({args.name if args.name else raw['last_analysis']})")
        plt.xlabel("Generation Number")
        plt.ylabel("Distance/Keystroke")
        plt.legend()
        plt.grid()
        plt.savefig(f"run_stats/{args.name if args.name else raw['last_analysis']}.genstats.png")
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
