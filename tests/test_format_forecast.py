from neso_solar_consumer.fetch_data import fetch_data
from neso_solar_consumer.format_forecast import format_to_forecast_sql
from nowcasting_datamodel.models import ForecastSQL, ForecastValue


def test_format_to_forecast_sql_real(db_session, test_config):
    """
    Test `format_to_forecast_sql` with real data fetched from the NESO API.
    """
    # Step 1: Fetch mock data from the API
    data = fetch_data(
        test_config["resource_id"],
        test_config["limit"],
        test_config["columns"],
        test_config["rename_columns"],
    )
    assert not data.empty, "fetch_data returned an empty DataFrame!"

    # Step 2: Format the data into a ForecastSQL object
    forecasts = format_to_forecast_sql(
        data, test_config["model_name"], test_config["model_version"], db_session
    )
    assert len(forecasts) == 1, "More than one ForecastSQL object was created!"

    # Step 3: Validate ForecastSQL content
    forecast = forecasts[0]
    assert len(forecast.forecast_values) == len(data), "Mismatch in ForecastValue entries!"
