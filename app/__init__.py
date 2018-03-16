from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import models, routes

if __name__ == '__main__':
   app.run(debug = True, use_reloader=True)

# I need this code to start the server on Heroku. Moved it to the bottom per Eric's suggestion. 

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))