import os

from app import create_app

#config_name = os.getenv('FLASK_CONFIG')
config_name = "development"
app = create_app(config_name)
app.app_context().push()

### Create some user data ###
#from app import db_main_data
#db_main_data.create_vid_test(50)

### Import Error pages ###
from app import error_handler

if __name__ == '__main__':
    app.run()
