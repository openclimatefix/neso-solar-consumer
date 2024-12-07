"""
Test Suite for `format_to_forecast_sql` Function

This script validates the functionality of the `format_to_forecast_sql` function.
It checks if the function correctly converts the input data into SQLAlchemy-compatible
ForecastSQL objects.

### How to Run the Tests:

You can run the entire suite of tests in this file using `pytest` from the command line:
   
    pytest tests/test_format_forecast.py

To run a specific test, you can specify the function name:

    pytest tests/test_format_forecast.py::test_format_to_forecast_sql_real

For verbose output, use the -v flag:

    pytest tests/test_format_forecast.py -v

To run tests matching a specific pattern, use the -k option:

    pytest tests/test_format_forecast.py -k "format_to_forecast_sql"

"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from nowcasting_datamodel.models.base import Base_Forecast
from nowcasting_datamodel.models import MLModelSQL
from neso_solar_consumer.fetch_data import fetch_data
from neso_solar_consumer.format_forecast import format_to_forecast_sql

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
def db_session() -> Generator:
    """
    Create a PostgreSQL database session for testing.

    Returns:
        Generator: A session object to interact with the database.
    """
    engine = create_engine("postgresql://postgres:12345@localhost/testdb")
    Base_Forecast.metadata.create_all(engine)  # Create tables
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add a dummy model entry for the test
    model = MLModelSQL(name=MODEL_NAME, version=MODEL_VERSION)
    session.add(model)
    session.commit()

    yield session

    session.close()
    engine.dispose()


def test_format_to_forecast_sql_real(db_session):
    """
    Test `format_to_forecast_sql` with real data fetched from NESO API.

    Steps:
    1. Fetch data from the NESO API.
    2. Convert the data to ForecastSQL objects using `format_to_forecast_sql`.
    3. Validate the number of generated forecasts matches the input data.
    4. Verify that the model metadata (name, version) is correctly assigned.
    """
    # Fetch data
    data = fetch_data(RESOURCE_ID, LIMIT, COLUMNS, RENAME_COLUMNS)
    assert not data.empty, "fetch_data returned an empty DataFrame!"

    # Format data to ForecastSQL objects
    forecasts = format_to_forecast_sql(data, MODEL_NAME, MODEL_VERSION, db_session)

    # Assertions
    assert len(forecasts) == len(data), "Mismatch in number of forecasts and data rows!"
    assert forecasts[0].model.name == MODEL_NAME, "Model name does not match!"
    assert forecasts[0].model.version == MODEL_VERSION, "Model version does not match!"
