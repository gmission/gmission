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

def merge_ply_file(model_dir_name):
    model_dir_path = os.path.join(MODELS_ROOT_DIR_PATH, model_dir_name, 'bundle')
    p = subprocess.Popen('ls ' + model_dir_path + '/*.ply', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    currentMaxNumber = 0
    choosenFile = None

    points_count = []

    ply_files = p.stdout.readlines()
    for line in ply_files:
        points_count.append(file_len(os.path.join(model_dir_path, line)) - 13)

    total_points_count = sum(points_count)

    f = open(os.path.join(model_dir_path, 'total_points.ply'), 'w')
    header = """ply
format ascii 1.0
element face 0
property list uchar int vertex_indices
element vertex lineNumber
property float x
property float y
property float z
property uchar diffuse_red
property uchar diffuse_green
property uchar diffuse_blue
end_header"""
    header = header.replace('lineNumber', str(total_points_count))
    f.write(header)
    f.write('\n')

    for index, ply_file in enumerate(ply_files):
        in_file = open(ply_file.strip(), 'r')
        line_number = 0

        for line in in_file:
            line_number += 1
            if line_number <= 12 or line_number > points_count[index] + 12 :
                continue
            else:
                f.write(line)

    f.close()
    return 'total_points.ply'



def file_len(fname):
    p = subprocess.Popen('wc -l '+ fname, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()[0]
    return int(result.strip().split()[0])

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
    clean_dir(model_dir_path)
    for image_name in images:
        iamge_path = os.path.join(IMAGE_DIR_PATH, image_name)
        out_image_path = os.path.join(model_dir_path, image_name)
        scale_image(iamge_path, out_image_path)


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


def clean_dir(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

