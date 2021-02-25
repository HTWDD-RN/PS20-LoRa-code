import json
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

from converter import ReturnRenderGeoData, renderGeoData, getGatewayIds

default_zoom = 14
default_mapbox_style = 'open-street-map'
default_schrittgröße = 10
# default_gatewayId = 'eui-dca632ffff85afc2'
default_gatewayId = 'eui-b827ebfffead3656'

csv_file_in = 'archive/2021_02_22_data_merged.csv'
geo_json = 'data.geo.json'
csv_file = 'id-rssi.csv'

rssi_min = -120
rssi_max = 0
schrittgröße = 10

# aufbereiten der Daten aus csv_file_in in geo_json und csv_file

ret = renderGeoData(csv_file_in, geo_json, csv_file, rssi_max, rssi_min, default_schrittgröße, default_gatewayId)

rssi_min = int(ret.rssi_min)
rssi_max = int(ret.rssi_max)

default_center_lon=ret.middle[0] # '13.737262'
default_center_lat=ret.middle[1] # '51.050407'

mapboxes = {
    0: 'open-street-map',
    1: 'white-bg',
    2: 'carto-positron',
    3: 'carto-darkmatter',
    4: 'stamen-terrain',
    5: 'stamen-toner',
    6: 'stamen-watercolor'
}

# Initialisierung der app
app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)

with open(geo_json, "r") as f:
    geojson = json.load(f)

# init data frame
df = pd.read_csv(csv_file, sep=',', dtype={"id": str})
scatter = pd.read_csv(csv_file_in)
# print(scatter[scatter['gtw-id'] == default_gatewayId])


def get_fig(zoom=default_zoom, mapbox_style=default_mapbox_style, center_lat=default_center_lat, center_lon=default_center_lon):
    fig = px.choropleth_mapbox(df, geojson=geojson, locations='id', color='rssi',
        color_continuous_scale="Viridis",
        range_color=(int(rssi_min),int(rssi_max)),
        zoom=zoom,
        opacity=0.5,
        mapbox_style=mapboxes.get(mapbox_style,'open-street-map'),
        center={'lat':float(center_lat), 'lon':float(center_lon)},
        labels={'rssi', 'RSSI'},
        title="LoRa Map",
        height=800
    )
    fig.add_trace(px.scatter_mapbox(scatter[scatter['gtw-id'] == default_gatewayId], lat="lat", lon="long", hover_name="gtw-id", hover_data=["rssi"], color='rssi', range_color=(rssi_min,rssi_max), color_continuous_scale="Viridis").data[0])
    # fig.update_geos(fitbounds="locations")
    fig.update_layout(
        autosize=True, showlegend=True,
    margin={"r":0, "t":0, "l":0, "b": 0}
    )
    return fig


app.layout = html.Div(children=[
    html.H3("LoRa Map", id="page_header"),
    dcc.Loading(id='loading', children=[
        dcc.Graph(
            id='map_graph',
            figure=get_fig()
        )
    ], fullscreen=False, type='default'),
    html.Form(children=[
        html.P(
            children=["Zoom: ", dcc.Slider(
                id='zoom_slider',
                min=1, max=20, marks={str(zoom): str(zoom) for zoom in range(1,21)}, step=None,
                value=default_zoom
            )]
        ),
        # TODO: change to dropdown
        html.P(
            children=["Map: ", dcc.Slider(
                id='mapbox_style_slider',
                min=0, max=6,
                marks={str(mapbox_style): str(mapboxes[mapbox_style]) for mapbox_style in mapboxes},
                step=None,
                value=0
            )]
        ),
        html.P(
            children=["Schrittgröße: ", dcc.Slider(
                id='schrittgröße_slider',
                min=1, max=60,
                marks={str(schrittgröße): str(schrittgröße) for schrittgröße in range(1,60)},
                step=None,
                value=default_schrittgröße
            )]
        ),
        html.P(
            children=[
                "Middle Lat: ", dcc.Input(
                    id='center_lat_text',
                    type='text',
                    value=default_center_lat
                ),
                "Middle Lon: ", dcc.Input(
                    id='center_lon_text',
                    type='text',
                    value=default_center_lon
                )
            ]
        ),
        html.P(
            children=[
                "Gateway-ID", dcc.Dropdown(
                    id='gatewayid_dropdown',
                    options=[{'label': elem, 'value': elem} for elem in getGatewayIds(csv_file_in) ],
                    value=default_gatewayId
                )
            ]
        )
        #,html.Button(children=['set_zoom'], type='submit', id='set_zoom_button')

    ], id='set_zoom_form')
])

# ergänzt Eventhandler
@app.callback(Output('map_graph', 'figure'),[   Input('zoom_slider', 'value'), 
                                                Input('mapbox_style_slider', 'value'),
                                                Input('schrittgröße_slider', 'value'),
                                                Input('center_lat_text', 'value'),
                                                Input('center_lon_text', 'value'),
                                                Input('gatewayid_dropdown', 'value')
                                            ])
def set_params(zoom, mapbox_style, schrittgröße, center_lat_text, center_lon_text, gatewayid):
    # aufbereiten der Daten aus csv_file_in in geo_json und csv_file

    global geojson, default_center_lon, default_center_lat, df, default_gatewayId, rssi_min, rssi_max

    ret = renderGeoData(csv_file_in, geo_json, csv_file, 0, -120, schrittgröße, gatewayid)

    default_center_lon = ret.middle[0] # '13.737262'
    default_center_lat = ret.middle[1] # '51.050407'
    default_gatewayId = gatewayid
    
    rssi_min = int(ret.rssi_min)
    rssi_max = int(ret.rssi_max)

    with open(geo_json, "r") as f:
        geojson = json.load(f)

    # init data frame
    df = pd.read_csv(csv_file, sep=',', dtype={"id": str})

    return get_fig(zoom, mapbox_style, center_lat_text, center_lon_text)


# Starten der App auf einem Webserver
if __name__ == '__main__':
    app.run_server( port=8080, 
                    debug=True,
                    host='0.0.0.0' # now it's possible to connect outside the localhost
    )
