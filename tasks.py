from invoke import run, task

try:
    import sys,os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'trulii'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trulii.settings")

    import django
    django.setup()
except ImportError:
    pass


@task
def load_data(command="",app_name=""):
    if not app_name:
        run('python manage.py loaddata data/cities_data.json')
        run('python manage.py loaddata data/categories_data.json')
        run('python manage.py loaddata data/subcategories_data.json')
        run('python manage.py loaddata data/socialapp_data.json')
    else:
        run('%s python manage.py loaddata data/cities_data.json --app %s' % (command,app_name) )
        run('%s python manage.py loaddata data/categories_data.json --app %s' % (command,app_name))
        run('%s python manage.py loaddata data/subcategories_data.json --app %s' % (command,app_name))
        run('%s python manage.py loaddata data/socialapp_data.json --app %s' % (command,app_name))


@task
def prepare_sqlclear():
    from django.conf import settings

    not_apps = ["django","allauth."]
    installed_apps = [app for app in settings.INSTALLED_APPS if not any(map(lambda x:x in app,not_apps)) ]


    sqlclear_all = ""
    from subprocess import check_output

    for app in installed_apps:
        command = ["python","manage.py","sqlclear","%s"%app]

        try:
            sqlclear_all += check_output(command, universal_newlines=True)
        except Exception as e:
            pass

    with open("sqlclear.sql", "w") as text_file:
        text_file.write(sqlclear_all)


@task
def reset_db(app_name=''):
    # prepare_sqlclear()

    if app_name:
        run("heroku pg:psql < sqlclear.sql --app %s" % app_name)
        run('heroku run python manage.py syncdb --app % s' % app_name)
        load_data("heroku run",app_name)
    else:
        run("python manage.py dbshell < sqlclear.sql")
        run('python manage.py syncdb')
        load_data()