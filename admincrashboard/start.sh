service cron start
service ssh start
sudo -u crashboard ./venv/bin/gunicorn --chdir app --bind [::]:5000 main:app #python3 app/main.py #gunicorn --bind [::]:5000 main