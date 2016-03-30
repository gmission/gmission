__author__ = 'haidaoxiaofei'


import subprocess
import os, sys, errno
import shutil
from PIL import Image

DATA_PATH_BASE = '/GMission-Server/hkust-gmission/gmission/static'
IMAGE_DIR_PATH = DATA_PATH_BASE + '/image/original'
MODELS_ROOT_DIR_PATH = DATA_PATH_BASE + '/3d_model'

def find_final_ply_file(model_dir_name):
    model_dir_path = os.path.join(MODELS_ROOT_DIR_PATH, model_dir_name)
    p = subprocess.Popen('ls '+model_dir_path+'/bundle/*.ply', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    currentMaxNumber = 0
    choosenFile = None

    for line in p.stdout.readlines():
        print line
        if line.find('ls') > -1:
            break
        tmpNumber = int(line[line.rfind('points') + 6:line.rfind('.')])
        if currentMaxNumber < tmpNumber:
            currentMaxNumber = tmpNumber
            choosenFile = line[line.rfind('points'):]

    choosenFile = choosenFile.strip()
    return choosenFile


def build_3d_model(model_dir_name):
    model_dir_path = os.path.join(MODELS_ROOT_DIR_PATH, model_dir_name)

    my_env = os.environ
    my_env["LD_LIBRARY_PATH"] = "/GMission-Server/services/bundler/bin"

    p = subprocess.Popen('bash /GMission-Server/services/bundler/RunBundler.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=model_dir_path, env=my_env)
    p.wait()
    # for line in p.stdout.readlines():
    #     print line


def prepare_images(model_dir_name, images):
    model_dir_path = os.path.join(MODELS_ROOT_DIR_PATH, model_dir_name)
    mkdir_p(model_dir_path)
    for image_name in images:
        iamge_path = os.path.join(IMAGE_DIR_PATH, image_name)
        out_image_path = os.path.join(model_dir_path, image_name)
        scale_image(iamge_path, model_dir_path)
        # shutil.copy2(iamge_path, model_dir_path)

def scale_image(inFilePath, outFilePath):
    size_vertical = 960, 1280
    size_horizon = 1280, 960
    try:
        im = Image.open(inFilePath)
        origin_width, origin_height = im.size

        if  origin_width > origin_height:
            im.thumbnail(size_horizon, Image.ANTIALIAS)
        else:
            im.thumbnail(size_vertical, Image.ANTIALIAS)
        im.save(outFilePath, "JPEG")
    except IOError:
        print
        "cannot create scaled file for '%s'" % inFilePath


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# build_3d_model('examples/ET')
# print find_final_ply_file('examples/ET')
