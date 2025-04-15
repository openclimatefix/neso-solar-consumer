import logging
from nowcasting_datamodel.save.save import save
from pvsite_datamodel.write.generation import insert_generation_values
from pvsite_datamodel.read.site import get_site_by_client_site_name
from pvsite_datamodel.write.user_and_site import create_site
from pvsite_datamodel.pydantic_models import PVSiteEditMetadata as PVSite
from sqlalchemy.orm.session import Session
import os
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


nl_national = PVSite(client_site_name="nl_national", latitude="52.15", longitude="5.23")


def save_generation_to_site_db(generation_data: pd.DataFrame, session: Session, country: str = "nl"):
    """Save generation data to the database.

    Parameters:
        generation_data (pd.DataFrame): DataFrame containing generation data to save.
            The following columns must be present: solar_generation_kw and target_datetime_utc
        session (Session): SQLAlchemy session for database access.
        country: (str): Country code for the generation data. Currently only 'nl' is supported.

    Return:
        None
    """
    # Check if generation_data is empty
    if generation_data.empty:
        logger.warning("No generation data provided to save!")
        return

    if country != 'nl':
        raise Exception("Only NL generation data is supported when saving (atm).")

    try:
        logger.info("Saving generation data to the database.")

        # get site uuid
        try:
            site = get_site_by_client_site_name(
                session=session,
                client_site_name=nl_national.client_site_name,
                client_name=nl_national.client_site_name, # this is not used
            )
        except Exception:
            logger.info(f"Creating site {nl_national.client_site_name} in the database.")
            site, _ = create_site(
                session=session,
                latitude=nl_national.latitude,
                longitude=nl_national.longitude,
                client_site_name=nl_national.client_site_name,
                client_site_id=1,
                country='nl',
                capacity_kw=20_000_000,
                dno='',  # these are UK specific things
                gsp='',  # these are UK specific things
            )

        # add site_uuid to the generation data
        generation_data["site_uuid"] = site.site_uuid

        # rename columns to match the database schema
        generation_data.rename(
            columns={
                "solar_generation_kw": "power_kw",
                "target_datetime_utc": "start_utc",
            },
            inplace=True,
        )

        # make sure start_utc is datetime
        generation_data["start_utc"] = pd.to_datetime(generation_data["start_utc"])

        insert_generation_values(
            session=session,
            df=generation_data,
        )
        session.commit()

        # update capacity
        if generation_data['power_kw'].max() > site.capacity_kw:
            old_site_capacity_kw = site.capacity_kw
            site.capacity_kw = generation_data['power_kw'].max()
            session.commit()
            logger.info(f"Updated site {nl_national.client_site_name} capacity "
                        f"from {old_site_capacity_kw} to {site.capacity_kw} kW.")

        logger.info(f"Successfully saved {len(generation_data)} rows of generation data.")
    except Exception as e:
        logger.error(f"An error occurred while saving generation data: {e}")
        raise e


def save_forecasts_to_db(forecasts: list, session: Session):
    """Save forecasts to the database.

    Parameters:
        forecasts (list): List of forecast objects to save.
        session (Session): SQLAlchemy session for database access.

    Return:
        None
    """
    # Check if forecasts is empty
    if not forecasts:
        logger.warning("No forecasts provided to save!")
        return

    try:
        logger.info("Saving forecasts to the database.")
        save(
            forecasts=forecasts,
            session=session,
        )
        logger.info(f"Successfully saved {len(forecasts)} forecasts to the database.")
    except Exception as e:
        logger.error(f"An error occurred while saving forecasts: {e}")
        raise e


def save_forecasts_to_csv(forecasts: pd.DataFrame, csv_dir: str):
    """Save forecasts to a CSV file.

    Parameters:
        forecasts (pd.DataFrame): DataFrame containing forecast data to save.
        csv_dir (str): Directory to save CSV files.

    Return:
        None
    """
    # Check if forecasts is empty
    if forecasts.empty:
        logger.warning("No forecasts provided to save!")
        return

    if not csv_dir:  # check if directory csv directory provided
        raise ValueError("CSV directory is not provided for CSV saving.")

    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, "forecast_data.csv")

    try:
        forecasts.drop(
            columns=["_sa_instance_state"], errors="ignore", inplace=True
        )  # Remove SQLAlchemy metadata

        logger.info(f"Saving forecasts to CSV at {csv_path}")
        forecasts.to_csv(csv_path, index=False)
        logger.info(f"Successfully saved {len(forecasts)} forecasts to CSV.")
    except Exception as e:
        logger.error(f"An error occurred while saving forecasts to CSV: {e}")
        raise e
