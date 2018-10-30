#!/usr/bin/env python3
from functools import wraps
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Categories, Items, User
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import string
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Items Catalog App"

engine = create_engine('sqlite:///ItemsCatalog.db')
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))

# This function creates a random characters for the state and stores in the
# login_session to verify user.


"""<------------------------------  login section for google account   --------------------------------->"""
# login decorator function


def login_required(f):
    @wraps(f)
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = CreateUser(login_session)
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session[
        'access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showAllCategories'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


"""<-------------------------  end of login section for google account   ------------------------------------>"""


"""<------------------  Start of CRUD operations for Database and routes in the web app   ------------------->"""


@app.route('/')
@app.route('/catalog/')
def showAllCategories():
    categories = session.query(Categories).all()
    # for the recently added items getting the recent added 5 items.
    items = session.query(Items).order_by(desc(Items.itemName)).limit(5).all()
    # Protecting the pages on the basis of login.
    if 'username' not in login_session:
        return render_template('publicHome.html', categories=categories, items=items)
    else:
        return render_template('home.html', categories=categories, items=items)


@app.route('/catalog/add/', methods=['GET', 'POST'])
# if a user not in login session, gets redirected to the login page.
@login_required
def addCategory():
    categories = session.query(Categories).all()
    if request.method == 'POST':
        # if user typed in a name for the category
        if request.form['name']:
            for category in categories:
                # since, we are quering categories in edit and delete functions,
                # we cannot have duplicate categoryName, making sure, there are
                # no duplicate names for categoryName.
                if request.form['name'] == category.categoryName:
                    return "<script>function myFunction(){alert('Choose different name');}\
		</script><body onload = 'myFunction()'>"
            categoryToAdd = Categories(categoryName=request.form['name'], categorySector=request.form['sector'],
                                       categoryDetails=request.form['details'],
                                       priceRange=request.form['pricerange'],
                                       categoryAgeGroup=request.form[
                                           'agegroup'],
                                       user_id=login_session['user_id'])
            session.add(categoryToAdd)
            session.commit()
            flash("Category %s successfully added" %
                  categoryToAdd.categoryName)
    # redirect showAllCategories after the POST is handled.
        return redirect(url_for('showAllCategories'))
    # GET function
    return render_template('addCategory.html', categories=categories)


@app.route('/catalog/<string:categoryName>/edit/', methods=['GET', 'POST'])
# if a user not in login session, gets redirected to the login page.
@login_required
def editCategory(categoryName):
    categoryToEdit = session.query(Categories).filter_by(
        categoryName=categoryName).one()
    # only the user who created category should be able to edit the item.
    if categoryToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Not Authorized');}\
		</script><body onload = 'myFunction()'>"
    itemsInCategory = session.query(Items).filter_by(
        category_name=categoryName).all()
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.categoryName = request.form['name']
            categoryToEdit.categorySector = request.form['sector']
            categoryToEdit.categoryDetails = request.form['details']
            categoryToEdit.priceRange = request.form['pricerange']
            categoryToEdit.categoryAgeGroup = request.form['agegroup']
# category_name is relationship to the category table, while we edit categoryName
# we have to make sure that the category_name in the items table is
# changed as well.
            for item in itemsInCategory:
                item.category_name = request.form['name']
                session.add(item)
            session.add(categoryToEdit)
            session.commit()
            flash("Category %s successfully edited" %
                  categoryToEdit.categoryName)
        return redirect(url_for('showAllCategories'))
    return render_template('editCategory.html', category=categoryToEdit)


@app.route('/catalog/<string:categoryName>/delete/', methods=['GET', 'POST'])
# if a user not in login session, gets redirected to the login page.
@login_required
def deleteCategory(categoryName):
    categoryToDelete = session.query(Categories).filter_by(
        categoryName=categoryName).one()
    # only user who created the category should be able to delete the item.
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Not Authorized');}\
		</script><body onload = 'myFunction()'>"
    # if there are any items related to categoryName, query that as well.
    try:
        itemsInCategory = session.query(Items).filter_by(
            category_name=categoryName).one()
    # if there is no item, do nothing.
    except:
        None
    if request.method == 'POST':
        # if there is a item found, delete it otherwise do nothing.
        session.delete(categoryToDelete)
        try:
            session.delete(itemsInCategory)
        except:
            None
        session.commit()
        flash("Category %s successfully deleted" %
              categoryToDelete.categoryName)
        return redirect(url_for('showAllCategories'))
    return render_template('deleteCategory.html', category=categoryToDelete)


@app.route('/catalog/<string:categoryName>/items/')
def showItems(categoryName):
    category = session.query(Categories).filter_by(
        categoryName=categoryName).one()
    items = session.query(Items).filter_by(
        category_name=category.categoryName).all()
    # only logged in users should be able to edit and delete items. showitems_public
    # doesnt have options to edit and delete.
    if 'username' not in login_session:
        return render_template('showItems_public.html', category=category, items=items)
    else:
        return render_template('showItems.html', category=category, items=items)


@app.route('/catalog/<string:categoryName>/<string:itemName>/')
def showDescription(categoryName, itemName):
    item = session.query(Items).filter_by(
        itemName=itemName, category_name=categoryName).one()
    if 'username' not in login_session:
        return render_template('showDescription_public.html', item=item)
    else:
        return render_template('showDescription.html', item=item)


@app.route('/catalog/<string:categoryName>/add/', methods=['GET', 'POST'])
# if a user not in login session, gets redirected to the login page.
@login_required
def addItems(categoryName):
    category = session.query(Categories).filter_by(
        categoryName=categoryName).one()
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Not Authorized');}\
		</script><body onload = 'myFunction()'>"
    if request.method == 'POST':
        itemToAdd = Items(itemName=request.form['name'],
                          description=request.form['description'],
                          price=request.form['price'],
                          category_name=categoryName, user_id=login_session['user_id'])
        session.add(itemToAdd)
        session.commit()
        flash("Item %s successfully added in %s !" %
              (itemToAdd.itemName, category.categoryName))
        return redirect(url_for('showItems', categoryName=categoryName))
    else:
        return render_template('addItem.html', category=category)


@app.route('/catalog/<string:categoryName>/<string:itemName>/edit/', methods=['GET', 'POST'])
# if a user not in login session, gets redirected to the login page.
@login_required
def editItem(itemName, categoryName):
    itemToEdit = session.query(Items).filter_by(
        itemName=itemName, category_name=categoryName).one()
    if itemToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Not Authorized');}\
		</script><body onload = 'myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.itemName = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        if request.form['price']:
            itemToEdit.price = request.form['price']
        session.add(itemToEdit)
        session.commit()
        flash("Item %s successfully added!" % itemToEdit.itemName)
        return redirect(url_for('showItems', categoryName=categoryName))
    else:
        return render_template('editItem.html', item=itemToEdit)


@app.route('/catalog/<string:categoryName>/<string:itemName>/delete/', methods=['GET', 'POST'])
# if a user not in login session, gets redirected to the login page.
@login_required
def deleteItem(categoryName, itemName):
    itemToDelete = session.query(Items).filter_by(
        itemName=itemName, category_name=categoryName).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Not Authorized');}\
		</script><body onload = 'myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item %s successfully deleted" % itemToDelete.itemName)
        return redirect(url_for('showItems', categoryName=categoryName))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


"""<------------------  End of CRUD operations for Database and routes in the web app   ------------------>"""


"""<------------------  Start of creating a users   ------------------------------------------------------>"""

# takes the login_session and returns to user's id.


def CreateUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# takes the user_id and returns the user.


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# takes the user's email and returns the id.


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

"""<------------------  End of creating a users   ------------------------------------------------------->"""


"""<------------------  Start of creating JSON end points  ---------------------------------------------->"""


@app.route('/catalog.json/')
def catalogJSON():
    category = session.query(Categories).all()
    return jsonify(categories=[i.serialize for i in category])


@app.route('/<string:categoryName>/items.json/')
def itemsJSON(categoryName):
    items = session.query(Items).filter_by(category_name=categoryName).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/<string:itemName>/item.json/')
def itemJSON(itemName):
    item = session.query(Items).filter_by(itemName=itemName).one()
    return jsonify(item=[item.serialize])

"""<------------------  End of creating JSON end points  ----------------------------------------------->"""

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
