import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table

app = dash.Dash(__name__)

# Function to check if a string contains all specified keywords
def contains_keywords(string, keywords):
    if not isinstance(string, str):
        return False
    return all(keyword.lower() in string.lower() for keyword in keywords)

# Function to filter a DataFrame
def filter_dataframe(df, search_keywords):
    df = df[df['Название'].apply(lambda x: contains_keywords(x, search_keywords))]
    return df

# Function to find all .xlsx files in a folder
def find_xlsx_files(root_folder, search_keywords):
    xlsx_files = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.xlsx') and contains_keywords(file, search_keywords):
                xlsx_files.append(os.path.join(root, file))
    return xlsx_files

data_tab_layout = html.Div([
    html.H1("Filtered Excel File Reading with Dash - Data"),

    # Input for search keywords (No Geographical Filter)
    dcc.Textarea(
        id='search-keywords-input-no-geo',
        placeholder='Enter search keywords (comma-separated)',
        style={'width': '100%'},
        value='',  # Set default value to an empty string
    ),

    dcc.Dropdown(
        id='file-dropdown-no-geo',
        options=[{'label': i, 'value': i} for i in find_xlsx_files('data/gis_rubrik/unzip/Россия', [])],
        multi=False
    ),

    dash_table.DataTable(
        id='filtered-contents-no-geo',
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell={
            'minWidth': '100px', 'maxWidth': '300px',
            'whiteSpace': 'normal',
            'textAlign': 'left'
        },
        # Show all columns in the Data tab
        columns=[
            {"name": col, "id": col} for col in ['Название', 'Регион', 'Район', 'Город', 'Район города', 'Адрес', 'Индекс',
                                                 'Телефон', 'Мобильный телефон', 'Email', 'Сайт', 'Рубрика', 'Подрубрика',
                                                 'Время работы', 'Способы оплаты', 'whatsapp', 'viber', 'telegram', 'facebook',
                                                 'instagram', 'vkontakte', 'odnoklassniki', 'youtube', 'twitter', 'skype', 'icq',
                                                 'googleplus', 'linkedin', 'pinterest', 'Широта', 'Долгота']
        ],
    ),
])

# Callback to update the filtered contents based on the selected file and input keywords (No Geographical Filter tab)
@app.callback(
    [Output('filtered-contents-no-geo', 'data'),
     Output('file-dropdown-no-geo', 'options')],
    [Input('file-dropdown-no-geo', 'value'),
     Input('search-keywords-input-no-geo', 'value')]
)
def update_filtered_contents_no_geo(selected_file, input_keywords):
    # Update search_keywords based on user input
    search_keywords = [keyword.strip() for keyword in input_keywords.split(',')]

    # Read the selected file and filter based on keywords
    if selected_file:
        df = pd.read_excel(selected_file)
        df = filter_dataframe(df, search_keywords)

        # Display the filtered DataFrame data
        data = df.to_dict('records')

        # Update options for the file dropdown
        file_options = [{'label': i, 'value': i} for i in find_xlsx_files('data/gis_rubrik/unzip/Россия', search_keywords)]

        # Return the filtered DataFrame data and updated file dropdown options
        return data, file_options

    else:
        # If no file is selected, update the file dropdown options based on the search keywords
        file_options = [{'label': i, 'value': i} for i in find_xlsx_files('data/gis_rubrik/unzip/Россия', search_keywords)]
        return [], file_options

# Set the layout of the app
app.layout = data_tab_layout

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8051, debug=True)
