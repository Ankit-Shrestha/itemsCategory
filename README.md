# Items Catalog App

The application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.


# Programming Knowledge

Knowledge of python3, flask, jinja2, SQLAlchemy, Bootstrap, OAuth, HTML, CSS, Google login, Database using SQLite

## Getting Started

The project can be done using the vagrant file provided by **Udacity**. Otherwise, download flask, SQLAlchemy for python3 and set up your own environment. Then, run ` python3 project.py` on command line and route to `localhost:8080/`. To change the port number, got to `project.py`, go to  `app.run(host = '0.0.0.0', port = 8080)` on the last line of the code and change the port number. There should be categories and items populated in the database otherwise the app will show nothing. 

## Create, Read, Update, or Delete entries
**Login and Home Page:**
`http://localhost:8080/login/` takes you to the login page.
`http://localhost:8080/catalog/` takes you to the home page with list of categories.

---
**Add Operations:**
`http://localhost:8080/catalog/add/` takes you to the add  a new category.
`﻿http://localhost:8080/catalog/Book/add/` takes you to add a item in a category. In this example, Book.

---
**Edit Operations:**
`http://localhost:8080/catalog/Book/edit/` takes you to edit a category. In this example, Book.
``http://localhost:8080/catalog/Book/Harrypotter/edit/`` takes you to edit a item in a category. In this example, category is Book and Harry Potter is a item.

---
**Delete Operations:**
`http://localhost:8080/catalog/Book/delete/` takes you to delete a category. In this example, Book.
``http://localhost:8080/catalog/Book/Harrypotter/delete/`` takes you to delete a item in a category. In this example, category is Book and Harry Potter is a item.

---
**List of items**
`http://localhost:8080/catalog/Book/items/` takes you to the list of items of a category . In this example, Book.
``http://localhost:8080/catalog/Book/Harrypotter/`` takes you the description page of the items. In the example, Harrypotter.

---
**JSON Endpoints**
``http://localhost:8080/catalog.json/`` takes you to the JSON for list of categories in the database.
``http://localhost:8080/Book/items.json/`` takes you to the JSON for items in a category. In this example, Book category.
``http://localhost:8080/Gloves/item.json/`` takes you the JSON for a item. In this example, Gloves item.

---
## Possible Improvements
Add login for facebook.
Better style the application.
Query the entire database with search box.