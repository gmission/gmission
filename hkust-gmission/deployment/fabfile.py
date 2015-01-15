__author__ = 'CHEN Zhao'
import time
import os.path
from fabric.api import local, env, run, cd, sudo
from fabric.contrib.project import rsync_project
from fabric.context_managers import settings

# put
# ################################
#   Host csp-lccpu3
#   User csp_team
# 	HostName lccpu3.cse.ust.hk
# 	IdentityFile ~/.ssh/your_rsa
#
#   Host csp-csz908
#   User csp_team
# 	HostName csz908.cse.ust.hk
# 	IdentityFile ~/.ssh/your_rsa
# ################################
# in your ~/.ssh/config

env.use_ssh_config = True
env.warn_only = True
env.timeout=2
env.connection_attempts=3
env.hosts = ['csp-azure-asia']
env.password='csp2014'

REMOTE_ROOTS = {
    'csp-azure-asia':'/home/csp_team/nginx_www/gmission_szww',
}


def sync_code(local, remote, exclude):
    rsync_project(local_dir=local, remote_dir=remote, extra_opts='--ignore-errors', exclude=exclude)


def set_folder_permission():
    def sudochmod777(d):
        sudo('chmod 777 '+d, shell=True, quiet=True)
    dirs = ['gmission/static/image/original',
            'gmission/static/image/thumb',
            'gmission/static/video/original',
            'gmission/static/video/thumb',
            'gmission/static/audio',
            'gmission/static/audio/original',
            'gmission/static/uploads',
            'gmission/static/data',
            'gmission/logs',
            'gmission/logs/GMission.log',
            'gmission/logs/GMissionPushMsg.log',
            'gmission/logs/GMissionProfiling.log',
            ]
    map(sudochmod777, dirs)


def restart_webserver():
    run('touch ../gmission_szww.uwsgi.ini')


def deploy():
    print '*'*80
    print env.host_string
    REMOTE_ROOT = REMOTE_ROOTS[env.host_string]
    exclude_list = ['.idea', '.DS_Store', '.git*', '*.log*', '*.pyc', '.idea',
                    'image/*.jpg', 'image/*.JPG', 'image/*.png', '*.mov', 'new.csv']
    sync_code(local='.', remote=REMOTE_ROOT, exclude=exclude_list)

    with cd(REMOTE_ROOT):
        set_folder_permission()
        # run('python db_util.py')
        restart_webserver()



if __name__=='__main__':
    # with settings(host_string='csp-csz908'):
    #     deploy()
    #     pass
    with settings(host_string='csp-azure-asia'):
        deploy()
        pass


