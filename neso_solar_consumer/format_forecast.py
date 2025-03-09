import logging
import pandas as pd
from datetime import datetime, timezone
from nowcasting_datamodel.read.read import get_latest_input_data_last_updated, get_location
from nowcasting_datamodel.read.read_models import get_model

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def format_forecast(data: pd.DataFrame, model_tag: str, model_version: str, session) -> pd.DataFrame:
    """
    Format solar forecast data into a standardized Pandas DataFrame.

    Parameters:
        data (pd.DataFrame): DataFrame containing `Datetime_GMT` (UTC) and `solar_forecast_kw`.
        model_tag (str): Model tag to fetch model metadata.
        model_version (str): Model version to fetch model metadata.
        session: Database session.

    Returns:
        pd.DataFrame: Formatted DataFrame with additional metadata.
    """
    logger.info("Starting forecast formatting process...")

    # Ensure required columns exist
    required_columns = {"Datetime_GMT", "solar_forecast_kw"}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"Missing required columns: {required_columns - set(data.columns)}")

    # Retrieve metadata
    model = get_model(name=model_tag, version=model_version, session=session)
    input_data_last_updated = get_latest_input_data_last_updated(session=session)
    location = get_location(session=session, gsp_id=0)  # National forecast

    # Drop rows with missing values
    data = data.dropna(subset=["Datetime_GMT", "solar_forecast_kw"])

    # Ensure Datetime_GMT is in datetime format
    data["Datetime_GMT"] = pd.to_datetime(data["Datetime_GMT"], utc=True)

    # Convert power to MW and add as a new column
    data["solar_forecast_mw"] = data["solar_forecast_kw"] / 1000  
    data.drop(columns=["solar_forecast_kw"], inplace=True)

    # Add metadata columns
    data["model_name"] = model.name
    data["model_version"] = model.version
    data["forecast_creation_time"] = datetime.now(tz=timezone.utc)
    data["location"] = location.name
    data["input_data_last_updated"] = input_data_last_updated

    logger.info(f"Formatted forecast data with {len(data)} entries.")
    return data
