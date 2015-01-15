__author__ = 'CHEN Zhao'
import time
import os.path
from fabric.api import local, env, run, cd, sudo
from fabric.contrib.project import rsync_project
from fabric.context_managers import settings

# put things like:
# ################################
#   Host csp-azure-asia
#   User csp_team
# 	HostName gmission-asia.cloudapp.net
# 	IdentityFile ~/.ssh/your_rsa
# ################################
# in your ~/.ssh/config

env.use_ssh_config = True
env.warn_only = True
env.timeout = 2
env.connection_attempts = 3
env.hosts = ['csp-aliyun']
env.password = 'csp2014'

REMOTE_ROOTS = {
    'csp-aliyun':'/home/csp_team/nginx_www/gmission',
}


def rsync_files(remote_dir, local_dir='.', more_exclude=None):
    exclude_list = ['.idea', '.DS_Store', '.git*', '*.log*', '*.pyc', '.idea',
                    'image/*.jpg', 'image/*.JPG', 'image/*.png', '*.mov', 'new.csv']
    if more_exclude:
        exclude_list += more_exclude

    rsync_project(local_dir=local_dir, remote_dir=remote_dir, extra_opts='--ignore-errors --chmod=g+w', exclude=exclude_list)

    # with cd(remote_dir):
    #     run('chgrp -R www-data .')



def setup_env(remote_dir):  # we need a docker
    # sudo ./depends.sh
    # mysql> source init_mysql.sql
    pass


def restart_webserver(remote_root):
    with cd(remote_root):
        run('touch 0deployment/uwsgi/vassals/hkust-gmission.ini')
        run('touch 0deployment/uwsgi/vassals/services.ini')
        # sudo('service uwsgi1 restart')


def deploy_all():
    print '*'*80
    remote_root = REMOTE_ROOTS[env.host_string]
    print 'server:', env.host_string, 'dir:', remote_root

    # how many steps are needed to deploy all services?
    # step 1
    rsync_files(remote_root)
    # step 2
    setup_env(remote_root)
    # step 3
    restart_webserver(remote_root)


if __name__ == '__main__':
    with settings(host_string='csp-aliyun'):
        deploy_all()
        pass


