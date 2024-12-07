from datetime import datetime, timezone
import pandas as pd
from nowcasting_datamodel.models import ForecastSQL, ForecastValue
from nowcasting_datamodel.read.read import get_latest_input_data_last_updated, get_location
from nowcasting_datamodel.read.read_models import get_model


def format_to_forecast_sql(data: pd.DataFrame, model_tag: str, model_version: str, session) -> list:
    """
    Convert fetched NESO solar data into ForecastSQL objects.

    Parameters:
        data (pd.DataFrame): The input DataFrame with solar forecast data.
        model_tag (str): The name/tag of the model.
        model_version (str): The version of the model.
        session (Session): SQLAlchemy session for database access.

    Returns:
        list: A list of ForecastSQL objects.
    """
    # Get the model object
    model = get_model(name=model_tag, version=model_version, session=session)

    # Fetch the last updated input data timestamp
    input_data_last_updated = get_latest_input_data_last_updated(session=session)

    forecasts = []
    for _, row in data.iterrows():
        if pd.isnull(row["start_utc"]) or pd.isnull(row["solar_forecast_kw"]):
            continue  # Skip rows with missing critical data

        # Convert "start_utc" to a datetime object
        target_time = datetime.fromisoformat(row["start_utc"]).replace(tzinfo=timezone.utc)

        forecast_values = [
            ForecastValue(
                target_time=target_time,
                expected_power_generation_megawatts=row["solar_forecast_kw"],
            ).to_orm()
        ]

        location = get_location(session=session, gsp_id=row.get("gsp_id", 0))

        forecast = ForecastSQL(
            model=model,
            forecast_creation_time=datetime.now(tz=timezone.utc),
            location=location,
            input_data_last_updated=input_data_last_updated,
            forecast_values=forecast_values,
            historic=False,
        )

        forecasts.append(forecast)

    return forecasts
