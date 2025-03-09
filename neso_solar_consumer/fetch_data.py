"""
Script to fetch NESO Solar Forecast Data
This script provides functions to fetch solar forecast data from the NESO API.
"""

import urllib.request
import urllib.parse
import json
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_API_URL = "https://api.neso.energy/api/3/action/"


def fetch_data(
    forecast_type: str = "embedded-wind-and-solar-forecasts",
) -> pd.DataFrame:
    """
    Fetch data from the NESO API and process it into a Pandas DataFrame.

    Parameters:
        forecast_type (str): The type of forecast to fetch (default: embedded solar & wind).

    Returns:
        pd.DataFrame: A DataFrame containing:
                      - `Datetime_GMT`: Combined date and time in UTC.
                      - `solar_forecast_kw`: Estimated solar forecast in kW.
    """
    try:
        meta_url = f"{BASE_API_URL}datapackage_show?id={forecast_type}"
        logger.info(f"Fetching metadata from {meta_url}...")

        response = urllib.request.urlopen(meta_url)
        data = json.loads(response.read().decode("utf-8"))

        # We take the latest path, which is the most recent forecast file
        url = data["result"]["resources"][0]["path"]
        logger.info(f"Fetching forecast data from {url}...")

        df = pd.read_csv(url)

        # Parse and combine DATE_GMT and TIME_GMT into a single timestamp
        df["Datetime_GMT"] = pd.to_datetime(
            df["DATE_GMT"].str[:10] + " " + df["TIME_GMT"].str.strip(),
            format="%Y-%m-%d %H:%M",
            errors="coerce",
        ).dt.tz_localize("UTC")

        # Convert solar forecast to kW
        df["solar_forecast_kw"] = df["EMBEDDED_SOLAR_FORECAST"] * 1000

        # Select only the required columns and drop rows with missing values
        df = df[["Datetime_GMT", "solar_forecast_kw"]].dropna()

        logger.info(f"Successfully fetched {len(df)} forecast records.")
        return df

    except urllib.error.URLError as e:
        logger.error(f"Network error while fetching data: {e}")
    except KeyError:
        logger.error("Unexpected API response format. Check NESO API structure.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return pd.DataFrame()


def fetch_data_using_sql(sql_query: str) -> pd.DataFrame:
    """
    Fetch data from the NESO API using an SQL query, process it, and return a DataFrame.

    Parameters:
        sql_query (str): The SQL query to fetch data from the API.

    Returns:
        pd.DataFrame: A DataFrame containing:
                      - `Datetime_GMT`: Combined date and time in UTC.
                      - `solar_forecast_kw`: Estimated solar forecast in kW.
    """
    try:
        encoded_query = urllib.parse.quote(sql_query)
        url = f"{BASE_API_URL}datastore_search_sql?sql={encoded_query}"
        logger.info(f"Fetching data using SQL query from {url}...")

        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf-8"))
        records = data["result"]["records"]

        df = pd.DataFrame(records)

        # Convert and clean timestamp fields
        df["Datetime_GMT"] = pd.to_datetime(
            df["DATE_GMT"].str[:10] + " " + df["TIME_GMT"].str.strip(),
            format="%Y-%m-%d %H:%M",
            errors="coerce",
        ).dt.tz_localize("UTC")

        # Rename forecast column and clean data
        df = df.rename(columns={"EMBEDDED_SOLAR_FORECAST": "solar_forecast_kw"})
        df = df[["Datetime_GMT", "solar_forecast_kw"]].dropna()

        logger.info(f"Successfully fetched {len(df)} forecast records.")
        return df

    except urllib.error.URLError as e:
        logger.error(f"Network error while fetching SQL data: {e}")
    except KeyError:
        logger.error("Unexpected API response format. Check NESO API structure.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return pd.DataFrame()
