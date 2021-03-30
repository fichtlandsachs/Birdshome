#source env/bin/activate
export FLASK_ENV=development
export ENV=development
gunicorn3 --bind 0.0.0.0:5000 --threads 5 -w 1 --timeout 120 app:app
