"""
Main Script to Fetch, Format, and Save NESO Solar Forecast Data

This script orchestrates the following steps:
1. Fetches solar forecast data using the `fetch_data` function.
2. Formats the forecast data into `ForecastSQL` objects using `format_forecast.py`.
3. Saves the formatted forecasts into the database using `save_forecast.py`.
"""

import os
import logging
from neso_solar_consumer.fetch_data import fetch_data
from neso_solar_consumer.format_forecast import format_to_forecast_sql
from neso_solar_consumer.save_forecast import save_forecasts
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models import Base_Forecast
from neso_solar_consumer import __version__  # Import version from __init__.py

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def app(db_url: str):
    """
    Main application function to fetch, format, and save solar forecast data.

    Parameters:
        db_url (str): Database connection URL from an environment variable.
    """
    logger.info(f"Starting the NESO Solar Forecast pipeline (version: {__version__}).")

    # Use the `Neso` class for hardcoded configuration
    model_tag = "neso-solar-forecast"

    # Initialize database connection
    connection = DatabaseConnection(url=db_url, base=Base_Forecast, echo=False)

    try:
        with connection.get_session() as session:
            # Step 1: Fetch forecast data
            logger.info("Fetching forecast data.")
            forecast_data = fetch_data()

            if forecast_data.empty:
                logger.warning("No data fetched. Exiting the pipeline.")
                return

            # Step 2: Format forecast data
            logger.info(f"Formatting {len(forecast_data)} rows of forecast data.")
            forecasts = format_to_forecast_sql(
                data=forecast_data,
                model_tag=model_tag,
                model_version=__version__,  # Use the version from __init__.py
                session=session,
            )

            if not forecasts:
                logger.warning("No forecasts generated. Exiting the pipeline.")
                return

            logger.info(f"Generated {len(forecasts)} ForecastSQL objects.")

            # Step 3: Save forecasts to the database
            logger.info("Saving forecasts to the database.")
            save_forecasts(forecasts, session)

            logger.info("Forecast pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Error in the forecast pipeline: {e}")
        raise


if __name__ == "__main__":
    # Step 1: Fetch the database URL from the environment variable
    db_url = os.getenv("DB_URL")  # Change from "DATABASE_URL" to "DB_URL"

    save_method = os.getenv("SAVE_METHOD", "db").lower()  # Default to "db"
    csv_dir = os.getenv("CSV_DIR")
    
    
    if save_method == "csv" and not csv_dir:
        logger.error("CSV_DIR environment variable is required for CSV saving. Exiting.")
        exit(1)

    if not db_url:
        logger.error("DB_URL environment variable is not set. Exiting.")
        exit(1)

    # Step 2: Run the application
    app(db_url=db_url, save_method=save_method, csv_dir=csv_dir)
