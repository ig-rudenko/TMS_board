python manage.py migrate --no-input;
celery -A board worker -c 2 -l INFO