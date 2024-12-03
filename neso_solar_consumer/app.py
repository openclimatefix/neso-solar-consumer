"""
Main Script to Fetch, Format, and Save NESO Solar Forecast Data

This script orchestrates the following steps:
1. Fetches solar forecast data using the `fetch_data` function from `fetch_data.py`.
2. Formats the forecast data (currently a placeholder for future enhancements).
3. Saves the forecast data (currently a placeholder for future enhancements).

Each step is modularized into functions to allow for testing and future extension.

Functions:
    - get_forecast: Fetches raw solar forecast data.
    - format_forecast: Processes the forecast data for a specific format (placeholder for now).
    - save_forecast: Saves the formatted forecast data (placeholder for now).
"""

from .fetch_data import fetch_data


def get_forecast():
    """
    Fetch solar forecast data from NESO API.

    This function retrieves the solar forecast data from the NESO API and processes
    it into a Pandas DataFrame using the `fetch_data` function.

    Returns:
        pd.DataFrame: A DataFrame containing solar forecast data with the following columns:
                      - `start_utc`: Start time of the forecast (UTC).
                      - `end_utc`: End time of the forecast (UTC).
                      - `solar_forecast_kw`: Forecasted solar energy in kW.
    """
    resource_id = "example_resource_id"  # Replace with the actual resource ID.
    limit = 100  # Number of records to fetch.
    columns = ["DATE_GMT", "TIME_GMT", "EMBEDDED_SOLAR_FORECAST"]  # Relevant columns to extract.
    rename_columns = {
        "DATE_GMT": "start_utc",
        "TIME_GMT": "end_utc",
        "EMBEDDED_SOLAR_FORECAST": "solar_forecast_kw",
    }

    # Fetch and return data as a DataFrame.
    return fetch_data(resource_id, limit, columns, rename_columns)


def format_forecast(data):
    """
    Format solar forecast data.

    Placeholder function for future enhancements. In its current form, it simply logs
    a message and returns the input data unmodified.

    Parameters:
        data (pd.DataFrame): The raw forecast data fetched from the NESO API.

    Returns:
        pd.DataFrame: The formatted forecast data (currently identical to input data).
    """
    print("Formatting forecast data...")
    return data  # Currently, no modifications are applied.


def save_forecast(data):
    """
    Save solar forecast data.

    Placeholder function for future enhancements. In its current form, it logs
    a message but does not persist data.

    Parameters:
        data (pd.DataFrame): The formatted forecast data to be saved.

    Returns:
        None
    """
    print("Saving forecast data...")
    # Future implementation will save data to a database or file.


if __name__ == "__main__":
    """
    Orchestrates the following steps:
        1. Fetch forecast data.
        2. Format forecast data.
        3. Save forecast data.
    """
    # Step 1: Get forecast data
    print("Fetching forecast data...")
    forecast_data = get_forecast()

    # Step 2: Format forecast data
    print("Formatting forecast data...")
    formatted_data = format_forecast(forecast_data)

    # Step 3: Save forecast data
    print("Saving forecast data...")
    save_forecast(formatted_data)

    print("Process completed successfully!")
