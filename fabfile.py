from fabric.api import local,env



import sys,os

sys.path.append(os.path.join(os.path.dirname(__file__), 'trulii'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trulii.settings")

import django
django.setup()



def load_data(command=""):
    local('%s python manage.py loaddata data/cities_data.json' % command)
    local('%s python manage.py loaddata data/categories_data.json' % command)
    local('%s python manage.py loaddata data/subcategories_data.json' % command)
    local('%s python manage.py loaddata data/socialapp_data.json' % command)





def deploy_heroku():
    local('pip freeze > requirements.txt')
    local('git add .')
    print("enter your git commit comment: ")
    comment = raw_input()
    local('git commit -m "%s"' % comment)
    #local('git push -u heroku master')
    #local('heroku maintenance:on')
    local('git push heroku master')
    #local('heroku run python manage.py collectstatic')
    #local('heroku maintenance:off')

def initial_deploy_heroku():
    deploy_heroku()
    local('heroku run python manage.py syncdb')
    load_data("heroku run")


def prepare_sqlclear():

    from django.conf import settings
    not_apps = ["django","allauth."]
    installed_apps = [app for app in settings.INSTALLED_APPS if not any(map(lambda x:x in app,not_apps)) ]


    sqlclear_all = ""
    from subprocess import check_output
    
    for app in installed_apps:
        command = ["python","manage.py","sqlclear","%s"%app]
        sqlclear_all += check_output(command)

    with open("sqlclear.sql", "w") as text_file:
        text_file.write(sqlclear_all)

def reset_db(server="local"):

    if server == "heroku":
        prepare_sqlclear()
        local("heroku pg:psql < sqlclear.sql")
        local('heroku run python manage.py syncdb')
        load_data("heroku run")
    elif server == "local":
        prepare_sqlclear()
        local("python manage.py dbshell < sqlclear.sql") 
        local('python manage.py syncdb')
        load_data()


def initial_deploy_local():
    local('pip install -r requirements.txt')
    local('python manage.py syncdb')
    load_data()