#!/usr/bin/env python3
from sqlalchemy import Column,String,Integer,ForeignKey,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = False)
    email = Column(String(100), nullable = False)
    picture = Column(String(500))

    @property
    def serialize(self):
        return {
           'name'         : self.name,
           'id'           : self.id,
           'email'		  : self.email,
           'picture' 	  : self.picture
        }

class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    categoryName = Column(String(250), nullable = False)
    categoryDetails = Column(String(1000), nullable=False)
    priceRange = Column(String(20))
    categorySector = Column(String(30),nullable=False)
    categoryAgeGroup = Column(String(20))
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))
    @property
    def serialize(self):
        return {
           'categoryName'         : self.categoryName,
           'id'                   : self.id,
           'categoryDetails'      : self.categoryDetails,
           'priceRange'           : self.priceRange,
           'categorySector'       : self.categorySector,
           'categoryAgeGroup'     : self.categoryAgeGroup
        }

class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key = True)
    itemName = Column(String(250), nullable = False)
    description = Column(String(500))
    price = Column(String(20))
    category_name = Column(String, ForeignKey('categories.categoryName')) 
    categories = relationship(Categories)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
           'itemName'         	  : self.itemName,
           'id'           		  : self.id,
           'description'	  	  : self.description,
           'price' 	      		  : self.price,
           'category_name'		  : self.category_name
        }


engine = create_engine('sqlite:///ItemsCatalog.db')
Base.metadata.create_all(engine)
