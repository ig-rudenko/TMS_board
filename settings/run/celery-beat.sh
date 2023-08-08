python manage.py migrate --no-input;
celery -A board beat -l INFO -S django