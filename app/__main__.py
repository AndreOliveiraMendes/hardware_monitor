import sys

from app import create_app
from app.jobs.cleanup import cleanup
from app.jobs.notifications import process_notifications
from config import DEBUG_MODE, FLASK_HOST, FLASK_PORT

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "cleanup":
            cleanup()
        elif sys.argv[1] == "notifications":
            process_notifications()
    else:
        app = create_app()
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG_MODE)