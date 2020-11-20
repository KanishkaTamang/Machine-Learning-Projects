
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import dash_table
import datetime as dt
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import sir as sirUtils
import os
import json


app =  dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server


df_sample = pd.read_csv('covid_resuls_v1.csv')
time_series = pd.read_csv('us_time_series.csv')

def getLatestDate(df):	
	dateStr = df["Date"].max()
	dateFormatter = dt.datetime.strptime(dateStr, '%m/%d/%y')
	return "Last Updated: " + dateFormatter.strftime("%B %d, %Y")

def getActiveCases(clusterNumber = None):
	if clusterNumber is None:
		return (df_sample.Active.sum())
	filteredDf = df_sample[df_sample["Cluster_labels"] == clusterNumber]
	return str((filteredDf.Active.sum()).astype(int))

def getTotalDeaths(clusterNumber = None):
	if clusterNumber is None:
		return df_sample.Deaths.sum()
	filteredDf = df_sample[df_sample["Cluster_labels"] == clusterNumber]
	return str(filteredDf.Deaths.sum().astype(int))

def getTotalRecovered(clusterNumber = None):
	if clusterNumber is None:
		return df_sample.Recovered.sum()
	filteredDf = df_sample[df_sample["Cluster_labels"] == clusterNumber]
	return str(filteredDf.Recovered.sum().astype(int))

def getBiWeeklyAverage(clusterNumber = None):
	if clusterNumber is None:
		return (df_sample["average"]).sum().astype(int)
	filteredDf = df_sample[df_sample["Cluster_labels"] == clusterNumber]
	return str(filteredDf["average"].sum().astype(int))

def getClusters(df):
	cluster = sorted(df.Cluster_labels.unique().tolist())
	return cluster

def getBarGraph(clusterNumber = None):
	county_bar = None
	if clusterNumber is None:
		county_bar = df_sample.groupby('County',as_index=0)['Confirmed'].sum().sort_values(by='Confirmed',ascending=False).head(10).sort_values(by='Confirmed')
	else:
		filteredDf = df_sample[df_sample["Cluster_labels"] == clusterNumber]
		county_bar = filteredDf.groupby('County',as_index=0)['Confirmed'].sum().sort_values(by='Confirmed',ascending=False).head(10).sort_values(by='Confirmed')

	barfig = px.bar(county_bar, x='Confirmed', y='County',orientation='h')
	barfig.update_layout(
		title=dict(
		x=0.5,
		text = "<b>Most Affected Counties</b>",
		font=dict(
			family="Arial",
			size=12,
			color='#383A35'
			)
		),
		showlegend=True,
		plot_bgcolor="rgba(0,0,0,0)",
		paper_bgcolor = "rgba(0,0,0,0)",
		margin=dict(t=24,b=0,l=0,r=0)
	)
	barfig.update_xaxes(
        title_font = {"size": 11},
        title_text = "Confirmed Cases",
        )
	barfig.update_yaxes(
         title_font = {"size": 11},
         title_text = "County",
         )
	return barfig

def getTimeSeriesGraph():
	fig = px.line(time_series, x='Date', y='Confirmed',title = "<b>Are new cases declining?</b>")
	fig.update_layout(
		title=dict(
		x=0.5,
		font=dict(
			family="Arial",
			size=12,
			color='#383A35'
			)
		),
		showlegend=False,
		margin=dict(t=24,b=0,l=0,r=0)
	)
	fig.update_xaxes(
        title_font = {"size": 11},
        title_text = "",
        )
	fig.update_yaxes(
         title_font = {"size": 11},
         title_text = "Confirmed Cases",
         )
	return fig
	
def getChoropleth(clusterNumber = None):
	with open('county-fips.json') as json_file:
		counties = json.load(json_file)
	df_sample['FIPS'] = df_sample['FIPS'].astype(int).astype(str)
	mask  = df_sample['FIPS'].str.len() < 5
	df_sample.loc[mask,'FIPS'] = '0' + df_sample.loc[mask,'FIPS']
	temp_df = df_sample.copy()
	temp_df['Cluster_labels'] = temp_df['Cluster_labels'].astype(str)
	fig = px.choropleth(data_frame = temp_df,geojson=counties, locations='FIPS', color='Cluster_labels',
	                       scope="usa",hover_data=['County'],color_discrete_sequence=['#fbb4b9','#ffffd4','#2c7fb8','#e34a33','#045a8d'],
	                       labels={'Cluster_labels':'Cluster',
	                              'County':'County'})
	fig.update_layout(
		margin=dict(t=0,b=0,l=0,r=0)
		)
	return fig

