
import plotly.graph_objs as go
import networkx as nx
from datetime import datetime


def network_graph(historic_df, windows, rolling_corr):
	''' !!!!!!! '''

    # if windows is int than range(windows, windows) ale as usual

	network_plotly_figures = []

	for window in windows:
		correlates_df = historic_df.iloc[ window:(rolling_corr + window) ]

		# sequence corr-matrix estimation (mst-graph eucliden-distance)
		corr_matrix = correlates_df.corr()
		dist_matrix = (1 - corr_matrix).stack().reset_index()
		dist_matrix.columns = ['coin1', 'coin2','weight']
		graph_matrice = dist_matrix.loc[ 
			dist_matrix['coin1'] != dist_matrix['coin2']
		]

		# package networkx: standard & nst-graph construction
		graph_TS = nx.from_pandas_edgelist(
			graph_matrice, 'coin1', 'coin2', ['weight']
		)
		graph_MST = nx.minimum_spanning_tree(graph_TS)

		# graph-nodes coordinates +callibration bitcoin-coin centrality
		fix_posit = {'bitcoin': (0,0)}
		fix_nodes = fix_posit.keys()
		positions = nx.spring_layout(graph_MST, 
			weight='weight', 
			pos=fix_posit, 
			fixed=fix_nodes,
			scale=3, 
			center=(0,0)
		)

		# mst-graph centrality params: betweeness & to-bitcoin-distance
		bitcenter = nx.single_source_shortest_path_length(
			graph_MST, 'bitcoin'
		)
		betweenness = nx.betweenness_centrality(graph_MST)

		# package plotly: mst edge traces-contruction
		edge_trace = go.Scatter(			
			x = [],
			y = [],
			line = dict(width=1.5, color='#888'), 
			opacity = 0.3,
			hoverinfo = 'none',
			name = window,
			mode = 'lines'
		)

		# plot parametrization -edges coordinates
		for edge1, edge2, weight in graph_MST.edges().data('weight'):
			x0, y0 = positions[edge1]
			x1, y1 = positions[edge2]
			edge_trace['x'] += tuple( [x0, x1, None] )
			edge_trace['y'] += tuple( [y0, y1, None] ) 

		# package plotly: mst node traces-contruction
		node_trace = go.Scatter(
			x = [],
			y = [],
			text = [],
			hoverinfo = 'text',
			name = window,
			mode = 'markers', 
			marker = dict(
				showscale = True,
				colorscale='YlGnBu', 
				reversescale = False,
				opacity = 0.9,
				cmin = 0.0,
				cmax = 0.6,
				size = [],
				color = [],
				colorbar = dict(
					thickness = 12,
					title = "Graph Centrality Metrics: "
							"Degree [size] & Betweenes [color]",
					xanchor = 'left',
					titleside = 'right'),
				line = dict(width = [], color='black') ) 
		)

		# plot parametrization -nodes coordinates
		for node in graph_MST.nodes():
			x, y = positions[node]
			node_trace['x'] += tuple([x])
			node_trace['y'] += tuple([y])

		# information for nodes interactive display capabilities
		for n, nghbr in enumerate( graph_MST.adjacency() ):
			# print("n: {}  + {}".format(n, nghbr[1]))
			node_trace['marker']['color'] += tuple( 
				[ betweenness[nghbr[0]] ] 
			)
			node_trace['marker']['size'] += tuple(
				[len(nghbr[1]) * 5 + 20] 
			) 
			node_trace['marker']['line']['width'] += tuple(
				[2 if nghbr[0] == 'bitcoin' else .2]
			)
			node_trace['text'] += tuple([
				"COIN: <b>> {} <</b>"
				"<br><i>distance to Bitcoin: {}</i>"
				"<br><i>neighbours: {}</i>"
				"<br><i>betweenness: {}</i>"
				"".format(nghbr[0], 
						  bitcenter[nghbr[0]], 
						  len(nghbr[1]), 
						  round(betweenness[nghbr[0]],6) ) 
			])

		mst_layout = go.Layout(
			title = "<br><b>MST graph representation"
					"of Cryptocurrency Market</b>",
			titlefont = dict(size=15),
			showlegend = False,
			hovermode = 'closest',
			margin = dict(b=5, l=5, r=5, t=15),
			# annotations = [dict(
			# 	# text = "LINK: <a href='https://plot.ly'>PLOTLY</a>",
			# 	showarrow = False,
			# 	xref = "paper", 
			# 	yref="paper",
			# 	x = 0.005, 
			# 	y=-0.002) ],
			xaxis = dict(
				showgrid=False, 
				zeroline=False,
				showticklabels=False, 
				range=[-3,4] ),  
			yaxis = dict(
				showgrid=False, 
				zeroline=False, 
				showticklabels=False,
				range=[-5,5] )
		)

		network_plotly_figures.append(
			go.Figure(data=[edge_trace, node_trace], layout=mst_layout)
		)

	return network_plotly_figures


def tseries_graph(bitcoins_df, windows, year):
	''' o jednym oknie symulacju..'''

	tseries_plotly_figures = []

	for window in windows:

		series_trace = go.Scatter(
			y = bitcoins_df.values[:(window + 1)], # pandas series!
			x = list(range(year))[:(window + 1)],
			line = dict(width=1.5, color='#888'), 
			opacity = 0.6,
			hoverinfo = 'text',
			text = '{:%d, %b %Y}'.format( bitcoins_df.index[window] ),
			fill = 'tozeroy',
			mode = 'lines+markers'
		)

		fixed_trace = go.Scatter(
			y = bitcoins_df.values, # pandas series!
			x = list(range(year)),  
			line = dict(width=1, color='black'), 
			opacity = 0.2,
			#hoverinfo = 'none',
			name = 'BTC',
			#text = list(bitcoins_df.index),
			#hoverinfo = 'text',
			mode = 'lines+markers'
		)

		tseries_plotly_figures.append(
			go.Figure(data=[fixed_trace, series_trace])
		)

	return tseries_plotly_figures