import argparse
import eel
import os
import multiprocessing as mp
import matplotlib.pyplot as plt
import math

from sys import argv
from json import load, dump
from zipfile import ZipFile
from datetime import datetime
from tqdm import tqdm


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


class Config:
    def __init__(self, path):
        self.finger_duty = dict()
        self.cost_matrix = dict()
        with open(path, 'r') as cfg:
            config_json = load(cfg)
            self.__fd_list = config_json['finger_duty']
            self.__parse_fd()
            self.original_finger_position = config_json['original_finger_position']
            self.alt_keys = config_json['alt_keys']
            self.return_to_home = config_json['return_to_home']
            self.__create_cm()

    def get_finger_duty_list(self):
        return self.__fd_list

    def __parse_fd(self):
        i = 0
        for duty in self.__fd_list:
            self.finger_duty[i] = duty
            i += 1

    def __create_cm(self):
        for key_a, finger_a in self.finger_duty.items():
            if self.return_to_home and not self.original_finger_position[finger_a] == key_a:
                continue
            for key_b, finger_b in self.finger_duty.items():
                if finger_a == finger_b:
                    self.cost_matrix[(key_a, key_b)] = self.calc_distance(key_a, key_b)

    def calc_distance(self, key_a, key_b):
        pt_a = self.__map_key_to_pt(key_a)
        pt_b = self.__map_key_to_pt(key_b)
        return math.sqrt(math.pow(pt_a[0] - pt_b[0], 2) + math.pow(pt_a[1] - pt_b[1], 2))

    @staticmethod
    def __map_key_to_pt(key):
        if key < 13:
            return key, 3
        elif key < 26:
            return 1.5 + (key - 13), 2
        elif key < 37:
            return 1.75 + (key - 26), 1
        elif key < 47:
            return 2 + (key - 37), 0


class Dataset:
    def __init__(self, path, base_valid, alt_valid):
        self.num_valid = 0
        self.num_invalid = 0
        self.data_inorder = list()
        self.data_dict = dict()
        self.filenames = list()

        zips = list()
        for root, direct, files in os.walk(path):
            for file in files:
                if '.zip' in file:
                    zips.append(os.path.join(root, file))
        if zips == list():
            raise Exception(f"No .zip files found in directory {path}. Please provide the -dataset arg with a"
                            f" directory that contains .zip compressed archives of .txt files.")
        print(f"Initializing dataset(s) from {path}\n")
        with tqdm(total=len(zips)) as pbar1:
            for zip_path in zips:
                with ZipFile(zip_path, 'r') as zipObj:
                    filenamelist = zipObj.namelist()
                    print(f"Initializing dataset {zip_path}")
                    with tqdm(total=len(filenamelist)) as pbar2:
                        for file in filenamelist:
                            if '.txt' in file:
                                self.filenames.append(file)
                                with zipObj.open(file) as dataset:
                                    while line := dataset.readline():
                                        for char in line.decode()[:-1].lower():
                                            if char not in base_valid and char not in alt_valid:
                                                self.num_invalid += 1
                                            elif char is not None:
                                                self.num_valid += 1
                                                self.data_inorder.append(char)
                                                try:
                                                    self.data_dict[char] += 1
                                                except KeyError:
                                                    self.data_dict[char] = 1
                            pbar2.update(1)
                pbar1.update(1)
        if self.filenames == list():
            raise Exception(f"No data was initialized from {path}. Please make sure the structure is valid.")
        cls()


