import os, shutil
from PIL import Image
from datetime import datetime
from watchdog.events import RegexMatchingEventHandler
import subprocess
import config


class DirEventHandler(RegexMatchingEventHandler):
    EXTENSIONS = config.images + config.documents + \
                 config.teamviewer_cache + config.files_to_move
    FILE_REGEX = [r".*\{}$".format(extention) for extention in EXTENSIONS]

    def __init__(self):
        super().__init__(self.FILE_REGEX)

    def on_created(self, event):
        print(event)
        filename, ext = os.path.splitext(event.src_path)
        self.image_converter(event, filename, ext)
        self.doc_converter(event, filename, ext)
        self.del_tvc_file(event, ext)
        self.move_file(event, ext)

    def on_deleted(self, event):
        def __repr__():
            return f'{os.path.abspath(event.src_path)} DELETED'

        self.loggin_to_file(__repr__())

    def on_modified(self, event):
        def __repr__():
            return f'{os.path.abspath(event.src_path)} MODIFIED'

        self.loggin_to_file(__repr__())

    def on_moved(self, event):
        def __repr__():
            return f'{os.path.abspath(event.dest_path)} CREATED'

        self.loggin_to_file(__repr__())

    def loggin_to_file(self, doc):
        with open('log.txt', 'a') as f:
            f.write(f'{datetime.now()} - {doc}\n')
        f.close()

    def image_converter(self, event, filename, ext):

        def __repr__():
            return f'{os.path.abspath(event.src_path)} CONVERTED to ' \
                   f'{filename}_converted.png'


        if ext.lower() in config.images:
            image = Image.open(event.src_path)
            image.save(f"{filename}_converted.png")
            self.loggin_to_file(__repr__())
            if config.del_original_image_after_converting:
                os.remove(event.src_path)
        else:
            pass

    def doc_converter(self, event, filename, ext):

        def __repr__():
            return f'{os.path.abspath(event.src_path)} CONVERTED to ' \
                   f'{filename}.pdf'

        if ext.lower() in config.documents:
            subprocess.check_output(['libreoffice', '--convert-to', 'pdf',
                                     '--outdir', filename.strip('/')[0],
                                     event.src_path])
            if config.del_original_document_after_converting:
                os.remove(event.src_path)
            self.loggin_to_file(__repr__())
        else:
            pass

    def del_tvc_file(self, event, ext):
        if ext.lower() in config.teamviewer_cache:
            os.remove(event.src_path)
        else:
            pass

    def move_file(self, event, ext):

        def __repr__():
            return f'{os.path.abspath(event.src_path)} MOVED to ' \
                   f'{config.path_to_move}'

        if ext.lower() in config.files_to_move:
            if config.path_to_move:
                try:
                    shutil.move(os.path.abspath(event.src_path),
                                config.path_to_move + event.src_path.split('/')[1])
                except FileNotFoundError:
                    os.mkdir(config.path_to_move)
                    self.move_file(event, ext)

                self.loggin_to_file(__repr__())
            else:
                config.path_to_move = os.getcwd() + '/moved_logs/'
                self. move_file(event, ext)
        else:
            pass


