import os
from PIL import Image
from datetime import datetime
from watchdog.events import RegexMatchingEventHandler
import subprocess


class DirEventHandler(RegexMatchingEventHandler):
    EXTENSIONS = ['.jpg', '.doc', '.db']
    FILE_REGEX = [r".*\{}$".format(EXTENSIONS[0]), r".*\{}$".format(EXTENSIONS[1]), r".*\{}$".format(EXTENSIONS[2])]

    def __init__(self):
        super().__init__(self.FILE_REGEX)

    def on_created(self, event):
        print(event)
        self.image_converter(event)
        self.doc_converter(event)
        self.del_file(event)

    def image_converter(self, event):
        filename, ext = os.path.splitext(event.src_path)
        if ext.lower() == self.EXTENSIONS[0]:
            image = Image.open(event.src_path)
            image.save(f"{filename}_converted.png")
            os.remove(event.src_path)
            with open('log.txt', 'a') as f:
                f.write(f'{datetime.now()} - '
                        f'{os.path.abspath(event.src_path)} CONVERTED to {filename}_converted.png and DELETED\n')
            f.close()
        else:
            pass

    def doc_converter(self, event):
        filename, ext = os.path.splitext(event.src_path)
        if ext.lower() == self.EXTENSIONS[1]:
            subprocess.check_output(['libreoffice', '--convert-to', 'pdf', '--outdir', filename.strip('/')[0], event.src_path])
            os.remove(event.src_path)
            with open('log.txt', 'a') as f:
                f.write(f'{datetime.now()} - '
                        f'{os.path.abspath(event.src_path)} CONVERTED to {filename}.pdf and DELETED\n')
            f.close()
        else:
            pass

    def del_file(self, event):
        filename, ext = os.path.splitext(event.src_path)
        if ext.lower() == self.EXTENSIONS[2]:
            os.remove(event.src_path)
            with open('log.txt', 'a') as f:
                f.write(f'{datetime.now()} - '
                        f'{os.path.abspath(event.src_path)} DELETED\n')
            f.close()
        else:
            pass
