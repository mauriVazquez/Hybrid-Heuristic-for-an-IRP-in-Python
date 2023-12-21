py .\manage.py migrate
py .\manage.py createsuperuser
py .\manage.py shell -c "from localidades.seeder import seeder"
py .\manage.py shell -c "from ZonaTransporte.seeder import seeder"
py .\manage.py shell -c "from entidades.seeder import seeder"
