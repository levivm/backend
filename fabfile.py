from fabric.api import local,env




try:
    import sys,os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'trulii'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trulii.settings")

    import django
    django.setup()
except ImportError:
    pass





def load_data(command="",app_name=""):
    if not app_name:
        local('%s python manage.py loaddata data/cities_data.json' % command)
        local('%s python manage.py loaddata data/categories_data.json' % command)
        local('%s python manage.py loaddata data/subcategories_data.json' % command)
        local('%s python manage.py loaddata data/socialapp_data.json' % command)
    else:
        local('%s python manage.py loaddata data/cities_data.json --app %s' % (command,app_name) )
        local('%s python manage.py loaddata data/categories_data.json --app %s' % (command,app_name))
        local('%s python manage.py loaddata data/subcategories_data.json --app %s' % (command,app_name))
        local('%s python manage.py loaddata data/socialapp_data.json --app %s' % (command,app_name))





def deploy_heroku(app_name=""):
    local('pip freeze > requirements.txt')
    local('git add --all')
    print("enter your git commit comment: ")
    comment = raw_input()
    local('git commit -m "%s"' % comment)
    local('git push %s master' % app_name)

def initial_deploy_heroku(app_name=""):
    local('git push %s master' % app_name)
    local('heroku run python manage.py syncdb --app %s' % app_name)
    load_data("heroku run",app_name)


def prepare_sqlclear():

    from django.conf import settings

    not_apps = ["django","allauth."]
    installed_apps = [app for app in settings.INSTALLED_APPS if not any(map(lambda x:x in app,not_apps)) ]


    sqlclear_all = ""
    from subprocess import check_output
    
    for app in installed_apps:
        command = ["python","manage.py","sqlclear","%s"%app]


        try:
            sqlclear_all += check_output(command)
        except Exception,e:
            pass

    with open("sqlclear.sql", "w") as text_file:
        text_file.write(sqlclear_all)

def reset_db(app_name=""):

    if app_name:
        prepare_sqlclear()
        local("heroku pg:psql < sqlclear.sql --app %s" % app_name)
        local('heroku run python manage.py syncdb --app % s' % app_name)
        load_data("heroku run",app_name)
    else:
        prepare_sqlclear()
        local("python manage.py dbshell < sqlclear.sql") 
        local('python manage.py syncdb')
        load_data()


def initial_deploy_local():
    local('pip install -r requirements.txt')
    local('python manage.py syncdb')
    load_data()