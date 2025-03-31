from logger_config import logger  
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from counter.domain.ports import ObjectCountRepo


# Define SQLAlchemy base model
Base = declarative_base()

# Define ORM model for Object Count
class ObjectCount(Base):
    __tablename__ = 'object_counts'

    id = Column(Integer, primary_key=True)
    object_class = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    confidence_threshold = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database adapter implementation of ObjectCountRepo interface
class DbObjectCountRepo(ObjectCountRepo):

    def __init__(self, connection_string):
        # Initialize database connection
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)  # Create tables
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Database connected and tables created successfully.")

    def save_counts(self, counts, threshold):
        """Save object counts to the database."""
        session = self.Session()
        try:
            logger.info("Saving object counts to database.")
            for object_class, count in counts.items():
                obj_count = ObjectCount(
                    object_class=object_class,
                    count=count,
                    confidence_threshold=threshold
                )
                session.add(obj_count)
                logger.debug(f"Queued for insert: {object_class} -> {count}")

            session.commit()
            logger.info("Object counts saved successfully.")

        except Exception as e:
            session.rollback()
            logger.exception(f"Error while saving object counts: {e}")
            raise
        finally:
            session.close()
            logger.debug("Database session closed.")
