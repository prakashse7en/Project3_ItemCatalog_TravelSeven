# project.py -- implementation of a Travel Seven website
#               contains methods to login,logout,insert,delete,view edit
#               places
from flask import Flask, render_template, request, \
     redirect, jsonify, url_for, flash


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Description, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


"""
get clienid from client_secrets.json for gmail login
"""
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Travel Seven"


# Connect to Database and create database session
engine = create_engine('sqlite:///travelseven.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    print"entered login from show login"
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
        connecting to the application via gmail.
        creates a user if it is not existed in Users database.
        user information like picture,name are accessed and stored
        in table
    """
    print "entered gconnect"
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
        print"inside gconect try"
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print"inside gconect exception"
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

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        print"inside gconect access token error try"
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        print"inside gconect invalid token error try"
        response.headers['Content-Type'] = 'application/json'
        return response

    """ Store the access token in the session for later use.
    #login_session['credentials'] = credentials"""
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    print"gconect building login details"

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    print"checking user exists from gconnect method"
    user_id = getUserID(login_session['email'])
    print user_id
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    """
        create a new user in USER table. users email id,name,image are stored
        in table
    """
    print"fb enetered create user"
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
        get the user details from USER email,image,name based on user id
    """
    print " user info entered"
    user = session.query(User).filter_by(id=user_id).one()

    return user


def getUserID(email):
    """
        get the user details from USER email,image,name based on email id
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
        gmail users are logged out. login_session variable is cleared when a
        valid 200 response is returned from gmail website
    """
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    print "inside gdisconnect"
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print login_session
    """access_token = credentials.access_token"""
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """connecting to the application via facebook.
        creates a user if it is not existed in Users database.
        user information like picture,name are accessed and stored
        in table.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    print(app_id)
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    print(app_secret)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    print "fb result data"
    print data
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    print "fb user id is"
    print user_id
    print login_session
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """
        fb users are logged out by sending the access token
        to the fb url
    """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


def getAppProvider():
    """
        identify the app provider either user is logged in
        via facebook or gmail
    """
    print " getting app provider entered"
    print login_session
    if 'gplus_id' in login_session:
        print "enetered google"
        print login_session['gplus_id']
        return "googleprovider"
    elif login_session['provider'] == 'facebook':
        print "enetered facebook"
        print login_session['facebook_id']
        return "fbprovider"
    else:
        print "enetered default"
        return "defaultProvider"

# index page
@app.route('/')
@app.route('/travleseven/')
def showIndex():
    """
        redirects to home page.if the user is logged in publicindex.html else
        index.html
    """
    city = session.query(City).order_by(asc(City.name))
    for i in city:
        print i.name
    print "after coming ut gconnect"
    print login_session
    if 'username' not in login_session:
        return render_template('publicindex.html', city=city)
    else:
        """check if the provider is facebook or gmail"""
        providerName = getAppProvider()

        if "fbprovider" in providerName:
            user_id=getUserID(login_session['email'])

        elif "googleprovider" in providerName:
            user_id=getUserID(login_session['email'])
        #user_id=login_session['user_id']
        print "else entered"
        print user_id
        creator = getUserInfo(user_id)
        print creator.name
        return render_template('index.html',
                               city=city,
                               creator = creator)

@app.route('/travleseven/<categoryName>')
def showAllCities(categoryName):
    """
        shows all the cities based on the category selected.if
        the user is logged in publictravelCity.html else
        travelCity.html
    """
    print "enetered"
    city= session.query(City).filter_by\
          (category=categoryName).order_by(asc(City.name))
    """ for users who r not logged starts"""

    print "entered show all cities"

    if 'username' not in login_session:
        return render_template('publictravelCity.html',
                               city=city,
                               categoryName = categoryName)
    else:
        """check if the provider is facebook or gmail"""
        providerName = getAppProvider()

        if "fbprovider" in providerName:
            user_id=getUserID(login_session['email'])

        elif "googleprovider" in providerName:
            user_id=getUserID(login_session['email'])
        #user_id=login_session['user_id']
        print "else entered"
        print user_id
        creator = getUserInfo(user_id)
        print creator.name
    """ for users who r not logged ends"""
    return render_template('travelCity.html',
                           city=city,
                           categoryName = categoryName,
                           creator = creator)

# JSON APIs to view travel seven category Information
@app.route('/travleseven/<categoryName>/JSON')
def showCategoryJSON(categoryName):
    """
        shows all the cities and in depth information of
        each city in JSON format
    """
    city= session.query(City).filter_by(category=categoryName).order_by(asc(City.name))
    cityDescripton = []
    for i in city:
       newcityDescripton =i.serialize
       items = session.query(Description).filter_by(city_id=i.id).all()
       serializedItems = []
       for j in items:
           serializedItems.append(j.serialize)
       newcityDescripton['items'] = serializedItems
       cityDescripton.append(newcityDescripton)
    return jsonify(categoryName=[cityDescripton])

@app.route('/travleseven/<int:city_id>/JSON')
def showCityJSON(city_id):
    """
        shows the selected city information in JSON format
    """
    city = session.query(City).filter_by(id=city_id).one()
    items = session.query(Description).filter_by(
        city_id=city_id).all()
    return jsonify(Description=[i.serialize for i in items])

@app.route('/travleseven/<int:city_id>')
def showCityDescription(city_id):
    """
        shows the selected city description.if
        the user is logged in publictravelcitydescription.html else
        travelcitydescription.html is shown
    """
    print "enetered city description"
    city= session.query(City).filter_by(id=city_id).one()

    #check city id and user is login
    items = session.query(Description).filter_by(
        city_id=city_id).all()

    #creator = getUserInfo(city.user_id)
    if 'username' not in login_session:
        return render_template('publictravelcitydescription.html',
                               items=items,
                               city=city)
    else:
        user_id=getUserID(login_session['email'])
        print "in else user_id and city id"
        print user_id
        print city_id
        """if user_id is not None and
            city.user_id is not None and
            user_id == city.user_id:"""
        creator = getUserInfo(user_id)
        return render_template('travelcitydescription.html',
                               items=items,
                               city=city,
                               creator=creator)

@app.route('/travleseven/<categoryName>/new/', methods=['GET', 'POST'])
def newCity(categoryName):
    """
        create a new city for a category selected
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        print "entered new city if post "
        newCity = City(
            name=request.form['name'],
            category=categoryName,
            user_id=login_session['user_id'])
        session.add(newCity)
        flash('New City %s Successfully Created' % newCity.name)

        newCityDescription = Description(user_id=login_session['user_id'],
                                         name=request.form['description'],
                                         bestseason=request.form['bestSeason'],
                                         place_pic=request.form['imageLink'],
                                         city=newCity)
        session.add(newCityDescription)
        print"success after creating new city"
        session.commit()
        return redirect(url_for('showAllCities',
                                categoryName=categoryName))
    else:
        print "entered new city else post "
        creator=getUserInfo(login_session['user_id'])
        print creator.name
        return render_template('newCity.html',
                               categoryName=categoryName,
                               creator=creator)

@app.route('/travleseven/<int:cityId>/edit', methods=['GET', 'POST'])
def editCity(cityId):
    """
        edit a selected city details
    """
    if 'username' not in login_session:
        return redirect('/login')
    editCity = session.query(City).filter_by(id=cityId).one()
    editCityDescription = session.query(Description).filter_by(id=cityId).one()
    if request.method == 'POST':
        if request.form['name']:
            editCity.name = request.form['name']
        if request.form['categoryName']:
            editCity.category = request.form['categoryName']
        if request.form['description']:
            editCityDescription.name = request.form['description']
        if request.form['bestSeason']:
            editCityDescription.bestseason = request.form['bestSeason']
            editCityDescription.place_pic = request.form['imageLink']
        session.add(editCity)
        session.add(editCityDescription)
        session.commit()
        flash('City and description updated succesfully')
        return redirect(url_for('showCityDescription', city_id=cityId))
    else:
        creator=getUserInfo(login_session['user_id'])
        return render_template('editcitydescription.html',
                               editCity=editCity,
                               editCityDescription=editCityDescription,
                               creator=creator)


# Delete a menu item
@app.route('/travleseven/<int:cityId>/delete', methods=['GET', 'POST'])
def deleteCity(cityId):
    """
        delete a selected city details
    """
    if 'username' not in login_session:
        return redirect('/login')
    deleteCity = session.query(City).filter_by(id=cityId).one()
    deleteDescription = session.query(Description).filter_by(id=cityId).one()
    categoryName = deleteCity.category
    if request.method == 'POST':
        print"entered post instead show city"
        session.delete(deleteDescription)
        session.delete(deleteCity)
        session.commit()
        flash('City and description deleted succesfully')
        return redirect(url_for('showAllCities', categoryName=categoryName))
    else:
        creator=getUserInfo(login_session['user_id'])

        return render_template('deletecitydescription.html',
                               deleteCity=deleteCity,
                               deleteDescription=deleteDescription,
                               creator=creator)

@app.route('/disconnect')
def disconnect():
    """
        logout from the application. checks from which app
        the user is logged in and then disconnects the user
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showIndex'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showIndex'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
