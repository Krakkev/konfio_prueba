from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///entregable/konfio.db', echo=True)
Base = declarative_base()

########################################################################
class Contact(Base):
    """"""
    __tablename__ = "contact"

    id_item = Column(String, primary_key=True)
    price = Column(Integer)
    title = Column(String)
    description = Column(String)
    site = Column(String)

    #----------------------------------------------------------------------
    def __init__(self, id_item, price, title, description, site):
        """"""
        self.id_item = id_item
        self.price = price
        self.title = title
        self.description = description
        self.site = site

# create tables
Base.metadata.create_all(engine)