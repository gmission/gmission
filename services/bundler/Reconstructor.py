__author__ = 'haidaoxiaofei'


import subprocess


def find_final_ply_file(dir):
    p = subprocess.Popen('ls '+dir+'/bundle/*.ply', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    currentMaxNumber = 0
    choosenFile = ''
    for line in p.stdout.readlines():
        tmpNumber = int(line[line.rfind('points') + 6:line.rfind('.')])
        if currentMaxNumber < tmpNumber:
            currentMaxNumber = tmpNumber
            choosenFile = 'bundle/'+line[line.rfind('points'):]
    return choosenFile



def build_3d_model(dir):


    p = subprocess.Popen('bash /GMission-Server/services/bundler/RunBundler.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dir)
    p.wait()
    # for line in p.stdout.readlines():
    #     print line

build_3d_model('examples/ET')
print find_final_ply_file('examples/ET')
