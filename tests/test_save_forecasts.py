"""
Integration Test for Fetching, Formatting, and Saving Forecast Data

This script validates the integration of fetching real data, formatting it into ForecastSQL objects,
and saving it to the database.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from nowcasting_datamodel.models.base import Base_Forecast
from nowcasting_datamodel.models import ForecastSQL
from neso_solar_consumer.fetch_data import fetch_data
from neso_solar_consumer.format_forecast import format_to_forecast_sql
from neso_solar_consumer.save_forecasts import save_forecasts_to_db

# Test configuration
RESOURCE_ID = "db6c038f-98af-4570-ab60-24d71ebd0ae5"
LIMIT = 5
COLUMNS = ["DATE_GMT", "TIME_GMT", "EMBEDDED_SOLAR_FORECAST"]
RENAME_COLUMNS = {
    "DATE_GMT": "start_utc",
    "TIME_GMT": "end_utc",
    "EMBEDDED_SOLAR_FORECAST": "solar_forecast_kw",
}
MODEL_NAME = "real_data_model"
MODEL_VERSION = "1.0"


@pytest.fixture
def db_session():
    """
    Create a PostgreSQL database session for testing.

    Returns:
        Generator: A session object to interact with the database.
    """
    engine = create_engine("postgresql://postgres:12345@localhost/testdb")
    Base_Forecast.metadata.create_all(engine)  # Create tables
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    engine.dispose()


def test_save_real_forecasts(db_session):
    """
    Integration test: Fetch real data, format it into forecasts, and save to the database.

    Steps:
    1. Fetch real data from the NESO API.
    2. Format the data into ForecastSQL objects.
    3. Save the forecasts to the database.
    4. Verify that the forecasts are correctly saved.
    """
    # Step 1: Fetch real data
    df = fetch_data(RESOURCE_ID, LIMIT, COLUMNS, RENAME_COLUMNS)
    assert not df.empty, "fetch_data returned an empty DataFrame!"

    # Step 2: Format data into ForecastSQL objects
    forecasts = format_to_forecast_sql(df, MODEL_NAME, MODEL_VERSION, db_session)
    assert forecasts, "No forecasts were generated from the fetched data!"

    # Step 3: Save forecasts to the database
    save_forecasts_to_db(forecasts, db_session)

    # Step 4: Verify forecasts are saved in the database
    saved_forecast = db_session.query(ForecastSQL).first()
    assert saved_forecast is not None, "No forecast was saved to the database!"
    assert saved_forecast.model.name == MODEL_NAME, "Model name does not match!"
    assert len(saved_forecast.forecast_values) > 0, "No forecast values were saved!"
