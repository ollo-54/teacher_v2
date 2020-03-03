set FLASK_APP=app.py
set FLASK_DEBUG=1
flask db migrate
flask db upgrade