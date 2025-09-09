from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from .users import User
from .form import Form
from .form_fields import FormField
from .form_response import FormResponse
from .form_response_field import FormResponseField
from .form_analytics import FormAnalytics 