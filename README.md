# time-tracker
Basic timetracker app. Built with Django

Following must be installed:
- Docker

To run via docker:
```
docker compose up --build -d
```

To migrate database:
```
docker compose run --rm web ./manage.py migrate
```

To create superuser:
```
docker compose run --rm web ./manage.py createsuperuser
```


To run tests:
```
docker compose run --rm web ./manage.py tests
```
