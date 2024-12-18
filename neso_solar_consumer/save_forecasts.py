# save_forecasts.py

from nowcasting_datamodel.save.save import save


def save_forecasts_to_db(forecasts: list, session):
    """
    Save a list of ForecastSQL objects to the database using the nowcasting_datamodel `save` function.

    Parameters:
        forecasts (list): The list of ForecastSQL objects to save.
        session (Session): SQLAlchemy session for database access.
    """
    save(
        forecasts=forecasts,
        session=session,
        save_to_last_seven_days=True,  # Save forecasts to the last seven days table
    )
