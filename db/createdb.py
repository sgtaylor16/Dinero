from sqlalchemy import create_engine
from models import Base  # Import Base from your models
import models  # Import all models to register them

engine = create_engine("sqlite:///investments.db", echo=True)

# Create all tables
Base.metadata.create_all(engine)

print("Database and tables created successfully!")



