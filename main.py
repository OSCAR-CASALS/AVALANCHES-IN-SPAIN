##########################################################
# Loading packages
##########################################################
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from src.functions import create_map, FilterData
import plotly.express as px

##########################################################
# Initialising app
##########################################################

app = Dash(__name__)

app.title = "Avalanches in Spain"

app._favicon = ("Icon.jpeg")

##########################################################
# Loading and processing data
##########################################################

DF = pd.read_csv('data/Alud_accidents.csv', sep = ',')
DF.drop(columns=DF.columns[0], axis=1, inplace=True)
DF.drop(columns="Size", axis=1, inplace=True)

DF['Date'] = DF['Day'].astype(str) + "/" + DF['Month'].astype(str) + "/" + DF['Year'].astype(str)

DF.rename(columns={'Danger_Score' : 'Danger Score'}, inplace=True)

###################################################################################################
## Top Bar of the web page
###################################################################################################

topBar = html.Div([
    html.H1("AVALANCHES IN SPAIN"), html.Hr(className="TitleSeparator")
    ],
    className="topBar")

Years = DF['Year'].unique()

###################################################################################################
## Filters of the points displayed in the map
###################################################################################################

InputElementsMap = html.Div([
                html.Div(
                    children=[
                    html.Div(
                        [
                            html.H3("Origin", style = {'color' : 'white', 'text-align' : 'center', 'margin-top': 0}),
                            dcc.Checklist(
                                    options=['Accidental', 'Unknown', 'Natural'], 
                                    value=['Accidental', 'Unknown', 'Natural'],
                                    id = "OrignSelector", className="DropdownOrigin"
                                    ),
                        ],
                        className="OriginAvalanche"
                    ),
                    html.Div(
                        [
                            html.H3("Years", style = {'color' : 'white', 'text-align' : 'center', 'margin-top': 0}),
                            html.Div(
                                [
                                    html.Label("From", style={'color': 'white', 'font-weight' : 'bold'}),
                                    dcc.Dropdown(
                                            options=Years, value=Years[0], multi=False, searchable=True, clearable=False, className="SelectorYear",
                                            id="FirstYear"
                                            ),
                                    html.Label("to", style={'color': 'white', 'font-weight' : 'bold'}),
                                    dcc.Dropdown(
                                            options=Years, value=Years[-1], multi=False, searchable=True, clearable=False, className="SelectorYear",
                                            id="LastYear"
                                            )
                                ],
                                className="YearRange"
                            )
                        ], className="OriginAvalanche"
                    )
                    ],
                    className="InputElements"
                )], style = {"margin" : 0, "padding" : 0}
            )

###################################################################################################
## Map
###################################################################################################

TheMap = html.Div(children=[
                html.Hr(className="TitleSeparator"), html.Br(), 
                html.H2("Map"),
                html.H3("Color by:", style = {'margin-top': '20px', 'margin-bottom': '10px'}),
                dcc.Dropdown(options=['Danger Score',
                              'Dragged', 
                              'Hurt',
                              'Dead'], 
                              value = 'Danger Score', 
                              id='SelectColor',
                              multi=False, searchable=False, clearable=False,
                              style = {'margin-bottom': '10px', 'color' : 'black'}), 
                html.Div(dcc.Graph(figure={}, id='Mapfigure'))
            ], className = "MapContainer")

###################################################################################################
## Table with points clicked in the map
###################################################################################################

TableWithData = html.Div(
    [
        #html.Br(),
        html.H3("Clicked point:", style = {'margin-bottom': '10px', 'margin-top': '0', 'color' : 'white'}),
        dash_table.DataTable(id="tableWithEntries", style_data={'whiteSpace': 'normal'},
                                      virtualization=False, style_cell={
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'maxWidth': 0,
                                    }, cell_selectable=False
                            ), html.Br(),
        html.Hr(className="TitleSeparator")
    ],
    className="TableWithData")

###################################################################################################
## Line plot of quantity of avalanches per year.
###################################################################################################

df_Plot = DF.copy()

df_Plot['Year'] = df_Plot['Year'].astype(str)

