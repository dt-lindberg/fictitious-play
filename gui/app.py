import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os
import argparse


# --- Add external stylesheets for refined styling ---
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css",
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Custom CSS for the app
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
                background-color: #f8f9fa;
                font-family: 'Inter', sans-serif;
            }
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem 1.5rem;
            }
            .app-header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1.5rem;
                border-bottom: 1px solid rgba(0,0,0,0.1);
            }
            .app-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 0.5rem;
            }
            .app-subtitle {
                font-weight: 300;
                color: #7f8c8d;
                font-size: 1.1rem;
            }
            .card {
                border-radius: 8px;
                border: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                transition: transform 0.2s, box-shadow 0.2s;
                overflow: hidden;
            }
            .card:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.1);
            }
            .card-header {
                background-color: white;
                border-bottom: 1px solid rgba(0,0,0,0.05);
                padding: 1.25rem 1.5rem;
                font-weight: 500;
                color: #2c3e50;
            }
            .card-body {
                padding: 1.5rem;
            }
            .section-title {
                font-weight: 500;
                margin-bottom: 1rem;
                color: #2c3e50;
                display: flex;
                align-items: center;
            }
            .section-title i {
                margin-right: 0.5rem;
                color: #3498db;
            }
            .dash-dropdown .Select-control {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                box-shadow: none;
                height: 42px;
            }
            .dash-dropdown .Select-control:hover {
                border-color: #3498db;
            }
            .Select--single > .Select-control .Select-value, .Select-placeholder {
                line-height: 42px;
            }
            .params-badge {
                display: inline-block;
                padding: 0.4rem 0.8rem;
                margin-right: 0.5rem;
                margin-bottom: 0.5rem;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 500;
                background-color: rgba(52, 152, 219, 0.1);
                color: #3498db;
                border: 1px solid rgba(52, 152, 219, 0.2);
            }
            .params-label {
                font-weight: 600;
                color: #2c3e50;
                margin-right: 0.25rem;
            }
            .params-value {
                color: #3498db;
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

# Define function to create layout
def create_layout(game_ids, fig_hist):
    # Extract hyperparameters from dataframe if available
    hyperparams = {}
    try:
        if 'seed' in df.columns:
            hyperparams['Seed'] = df['seed'].iloc[0] if df['seed'].nunique() == 1 else 'Multiple'
        if 'max_iteration' in df.columns:
            hyperparams['Max Iterations'] = df['max_iteration'].iloc[0]-1 if df['max_iteration'].nunique() == 1 else 'Multiple'
        if 'window_size' in df.columns:
            hyperparams['Window Size'] = df['window_size'].iloc[0] if df['window_size'].nunique() == 1 else 'Multiple'
        if 'epsilon' in df.columns:
            hyperparams['Epsilon'] = df['epsilon'].iloc[0] if df['epsilon'].nunique() == 1 else 'Multiple'
    except:
        # Handle the case where we can't extract hyperparameters
        hyperparams = {}
    
    return html.Div(
        className="main-container",
        children=[
            # Header Section
            html.Div(
                className="app-header",
                children=[
                    html.H1("Fictitious Play Analysis", className="app-title"),
                    html.P("Interactive dashboard of convergence behavior during Fictitious play", className="app-subtitle")
                ]
            ),
            
            # Parameters Section
            html.Div(
                className="row mb-4",
                children=[
                    html.Div(
                        className="col-12",
                        children=[
                            html.Div(
                                className="card",
                                children=[
                                    html.Div(
                                        className="card-header",
                                        children=[
                                            html.I(className="fas fa-cogs me-2"),
                                            " Simulation Parameters"
                                        ]
                                    ),
                                    html.Div(
                                        className="card-body",
                                        children=[
                                            html.Div([
                                                html.Span(
                                                    className="params-badge",
                                                    children=[
                                                        html.Span(f"{key}: ", className="params-label"),
                                                        html.Span(f"{value}", className="params-value")
                                                    ]
                                                ) for key, value in hyperparams.items()
                                            ] if hyperparams else [
                                                html.Em("No hyperparameters available in dataset", className="text-muted")
                                            ])
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),

            # Chart Section
            html.Div(
                className="row",
                children=[
                    # Histogram card
                    html.Div(
                        className="col-md-6 mb-4",
                        children=[
                            html.H3(
                                className="section-title",
                                children=[
                                    html.I(className="fas fa-chart-histogram"),
                                    "Convergence Distribution"
                                ]
                            ),
                            html.Div(
                                className="card",
                                children=[
                                    html.Div(
                                        className="card-body",
                                        children=[
                                            dcc.Graph(
                                                id='convergence-histogram',
                                                figure=fig_hist,
                                                config={'displayModeBar': 'hover'}
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),

                    # Time-series card
                    html.Div(
                        className="col-md-6 mb-4",
                        children=[
                            html.H3(
                                className="section-title",
                                children=[
                                    html.I(className="fas fa-chart-line"),
                                    "Strategy Evolution"
                                ]
                            ),
                            html.Div(
                                className="card",
                                children=[
                                    html.Div(
                                        className="card-body",
                                        children=[
                                            html.Label(
                                                "Select Game:",
                                                className="mb-2 fw-bold"
                                            ),
                                            html.Div(
                                                dcc.Dropdown(
                                                    id='game-id-dropdown',
                                                    options=[
                                                        {'label': f'Game {gid}', 'value': gid}
                                                        for gid in game_ids
                                                    ],
                                                    value=game_ids[0] if game_ids else None,
                                                    clearable=False,
                                                    className="dash-dropdown mb-4"
                                                )
                                            ),
                                            dcc.Graph(
                                                id='time-series-chart',
                                                config={'displayModeBar': 'hover'}
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Define the callback to update the line chart
@app.callback(
    Output('time-series-chart', 'figure'),
    Input('game-id-dropdown', 'value')
)

def update_line_chart(selected_game_id):
    """Updates the line chart based on the selected game_id."""
    if selected_game_id is None:
        # Handle case where no game is selected
        return px.line(title="Select a Game ID to view its time series")

    # Filter the DataFrame for the selected game_id
    filtered_df = df[df['game_id'] == selected_game_id]

    if filtered_df.empty:
        return px.line(title=f"No data found for Game ID {selected_game_id}")

    # Create the line chart figure for the selected game
    try:
        # Melt the filtered data
        df_melted = filtered_df.melt(id_vars=['iteration'],
                                     value_vars=['rowena_probabilities', 'colin_probabilities'],
                                     var_name='Player', value_name='Value')
        # Update the names for the line plot
        value_map = {'rowena_probabilities' : 'Rowena',
                     'colin_probabilities' : 'Colin'}
        df_melted["Player"] = df_melted['Player'].replace(value_map)

        # Create a more visually appealing figure
        colors = {"Rowena": "#3498db", "Colin": "#e74c3c"}
        
        fig = px.line(
            df_melted,
            x='iteration',
            y='Value',
            color='Player',
            title=f'Strategy Evolution for Game {selected_game_id}',
            labels={'Value': 'Probability', 'iteration': 'Iteration'},
            color_discrete_map=colors,
            template='plotly_white'
        )
        fig.update_layout(
            font=dict(family='Inter, sans-serif', size=12, color='#2c3e50'),
            title_font=dict(size=16, family='Inter, sans-serif', color='#2c3e50'),
            title_x=0.5,  # Center the title
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)',
            showline=True, linewidth=1, linecolor='rgba(0,0,0,0.1)'
        )
        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)',
            showline=True, linewidth=1, linecolor='rgba(0,0,0,0.1)'
        )
        
        return fig
    except KeyError as e:
        print(f"Error creating line chart for game {selected_game_id}: Missing column {e}")
        return px.line(title=f"Error: Data missing for Game ID {selected_game_id}")

# Run the App
if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description="Visualize Fictitious Play Data")
    parser.add_argument("--output_file", type=str, required=True,
                        help="Path to the CSV file containing the data.")
    args = parser.parse_args()
    output_file = args.output_file
    
    # --- Load CSV Experiment Data ---
    # Try to load the csv file, attempting to default to other CSV files in the output
    # directory if the provided one cannot be loaded.
    # Declare df as global so the callback can access it
    global df 
    try:
        # df = pd.read_csv(output_file)
        df = pd.read_parquet(output_file)
    except Exception as e:
        print(f"Error loading or processing CSV file {output_file}:\n{e}")
        # Try to select another csv file from the output directory
        output_dir = os.listdir(os.path.join("outputs"))
        
        # If no other CSV files are found, then exit
        if len(output_dir) == 0:
            exit(1)
        # Otherwise try to load CSV files from the directory
        for i in range(len(output_dir)):
            try: 
                # df = pd.read_csv(os.path.join("outputs", output_dir[i]))
                df = pd.read_parquet(os.path.join("outputs", output_dir[i]))
                print(f"Defaulted to another CSV file in the output directory: {output_dir[i]}")
            except Exception as e:
                continue
        # If none succeed, then exit
        exit(1) 
    # --- End Load CSV Experiment Data ---

    # --- Create Histogram Figure ---
    # Make a histogram of how long it took for each game to converge
    # Group by game_id and get the last iteration (convergence time)
    convergence_times = df.groupby("game_id")["iteration"].last()

    # Create the histogram figure with improved style
    fig_hist = px.histogram(
        convergence_times,
        x="iteration",
        title="Distribution of Convergence Rates",
        labels={'iteration': 'Iterations to Converge', 'count': 'Number of Games'},
        nbins=50,
        template='plotly_white',
        color_discrete_sequence=["#3498db"]
    )
    fig_hist.update_layout(
        font=dict(family='Inter, sans-serif', size=12, color='#2c3e50'),
        title_font=dict(size=16, family='Inter, sans-serif', color='#2c3e50'),
        title_x=0.5,  # Center the title
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Number of Games",
        xaxis_title="Iterations to Converge",
        bargap=0.1
    )
    
    fig_hist.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)',
        showline=True, linewidth=1, linecolor='rgba(0,0,0,0.1)'
    )
    fig_hist.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)',
        showline=True, linewidth=1, linecolor='rgba(0,0,0,0.1)'
    )
    # --- End Create Histogram Figure ---


    # --- Get Unique Game IDs for Dropdown ---
    try:
        unique_game_ids = sorted(df['game_id'].unique())
    except KeyError:
        print("Error: 'game_id' column not found in CSV. Cannot create dropdown.")
        unique_game_ids = [] # Set empty list if column is missing

    
    # --- Assign Initial Layout ---
    # Pass unique game IDs and the histogram figure to the layout function
    app.layout = create_layout(unique_game_ids, fig_hist)
    # --- End Assign Layout ---


    # --- Run the App ---
    app.run(debug=True)

    # Features I'd like to have:
    # 1. Display a histogram of the number of iterations it takes for games to converge.
    # 2. Display some of the "hyperparameter" choices such as:
    #   - seed,
    #   - maximum number of iterations,
    #   - window_size,
    #   - epsilon.
    # 3. Create a two line of the average convergence rate over time and include the std, make it
    #   a line with shaded regions around it showing how much it deviates from the average. Create
    #   one such line for each value. 