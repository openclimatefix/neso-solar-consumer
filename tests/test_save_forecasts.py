"""
Integration Test for Fetching, Formatting, and Saving Forecast Data

This script validates the integration of fetching real data, formatting it into ForecastSQL objects,
and saving it to the database.
"""

import pytest
from nowcasting_datamodel.models import ForecastSQL
from neso_solar_consumer.fetch_data import fetch_data
from neso_solar_consumer.format_forecast import format_to_forecast_sql
from neso_solar_consumer.save_forecasts import save_forecasts_to_db


def test_save_real_forecasts(db_session, test_config):
    """
    Integration test: Fetch real data, format it into forecasts, and save to the database.

    Steps:
    1. Fetch real data from the NESO API.
    2. Format the data into ForecastSQL objects.
    3. Save the forecasts to the database.
    4. Verify that the forecasts are correctly saved.
    """
    # Step 1: Fetch real data
    df = fetch_data(
        test_config["resource_id"],
        test_config["limit"],
        test_config["columns"],
        test_config["rename_columns"],
    )
    assert not df.empty, "fetch_data returned an empty DataFrame!"

    # Step 2: Format data into ForecastSQL objects
    forecasts = format_to_forecast_sql(
        df, test_config["model_name"], test_config["model_version"], db_session
    )
    assert forecasts, "No forecasts were generated from the fetched data!"

    # Step 3: Save forecasts to the database
    save_forecasts_to_db(forecasts, db_session)

    # Step 4: Verify forecasts are saved in the database
    saved_forecast = db_session.query(ForecastSQL).first()
    assert saved_forecast is not None, "No forecast was saved to the database!"
    assert saved_forecast.model.name == test_config["model_name"], "Model name does not match!"
    assert len(saved_forecast.forecast_values) > 0, "No forecast values were saved!"

    # Debugging Output (Optional)
    print("Forecast successfully saved to the database.")
    print(f"Number of forecast values: {len(saved_forecast.forecast_values)}")
