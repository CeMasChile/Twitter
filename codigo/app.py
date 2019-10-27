import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
<<<<<<< HEAD

# direction of the css file
direction = './OutputStreaming_20191026-153306.csv'
=======
from main import get_keywords
import numpy as np



# direction of the css file
direction = './OutputStreaming_20191026-225744.csv'


# ACÁ SE VAN A CONSTRUIR LAS PARTES DE LA APP, EN ESPECÍFICO, DE LA PARTE DE PALABRAS

df = pd.read_csv(direction)
key_words = get_keywords()

def get_KWdic(df):
    '''
    devuelve un diccionario con los índices del df que tienen la palabra
    '''
    return {key_words[i]: df[df['text'].str.contains(key_words[i])].index for i in range(len(key_words))}


# dropdown menu
options_dropdown = [{'label' : 'Todo', 'value' : 'All'}] + \
                   [{'label' : key_words[i], 'value' : key_words[i]} for i in range(len(key_words[:9]))]

dropdown_menu = dcc.Dropdown(
    id='dropdown',
    options=options_dropdown,
    value='All',
    multi=True,
    placeholder="Seleccione las palabras clave"
    )


#  time inteval
time_interval = dcc.Interval(
    id='interval',
    interval=30 * 1 * 1000,  # in milliseconds
    n_intervals=0
    )


# figure
figure = dcc.Graph(id='plot')




# ACÁ TERMINA



texto_explicativo = 'En esta página usted tiene acceso a distintas herramientas para filtrar ' \
                    'los datos que desde el CeMAS dejamos a su disposición.'
>>>>>>> 2622aa5420a4d7ff4524466e955fa30c7af6c800

# css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# se crea un objeto dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

<<<<<<< HEAD
=======




def getDf2plot(direction):
    df = pd.read_csv(direction)
    DF = pd.to_datetime(df['created_at']).dt.floor('min')
    max_date = DF.max()
    DF = pd.to_datetime(DF.loc[DF < max_date])
    DF = DF.sort_index().value_counts()
    data = {'date': DF.index, 'freq': DF.values}
    data = pd.DataFrame(data).sort_values('date')
    return data


>>>>>>> 2622aa5420a4d7ff4524466e955fa30c7af6c800
# layout config
app.layout = html.Div([
    html.H1('¡Bienvenid@ al DashBoard del CeMAS!'),
    # figure object
    html.Div(texto_explicativo),
    dropdown_menu,
    figure,
    # interval in milliseconds to update the figure
<<<<<<< HEAD
    dcc.Interval(
        id='interval',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
=======
    time_interval
>>>>>>> 2622aa5420a4d7ff4524466e955fa30c7af6c800
])



@app.callback(
    Output('plot', 'figure'),           # the output is what to modify and which property
    [Input('interval', 'n_intervals')]  # input is the trigger and the property
)
# how to update the figure
def update_graph(n):        # no sé pq está esa 'n' ahí, pero no la saquen que si no no funciona
    # update a pandas DataFrame
    df = pd.read_csv(direction)

    # assign the 'created_at' column to the histogram
    data = {
        'data': [go.Histogram(
            x=df['created_at']
        )]
    }

    return go.Figure(data)  # returns the figure to be updated



# acá va la accion dropdown    @app.callback(
# acá va la accion dropdown        Output('plot', 'figure'),
# acá va la accion dropdown        [Input('dropdown','values')]
# acá va la accion dropdown    )
# acá va la accion dropdown    def update_dropdown(n):




if __name__ == '__main__':
    app.run_server(debug=True)
