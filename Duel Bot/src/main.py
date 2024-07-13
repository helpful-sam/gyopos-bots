from flask import Flask
import os

app = Flask(__name__)

# Import routes
import bot_handler

if __name__ == '__main__':
    app.run(debug=True)