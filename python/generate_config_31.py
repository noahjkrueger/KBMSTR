from sys import argv


class KBGraph:
    def __int__(self):
        pass

    @staticmethod
    def __map_key_to_pt(key):
        if key < 10:
            return 0.5 + key, 2
        elif 10 <= key < 21:
            return 0.75 + (key - 10), 1
        elif 21 <= key < 32:
            return 1.25 + (key - 21), 0
        raise Exception('bad')

    def calc_distance(self, key_a, key_b):
        pt_a = self.__map_key_to_pt(key_a)
        pt_b = self.__map_key_to_pt(key_b)
        return ((pt_a[0] - pt_b[0])**2 + (pt_a[1] - pt_b[1])**2)**0.5


def create_config(config_file):
    with open(config_file, 'r') as cfg:
        dic = eval(cfg.read())
        finger_duty = eval(dic['finger_duty'])
    dic['cost_matrix'] = {}
    g = KBGraph()
    items = list(finger_duty.items())
    for x in range(0, len(items)):
        key_x, finger_x = items[x]
        for y in range(x + 1, len(items)):
            key_y, finger_y = items[y]
            if finger_x == finger_y:
                dic['cost_matrix'][(key_x, key_y)] = g.calc_distance(key_x, key_y)
    with open(config_file, 'w') as cfg:
        cfg.write(str(dic))


def main(args):
    create_config(args[0])


if __name__ == "__main__":
    main(argv[1:])