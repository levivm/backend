from fabric.api import local,env



import sys,os

sys.path.append(os.path.join(os.path.dirname(__file__), 'trulii'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trulii.settings")

import django
django.setup()



def load_data(where):
    local('%s python manage.py loaddata data/cities_data.json' % where)
    local('%s python manage.py loaddata data/categories_data.json' % where)
    local('%s python manage.py loaddata data/subcategories_data.json' % where)
    local('%s python manage.py loaddata data/socialapp_data.json' % where)





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
    invoke(deploy_heroku)
    env.where = "heroku"
    local('python manage.py syncdb')
    invoke(load_data)


def clear_db(which):

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

    local("%s python manage.py dbshell < sqlclear.sql" % which )
    local("%s rm sqlclear.sql",which)

def reset_db(which=None):
    if not which:
        clear_local_db("heroku run")
        local('python manage.py syncdb')
        load_data("")
    
    # if which=='Heroku':

    #     pass
    # else:
    #     clear_local_db("heroku run")
    #     local('python manage.py syncdb')
    #     load_data("")


def reset_heroku_db():
    env.where = ""
    local('./manage.py sqlclear | heroku run python manage.py dbshell')
    local('python manage.py syncdb')
    invoke(load_data)


def initial_deploy_local():
    local('pip install -r requirements.txt')
    env.where = ""
    local('python manage.py syncdb')
    invoke(load_data)
