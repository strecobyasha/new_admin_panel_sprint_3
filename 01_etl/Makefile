include ./app/config/.env
#vars
env_file = --env-file ./app/config/.env
app = 01_etl-web-1
transfer = 01_etl-transfer-1
db = 01_etl-db-1
nginx = 01_etl-nginx-1
elastic = 01_etl-elastic-1


# Порядок запуска:
# 	build, up
# 
# Если БД отсуствует:
# 	create_schema, migrate, fill_db
#
# Если нужен доступ в админку:
#	collect_static, create_superuser
#
# Отложенный запуск загрузчика данных в ES:
# 	run_transfer (автоматически останавливается после одного прогона скрипта).


help:
	@echo "Makefile commands:"
	@echo "build"
	@echo "up"
	@echo "create_schema"
	@echo "migrate"
	@echo "collect_static"
	@echo "create_superuser"
	@echo "fill_db"
	@echo "run_transfer"
	@echo "app_connect"
	@echo "db_connect"
	@echo "transfer_connect"
build:
	docker-compose -f docker-compose.yml ${env_file} build $(c)
up:
	docker-compose -f docker-compose.yml ${env_file} up -d --no-start
	docker-compose -f docker-compose.yml ${env_file} up -d db -d web -d nginx -d elastic
create_schema:
	docker exec -it ${db} psql --username=${DB_USER} --dbname=${DB_NAME} -c \
	'CREATE SCHEMA IF NOT EXISTS content;'
migrate:
	docker-compose exec web ./manage.py migrate
collect_static:
	docker-compose exec web ./manage.py collectstatic --noinput
create_superuser:
	docker-compose exec web ./manage.py createsuperuser --email=admin@mail.com --noinput
fill_db:
	docker-compose exec web python ./sqlite_to_postgres/load_data.py
run_transfer:
	docker-compose -f docker-compose.yml ${env_file} up -d transfer
app_connect:
	docker exec -it ${app} sh
db_connect:
	docker exec -it ${db} psql --username=${DB_USER} --dbname=${DB_NAME}
transfer_connect:
	docker exec -it ${transfer} sh