def updateChoropleth(clusterNumber = None):
	filteredDf = None
	if clusterNumber is None:
		filteredDf = df_sample
	else:
		filteredDf = df_sample[df_sample["Cluster_labels"] == clusterNumber]
	temp_df = filteredDf.copy()
	temp_df['Cluster_labels'] = temp_df['Cluster_labels'].astype(str)
	temp_df['text'] = 'County:' + temp_df['County'] + ', Active Cases: ' + temp_df['Active'].astype(str)

	fig = go.Figure(data=go.Scattergeo(
	        lon = temp_df['Long'],
	        lat = temp_df['Lat'],
	        text = temp_df['text'],
	        mode = 'markers',
	        marker = dict(
            size = 10,
            opacity = 0.8,
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(242, 102, 102)'
            )
	)))
	fig.update_layout(
        geo_scope='usa',
        margin=dict(t=0,b=0,l=0,r=0)
    )
	return fig


def getSIRGraphBeforeVaccine(beta,gamma,vaccineEfficacy,clusterList):
	sir_fig = sirUtils.getSIRplotWithoutVaccine(beta, gamma,vaccineEfficacy,clusterList)
	sir_fig.update_layout(
		title=dict(
		text='<b>Before Vaccination</b>',
		x=0.5,
		y=1,
		font=dict(
			family="Arial",
			size=12,
			color='#383A35'
			)
		),
		showlegend=True,
		plot_bgcolor="rgba(0,0,0,0)",
		paper_bgcolor = "rgba(0,0,0,0)",
		margin=dict(t=0,b=0,l=0,r=0),
		legend_title='',
	)

	sir_fig.update_xaxes(
        title_font = {"size": 11},
        title_text = "No. of days",
        )
	sir_fig.update_yaxes(
         title_font = {"size": 11},
         title_text = "Population",
         )

	return sir_fig
	 

def getSIRGraphAfterVaccine(beta,gamma,vaccineProportion,vaccineEfficacy,clusterList):
	sir_fig = sirUtils.getSIRplotAfterVaccine(beta,gamma,vaccineProportion,vaccineEfficacy,clusterList)
	sir_fig.update_layout(
		title=dict(
		text='<b>After Vaccination</b>',
		x=0.5,
		y=1,
		font=dict(
			family="Arial",
			size=12,
			color='#383A35'
			)
		),
		showlegend=True,
		plot_bgcolor="rgba(0,0,0,0)",
		paper_bgcolor = "rgba(0,0,0,0)",
		margin=dict(t=0,b=0,l=0,r=0),
		legend_title='',
	)
	sir_fig.update_xaxes(
        title_font = {"size": 11},
        title_text = "No. of days",
        )
	sir_fig.update_yaxes(
         title_font = {"size": 11},
         title_text = "Population",
         )
	return sir_fig


