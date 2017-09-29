
## Synopsis

Django project with math tournaments application, where user can subscribe to different rounds of tournaments except final round and when round start he can get acces to pass tasks from round. Also user can view table of top participants in the tournament.
User have access to final round, if he in top N list of who have the maximum score in tournier.
Application has forms of creating and editing tournaments, for users with the appropriate privileges.

## Installation

Default installation of Django project. Clone this repo.

Install all requirements.
```
pip install -r requirements/base.txt
```

Add '.env' file with all settings in [settings.py](./math_tournaments/blob/master/math_tournaments/math_tournaments/settings.py) which loaded with 'os.getenv'.
