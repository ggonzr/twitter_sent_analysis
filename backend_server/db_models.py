from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()


class Prediction(Base):
    """
    Resultados de la prediccion de una cadena de texto
    """

    __tablename__ = "prediction"
    text = Column(String, primary_key=True)
    label = Column(String)
    score = Column(Float)
    time = Column(Float)
