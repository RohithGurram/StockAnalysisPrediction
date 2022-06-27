from cmath import inf
from multiprocessing.dummy import Value
import py_compile
from pydoc import classname
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from pyparsing import line
from matplotlib.pyplot import figure

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("Welcome to the Stock Dash App!", className="start"),
        html.H3(["Stock code input:"],className='start'),
        html.Div([dcc.Input(id='my-id',value='', type='text'),
        html.Button('Submit', id='subm', n_clicks=0)]),
        html.Div([dcc.DatePickerRange(
                id='date-picker-range',
                initial_visible_month=date.today(),
                start_date_placeholder_text='Start date',
                end_date=date.today(),
                display_format='DD/MM/YYYY',
            )],className="plotly-datepicker"),

        html.Div([
        html.Button(['Stock price'],id='stock-but',className='button'),
        html.Button(['Indicators'],id='indi-but',className='button')]),
    html.Div([
        dcc.Input(value='Days of forecast', type='text'),
        html.Button(['Forecast'],className='button'),]),],className="nav"),
    html.Div([
        html.Div(children=[],id="head",className="header"),
        html.Div(children=[], id="description", className="decription_ticker"),
        html.Img(src=" ",id="img"),
        dcc.Graph(id="graphs-content"),
        dcc.Graph(id="main-content"),
html.Div([
# Forecast plot
], id="forecast-content")
],
className="content")],className="container")
@app.callback([
    Output("head", "children"),
    Output("description","children"),
    Output("img","src")
    ],
    [Input('subm', 'n_clicks')],
    [State('my-id', 'value')]
)
def update_data(n_clicks,valu):
    global store
    store=valu
    if n_clicks is None:
        raise PreventUpdate
    else:
        ticker = yf.Ticker(valu)
        inf = ticker.info
        df = pd.DataFrame().from_dict(inf, orient="index").T
        lit=[df["longName"]]
        lit.append(df["longBusinessSummary"])
        lit.append(df["logo_url"][0])
        return lit
@app.callback(
    Output("graphs-content", "figure"),
    [Input('date-picker-range','start_date')],
    [Input('date-picker-range','end_date')],
    [Input('stock-but','n_clicks')],
)
def modify(st,en,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        df = yf.download(store,st,en)
        df.reset_index(inplace=True)
        fig = get_stock_price_fig(df)
        return fig
def get_stock_price_fig(df):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],),
    ])
    fig.update_layout(
    title={
        'text': "Candlestick Chart",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    xaxis_title="Date",
    yaxis_title="Price")
    return fig
@app.callback(Output('graphs-content', 'style'), [Input('stock-but','n_clicks')])
def hide_graph(n_clicks):
    if n_clicks is not None:
        return {'display':'block'}
    else:
        return {'display':'none'}
@app.callback(Output('main-content', 'style'), [Input('indi-but','n_clicks')])
def hide_grap(n_clicks):
    if n_clicks is not None:
        return {'display':'block'}
    else:
        return {'display':'none'}
@app.callback(Output('img', 'style'), [Input('subm','n_clicks')])
def hide_img(n_clicks):
    if n_clicks is not None:
        return {'display':'block'}
    else:
        return {'display':'none'}
@app.callback(
    Output("main-content","figure"),
    [Input('date-picker-range','start_date')],
    [Input('date-picker-range','end_date')],
    [Input('indi-but','n_clicks')],
)
def modif(st,en,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        df = yf.download(store,st,en)
        df.reset_index(inplace=True)
        fig = get_more(df)
        return fig
def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
    x= "Date",
    y= "EWA_20",
    title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines')
    return fig
if __name__ == '__main__':
    app.run_server(debug=True)
