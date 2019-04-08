from flask import Flask
from Service import UserCrud

app = Flask(__name__)

UserCrud.user(app)

if __name__ == '__main__':
    app.run()
