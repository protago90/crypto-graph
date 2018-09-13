
import dash
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np 
import pandas as pd  
from datetime import date

# from plotly_builder import network_graph_pre, tseries_graph_pre 
from plotly_onthefly import network_graph_fly, tseries_graph_fly   # custom


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
interval = 5
windows = list(range(year))[::interval]
historic_df = historic_df.tail(year + rolling_corr)


# # customized mst-network & tseries plotly-traces -in advance due delay
# network_graph_figures = network_graph_pre(historic_df, windows, rolling_corr)
# tseries_graph_figures = tseries_graph_pre(bitcoins_df, windows, year)


# DASH APPs-class & server initiation +dashboard web-layout composition
app = dash.Dash(__name__)
server = app.server

app.css.append_css(
	{"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"}
)


app.layout = html.Div([
	html.Div([
		dcc.Graph(
			id='network_graph'
		),
	], className='row'),

	html.Div([
		dcc.Graph(
			id='tseries_graph'
		),
	], className='row'),	

	html.Div([
		dcc.Slider(
			id='slide_roller',
			min=0,
			max=len(windows)-1,
			value=0,
			updatemode='drag',
			marks=[i if (i%10 == 0) else '' for i in windows]
		),
	], className='row'),

	html.Hr(),

	html.Div([
		dcc.Input(id='input_state', value=year),
		html.Button('reset', id='button_reset', n_clicks=0),
		html.Button('o/>', id='button_play_stop', n_clicks=0),
		html.H6('pause!', id='animation_info')
	], className='row'),

	dcc.Interval(
		id='phase_sequencer',
		interval=1*99999,
		n_intervals=0
	)

], className='container', style=dict(width='150%'))


# MAIN-callback: animation alike updates via 'dcc.interavtive' component
# workflow: |upadate ->slider ->plots| so slider manual-control possible
@app.callback(
	Output('slide_roller', 'value'),
	[Input('phase_sequencer', 'n_intervals')] )
def update_slide_roller(n_intervals):
	return min(n_intervals, len(windows)-1)


# SLIDE-callback: values from slider influence network & tseries plots
@app.callback(
	Output('network_graph', 'figure'),
	[Input('slide_roller', 'value')] )
def update_network_graph(slide_value):
	# return network_graph_figures_pre[slider_value]   # in-advence case
	window = slide_value * interval
	return network_graph_fly(historic_df, window, rolling_corr)

@app.callback(
	Output('tseries_graph', 'figure'),
	[Input('slide_roller', 'value')] )
def update_tseries_graph(slide_value):
	# return tseries_graph_figures_pre[slider_value]   # in-advence case
	window = slide_value * interval
	return tseries_graph_fly(bitcoins_df, window, year)


# BUTTON-callback: animation control: updates reset & play/pause state
@app.callback(
	Output('phase_sequencer', 'n_intervals'),
	[Input('button_reset', 'n_clicks')] )
def phase_seq_reset(n_clickseq):
	return 0

@app.callback(
	Output('phase_sequencer', 'interval'),
	[Input('button_play_stop', 'n_clicks')] )
def update_phase_seq(n_clicks):
	if n_clicks % 2 != 0:
		return 1*1500
	else:
		return 1*999999

@app.callback(
	Output('animation_info', 'children'),
	[Input('button_play_stop', 'n_clicks')] )
def animation_info(n_clicks):
	if n_clicks % 2 != 0:
		return 'playing..'
	else:
		return 'pause'


# DASH_app evaluation
if __name__ == '__main__':
	app.run_server(debug=True)