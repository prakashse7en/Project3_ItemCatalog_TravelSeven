from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import City, Base, Description, User

engine = create_engine('sqlite:///travelseven.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

#delete all rows from db for table users/city/description
"""
try:
    num_rows_deleted = session.query(User).delete()
    session.query(City).delete()
    session.query(Description).delete()
    session.commit()
    print"rows deleted"
    print num_rows_deleted
except:
    print "not deleted"
    session.rollback()
"""

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()



# City 1 for chikmagalur
city1 = City(user_id=1, name="Chikmagalur",category="Adventure")

session.add(city1)
session.commit()

description2 = Description(user_id=1, name="good for adventure", bestseason="November",place_pic="https://goo.gl/4dOYlI",city=city1)

session.add(description2)
session.commit()


# Menu for Super Stir Fry
city2 = City(user_id=1, name="Shimoga",category="Adventure")

session.add(city2)
session.commit()


description1 = Description(user_id=1, name="good to bath in water falls", bestseason="May",place_pic="https://goo.gl/4dOYlI",city=city2)

session.add(description1)
session.commit()


print "added menu items!"
