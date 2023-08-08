python manage.py migrate --no-input;
gunicorn --bind 0.0.0.0:8000 -w 2 board.wsgi:application;