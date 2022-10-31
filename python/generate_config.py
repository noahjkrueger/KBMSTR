import math
from sys import argv


class KBGraph:
    def __int__(self):
        pass

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
        raise Exception('bad')

    def calc_distance(self, key_a, key_b):
        pt_a = self.__map_key_to_pt(key_a)
        pt_b = self.__map_key_to_pt(key_b)
        return math.sqrt(math.pow(pt_a[0] - pt_b[0], 2) + math.pow(pt_a[1] - pt_b[1], 2))


def create_config(config_file):
    with open(config_file, 'r') as cfg:
        dic = eval(cfg.read())
        finger_duty = eval(dic['finger_duty'])
    dic['cost_matrix'] = {}
    g = KBGraph()
    for key_a, finger_a in finger_duty.items():
        for key_b, finger_b in finger_duty.items():
            if finger_a == finger_b:
                dic['cost_matrix'][(key_a, key_b)] = g.calc_distance(key_a, key_b)
    dic['cost_matrix'] = str(dic['cost_matrix'])
    with open(config_file, 'w') as cfg:
        cfg.write(str(dic))


def main(args):
    create_config(args[0])


if __name__ == "__main__":
    main(argv[1:])