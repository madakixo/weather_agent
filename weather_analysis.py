import os
from groq import Groq
from dotenv import load_dotenv
import logging
import pandas as pd
from voluptuous import Schema, Required, All, Length, Range

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

# Input validation schema
location_schema = Schema({
    Required('location'): All(str, Length(min=2, max=100)),
})

def get_weather_query(prompt, model_name="llama3-8b-8192"):
    """
    Use Groq with Llama-3 to interpret and respond to a weather query.

    :param prompt: The query about weather.
    :param model_name: The name of the model to use, defaulting to 'llama3-8b-8192'.
    :return: Groq's response to the query.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a weather assistant specialized in weather analysis."},
                {"role": "user", "content": prompt}
            ],
            model=model_name
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"An error occurred while querying Groq: {e}")
        return f"Error: Could not retrieve weather information - {str(e)}"

def fetch_weather_data(location):
    """
    Fetch weather data for a given location using Groq and Llama-3.
    """
    try:
        # Validate input
        location_schema({'location': location})
        
        # Simulated data retrieval - in real use, you'd use an actual weather API or more complex query
        history_query = f"Provide a 7-day weather history for {location}"
        prediction_query = f"Predict the next 3 days weather for {location}"
        
        history_response = get_weather_query(history_query)
        prediction_response = get_weather_query(prediction_query)
        
        # Parse responses (this would be more complex in reality)
        history_data = parse_weather_response(history_response, days=7)
        prediction_data = parse_weather_response(prediction_response, days=3)
        
        return pd.DataFrame(history_data), pd.DataFrame(prediction_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(), pd.DataFrame()

def parse_weather_response(response, days):
    """Parse the weather response into a list of dictionaries."""
    # This is a placeholder; in reality, you'd need to parse Groq/Llama-3's text output into structured data
    return [{'date': f"Day {i}", 'temp': f"{20+i}°C", 'humidity': f"{50+i}%", 'condition': 'Sunny'} for i in range(days)]

def main():
    location = input("Enter Location: ")
    history_df, prediction_df = fetch_weather_data(location)
    
    if not history_df.empty and not prediction_df.empty:
        print("\n7-Day Weather History:")
        print(history_df.to_string(index=False))
        
        print("\n3-Day Weather Prediction:")
        print(prediction_df.to_string(index=False))
    else:
        print("No data available for the given location.")

if __name__ == "__main__":
    main()
