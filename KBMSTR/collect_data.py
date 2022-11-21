from pynput.keyboard import Listener
from random import choices
from string import ascii_lowercase, ascii_uppercase, digits
from tqdm import tqdm
import os
import zipfile

FILE_CHAR_LIM = 10000


class Logger:
    def __init__(self):
        self.__captured = list()
        self.__prog = tqdm(total=FILE_CHAR_LIM)
        self.__num_files = 0
        self.__dir_name = f"KBMSTR-DATA-{''.join(choices(ascii_lowercase.join(ascii_uppercase).join(digits), k=16))}"
        print("Generated 0 files. Press (CTRL-C) to stop capture. Progress to next file:")

    def start(self):
        os.mkdir(self.__dir_name)
        try:
            with Listener(on_press=self._key_event_press) as the_listener:
                the_listener.join()
        except KeyboardInterrupt:
            self._store_data(rm=1)
            try:
                os.mkdir("KBMSTR-Datasets")
            except FileExistsError:
                pass
            zf = zipfile.ZipFile(f"KBMSTR-Datasets/{self.__dir_name}.zip", "w")
            for dirname, subdirs, files in os.walk(self.__dir_name):
                for filename in files:
                    if 'KBMSTR.capture.txt' in filename:
                        zf.write(os.path.join(dirname, filename))
            zf.close()
            for root, dirs, files in os.walk(self.__dir_name):
                for name in files:
                    os.remove(os.path.join(root, name))
            os.rmdir(self.__dir_name)

    def _key_event_press(self, key):
        if len(str(key)) == 3:
            self.__prog.update(1)
            self.__captured.append(key)
        if len(self.__captured) >= FILE_CHAR_LIM:
            self._store_data()

    def _store_data(self, rm=0):
        os.system('cls' if os.name == 'nt' else 'clear')
        if rm > 0:
            self.__captured = self.__captured[0:(-1 * rm)]
        with open(f'{self.__dir_name}/{"".join(choices(ascii_lowercase.join(ascii_uppercase).join(digits), k=16))}'
                  f'.KBMSTR.capture.txt', 'w') as log:
            for the_key in self.__captured:
                the_key = str(the_key).replace("'", "")
                log.write(the_key)
        self.__prog = tqdm(total=FILE_CHAR_LIM)
        self.__num_files += 1
        print(f"Generated {self.__num_files} files of {FILE_CHAR_LIM if self.__num_files > 1 else len(self.__captured)}"
              f" characters. {'Press (CTRL-C) to stop capture. Progress to next file:' if rm == 0 else ''}")
        self.__captured = list()


if __name__ == "__main__":
    l = Logger()
    l.start()
