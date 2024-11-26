echo "setup trade_steal"
sudo service postgresql restart
echo "drop trade steal db: enter db password"
dropdb trade_steal -U dbadmin -h localhost -i -p 5433
echo "create database: enter db password"
createdb -h localhost -p 5433 -U dbadmin -O dbadmin trade_steal
echo "restore database: enter db password"
pg_restore -v --no-owner --role=dbowner --host=localhost --port=5433 --username=dbadmin --dbname=trade_steal database_dumps/trade_steal.sql