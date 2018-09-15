
import dash
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np 
import pandas as pd  
from datetime import date

# from plotly_builder import network_graph_pre, tseries_graph_pre 
from plotly_onthefly import network_graph_fly, tseries_graph_fly


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
rolling_corr = 60   # max 92
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

# DAHBOARD web-composition
app.layout = html.Div([
	
	html.Div([
		html.Img(src="assets/cryptoBIT.png",
				 style={'width': '4.25%', 'float': 'left'}
		),
		html.H1('. CryptoBit',
				style={'margin-bottom': '12',
					   'margin-top': '5',
					   'font-size': '34',
					   'text-align': 'left',
					   'float': 'left'}
		),
		html.Img(src="assets/prologo_UW.png",
				 style={'width': '14%', 'float': 'right'}
		),
		html.Div(dcc.Markdown('''*❖ Postgraduate thesis-project in* [
							  🔗](http://datascience.wne.uw.edu.pl/)*-DataScience  .*'''
				),
				style={'float': 'right', 'text-align': 'right', 'margin-top': '22'}
		)
	],
	className='row' ),

	html.Div([
		dcc.Slider(
			id='slide_roller',
			min=0,
			max=len(windows)-1,
			value=0,
			updatemode='drag',
			marks=['' if (i%300 == 0) else '' for i in windows]
		),
		dcc.Interval(
			id='phase_sequencer',
			interval=1*99999,
			n_intervals=0
		)
	],
	style={'margin-bottom': '14', 'margin-top': '0'},
	className='row' ),

	html.Div([
		html.Div([
			dcc.Markdown('''*Graph theory application in hyped-realm of cryptocurrencies.* **- "Minimal Spanning Tree" -** *net-structure as reflection of the dependencies between coins. Potentialy, mechanism of turning t.series correlates into graph's edge-distances should provide, otherwise elusive, introspection into formated clusters.* **⌘**'''
			),
			html.P('---------------- PAUSE ----------------', 
				   id='animation_info',
				   style={'margin-bottom': '0',
				   		  'margin-top': '30',
				   		  'font-size': '11',
				   		  'font-style': 'bold'} 
			),
			html.Button('■', id='button_reset', n_clicks=0),
			html.Button('▶▮', id='button_play_stop', n_clicks=0)
		],
		style={'margin-top': '32', 'float': 'left', 'text-align': 'center'},
		className='three columns' 
		),
		dcc.Graph(id='network_graph',
				  style={'width': '78%', 'float': 'right'},
				  className='nine colummns'
		),
	], 
	className='row' ),

	html.Div(
		dcc.Graph(id='tseries_graph'),
	className='row' ),

	html.Div(
		dcc.Markdown('''**⌘** TECHnicals:: *simulation data-horizon in 2017-2-1 : 2018-2-1* | *sequence interval of {} days* | *correaltion-matrix for 'MSTgraph' based on {} days window* **⌘** TECHcoins:: *top23 due to 2018-2-1 market-cap* | *'bitcoin' centerd -quotations nominated in usd* | *others: ethereum ripple stellar neo litecoin nem dash monero lisk ethereum-classic zcash steem stratis bitshares bytecoin-bcn siacoin verge ardor waves augur dogecoin decred* '''.format(interval, rolling_corr)
		),
	style={'text-align': 'center', 'margin-top': '26'},
	className='row' ),

	html.Hr(style={'margin-top': '0', 'margin-bottom': '30'}),
	
	html.Div(
		dcc.Markdown(
			'''*Dashboard realised as side-project of postgraduate thesis commited during* [🔗](http://datascience.wne.uw.edu.pl/)**DSinR** *studies at UW: "Data Science in Bussiness Applications -workshops with R-language". My attention was mainly dedicated to addoption of widely understood Machine Learning methods in realm of algorithimc supported strategies. To precise: **"Potential of MST graph and LSTM neural-nets in Cryptocurrencies crashes predition"**. Dissertation written under direct supervision of head of DS post-studies* [🔗](http://coin.wne.uw.edu.pl/pwojcik)*Dr Piotr Wójcik from the Quantitative Finance Institiute. Inspiration for "Minnimal Spanning Tree" cames from 'Physics of Complexity'* [🔗](https://usosweb.uw.edu.pl/kontroler.php?_action=katalog2%2Fprzedmioty%2FpokazPrzedmiot&kod=1100-WFZ-OG&lang=en)*course lectured by* [🔗](http://www.fuw.edu.pl/~erka/Ryszard_Kutner/Home.html)*Prof. Ryszard Kutner from Experimental Physics Institiute. ..~Still studying a promise of shocks early-detection system.. <IN PROGRES>. Resources: paper+code available at GitHub* [🔗](https://github.com/Protago90/grad.thesis_DS-cryptoBit)*repository.*''' 
		),
	style={'text-align': 'justify', 'margin-bottom': '20'},
	className='row' ),

	html.Div([
		html.Img(src="assets/logo_WNE.jpg",
				 style={'width': '26%', 'float': 'left'}
		),
		html.A(html.Img(src="assets/linkedin.png",
				 		style={'width': '4%', 'float': 'right'}
			  ), href="https://www.linkedin.com/in/protago90/",
		),
		html.A(html.Img(src="assets/github.png",
				 		style={'width': '3.55%', 'float': 'right'}
			  ), href="https://github.com/Protago90"
		),
		html.H2('by Michał Gruszczyński  ➟',
				style={'margin-top': '16',
					   'font-size': '15',
					   'float': 'right',
					   'text-align': 'center'},
				className='three columns'
		),
	], 
	className='row' )

],
style={'width' :'100%'},
className='container' )


# MAIN-callback: animation alike updates via 'dcc.interval' component
# flow: |upadate ->slider ->plots|  so plots control via slider possible
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
		return 1*1200
	else:
		return 1*999999

@app.callback(
	Output('animation_info', 'children'),
	[Input('button_play_stop', 'n_clicks')] )
def animation_info(n_clicks):
	if n_clicks % 2 != 0:
		return '--------------- PLAYING ---------------'
	else:
		return '---------------- PAUSE ----------------'


# CryptoBIT dash_app evaluation
if __name__ == '__main__':
	app.run_server(debug=True)