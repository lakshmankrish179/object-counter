import os
import logging
from counter.adapters.db_count_repo import DbObjectCountRepo
from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env file automatically

# Configure logger for the configuration module
logger = logging.getLogger(__name__)

def get_count_repo():
    """
    Returns an instance of DbObjectCountRepo with environment-based configuration.
    For development, it defaults to SQLite. For production, it uses PostgreSQL.
    """

    # Get environment variable to check current environment (dev or prod)
    environment = os.getenv('ENVIRONMENT', 'dev').lower()

    if environment == 'prod':
        # Fetch PostgreSQL credentials securely from environment variables
        postgres_user = os.getenv('POSTGRES_USER')
        postgres_password = os.getenv('POSTGRES_PASSWORD')
        postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        postgres_port = os.getenv('POSTGRES_PORT', '5432')
        postgres_db = os.getenv('POSTGRES_DB', 'object_counter')

        if not postgres_user or not postgres_password:
            logger.error("PostgreSQL credentials are not properly set in environment variables.")
            raise EnvironmentError("Missing PostgreSQL credentials in environment variables.")

        # Construct PostgreSQL connection string
        connection_string = (
            f"postgresql://{postgres_user}:{postgres_password}"
            f"@{postgres_host}:{postgres_port}/{postgres_db}"
        )
        logger.info("Configured PostgreSQL for production environment.")

    else:
        # SQLite for local development/testing
        connection_string = "sqlite:///object_counter.db"
        logger.info("Configured SQLite for development environment.")

    # Initialize and return the database repository instance
    return DbObjectCountRepo(connection_string)
