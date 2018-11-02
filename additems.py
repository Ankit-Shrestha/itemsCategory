#!/usr/bin/env python3
#for deploymnet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Base, Items, User
engine = create_engine('postgresql://catalog:surviver123@localhost/catalog')
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


# Create dummy user
# User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
#              picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
# session.add(User1)
# session.commit()

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

Category1 = Categories(user_id=1, categoryName="Book",
                       categoryDetails="This Category is for people who love reading",
                       categoryAgeGroup="Any", priceRange="$40-$1000", categorySector="Books")

session.add(Category1)
session.commit()

Item1 = Items(user_id=1, itemName="Harry potter",
              description="Harry potter season 3", price="$350", categories=Category1)

session.add(Item1)
session.commit()

Item2 = Items(user_id=1, itemName="Gloves",
              description="Synthetic leather gloves good for cold weather", price="$10", categories=Category1)

session.add(Item2)
session.commit()

Category2 = Category1 = Categories(user_id=1, categoryName="Cricket",
                                   categoryDetails="This Category is for people who love Cricket",
                                   categoryAgeGroup="8-50", priceRange="$40-$1000", categorySector="Sports")

session.add(Category2)
session.commit()

Item1 = Items(user_id=1, itemName="Bat",
              description="English willow with 8 grains", price="$20", categories=Category2)

session.add(Item1)
session.commit()


Item2 = Items(user_id=1, itemName="Ball",
              description="leather ball with longer durability", price="$30", categories=Category2)

session.add(Item2)
session.commit()


Item3 = Items(user_id=1, itemName="Guard",
              description="plastic guards for longer durability", price="$40", categories=Category2)

session.add(Item3)
session.commit()

Category3 = Category1 = Categories(user_id=1, categoryName="Football",
                                   categoryDetails="This Category is for people who love Football",
                                   categoryAgeGroup="8-50", priceRange="$40-$1000", categorySector="Sports")

session.add(Category3)
session.commit()

Item1 = Items(user_id=1, itemName="Ball",
              description="champions league ball made of leather", price="$30", categories=Category3)

session.add(Item1)
session.commit()


print("added menu items!")
