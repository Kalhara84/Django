# curd  -  Django + PostgreSQL (users CRUD + login + Expire module)

1. PostgreSQL eke database ekak hadanna:   CREATE DATABASE curd;
2. curd/curd/settings.py -> DATABASES eke PASSWORD (saha wenath ewa) edit karanna
3. cd curd
   pip install -r ../requirements.txt
   python manage.py migrate        (tables hadala default users + dummy combo data insert karanawa)
   python manage.py runserver
4. http://127.0.0.1:8000/     login:  2000 / "2000 rbf"   or   ADMIN / 0777289242

Code thiyenne  curd/postgresql/  app eka athule:
  models.py (usdmast + expire tables) | auth.py | views.py | forms.py | urls.py
  expire_views.py / expire_forms.py   (Expire Module)
  migrations/0001 usdmast, 0002 default users, 0003 expire tables, 0004 dummy combo data
  templates/postgresql/ (expire/ folder eke expire pages) | static/assesst/
