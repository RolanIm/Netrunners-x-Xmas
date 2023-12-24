import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_leaflet as dl
from geopy.distance import geodesic

# Function to check if a string contains all specified keywords
def contains_keywords(string, keywords):
    if not isinstance(string, str):
        return False
    return all(keyword.lower() in string.lower() for keyword in keywords)

# Function to filter a DataFrame
def filter_dataframe(df, search_keywords, latitude, longitude, radius, filter_column, filter_value):
    df = df[df['Название'].apply(lambda x: contains_keywords(x, search_keywords))]
    df = df.dropna(subset=['Широта', 'Долгота'])
    
    # Filter by latitude and longitude
    if latitude and longitude:
        user_location = (latitude, longitude)
        df['Расстояние (В км)'] = df.apply(lambda row: geodesic((row['Широта'], row['Долгота']), user_location).km, axis=1)
        df = df[df['Расстояние (В км)'] < radius]
    
    # Filter based on a specific column and value
    if filter_column and filter_value:
        df = df[df[filter_column].apply(lambda x: contains_keywords(str(x), [filter_value]))]
    
    return df

# Function to find all .xlsx files in a folder
def find_xlsx_files(root_folder, search_keywords):
    xlsx_files = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.xlsx') and contains_keywords(file, search_keywords):
                xlsx_files.append(os.path.join(root, file))
    return xlsx_files

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Filtered Excel File Reading with Dash"),
    
    # Input for search keywords
    dcc.Textarea(
        id='search-keywords-input',
        placeholder='Enter search keywords (comma-separated)',
        style={'width': '100%'},
        value='',  # Set default value to an empty string
    ),
    
    dcc.Dropdown(
        id='file-dropdown',
        options=[{'label': i, 'value': i} for i in find_xlsx_files('data/gis_rubrik/unzip/Россия', [])],
        multi=False
    ),
    
    dcc.Input(
        id='latitude-input',
        type='number',
        placeholder='Enter latitude',
        value=55.7522  # Default value for Moscow
    ),
    
    dcc.Input(
        id='longitude-input',
        type='number',
        placeholder='Enter longitude',
        value=37.6156  # Default value for Moscow
    ),
    
    dcc.Input(
        id='radius-input',
        type='number',
        placeholder='Enter radius (in km)',
        value=3  # Default radius
    ),
    
    dcc.Input(
        id='filter-column-input',
        type='text',
        placeholder='Enter column for filtering',
        value=''  # Default value for column filtering
    ),
    
    dcc.Input(
        id='filter-value-input',
        type='text',
        placeholder='Enter value for filtering',
        value=''  # Default value for column filtering
    ),
    
    dl.Map(id="map", style={'width': '100%', 'height': '500px'}, center=(55.7522, 37.6156), zoom=10,
           children=[
               dl.TileLayer(),
               dl.LayerGroup(id='layer-group'),
           ]),
    
    dash_table.DataTable(
        id='filtered-contents',
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell={
            'minWidth': '100px', 'maxWidth': '300px',
            'whiteSpace': 'normal',
            'textAlign': 'left'
        },
        columns=[
            {"name": i, "id": i} for i in ['Название', 'Регион', 'Район', 'Город', 'Адрес', 'Широта', 'Долгота', 'Телефон', 'Email', 'Сайт']
        ],
    ),
    # Add more components as needed
])

# Callback to update the filtered contents based on the selected file, input keywords, latitude, longitude, radius,
# filter column, and filter value
@app.callback(
    [Output('filtered-contents', 'data'),
     Output('file-dropdown', 'options'),
     Output('layer-group', 'children')],
    [Input('file-dropdown', 'value'),
     Input('search-keywords-input', 'value'),
     Input('latitude-input', 'value'),
     Input('longitude-input', 'value'),
     Input('radius-input', 'value'),
     Input('filter-column-input', 'value'),
     Input('filter-value-input', 'value')]
)
def update_filtered_contents(selected_file, input_keywords, latitude, longitude, radius, filter_column, filter_value):
    # Update search_keywords based on user input
    search_keywords = [keyword.strip() for keyword in input_keywords.split(',')]
    
    # Read the selected file and filter based on keywords, latitude, longitude, radius, filter column, and filter value
    if selected_file:
        df = pd.read_excel(selected_file)
        df = filter_dataframe(df, search_keywords, latitude, longitude, radius, filter_column, filter_value)
        
        # Display the filtered DataFrame data
        data = df.to_dict('records')
        
        # Update options for the file dropdown
        file_options = [{'label': i, 'value': i} for i in find_xlsx_files('data/gis_rubrik/unzip/Россия', search_keywords)]
        
        # Create markers for the map
        markers = [dl.Marker(position=[row['Широта'], row['Долгота']], children=[
            dl.Tooltip(row['Название'])
        ]) for _, row in df.iterrows()]
        
        # Return the filtered DataFrame data, updated file dropdown options, and markers for the map
        return data, file_options, markers
    
    else:
        # If no file is selected, update the file dropdown options based on the search keywords
        file_options = [{'label': i, 'value': i} for i in find_xlsx_files('data/gis_rubrik/unzip/Россия', search_keywords)]
        return [], file_options, []

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
