from flask_migrate import Migrate
from flaskr import create_app
from models import db, Event, Attendee, Schedule

# Create the app instance
app = create_app()

# Set up the migration environment
migrate = Migrate(app, db)
