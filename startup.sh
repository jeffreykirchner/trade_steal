echo "*** Startup.sh ***"
apt-get update
echo "Run Migrations:"
python manage.py migrate
echo "Install htop:"
apt-get -y install htop
echo "Install redis"
sysctl vm.overcommit_memory=1
echo madvise > /sys/kernel/mm/transparent_hugepage/enabled
apt-get -y install redis
echo "Start Server:"
redis-server & daphne -b 0.0.0.0 _trade_steal.asgi:application