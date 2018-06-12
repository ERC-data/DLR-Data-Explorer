#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 16:09:33 2017

@author: saintlyvi
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output#, State

import plotly.graph_objs as go
import plotly.offline as offline
offline.init_notebook_mode(connected=True)

import pandas as pd
import numpy as np
import os
import base64

import features
from support import appProfiles 

app = dash.Dash(__name__)
server = app.server

# Load images
erc_logo = os.path.join('img', 'erc_logo.jpg')
erc_encoded = base64.b64encode(open(erc_logo, 'rb').read())
sanedi_logo = os.path.join('img', 'sanedi_logo.jpg')
sanedi_encoded = base64.b64encode(open(sanedi_logo, 'rb').read())

# Get mapbox token
mapbox_access_token = 'pk.eyJ1Ijoic2FpbnRseXZpIiwiYSI6ImNqZHZpNXkzcjFwejkyeHBkNnp3NTkzYnQifQ.Rj_C-fOaZXZTVhTlliofMA'

# Get load profile data from disk
print('...loading load profile data...')
profiles = appProfiles(1994,2014)  

# Load datasets
print('...loading socio demographic data...')
ids = features.loadID()

#a little bit of data wrangling
loc_summary = pd.pivot_table(ids, values = ['AnswerID'], index = ['Year','LocName','Lat','Long','Municipality','Province'],aggfunc = np.count_nonzero)
loc_summary.reset_index(inplace=True)
loc_summary.rename(columns={'AnswerID':'# households'}, inplace=True)

#load socio-demographic feature frame
appliances = ['fridge freezer','geyser','heater','hotplate','iron','kettle','microwave','3 plate', '4 plate','tv','washing machine']
sd = features.socio_demographics(appliances)

print('Your app is starting now. Visit 127.0.0.1:8050 in your browser')

app = dash.Dash()
app.config['suppress_callback_exceptions']=True

external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

