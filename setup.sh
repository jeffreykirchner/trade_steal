echo "setup trade_steal"
sudo service postgresql restart
echo "drop db: enter db password"
dropdb trade_steal -U dbadmin -h localhost -i
echo "create database: enter db password"
createdb -h localhost -U dbadmin -O dbadmin trade_steal
source _trade_steal_env/bin/activate
python manage.py migrate
echo "create super user"
python manage.py createsuperuser 
echo "load fixtures"
python manage.py loaddata main.json
echo "setup done"
python manage.py runserver