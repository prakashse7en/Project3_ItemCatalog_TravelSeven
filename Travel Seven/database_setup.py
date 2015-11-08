from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

	
class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    category = Column(String(250), nullable=False)
	
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
	    'category' : self.category,
            'id': self.id,
        }

class Description(Base):
    __tablename__ = 'description'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    bestseason = Column(String(250), nullable=False)
    place_pic = Column(String(250), nullable=False)
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship(City)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
	    'bestseason' : self.bestseason,
            'id': self.id,
        }
	



#engine = create_engine('sqlite:///restaurantmenu.db')
engine = create_engine('sqlite:///travelseven.db')


Base.metadata.create_all(engine)
