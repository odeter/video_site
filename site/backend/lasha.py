import os
from dotenv import load_dotenv
from app import create_app

config_name = os.getenv('FLASK_STATE', None)
#config_name = "development"
static_path = "/static"
login_view = "login"
app = create_app(config_name, static_path, login_view)
app.app_context().push()

### Import Error pages ###
from app import error_handler

if __name__ == '__main__':
    load_dotenv('.env')
    app.run()
