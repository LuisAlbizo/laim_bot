from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hola Mundo 2</h1>"

@app.route("/mutt")
def patan():
    text = request.args.get('text','sample text')
    return render_template("mutt.html",text=text)

#@app.route("/profile/<int:ID>")

app.run(host="127.0.0.1",port=8080,debug=True)

#Luis Albizo 15/02/2018
