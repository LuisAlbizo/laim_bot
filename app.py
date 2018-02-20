from flask import Flask, request, render_template
from bokeh.plotting import figure
from bokeh.embed import components
import base64, pickle

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hola Mundo 2</h1>"

@app.route("/mutt")
def patan():
    text = request.args.get('text','sample text')
    return render_template("mutt.html",text=text)

@app.route("/meme")
def meme():
    url = request.args.get('url','/static/images/sky-kitten.jpg')
    top = request.args.get('top','TOP TEXT')
    bottom = request.args.get('bottom','BOTTOM TEXT')
    css1 = request.args.get('css1','')
    css2 = request.args.get('css2','')
    css3 = request.args.get('css3','')
    if css1:
        css1 = base64.b16decode(css1.encode()).decode().strip('[]')
    if css2:
        css2 = base64.b16decode(css2.encode()).decode().strip('[]')
    if css3:
        css3 = base64.b16decode(css3.encode()).decode().strip('{}')
    return render_template('meme.html',url=url,top=top,bottom=bottom,css1=css1,css2=css2,css3=css3)

@app.route("/profile")
def profile():
    with open(base64.b16decode(request.args.get('pkfile','').encode()).decode(),'rb') as pkf:
        cuenta = pickle.load(pkf)
        pkf.close()
    duracion = "%.2f dias" % (sum([m['expiracion'] for m in cuenta['cuenta']['saldo_monedas']])/60/60/24)
    
    #First Plot
    p = figure(plot_width=400, plot_height=240,sizing_mode = 'scale_width')
    p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=10, color="navy", alpha=0.5)
    p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)
    p.square([1, 2, 3, 4, 5], [2, 4, 8, 16,32], size=10, color="#88bbbb", alpha=1)
    p.line([1, 2, 3, 4, 5], [2, 4, 8, 16,32], line_width=3, color="#88bbbb", alpha=1)
    p.toolbar.logo = None
    p.toolbar_location = None
    script, div = components(p)
    return render_template('cuenta.html',cuenta=cuenta,duracion=duracion,script=script,div=div)

app.run(host="127.0.0.1",port=8080,debug=True)

#Luis Albizo 15/02/2018
