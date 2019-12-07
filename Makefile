#!/usr/bin/make

include .env

SHELL = /bin/sh
CURRENT_UID := $(shell id -u):$(shell id -g)

export CURRENT_UID

upb:
	docker-compose up -d --force-recreate --build
down:
	docker-compose down
sh:
	docker exec -it /bday_admin_panel /bin/sh
migrations:
	docker exec -it /bday_admin_panel python3 manage.py makemigrations
su:
	docker exec -it /bday_admin_panel python3 manage.py createsuperuser
