from sys import argv


class KBGraph:
    def __int__(self):
        pass

    @staticmethod
    def __map_key_to_pt(key):
        if key < 10:
            return key, 3
        elif key < 20:
            return 0.25 + (key - 10), 2
        elif key < 31:
            return 0.75 + (key - 21), 1
        elif key < 42:
            return 1.25 + (key - 32), 0
        raise Exception('bad')

    def calc_distance(self, key_a, key_b):
        pt_a = self.__map_key_to_pt(key_a)
        pt_b = self.__map_key_to_pt(key_b)
        return ((pt_a[0] - pt_b[0])**2 + (pt_a[1] - pt_b[1])**2)**0.5


def create_config(config_file):
    with open(config_file, 'r') as cfg:
        dic = eval(cfg.read())
        finger_duty = eval(dic['finger_duty'])
        finger_pos = eval(dic['finger_pos'])
    dic['cost_matrix'] = {}
    g = KBGraph()
    for key, finger in finger_duty.items():
        print(finger, key, (finger_pos[finger], key), g.calc_distance(finger_pos[finger], key))
        dic['cost_matrix'][(finger_pos[finger], key)] = g.calc_distance(finger_pos[finger], key)
    dic['cost_matrix'] = str(dic['cost_matrix'])
    with open(config_file, 'w') as cfg:
        cfg.write(str(dic))


def main(args):
    create_config(args[0])


if __name__ == "__main__":
    main(argv[1:])