class AnalyzeKeyboards:
    def __init__(self, path_to_dataset, path_to_config, valid_chars, char_checkpoint):
        self.__config = Config(path_to_config)
        self.__dataset = Dataset(path_to_dataset, valid_chars, self.__config.alt_keys)
        self.__kb_costs = dict()
        if char_checkpoint == math.inf:
            char_checkpoint = self.__dataset.num_valid
        self.__distance_limits = [(char_checkpoint * (i + 1), math.inf) for i in
                              range(0, self.__dataset.num_valid // char_checkpoint)]

    def get_num_valid_chars(self):
        return self.__dataset.num_valid

    def get_num_invalid_chars(self):
        return self.__dataset.num_invalid

    def get_filenames(self):
        return self.__dataset.filenames

    def update_keyboards(self, keyboards):
        self.__kb_costs = dict()
        for kb in keyboards:
            self.__kb_costs[kb] = 0

    def _analyze_thread_return(self, kb, out_queue):
        mapping = dict()
        i = 0
        for key in kb:
            mapping[key] = i
            i += 1
        cost = 0
        finger_pos = self.__config.original_finger_position
        for char, count in self.__dataset.data_dict.items():
            try:
                destination = mapping[char]
            except KeyError:
                destination = mapping[self.__config.alt_keys[char]]
            responsible_finger = self.__config.finger_duty[destination]
            transition = (finger_pos[responsible_finger], destination)
            try:
                cost += self.__config.cost_matrix[transition] * count * 2
            except KeyError:
                cost += self.__config.cost_matrix[(transition[1], transition[0])] * count * 2
        out_queue.put((kb, cost))

    def _analyze_thread_remain(self, kb, out_queue, get_check=False):
        mapping = dict()
        i = 0
        for key in kb:
            mapping[key] = i
            i += 1
        cost = 0
        chk = 0
        count = 0
        checkpoints = list()
        finger_pos = self.__config.original_finger_position
        for char in self.__dataset.data_inorder:
            try:
                destination = mapping[char]
            except KeyError:
                destination = mapping[self.__config.alt_keys[char]]
            responsible_finger = self.__config.finger_duty[destination]
            transition = (finger_pos[responsible_finger], destination)
            try:
                cost += self.__config.cost_matrix[transition]
            except KeyError:
                cost += self.__config.cost_matrix[(transition[1], transition[0])]
            finger_pos[responsible_finger] = destination
            if chk < len(self.__distance_limits) and count >= self.__distance_limits[chk][0]:
                if cost > self.__distance_limits[chk][1]:
                    cost = math.inf
                    break
                elif get_check:
                    checkpoints.append((self.__distance_limits[chk][0], cost))
                chk += 1
            count += 1
        if get_check:
            return checkpoints
        elif out_queue is not None:
            out_queue.put((kb, cost))

    def _listener(self, q):
        pbar = tqdm(total=len(self.__kb_costs.keys()))
        last_size = 0
        total = 0
        while total < len(self.__kb_costs.keys()):
            size = q.qsize()
            pbar.update(max(0, size - last_size))
            total += max(0, size - last_size)
            last_size = size

    def preform_analysis(self):
        if self.__kb_costs == dict():
            raise Exception("no keyboards initialized. use AnalyzeKeyboards.update_keyboards(list)")
        out_queue = mp.Queue()
        proc = mp.Process(target=self._listener, args=(out_queue,))
        proc.start()
        x = 0
        max = os.cpu_count() - 2
        num_kb = len(self.__kb_costs.keys())
        while x < num_kb:
            workers = []
            if x + max >= num_kb:
                segment = list(self.__kb_costs.keys())[x:]
            else:
                segment = list(self.__kb_costs.keys())[x:x+max]
            for kb in segment:
                if not self.__config.return_to_home:
                    workers.append(mp.Process(target=self._analyze_thread_remain, args=(kb, out_queue)))
                else:
                    workers.append(mp.Process(target=self._analyze_thread_return, args=(kb, out_queue)))
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()
            while not out_queue.empty():
                res = out_queue.get()
                self.__kb_costs[res[0]] = res[1]
            x += max
        proc.join()
        if not self.__config.return_to_home:
            best = self.get_ordered_results()[0][0]
            self.__distance_limits = self._analyze_thread_remain(best, None, get_check=True)
        cls()

    def get_ordered_results(self):
        return [(k, v) for k, v in sorted(self.__kb_costs.items(), key=lambda x: x[1])]


class GeneticKeyboards:
    def __init__(self, valid_chars, path_to_dataset, path_to_config, char_checkpoint, save_stats):
        self.__judge = AnalyzeKeyboards(path_to_dataset, path_to_config, valid_chars, char_checkpoint)
        self.__original = valid_chars
        self.__save_stats = save_stats
        self.__stats_best = []
        self.__delta = math.inf
        self.__current_layout = valid_chars
        self.__best_cost = math.inf
        self.__delta = math.inf
        self.__gen_number = 0

    def _print_status(self):
        print(f"---------------------GENERATION {self.__gen_number:>4}\n"
              f"Best Efficiency:{self.__best_cost/self.__judge.get_num_valid_chars():>20}\n"
              f"Δ:{self.__delta:>34}\n"
              f"{self.__current_layout}")

    def generate(self):
        while True:
            new_gen = dict()
            for i in range(0, len(self.__original)):
                for j in range(i, len(self.__original)):
                    copy = list(self.__current_layout)
                    tmp = copy[i]
                    copy[i] = copy[j]
                    copy[j] = tmp
                    copy_str = "".join(copy)
                    new_gen[copy_str] = {
                        "i": i,
                        "j": j,
                        "cost": math.inf
                    }
            self.__judge.update_keyboards(new_gen.keys())
            self._print_status()
            self.__judge.preform_analysis()
            results = self.__judge.get_ordered_results()
            for k, v in results:
                new_gen[k]["cost"] = v
            self.__delta = min(new_gen[self.__current_layout]["cost"] / self.__judge.get_num_valid_chars(),
                               (self.__best_cost - new_gen[self.__current_layout]["cost"])
                               / self.__judge.get_num_valid_chars())
            self.__best_cost = new_gen[self.__current_layout]["cost"]
            if self.__delta <= 0:
                break
            if self.__save_stats:
                self.__stats_best.append(self.__best_cost / self.__judge.get_num_valid_chars())
            not_swapped = [True for x in range(0, len(self.__original))]
            next_layout = list(self.__current_layout)
            for k, v in results:
                if v > self.__best_cost:
                    break
                i = new_gen[k]["i"]
                j = new_gen[k]["j"]
                if not_swapped[i] and not_swapped[j]:
                    not_swapped[i] = False
                    not_swapped[j] = False
                    tmp = next_layout[i]
                    next_layout[i] = next_layout[j]
                    next_layout[j] = tmp
            self.__current_layout = "".join(next_layout)
            self.__gen_number += 1
        return self._get_result()

    def _get_result(self):
        if self.__save_stats:
            plt.plot([i for i in range(0, self.__gen_number)], self.__stats_best, label='Raw')
            plt.text(0, self.__stats_best[0],
                     f"Best:{self.__best_cost / self.__judge.get_num_valid_chars():>3f}",
                     fontsize=8,
                     bbox={"facecolor": "white", "pad": 2})
        return {
            'layout': self.__current_layout,
            'total_distance': self.__best_cost,
            'valid_chars': self.__judge.get_num_valid_chars(),
            'invalid_chars': self.__judge.get_num_invalid_chars(),
            'efficiency': self.__best_cost / self.__judge.get_num_valid_chars(),
            'dataset_names': self.__judge.get_filenames(),
            'last_analysis': datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        }


def show_keyboards(keyboard, path_to_config):
    eel.init('display')

    def load_json_to_html(name, layout, layout_alt_keys, finger_res, last_analysis, efficiency, datasets):
        eel.read_data(name, layout, layout_alt_keys, finger_res, last_analysis, efficiency, datasets)

    config = Config(path_to_config)
    alt_k = []
    for c in keyboard['layout']:
        if c not in config.alt_keys.values():
            alt_k.append(str(c).upper())
        else:
            for k, v in config.alt_keys.items():
                if v == c:
                    alt_k.append(k)
    load_json_to_html(
        keyboard['name'].split("/")[-1],
        keyboard['layout'],
        "".join(alt_k),
        config.get_finger_duty_list(),
        keyboard['last_analysis'],
        keyboard['efficiency'],
        keyboard['dataset_names']
    )
    eel.start('index.html', size=(1200, 500))


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
        "-char_checkpoint",
        metavar="SIZE",
        type=int,
        default=100000,
        help="Create character checkpoints for large datasets. For each keyboard, disregard if the total distance is "
             "greater than the last best total distance at every [char_checkpoint] number of "
             "characters. Ignored if the loaded config has return_to_home flag set True."
    )
    parser.add_argument(
        "-name",
        metavar="NAME",
        type=str,
        default="",
        help="Name the keyboard being generated. Default "
             "naming scheme: yyyy/mm/dd:hh:mm:ss.raw"
    )
    parser.add_argument(
        "-save_stats",
        action="store_true",
        help="Create a visual plot for the generation statistic in /run_stats."
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
        kb_json = load(json_file)
        if args.display:
            show_keyboards(kb_json, args.config)
            exit()
    if not args.dataset:
        raise Exception("A dataset is required for this action.")
    if args.analyze:
        analysis = AnalyzeKeyboards(args.dataset, args.config, kb_json['layout'], math.inf)
        analysis.update_keyboards([kb_json['layout']])
        analysis.preform_analysis()
        result = analysis.get_ordered_results()[0]
        kb_json['total_distance'] = result[1]
        kb_json['valid_chars'] = analysis.get_num_valid_chars()
        kb_json['invalid_chars'] = analysis.get_num_invalid_chars()
        kb_json['efficiency'] = result[1] / analysis.get_num_valid_chars()
        kb_json['dataset_names'] = analysis.get_filenames()
        kb_json['last_analysis'] = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        with open(args.keyboard, "w") as json_file:
            dump(kb_json, json_file)
        exit()

    generator = GeneticKeyboards(kb_json['layout'], args.dataset, args.config, args.char_checkpoint, args.save_stats)
    result = generator.generate()
    if args.save_stats:
        plt.title(f"Efficiency by Generation ({args.name if args.name else result['last_analysis']})")
        plt.xlabel("Generation Number")
        plt.ylabel("Distance/Keystroke")
        plt.legend()
        plt.grid()
        plt.savefig(f"run_stats/{args.name if args.name else result['last_analysis']}.genstats.png")
    with open(f"keyboards/{args.name if args.name else result['last_analysis']}.json", "w") as json_file:
        result['name'] = f"keyboards/{args.name if args.name else result['last_analysis']}"
        dump(result, json_file)
    cls()
    print(f"Finished running KBMSTR with args:\n\n\t"
          f"keyboard={args.keyboard}\n\t"
          f"dataset={args.dataset}\n\t"
          f"char_checkpoint={args.char_checkpoint}\n\t"
          f"name={args.name}\n\t"
          f"save_stats={args.save_stats}\n\t"
          f"analyze={args.analyze}\n\t"
          f"display={args.display}\n")


if __name__ == "__main__":
    main(argv[1:])
