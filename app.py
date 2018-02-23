from flask import Flask, request, render_template
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Label
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
    duracion = "%.2f dias" % (cuenta['cuenta']['saldo_duracion']/60/60/24)
    data = cuenta['data']
    datavalor = [d['data']['saldo_valor'] for d in data]
    datatiempo = [int(d['data']['saldo_duracion']/60/60) for d in data]
    #Plot
    p = figure(plot_width=400, plot_height=240,sizing_mode = 'scale_width',
        title = 'Relacion Duracion(horas)-Valor total')
    p.circle(range(len(datavalor)), datavalor, size=4, color="navy", alpha=0.5)
    p.line(range(len(datavalor)), datavalor, line_width=3, color="navy", alpha=0.5)
    p.square(range(len(datatiempo)), datatiempo, size=4, color="#88bbbb", alpha=1)
    p.line(range(len(datatiempo)), datatiempo, line_width=3, color="#88bbbb", alpha=1)
    p.toolbar.logo = None
    p.toolbar_location = None
    script, div = components(p)
    return render_template('cuenta.html',cuenta=cuenta,duracion=duracion,script=script,div=div)

app.run(host="127.0.0.1",port=8080,debug=True)

#Luis Albizo 15/02/2018
