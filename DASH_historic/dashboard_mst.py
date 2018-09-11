
import dash
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np 
import pandas as pd  
from datetime import date

from plotly_builder import network_graph, tseries_graph  # custom


# resources preprocesing ->analysis data-horizon & NaNs coins removal
historic_df = pd.read_csv(
	'crypto_history_top50', header=0, index_col=0, parse_dates=True
)
delta = (date(2018, 2, 1) - date(2016, 10, 31)).days 
historic_df = historic_df.sort_index()
historic_df = historic_df.loc[:, historic_df.notna().sum() >= delta]
historic_df = historic_df.fillna(method='ffill')


# fixed animation-range: 2017-02-01:2018-02-01 -> "0:365" -366 sequences
year = (date(2018, 2, 1) - date(2017, 2, 1)).days + 1
bitcoins_df = historic_df['bitcoin'].tail(year)


# hist-data log-return for stacjonarity ->for mst-graph construction
historic_df = np.log( (historic_df / historic_df.shift(1)).dropna() )
historic_df.drop(['tether'], axis=1, inplace=True)   # optional


# animation params: day-units-> rolling-corr & single-seq step-interval
rolling_corr = 45   # max 92
interval = 10
windows = list(range(year))[::interval]
historic_df = historic_df.tail(year + rolling_corr)


# customized mst-network & tseries plotly-traces -in advance due delay
network_graph_figures = network_graph(historic_df, windows, rolling_corr)
tseries_graph_figures = tseries_graph(bitcoins_df, windows, year)



# DASH APPs-class & server initiation +dashboard web-layout composition
app = dash.Dash()
server = app.server

app.css.append_css(
	{"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div([
	html.Div([
		dcc.Graph(
            id='network_graph'
        ), 
	], className="row"),

	html.Div([
		dcc.Graph(
            id='tseries_graph'
        ), 
	], className="row"),	

	html.Div([
		dcc.Slider(
			id='slide_roller',
			min=0,
			max=len(windows)-1,
			#step=None,
			value=0,
			updatemode='drag',
			marks=windows #[str(i) if (i%interval == 0) else '' for i in windows]
        )
	], className="row"),
# {i: '{}'.format(i) if (i % 10 == 0) else '' for i in range(len(historic_df))}
	html.Div([
		dcc.Input(id='input_state', value=0)
	], className="row")
], className="container", style=dict(width='150%'))


@app.callback(
	Output('network_graph', 'figure'),
	[Input('slide_roller', 'value')] )
def update_network_graph(slider_value):
	return network_graph_figures[slider_value]

@app.callback(
	Output('tseries_graph', 'figure'),
	[Input('slide_roller', 'value')] )
def update_tseries_graph(slider_value):
	return tseries_graph_figures[slider_value]


@app.callback(
	Output('input_state', 'value'),
	[Input('slide_roller', 'value')] )
def update_network_graph(value):
	return value*interval


if __name__ == '__main__':
	app.run_server(debug=True)