app.layout = html.Div([

###############################

        html.Div([
            html.Div([
                html.Img(src='data:image/png;base64,{}'.format(erc_encoded.decode()), 
                         style={'width': '100%', 'paddingLeft':'5%', 'marginTop':'20%' })    
            ],
                className='three columns',
                style={'margin_top':'20'}
            ),
            html.Div([
                html.H2('South African Domestic Load Research',
                        style={'textAlign': 'center'}
                ),
                html.H1('Data Explorer',
                        style={'textAlign':'center'}
                )                    
            ],
                className='six columns'
            ),        
            html.Div([
                 html.Img(src='data:image/png;base64,{}'.format(sanedi_encoded.decode()), 
                          style={'width':'100%','margin-left':'-5%','marginTop':'10%' })                       
            ],
                className='three columns'
            ),              
        ],
            className='row',
            style={'background':'white',
                   'margin-bottom':'40'}
        ), 
    
################~Survey Locations~###############
    
        html.Div([
            html.Div([
                html.H3('Survey Locations'
                ),
                html.Div([
                    dcc.Graph(
                        animate=True,
                        style={'height': 450},
                        id='map'
                    ),
                ],
                    className='columns',
                    style={'margin-left':'0'}
                ),
                html.Div([
                    dcc.Slider(
                        id = 'input-years',
                        marks={i: i for i in range(1994, 2015, 2)},
                        min=1994,
                        max=2014,
                        step=1,
                        included=False,
                        value= 2010,#[1994, 2014],
                        updatemode='drag',
                        dots = True
                    )       
                ],
                    className='eleven columns',
                    style={'margin-left':'25',
                           'margin-right':'15'}
                ),
            ],
                className='columns',
                style={'margin-bottom':'10',
                       'margin-left':'0',
                       'width':'50%',
                       'float':'left'}
            ),

#######~~~~~~~~Specify Socio-demographic Indicators~~~~~~~~~########

            html.Div([
                html.H5('Specify Socio-demographic Indicators'
                ),                  

#~~~~---Select number of years electrified---~~~~

                html.Div([
                    html.P('Select number of years electrified'),
                    html.Div([
                        dcc.RangeSlider(
                            id = 'input-electrified',
                            marks= list(range(0, 15, 1)) + ['+15'],
                            min=0,
                            max=15,
                            included=True,
                            value= [0,15],
                            updatemode='drag'
                        )     
                    ],
                        style={'margin-bottom':'50',
                               'margin-left':'20'}
                    )     
                ],
                    className='columns',
                    style={'margin-top':'25',
                           'margin-left':'0'}
                ),

#~~~~---Select household income range---~~~~

                html.Div([
                    html.P('Select household income range'),
                    html.Div([
                        dcc.RangeSlider(
                            id = 'input-income',
                            marks={i: 'R {}k'.format(i/1000) for i in range(0, 26000, 2500)},
                            min=0,
                            max=25000,
                            included=True,
                            value= [0,25000],
                            updatemode='drag'
                        )     
                    ],
                        style={'margin-bottom':'50',
                               'margin-left':'20'}
                    )     
                ],
                    className='columns',
                    style={'margin-left':'0'}
                ),

#~~~~---Select household appliances---~~~~

                html.Div([
                    html.P('Select household appliances'),
                    html.Div([
                        dcc.Dropdown(
                            id = 'input-appliances',
                            options=[{'label': 'Fridge-Freezer', 'value': 'fridge_freezer'},
                                     {'label': 'Geyser', 'value': 'geyser'},
                                     {'label': 'Heater', 'value': 'heater'},
                                     {'label': 'Hotplate', 'value': 'hotplate'},
                                     {'label': 'Iron', 'value': 'iron'},
                                     {'label': 'Kettle', 'value': 'kettle'},
                                     {'label': 'Microwave', 'value': 'microwave'},
                                     {'label': '3-plate Stove', 'value': '3_plate'},
                                     {'label': '4-plate Stove', 'value': '4_plate'},
                                     {'label': 'TV', 'value': 'tv'},
                                     {'label': 'Washing machine', 'value': 'washing_machine'},
                            ],
                            placeholder="Select appliances",
                            multi=True,
                            value = []
                        )
                    ],
                    style={'margin-bottom':'50',
                           'margin-left':'20'}
                    ),
                ],
                    className='columns',
                    style={'margin-left':'0'}
                ),                
########~~~~~~~~section end~~~~~~~~########
            ],
                className='columns',
                style={'margin-top':'75',
                       'margin-bottom':'10',
                       'margin-right':'15',
                       'margin-left':'25',
                       'width':'45%',
                       'float':'right'}
            ),    
################~section end~################
        ],
            className='row',
        ),
        html.Div(id='sd-features', style={'display': 'none'}),
        html.Div(id='selected-ids', style={'display': 'none'}),
        html.Div(id='map-select', style={'display': 'none'}),
#Uncomment to test input variables
#        html.Div([
#            html.Pre(id='test'),
#        ], className='three columns'),
        html.Hr(),

#################~View Load Profiles~###############

        html.Div([
            html.H3('View Load Profiles'),
            dcc.RadioItems(
                id = 'input-daytype',
                options=[
                        {'label': 'Weekday', 'value': 'Weekday'},
                        {'label': 'Saturday', 'value': 'Saturday'},
                        {'label': 'Sunday', 'value': 'Sunday'}
                        ],
                value='Weekday'
            ),
            dcc.Graph(
                id='graph-profiles'
            ),
        ]),                        
        html.Hr(),

###############~Explore Profile Meta-data~###############

        html.Div([
            html.H3('Explore Profile Meta-data'),

########~~~~~~~~Discover Survey Questions~~~~~~~~########

            html.Div([
                html.H5('Discover Survey Questions'
                ),
                html.Div([
                    dcc.Input(
                        id='input-search-word',
                        placeholder='search term',
                        type='text',
                        value=''
                    )
                ],
                    className='container',
                    style={'margin': '10'}
                ),
                dt.DataTable(
                    id='output-search-word-questions',
                    rows=[{}], # initialise the rows
                    row_selectable=True,
                    columns = ['Question','Survey','Datatype'],
                    filterable=False,
                    sortable=True,
                    selected_row_indices=[]
                )
            ],
                className='columns',
                style={'margin-bottom':'10',
                       'margin-left':'0',
                       'width':'50%',
                       'float':'left'}
            ),

########~~~~~~~~Location Output Summary~~~~~~~~########

            html.Div([
                html.H5('Location Output Summary'),
                html.Div([
                    dt.DataTable(
                        id='output-location-summary',
                        rows=[{}], # initialise the rows
                        row_selectable=False,
                        columns = ['Year','Province','Municipality','LocName','# households'],
                        filterable=False,
                        sortable=True,
                        column_widths=100,
                        min_height = 450,
                        resizable=True,
                        selected_row_indices=[]),
                    html.P('"# households" is the number of households for which socio-demographic survey data is available',
                           style={'font-style': 'italic'}
                           )
                ],
                    style={'margin-top':'57'}
                )
            ],
                className='columns',
                style={'margin-bottom':'10',
                       'width':'45%',
                       'float':'right'}
            ),
#######~~~~~~~~section end~~~~~~~~########
        ],
            className='row'
        ),
    ],

##############################

    #Set the style for the overall dashboard
    style={
        'width': '100%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': '#F3F3F3',
        'padding': '40',
        'padding-top': '20',
        'padding-bottom': '20',
    },
)

