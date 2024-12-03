echo "*** Startup.sh ***"
app-get update
echo "Run Migrations:"
python manage.py migrate
echo "Install htop:"
apt-get -y install htop
echo "Install redis"
apt-get -y install redis
echo "Start Daphne:"
redis-server & daphne -b 0.0.0.0 _trade_steal.asgi:application