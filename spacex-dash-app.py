# SpaceX Launch Records Dashboard - Complete Implementation
# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Print dataset info for debugging
print("Dataset Info:")
print(f"Total records: {len(spacex_df)}")
print(f"Columns: {list(spacex_df.columns)}")
print(f"Launch Sites: {spacex_df['Launch Site'].unique()}")
print(f"Payload range: {min_payload} - {max_payload} kg")
print(f"Class distribution: {spacex_df['class'].value_counts()}")

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    html.Div([
        html.Label("Select Launch Site:", style={'font-weight': 'bold'}),
        dcc.Dropdown(id='site-dropdown',
                    options=[
                        {'label': 'All Sites', 'value': 'ALL'}
                    ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                    value='ALL',
                    placeholder="Select a Launch Site here",
                    searchable=True,
                    style={'width': '50%', 'margin': '0 auto'}
                    )
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'font-weight': 'bold', 'textAlign': 'center'}),
    
    # TASK 3: Add a slider to select payload range
    html.Div([
        dcc.RangeSlider(id='payload-slider',
                       min=0, 
                       max=10000, 
                       step=1000,
                       marks={i: f'{i}' for i in range(0, 11000, 2500)},
                       value=[min_payload, max_payload],
                       tooltip={"placement": "bottom", "always_visible": True}
                       )
    ], style={'margin': '20px 50px'}),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Use all data for all sites
        fig = px.pie(spacex_df, 
                    values='class', 
                    names='Launch Site', 
                    title='Total Success Launches By Site',
                    color_discrete_sequence=px.colors.qualitative.Set3)
    else:
        # Filter dataframe for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Create success vs failure pie chart for selected site
        success_counts = filtered_df['class'].value_counts()
        
        fig = px.pie(values=success_counts.values, 
                    names=['Failed', 'Success'] if 0 in success_counts.index else ['Success'],
                    title=f'Total Success Launches for site {entered_site}',
                    color_discrete_sequence=['#ff7f7f', '#7fbf7f'])
    
    # Update layout for better appearance
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        font=dict(size=14)
    )
    
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, 
# `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    # Filter dataframe based on payload range
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    if entered_site == 'ALL':
        # Use filtered data for all sites
        fig = px.scatter(filtered_df, 
                        x='Payload Mass (kg)', 
                        y='class',
                        color='Booster Version Category',
                        size='Payload Mass (kg)',
                        hover_data=['Launch Site'],
                        title='Correlation between Payload and Success for all Sites',
                        labels={'class': 'Launch Outcome'})
    else:
        # Filter for specific site and payload range
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        fig = px.scatter(site_filtered_df, 
                        x='Payload Mass (kg)', 
                        y='class',
                        color='Booster Version Category',
                        size='Payload Mass (kg)',
                        title=f'Correlation between Payload and Success for site {entered_site}',
                        labels={'class': 'Launch Outcome'})
    
    # Update layout for better appearance
    fig.update_layout(
        title_font_size=16,
        title_x=0.5,
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Launch Outcome",
        font=dict(size=12),
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success'])
    )
    
    # Add grid for better readability
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

# Add custom CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .dash-graph {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 20px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    # 修正版：最新のDash APIを使用
    app.run(debug=True, host='0.0.0.0', port=8050)