#Define outputs
                    
#@app.callback(
#        Output('test','children'),
#        [Input('input-appliances','value')])
#def selected_ids(input):
#    
#    return json.dumps(input, indent=2)

@app.callback(
        Output('sd-features','children'),
        [Input('input-electrified', 'value'),
         Input('input-electrified', 'max'),
         Input('input-income', 'value'),
         Input('input-income', 'max'),
         Input('input-appliances', 'value')
        ])
def socio_demographics(electrified, electrified_max, income, income_max, appliances):

    if electrified[1] == electrified_max:
        electrified[1] = sd.years_electrified.max()
    if income[1] == income_max:
        income[1] = sd.monthly_income.max()
    
    sd1 = sd[sd.monthly_income.isin(range(int(income[0]),int(income[1])+1))]
    sd2 = sd1[sd1.years_electrified.isin(range(int(electrified[0]),int(electrified[1])+1))]
    try:
        sd_features = sd2.dropna(subset=appliances)
    except:
        sd_features = sd

    return sd_features.to_json(date_format='iso', orient='split')

@app.callback(
        Output('selected-ids','children'),
        [Input('sd-features','children'),
         Input('input-years','value')
        ])
def selected_ids(sd_features, input_years):
    
    sd_df = pd.read_json(sd_features, orient='split')
    id_select = sd_df.merge(ids, on='AnswerID', how='inner')
    yrs = [input_years]
#    yrs = list(range(input_years[0],input_years[1]+1))
    output = id_select[id_select.Year.isin(yrs)].reset_index(drop=True)
    
    return output.to_json(date_format='iso', orient='split')

@app.callback(
        Output('map','figure'),        
        [Input('selected-ids','children')
        ])
def update_map(selected_ids):
    
    ids_df = pd.read_json(selected_ids, orient='split')
    
    georef = pd.pivot_table(ids_df, values = ['AnswerID'], index = ['Year','LocName','Lat','Long','Municipality','Province'],aggfunc = np.count_nonzero)
    georef.reset_index(inplace=True)
    georef.rename(columns={'AnswerID':'# households'}, inplace=True)
                           
    traces = []
    for y in range(georef.Year.min(), georef.Year.max()+1):
        lat = georef.loc[(georef.Year==y), 'Lat']
        lon = georef.loc[(georef.Year==y), 'Long']
        text = georef.loc[(georef.Year==y), '# households'].astype(str) + ' household surveys</br>'+ georef.loc[(georef.Year==y), 'LocName'] + ', ' + georef.loc[(georef.Year==y), 'Municipality']
        marker_size = georef.loc[georef.Year==y,'# households']**(1/2.5)*2.7
        marker_size.replace([0,1,2,3,4, 5], 6, inplace=True)
        trace=go.Scattermapbox(
                name=y,
                lat=lat,
                lon=lon,
                mode='markers',
                marker=go.Marker(
                    size=marker_size
                ),
                text=text,
            )
        traces.append(trace)
    figure=go.Figure(
        data=go.Data(traces),
        layout = go.Layout(
                autosize=True,
                hovermode='closest',
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=dict(
                        lat=-29.1,
                        lon=25
                    ),
                    pitch=0,
                    zoom=4.32,
                    style='light'
                ),
                margin = go.Margin(
                        l = 10,
                        r = 10,
                        t = 20,
                        b = 30
                ),
                showlegend=False
            )
    )
    return figure