AmmountOfAvalanchesPerYear = df_Plot.query("Year != '2007'").groupby("Year")["Year"].value_counts().reset_index().rename(columns={'index': 'Year', 0: 'count'})

LinePlot = px.line(
                AmmountOfAvalanchesPerYear,
                x = "Year", y = "count"
                )

LinePlot.update_layout(
    font=dict(color="white"),
    paper_bgcolor='black',
    plot_bgcolor='black'
)

EvolutionPlot = html.Div([
    html.P('''
        Due to the fact that avalanche accidents published on ACNA's website start at season 200708, 
        avalanches prior to December 2007 are not included on the data and, therefore, this year has been
        removed from the line plot. 
        ''', style = {"text-align" : "center"}
        ),
    dcc.Graph(
        figure = LinePlot
    ), html.Br(), html.Br()
], className="LinePlotContainer")


###################################################################################################
## Footer
###################################################################################################

Footer = html.Footer(children=[
    html.Br(),
    html.H3("Web Scrapper created for extracting data from ACNA's database"),
    html.A("https://github.com/OSCAR-CASALS/Avalnche-Accidents-WebScrapper",
           href="https://github.com/OSCAR-CASALS/Avalnche-Accidents-WebScrapper"),
    html.H3("Source of data used"),
    html.A("https://www.acna.es/estadisticas-de-accidentes/", href="https://www.acna.es/estadisticas-de-accidentes/"),
    html.H3("GitHub of the web app"),
    html.A("https://github.com/OSCAR-CASALS/AVALANCHES-IN-SPAIN.git", href="https://github.com/OSCAR-CASALS/AVALANCHES-IN-SPAIN.git"),
    html.H3("Portfolio"),
    html.A("https://oscar-casals.github.io/Oscar_Casals_Morro_Portfolio", href="https://oscar-casals.github.io/Oscar_Casals_Morro_Portfolio"),
    html.Br(), html.H3(), html.Br()
],
className="Footer")

###################################################################################################
## Joining all previous divs into app layout
###################################################################################################

app.layout = [topBar, html.H2("Filters"),
    InputElementsMap, TheMap, TableWithData, html.H2("Quantity of avalanches per Year"),
    EvolutionPlot, Footer]

###################################################################################################
## Callbacks for modifiying the points showed in the scatter_map and selecting the results
## the user has clicked in the map to show them in a DataTable.
###################################################################################################

@callback(
    Output(component_id='Mapfigure', component_property='figure'),
    Input(component_id='SelectColor', component_property='value'),
    Input(component_id='OrignSelector', component_property='value'),
    Input(component_id='FirstYear', component_property='value'),
    Input(component_id='LastYear', component_property='value')
)
def update_graph(ValueChosen, OriginsChosen, YearOne, LastYear):
    DataF = FilterData(DF, OriginsChosen, [YearOne, LastYear])
    return create_map(DataF, ValueChosen)


@callback(
    Output('tableWithEntries', 'data'),
    Input(component_id='SelectColor', component_property='value'),
    Input(component_id='Mapfigure', component_property='clickData'),
    Input(component_id='OrignSelector', component_property='value'),
    Input(component_id='FirstYear', component_property='value'),
    Input(component_id='LastYear', component_property='value')
)
def UpdateTable(ValueChosen,ClickData, OriginsChosen, YearOne, LastYear):

    res = pd.DataFrame()

    if ClickData:

        res = FilterData(DF, OriginsChosen, [YearOne, LastYear])

        Lat = ClickData["points"][0]["lat"]
        Long = ClickData["points"][0]["lon"]

        res = res.query("(lat == @Lat) and (long == @Long)")

        res = res[["Date","Location",ValueChosen, "Origin", "Members", "Activity"]]
    
    return res.to_dict("records")

@callback(
    Output('tableWithEntries', 'tooltip_data'),
    Input('tableWithEntries', 'data'),
)
def update_tooltips(data):
    if not data:
        return []
    return [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in data
    ]

@callback(
    Output('tableWithEntries', 'tooltip_header'),
    Input('tableWithEntries', 'data'),
    prevent_initial_call=True
)
def update_tooltips(data):
    if not data:
        return {}
    return {i: i for i in data[0].keys()}






if __name__ == '__main__':
    app.run(debug=False)
