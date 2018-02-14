from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hola Mundo 2</h1>"

#app.run(host="177.237.31.25",port=8080)
app.run(host="0.0.0.0",port=8080)




