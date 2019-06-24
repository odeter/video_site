#!/bin/bash
if [ $# -eq 1 ]; then
    case "$1" in
	-r)
	    echo "-- Beginning Mysql Server..." >&2
	    systemctl start mysql &
	    echo "-- MYSQL server started" >&2
	    echo "-- Beginning Gunicorn..." >&2
	    gunicorn -k gevent -w 5 lasha:app -D &
	    echo "-- Gunicorn Started" >&2
	    ;;
	-e)
	    echo "-- Shutting down Mysql Server..." >&2
	    systemctl stop mysql &
	    echo "-- MYSQL server stopped" >&2
	    echo "-- Shutting down Gunicorn..." >&2
	    pkill -f gunicorn &
	    echo "-- Gunicorn Stopped" >&2
	    ;;
	-s)
	    echo "-- Beginning Mysql Server..." >&2
	    systemctl start mysql &
	    echo "-- MYSQL server started" >&2
	    ;;
	-h|--help)
	    echo "-- -r) To start mysql server and gunicorn." >&2
	    echo "-- -e) To end mysql server and gunicorn." >&2
	    echo "-- -s) To start mysql server only." >&2
	    echo "-- -h) To show help." >&2
	    ;;
	*)
	    echo "-- Invalid option: $1" >&2
	    ;;
    esac
else
    echo "-- Please give a flag, -h for help.." >&2
fi
