# @madakixo update of weather_kd_flask
## visuals in barchat
# 3 day forecast
import os
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Groq API key from environment variable
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("Groq API key not found. Ensure GROQ_API_KEY is set in your environment.")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Create a new Dash application
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div([
    html.H1('Weather Assistant for Kaduna State'),
    html.Div([
        dcc.Input(id='query', type='text', placeholder='Enter location in Kaduna', style={'width': '70%'}),
        html.Button('Check Now', id='submit-button', n_clicks=0, style={'width': '25%', 'marginLeft': '5%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),
    html.Div(id='weather-info', style={'marginBottom': '20px'}),
    html.Div([
        html.Div(id='history-visualization', style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
        html.Div(id='forecast-visualization', style={'width': '48%', 'display': 'inline-block'})
    ]),
    html.Div(id='forecast-text', style={'marginTop': '20px'})
])

# Define a callback function to handle user input
@app.callback(
    [Output('weather-info', 'children'),
     Output('history-visualization', 'children'),
     Output('forecast-visualization', 'children'),
     Output('forecast-text', 'children')],
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('query', 'value')]
)
def get_weather_info(n_clicks, query):
    if n_clicks is None or query is None:
        raise PreventUpdate

    try:
        # Here we use Groq's chat completion API for reasoning and response
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a weather assistant specialized in Kaduna State's weather."},
                {"role": "user", "content": f"Provide weather for {query} including past 10 days history and 3 days forecast"}
            ],
            model="llama3-8b-8192"
        )
        weather_info = response.choices[0].message.content

        # Simulating data for history and forecast
        history_data = pd.DataFrame({
            'Date': [f'Day {i}' for i in range(10, 0, -1)],
            'Temperature': range(20, 30),
            'Humidity': range(60, 70)
        })
        forecast_data = pd.DataFrame({
            'Date': [f'Day {i}' for i in range(1, 4)],
            'Temperature': range(30, 33),
            'Humidity': range(55, 58)
        })

        # Create bar plots
        history_fig = px.bar(history_data, x='Date', y=['Temperature', 'Humidity'], barmode='group', 
                             title='10-Day Weather History', labels={'value': 'Value', 'variable': 'Metric'})
        forecast_fig = px.bar(forecast_data, x='Date', y=['Temperature', 'Humidity'], barmode='group', 
                              title='3-Day Weather Forecast', labels={'value': 'Value', 'variable': 'Metric'})

        history_visualization = dcc.Graph(figure=history_fig)
        forecast_visualization = dcc.Graph(figure=forecast_fig)

        # Extract and format forecast text
        forecast_text = "3-Day Forecast:\n"
        for _, row in forecast_data.iterrows():
            forecast_text += f"- {row['Date']}: Temp {row['Temperature']}°C, Humidity {row['Humidity']}%<br>"

        return weather_info, history_visualization, forecast_visualization, html.P(forecast_text)

    except Exception as e:
        logger.error(f"An error occurred while querying Groq: {e}")
        return f"Error: Could not retrieve weather information - {str(e)}", None, None, None

# Run the application
if __name__ == "__main__":
    app.run_server(debug=True)



"""
Bar Plots: The visualization has been changed from line plots to bar plots
using px.bar for both history and forecast, providing a clearer comparison
between temperature and humidity.
Layout: The layout has been restructured to display the input field and button
on the
same line, followed by textual weather information, then side-by-side bar plots for history and forecast, and finally, a textual summary of the forecast.
Data: Example data for both history and forecast has been included. In a real
scenario, you would parse this from the Groq response or fetch from an actual
weather API.
Forecast Text: Added a textual representation of the 3-day forecast for easier reading.

"""