app.layout = html.Div(className='container-fluid bg-light',children=[

	dbc.Row(children=[
		dbc.Col(className = "p-2",children=[
			html.H4("COVID-19 Dashboard for Vaccine Deployment")
			]),
		dbc.Col(className="text-right p-2",children=[
			html.P(getLatestDate(df_sample))
			])	
	]),

	dbc.Row(className="my-3",children=[
		dbc.Col(
			dbc.Card(
				dbc.CardBody(className="p-2",children=[
					html.H4(children=getActiveCases(), id="id_active_cases", className="card-title"),
   					 html.H6("Active Cases", className="card-subtitle"),

				])
			)
		),

		dbc.Col(
			dbc.Card(
				dbc.CardBody(className="p-2",children=[
						html.H4(children=getTotalDeaths(), id="id_total_deaths", className="card-title"),
   					 html.H6("Total Deaths", className="card-subtitle"),

				])
			)
		),

		dbc.Col(
			dbc.Card(
				dbc.CardBody(className="p-2",children=[
						html.H4(children=getTotalRecovered(),id="id_total_recovered", className="card-title"),
   					 html.H6("Total Recovered", className="card-subtitle"),

				])
			)
		),

		dbc.Col(
			dbc.Card(
				dbc.CardBody(className="p-2",children=[
						html.H4(children=getBiWeeklyAverage(),id="id_population_density", className="card-title"),
   					 html.H6("14-day Moving Average", className="card-subtitle"),

				])
			)
		)

		]),

	dbc.Row([
		dbc.Col(children=[
			dbc.Card(
				dbc.CardBody(className="p-2",children=[
					dcc.Graph(id='id_bar_topCounties', figure= getBarGraph(), config={
					'displayModeBar': False }),


					dcc.Graph(id='timeSeries_graph', figure= getTimeSeriesGraph(),  config={
						'displayModeBar': False })

				])
			)

		],width=3),

		dbc.Col(children=[
			dbc.Card(
				dbc.CardBody(children=[

			dbc.Row(className="",children=[
				dbc.Col(
					dcc.Dropdown(
        			id='cluster_dropDown',
        			options = [{'label':"Cluster " + str(name), 'value':name} for name in getClusters(df_sample)],
        			placeholder= "Select Cluster"
    			)
				,width=12),

				dbc.Col(className="map",children=[
					dcc.Graph(id='id_graph_choropleth', figure= getChoropleth(), config={
					'displayModeBar': False })])
				]),

			])
		)

		]),

		dbc.Col(children=[
			dbc.Card(
				dbc.CardBody(className="p-2",children=[
					dbc.Col(children = [
							dcc.Graph(id='sir_graph_before', figure= getSIRGraphBeforeVaccine(0.5, 0.5, 0.6, getClusters(df_sample)), config={
						  	'displayModeBar': False }),
						dcc.Graph(id='sir_graph_after', figure= getSIRGraphAfterVaccine(0.5, 0.5, 0.0001, 0.6, getClusters(df_sample)), config={
							'displayModeBar': False }),
					]),

					dbc.Row(className="user_input",children=[
						dbc.Col(children=[
							html.P("Transmission Rate"),
							dcc.Slider(id="id_slider_transmission", min=0, max=1, step=0.1, value=0.5, marks={ 0: '0', 1: '1'}),
						]),

						dbc.Col(children=[
							html.P("Recovery Rate"),
							dcc.Slider(id="id_slider_recovery", min=0, max=1, step=0.1, value=0.5, marks={ 0: '0', 1: '1'}),
						])
					]),

				 	 dbc.Row(className="user_input",children=[
				 	 	dbc.Col(children=[
							html.P("Vaccinated Proportion"),
							dbc.Input(id="id_vaccine_proportion",type="number", min=0, max=1, step=0.0001,bs_size="sm", value=0.0001)						
						]),

						dbc.Col(children=[
							html.P("Vaccine Efficacy"),
							dcc.Slider(id="id_vaccine_efficacy", min=0, max=1, step=0.1, value=0.6, marks={ 0: '0', 1: '1'}),
						])

					])

				])
			)

		],width=4),
	])

	])


@app.callback(
    [Output("id_active_cases", "children"),
        Output("id_total_deaths", "children"),
        Output("id_total_recovered", "children"),
        Output("id_population_density", "children"),
        Output("id_bar_topCounties", "figure")],
    [Input('cluster_dropDown', "value")]
)
def update_app(value):
	if value is None:
		raise PreventUpdate
	fig = getBarGraph(value)
	return getActiveCases(value), getTotalDeaths(value), getTotalRecovered(value), getBiWeeklyAverage(value), fig

@app.callback(
    Output("id_graph_choropleth", "figure"),
    [Input('cluster_dropDown', "value")]
)
def update_choropleth(value):
	if value is None:
		raise PreventUpdate
	return updateChoropleth(value)

@app.callback(
    [Output("sir_graph_before", "figure"),
     Output("sir_graph_after", "figure")],
    [Input('id_slider_transmission', "value"),
    Input('id_slider_recovery', "value"),
    Input('id_vaccine_proportion', "value"),
    Input('id_vaccine_efficacy', "value"),
    Input('cluster_dropDown', "value"),
    ]
)

def update_SIRGraphs(transmissionRate, recoveryRate, vaccineProportion, vaccineEfficacy, cluster):
	if cluster is None:
			sir_graph_before = getSIRGraphBeforeVaccine(transmissionRate,recoveryRate,vaccineEfficacy,getClusters(df_sample))
			sir_graph_after = getSIRGraphAfterVaccine(transmissionRate,recoveryRate,vaccineProportion, vaccineEfficacy, getClusters(df_sample))
			return sir_graph_before, sir_graph_after

	sir_graph_before = getSIRGraphBeforeVaccine(transmissionRate,recoveryRate,vaccineEfficacy,[cluster])
	sir_graph_after = getSIRGraphAfterVaccine(transmissionRate,recoveryRate,vaccineProportion, vaccineEfficacy,[cluster])
	return sir_graph_before, sir_graph_after


if __name__ == '__main__':
	app.run_server(debug=True)


