import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Set log level to DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)

# Load your Excel data (replace 'data.xlsx' with the actual path to your Excel file)
excel_file_path = 'data.xlsx'
# Load your Excel data (replace 'data.xlsx' with the actual path to your Excel file)
excel_file_path = 'data.xlsx'
try:
    df = pd.read_excel(excel_file_path)
except FileNotFoundError:
    df = pd.DataFrame(columns=['Супермаркеты', 'Такси'])  # Create an empty DataFrame if the file is not found
else:
    # Specify the columns of interest for conversion
    columns_of_interest = ['Супермаркеты', 'Такси']

    # Convert non-numeric values to NaN and replace NaN with 0 for the specified columns
    df[columns_of_interest] = df[columns_of_interest].apply(pd.to_numeric, errors='coerce').fillna(0)

    
print(df)

app = dash.Dash(__name__)

# Define the layout of the app with tabs
app.layout = html.Div([
    html.H1("Кластеризация спроса на Такси и супермаркеты с фильтрацией по городам"),

    html.Div([
        html.Label("Select City to Filter:"),
        dcc.Dropdown(
            id='city-filter-dropdown',
            options=[{'label': city, 'value': city} for city in df['Город'].unique()],
            multi=True,
            style={'width': '50%'}
        ),
        dcc.Input(
            id='num-clusters-input',
            type='number',
            placeholder='Enter Number of Clusters',
            value=3
        ),
        html.Img(id='cluster-plot'),
    ])
])

# Define callback to update clustering plot based on user-selected options
@app.callback(
    Output('cluster-plot', 'src'),
    [Input('city-filter-dropdown', 'value'),
     Input('num-clusters-input', 'value')]
)
def update_cluster_plot(selected_cities, num_clusters):
    # Filter data based on selected cities
    if selected_cities:
        df_filtered = df[df['Город'].isin(selected_cities)]
    else:
        df_filtered = df

    # Select relevant columns for clustering (adjust the columns as needed)
    clustering_columns = ['Супермаркеты', 'Такси']
    data_for_clustering = df_filtered[clustering_columns]

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_for_clustering)

    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    df_filtered['Cluster'] = kmeans.fit_predict(scaled_data)

    # Create a scatter plot for the first two columns with color-coded clusters
    plt.figure(figsize=(8, 6))
    for cluster in range(num_clusters):
        cluster_data = df_filtered[df_filtered['Cluster'] == cluster]
        plt.scatter(cluster_data[clustering_columns[0]], cluster_data[clustering_columns[1]], label=f'Cluster {cluster}')

    plt.title(f'Clustering: {clustering_columns[0]} vs {clustering_columns[1]}')
    plt.xlabel(clustering_columns[0])
    plt.ylabel(clustering_columns[1])
    plt.legend()

    # Save the plot to a BytesIO object
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close()

    # Encode the image as base64 and return the source for the HTML img tag
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    return f'data:image/png;base64,{img_base64}'

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
