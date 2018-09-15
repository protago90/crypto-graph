
import plotly.graph_objs as go
import networkx as nx


def network_graph_fly(historic_df, window, rolling_corr):
	'''function for on-the-fly poin in time network-figure generation'''

	correlates_df = historic_df.iloc[ window:(rolling_corr + window) ]

	# sequence corr-matrix estimation (mst-graph eucliden-distance)
	corr_matrix = correlates_df.corr()
	dist_matrix = (1 - corr_matrix).stack().reset_index()
	dist_matrix.columns = ['coin1', 'coin2', 'weight']
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
		scale=1, 
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
		textposition = 'top right',
		hoverinfo = 'text',
		name = window,
		mode = 'markers', 
		marker = dict(
			showscale = True,
			colorscale = [[0.0, 'rgb(189,189,189)'],
						  [.12, 'rgb(150,150,150)'], 
						  [.30, 'rgb(115,115,115)'],
						  [.64, 'rgb(82,82,82)'], 
						  [1.0, 'rgb(37,37,37)']], 
			reversescale = False,
			opacity = 0.88,
			cmin = 0.0,
			cmax = 0.6,
			size = [],
			color = [],
			colorbar = dict(
				thickness = 5.75,
				title = "centrality metrics: "
						"degree =size & betweenes =color",
				xanchor = 'left',
				titleside = 'right',
				borderwidth = 0),
			line = dict(width = [], color='rgb(144, 213, 229)') ) 
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
			[len(nghbr[1]) * 6 + 15] 
		) 
		node_trace['marker']['line']['width'] += tuple(
			[3 if nghbr[0] == 'bitcoin' else 0.4]
		)
		node_trace['text'] += tuple([
			"COIN: <b>- {} -</b>"
			"<br><i>distance to Bitcoin: {}</i>"
			"<br><i>neighbours: {}</i>"
			"<br><i>betweenness: {}</i>"
			"".format(nghbr[0], 
					  bitcenter[nghbr[0]], 
					  len(nghbr[1]), 
					  round(betweenness[nghbr[0]],6) ) 
		])

	# package plotly: network constant lyout-aesthetics
	mst_layout = go.Layout(
		# title = "<b>MST-graph Crypto-representation</b>",
		# titlefont = dict(size=8),
		showlegend = False,
		hovermode = 'closest',
		height=325,
		margin = dict(b=0, l=0, r=0, t=20),
		annotations = [dict(
			text = "workbook: <a href='https://github.com/Protago90/grad.thesis_DS-cryptoBit/blob/master/mstgraph_workbook.ipynb''>MST-graph</a>",
			showarrow = False,
			xref = "paper", 
			yref="paper",
			x = 0.48, 
			y=0) ],
		xaxis = dict(
			showgrid=False, 
			zeroline=False,
			showticklabels=False, 
			range=[-3,3.3] ),  
		yaxis = dict(
			showgrid=False, 
			zeroline=False, 
			showticklabels=False,
			range=[-3,3.3] )
	)

	return go.Figure(data=[edge_trace, node_trace], layout=mst_layout)



def tseries_graph_fly(bitcoins_df, window, year):
	'''function for on-the-fly poin in time tseries-figure generation'''

	# package plotly: t.series traces-contruction
	series_trace = go.Scatter(
		y = bitcoins_df.values[:(window + 1)], # pandas series!
		x = list(range(year))[:(window + 1)],
		line = dict(width=2.5, shape='spline', color='rgb(144, 213, 229)'),
		opacity = 0.9,
		hoverinfo = 'text',
		text = '{:%d, %b %Y}'.format( bitcoins_df.index[window] ),
		fill = 'tozeroy',
		mode = 'lines'
	)

	# package plotly: t.series fixed trace-contruction
	fixed_trace = go.Scatter(
		y = bitcoins_df.values, # pandas series!
		x = list(range(year)),   
		opacity = 0.75,
		name = 'BTC',
		line = dict(width=3.25, shape='spline', color='rgb(37, 37, 37)'),
		mode = 'lines'
	)

	# package plotly: t.series constant lyout-aesthetics
	series_layout = go.Layout(
		title = "<b>Crypto Timse-series",
		titlefont = dict(size=8),
		showlegend = False,
		annotations = [dict(
			x=39, 
			y=6000,
            xref='x',
            yref='y',
            text='Day: -{0:0=3d}-'.format(window),
            showarrow=True,
            arrowhead=0,
            ax=0,
            ay=0,
            font=dict(size=24) )],
		autosize = False,
		height = 210,
		margin = dict(b=0, l=0, r=0, t=0, pad=2),
		xaxis = dict(showgrid=False, zeroline=False),  
		yaxis = dict(showgrid=False, zeroline=False)
	)

	return go.Figure(data=[fixed_trace, series_trace], layout=series_layout)