web: gunicorn fl:app --logger-class=fl.logger.GunicornLogger --access-logfile=/dev/null --error-logfile=- -b "0.0.0.0:$PORT"
