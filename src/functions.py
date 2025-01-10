import plotly.express as px

def FilterData(dataFrame, origin, years):
    '''
    Selects the rows that have column Origin
    present in argument origin and belong to a Year present in
    argument years from a dataframe structured like the file Alud_accidents.csv

    Positional arguments:
    dataFrame ----- pandas dataframe with data.
    years ---- Years that are going to be queried.

    Returns:
    DataFrame: dataframe with filtered entries
    '''
    Years = range(years[0], years[1] + 1)

    if years[0] > years[1]:
        Years = range(years[1], years[0] + 1)

    DataFrame = dataFrame.query("(Origin in @origin) and (Year in @Years)")

    return DataFrame


def create_map(DataFrame, colorVariable):
    '''
    Create a scatter_map with a datframe like Alud_accidents.csv.

    Positional arguments:
    DataFrame ---- pandas dataframe with data
    colorVariable ---- variable by which color the heatmap.

    Returns:
    px.scatter_map: scatter_map with dots colored by colorVariable.
    '''
    #Define coordinates of where we want to center our map
    boulder_coords = {"lat": 40.416775, "lon": -3.703790}
    
    #Create the map
    my_map = px.scatter_map(
                            DataFrame, lat = "lat",
                            lon="long",
                            color = colorVariable,
                            hover_name="Location", zoom = 5, center=boulder_coords,
                            category_orders={"Danger Score" : ['1', '2', '3', '4', 'No prediction', 'Out of prediction period', 'Unknown']}
                            )

    my_map.update_layout(
                        height = 400,
                        legend_y = 0.99,
                        legend_x = 0.01,
                        margin=dict(l=0, r=0, t=0, b=0)
                        )
    
    my_map.update_coloraxes(
        colorbar={"orientation":"h"}
    )

    if colorVariable != "Danger Score":

        tickVals = DataFrame[colorVariable].unique()

        tickText = list(map(lambda x : "UNK" if x == -1 else str(x), tickVals))

        my_map.update_layout(
                coloraxis_colorbar=dict(
                    tickvals=tickVals,
                    ticktext=tickText
                )
        )

        my_map.update_layout(
            font=dict(color="white"),
            paper_bgcolor='black'
        )

    return my_map