from fabric.api import *

env.user = 'ubuntu'
env.key_filename = '~/frankly.pem'
env.serverDir = '/home/ubuntu/franklysql'
env.git_repo = 'https://bitbucket.org/shashank_shekhar_inox/franklysql'

def set_host(_type):
    if _type == 'api':
        env.hosts = ['api1.frankly.me']
    elif _type == 'encoder':
        env.hosts = ['celery.frankly.me']
    
def setup_api():
    with cd('/home/ubuntu'):
        sudo('apt-get update')
        sudo('apt-get install -y git')
        sudo('apt-get install -y python-pip python-dev libmysqlclient-dev')
        sudo('apt-get install -y nginx')
        sudo('apt-get install supervisor')
        git_command = 'git clone %s'%env.git_repo
        run(git_command, warn_only = True)
   
    with cd('/home/ubuntu/franklysql'):
        sudo('ln -s /home/ubuntu/franklysql/franklyapi_nginx.conf /etc/nginx/sites-enabled/frankly')
        sudo('rm /etc/nginx/sites-enabled/default')
        sudo('service nginx restart')
        sudo('pip install -r requirements.txt', warn_only = True)
        sudo('pip install https://github.com/tusharbabbar/flask-login/archive/master.zip')
        supervisord_conf_result = run('grep program:gunicorn /etc/supervisor/supervisord.conf')
        if not supervisord_conf_result:
            sudo('cat super_guni >> /etc/supervisor/supervisord.conf')
        sudo('service supervisor restart')

def setup_encoder():
    with cd('/home/ubuntu'):
        sudo('apt-get update')
        sudo('apt-get install -y git')
        sudo('apt-get install -y python-pip python-dev libmysqlclient-dev')
        sudo('apt-get install -y nginx')
        sudo('apt-get install supervisor')
        git_command = 'git clone %s'%env.git_repo
        run(git_command, warn_only = True)
   
    with cd('/home/ubuntu/franklysql'):
        sudo('ln -s /home/ubuntu/franklysql/franklyapi_nginx.conf /etc/nginx/sites-enabled/frankly')
        sudo('rm /etc/nginx/sites-enabled/default')
        sudo('service nginx restart')
        sudo('pip install -r requirements.txt')
        sudo('pip install https://github.com/tusharbabbar/flask-login/archive/master.zip')
        supervisord_conf_result = run('grep program:celery_encoder /etc/supervisor/supervisord.conf')
        if not supervisord_conf_result:
            sudo('cat super_encoder >> /etc/supervisor/supervisord.conf')
        sudo('service supervisor restart')

