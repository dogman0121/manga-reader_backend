import os
import uuid

class Storage:
    def __init__(self, app=None):
        self.app = app
        self.upload_folder = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.upload_folder = app.config['UPLOAD_FOLDER']

    def save(self, file, relative_path):
        if not os.path.exists(os.path.join(self.upload_folder, relative_path)):
            os.makedirs(os.path.join(self.upload_folder, relative_path))

        name, ext = os.path.splitext(file.filename)

        filename = str(uuid.uuid4()) + ext

        file_path = os.path.join(self.upload_folder, relative_path, filename)

        file.save(file_path)
        return filename

    def delete(self, relative_path):
        file_path = os.path.join(self.upload_folder, relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_url(self, relative_path):
        return "https://kanwoo.ru/uploads/{}".format(relative_path)
