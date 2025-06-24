import os

from dotenv import load_dotenv


def load_config():
    """
    Load Odoo configuration from environment variables or config file

    Returns:
        dict: Configuration dictionary with url, db, username, password
    """

    load_dotenv()

    env = ("ODOO_URL", "ODOO_DB", "ODOO_USERNAME", "ODOO_PASSWORD")
    for var in env:
        if var not in os.environ:
            raise OSError(f"Missing required environment variable: {var}")
    return {
        "url": os.environ["ODOO_URL"],
        "db": os.environ["ODOO_DB"],
        "username": os.environ["ODOO_USERNAME"],
        "password": os.environ["ODOO_PASSWORD"],
    }
