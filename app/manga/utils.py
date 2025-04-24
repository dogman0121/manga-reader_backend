import os
import uuid
from flask import current_app

def get_uuid4_filename():
    return str(uuid.uuid4())

def get_external_path(path):
    if current_app.config["USE_SSL"]:
        return "https://" + current_app.config["SERVER_NAME"] + "/" + path
    else:
        return "http://" + current_app.config["SERVER_NAME"] + "/" + path