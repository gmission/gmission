__author__ = 'chenzhao'


# import os
# import glob
# __all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]


# import user
# print user
# print dir(user)
# print user.user_blueprint

from user import user_blueprint as user_bp
from shortcut import shortcut_blueprint as shortcut_bp
from schemadefinition import schemadefinition_blueprint as shortcut_sd
from image import image_blueprint as image_bp
from video import video_blueprint as video_bp
from audio import audio_blueprint as audio_bp
from d3 import d3_blueprint as d3_bp
from test import test_blueprint as test_bp