@app.callback(
    Output('map-select','children'),
    [Input('map','selectedData'),
     Input('selected-ids','children')
     ])
def map_data(selected_data, selected_ids):

    ids_df = pd.read_json(selected_ids, orient='split')

    try:    
        geos = pd.DataFrame(selected_data['points'])
        geos['LocName'] = geos['text'].apply(lambda x: x.split(',')[0].split('>')[1])
        geos.drop_duplicates('LocName',inplace=True)
        output = ids_df[ids_df.LocName.isin(geos.LocName)].reset_index(drop=True)
        
    except:
        output = ids_df
                
    return output.to_json(date_format='iso', orient='split')

   
@app.callback(
        Output('graph-profiles','figure'),
        [Input('input-daytype','value'),
         Input('map-select','children'),
        ])
def graph_profiles(day_type, map_select):  
    
    map_df = pd.read_json(map_select, orient='split')
    id_select = map_df[map_df.AnswerID!=0]
    
    g = profiles[profiles.ProfileID_i.isin(id_select.ProfileID)]
    gg = g.groupby(['daytype','season','hour'])['kw_mean'].describe().reset_index()
    dt_mean = gg[(gg.daytype==day_type)]

    traces = []
    
    for s in ['high','low']:
    
        trace = go.Scatter(
            showlegend=True,
            opacity=1,
            x=dt_mean.loc[dt_mean['season']==s, 'hour'],
            y=dt_mean.loc[dt_mean['season']==s, 'mean'],
            mode='lines',
            name=s+ ' season',
            line=dict(
                #color='red',
                width=2.5),
            hoverinfo = 'name+y+x'
        )
        traces.append(trace)
    
    layout = go.Layout(showlegend=True, 
        title= day_type + ' Average Daily Demand for Selected Locations',
        margin = dict(t=150,r=150,b=50,l=150),
        height = 450,
        yaxis = dict(
                title = 'mean hourly demand (kW)',
                ticksuffix=' kW'),
        xaxis = dict(                        
                title = 'time of day',
                ticktext = dt_mean['hour'].unique(),
                tickvals = dt_mean['hour'].unique(),
                showgrid = True)
                )
    fig = go.Figure(data=traces, layout=layout)   
    
    return fig

@app.callback(
        Output('output-location-summary','rows'),
        [Input('map-select','children'),
        ])
def location_summary(map_select):
    
    map_df = pd.read_json(map_select, orient='split')

    output = pd.pivot_table(map_df, values = ['AnswerID'], index = ['Year','LocName','Lat','Long','Municipality','Province'],aggfunc = np.count_nonzero)
    output.reset_index(inplace=True)
    output.rename(columns={'AnswerID':'# households'}, inplace=True)
                                
    return output.to_dict('records')
            
@app.callback(
        Output('output-search-word-questions','rows'),
        [Input('input-search-word','value')
        ])
def update_questions(search_word):
    df = features.searchQuestions(search_word)[['Question','QuestionaireID','Datatype']]
    dff = df.loc[df['QuestionaireID'].isin([3,6])]
    dff.loc[:,'Survey'] = dff.QuestionaireID.map({3:'2000-2014',6:'1994-1999'})
    dff.drop(columns='QuestionaireID', inplace=True)
    return dff.to_dict('records')


# Run app from script. Go to 127.0.0.1:8050 to view
if __name__ == '__main__':
    app.run_server(debug=False)