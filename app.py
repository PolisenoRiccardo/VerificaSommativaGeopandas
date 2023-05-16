import io
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, Response
from shapely.ops import cascaded_union
app = Flask(__name__)

# plt.savefig('grafico.png')

df = pd.read_csv("sosta_turistici.csv", delimiter=";")
soste = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df['LONG_X_4326'], df['LAT_Y_4326']), crs = 'EPSG:4326')
soste3857 = soste.to_crs(3857)

quartieri = gpd.read_file('ds964_nil_wm.zip')
quartieri3857 = quartieri.to_crs(3857)
quartieriSenzaParcheggio = quartieri3857[~quartieri3857.intersects(cascaded_union(soste3857.geometry))]

@app.route('/', methods=['GET'])
def home():   
    return render_template('home.html', quartieriNomi = quartieriSenzaParcheggio['NIL'].tolist())

@app.route('/quartiere', methods=['GET'])
def quartiere():
    inQuartiere = request.args.get('quartieri')
    quartiereTrovato = quartieri3857[quartieri3857['NIL'].str.contains(str(inQuartiere))]
    if len(quartiereTrovato) > 0:
        fig, ax = plt.subplots()
        soste3857[soste3857.geometry.intersects(cascaded_union(quartiereTrovato.geometry))].plot(ax = ax, color='r')
        quartiereTrovato.plot(ax=ax, facecolor='None')
        ctx.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    else: 
        return 'errore'

@app.route('/grafico', methods=['GET'])
def grafico():
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=32245, debug=True)