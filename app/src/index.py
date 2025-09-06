# this will hold flask logic
from flask import Flask

app = Flask(__name__)


@app.route("/about")

def home() : 
    return 'hello from flask in the about page'


if __name__ == '__main__':
    app.run(debug=True)
