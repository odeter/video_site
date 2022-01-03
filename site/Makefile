SHELL := /bin/bash

VENV_ACTIVATE=. backend/venv/bin/activate
CHRISTOPHER=christopher
# Gnome terminal positions (Simon)
POSFS=80x24+1920+1000
POSBS=80x24+1920+480

# Gnome terminal position (Default)
POSFD=80x24+700+200
POSBD=80x24+630+300

# Postgres database
DBNAME=lasha_db

# env variables:
export URL=http://localhost:5000/apicall
export APIKEY=testkey123
# url for build should be in for mat of 'https://demosite.com'
export BUILD_URL=https://lasha.com

# setting log folder
export BACKEND_PROC_LOG_DIR=logs/

# Database url to the db container
export DATABASE_URL=postgresql://postgres:123test@localhost:5222/postgres

# echo color
RED=\033[0;31m
GREEN=\033[0;32m
BLUE=\033[0;34m
NC=\033[0m

###############################################################################
# Help
###############################################################################

# To catch make call from terminal. Prints available functions
help:
	@echo "Available recipes:"
	@echo "  backend_start     - Launches a terminal with only the Lasha backend"

# Start frontend vue application in a seperate terminal
# frontend_start:
# ifeq ($(shell whoami), ${SIMON})
# 	@gnome-terminal --geometry ${POSFS} --hide-menubar -- bash -c 'cd frontend_vue; npm run dev; bash' 2>/dev/null
# else ifeq ($(shell whoami), ${FREDERIK})
# 	@terminator --new-tab -e 'cd frontend_vue; npm run dev; bash'
# else
# 	@gnome-terminal --geometry ${POSFD} --hide-menubar -- bash -c 'cd frontend_vue; npm run dev; bash' 2>/dev/null
# endif

# start lasha
start_lasha: backend_start

# Start flask backend in a seperate terminal
backend_start:
	@gnome-terminal --geometry ${POSBD} --hide-menubar -- bash -c '$(VENV_ACTIVATE) && cd backend; flask run; bash' 2>/dev/null

## setup docker
setup_db:
	@docker pull postgres && docker run -d --restart unless-stopped --name lasha_db -p 5222:5432 -e POSTGRES_PASSWORD=123test postgres

## connect to db in docker
connect_db:
	@export PGPASSWORD=123test; psql -p 5222 -U postgres -h localhost -d postgres

## clear stopped containers
clear_containers:
	@docker container prune -f

# Starting both front- and backend for "Derant Angle" in seperate reminals
#start_lasha: backend_start frontend_start

drop_db:
	@echo ${DATABASE_URL}
	@psql ${DATABASE_URL} -c "DROP SCHEMA public CASCADE;"
	@psql ${DATABASE_URL} -c "CREATE SCHEMA public;"
	@${VENV_ACTIVATE} && cd backend && rm -rf migrations/ && flask db init && flask db migrate && flask db upgrade

show_db:
	@echo ${DATABASE_URL}
