#!/bin/sh

# defaults
WORKERS=${GUNICORN_WORKERS:-4}
BIND=${GUNICORN_BIND:-0.0.0.0:5000}
APP=${GUNICORN_APP:-wsgi:app}
TIMEOUT=${GUNICORN_TIMEOUT:-30}
LOG_LEVEL=${GUNICORN_LOG_LEVEL:-info}

# reload (dev)
if [ "$GUNICORN_RELOAD" = "true" ]; then
    RELOAD="--reload"
else
    RELOAD=""
fi

echo "Starting gunicorn:"
echo "  workers: $WORKERS"
echo "  bind: $BIND"
echo "  app: $APP"
echo "  reload: $GUNICORN_RELOAD"

exec gunicorn $RELOAD \
    -w $WORKERS \
    -b $BIND \
    --timeout $TIMEOUT \
    --log-level $LOG_LEVEL \
    $APP
