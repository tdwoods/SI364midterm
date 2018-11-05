###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import requests
import json

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/SI364midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)

#api key for Google Maps REST api
api_key = "AIzaSyDUu64r2YrWWyIpCKkR2sovh0Jr5HU556M"
base_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"



######################################
######## HELPER FXNS (If any) ########
######################################

@app.errorhandler(404)
def route_not_found(error):
    return render_template('404_error.html')



##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class Chef(db.Model):
    __tablename__ = "chefs"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))

    def __repr__(self):
        return "{}".format(self.name, self.id)

class Restaurant(db.Model):
    __tablename__ = "restaurants"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    address = db.Column(db.String(128))
    rating = db.Column(db.Float)
    chefs = db.relationship("Chef",backref="restaurant",lazy="dynamic")

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)
###################
###### FORMS ######
###################

def validate_restaurant(form,field):
    name = field.data
    try:
        base_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
        params = {"key":api_key,"fields":'types',"input":name,"inputtype":"textquery"}
        resp = requests.get(base_place_url,params)
        data = json.loads(resp.text)
    except:
        raise ValidationError("Internet connection issues. Please make sure you have valid internet connection.")
    if data['status'] == 'OK':
        if "restaurant" not in data['candidates'][0]['types']:
            raise ValidationError("This place doesn't seem to be a restaurant. Make sure it is spelled right.")
    else:
        raise ValidationError("API Provided 0 Results for your search query. Please make sure it is spelled right and is a valid restaurant")

def validate_school(form,field):
    name = field.data
    try:
        base_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
        params = {"key":api_key,"fields":"formatted_address,name,types","input":name,"inputtype":"textquery"}
        data = requests.get(base_place_url,params)
        data = json.loads(data.text)
    except:
        raise ValidationError("Internet connection issues. Please make sure you have valid internet connection.")
    if data['status'] == 'OK':
        if "school" not in data['candidates'][0]['types'] and "university" not in data['candidates'][0]['types']:
            raise ValidationError("This place doesn't seem to be a school. Make sure it is spelled right.")
    else:
        raise ValidationError("API Provided 0 Results for your search query. Please make sure it is spelled right and is a valid school")


class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField()

class RestaurantForm(FlaskForm):
    chef = StringField("Please enter a chef: (ex: Trevor Woods)",validators=[Required()])
    restaurant = StringField("Please enter the restaurant and city he/she cooks at: (ex: NYPD, Ann Arbor)",validators=[Required(),validate_restaurant])
    submit = SubmitField()

class SchoolForm(FlaskForm):
    school = StringField("Please enter a school to look up: (ex: University of Michigan, Ann Arbor)",validators=[Required(),validate_school])
    submit = SubmitField()

#######################
###### VIEW FXNS ######
#######################

@app.route('/',methods=["GET","POST"])
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET

    ## base.html FORM USED POST SO I MODIFIED THIS VIEW FUNCTION TO USE POST ##
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name=name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)

@app.route('/restaurant_form',methods=["GET","POST"])
def restaurant_form():
    form = RestaurantForm()
    if form.validate_on_submit():

        chef = form.chef.data
        restaurant = form.restaurant.data
        #Call to API
        try:
            base_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
            params = {"key":api_key,"fields":"rating,formatted_address,name","input":restaurant,"inputtype":"textquery"}
            resp = requests.get(base_place_url,params)
            data = json.loads(resp.text)
            #Parse data from API
            restaurant_name = data['candidates'][0].get('name','NA')
            restaurant_address = data['candidates'][0].get('formatted_address','NA')
            restaurant_rating = data['candidates'][0].get('rating', 'NA')
        except:
            flash("Internet connection issues. Please make sure you have valid internet connection.")
            return redirect("/restaurant_form")
        #If valid call to API add to database
        new_restaurant = Restaurant(name=restaurant_name,address=restaurant_address,rating = restaurant_rating)
        #checking to see if restauratn in the database
        restaurant_query = Restaurant.query.filter_by(name=new_restaurant.name,address=new_restaurant.address).first()
        if not restaurant_query:
            db.session.add(new_restaurant)
            db.session.commit()
            flash("Restaurant successfully added to database")
        else:
            flash("Restaurant already exists in database")
            new_restaurant = restaurant_query

        new_chef = Chef(name=chef,restaurant_id=new_restaurant.id)
        #Checking to see if chef already in the database
        chef_query = Chef.query.filter_by(name=new_chef.name).first()
        if not chef_query:
            db.session.add(new_chef)
            db.session.commit()
            flash("Chef successfully added to database")
            return redirect("/restaurant_form")
        else:
            flash("Chef {} already exists in database.".format(new_chef.name))
            return redirect("/all_restaurants")

    #If form not validated, flash error messages and return back to form
    error_list = [error for error in form.errors.values()]
    if len(error_list) > 0:
        flash("Error in form submission!" + str(error_list))
    return render_template("restaurant_form.html",form = form)

@app.route('/all_restaurants')
def all_restaurants():
    restaurants = Restaurant.query.all()
    chefs = Chef.query.filter_by(restaurant_id=1).all()
    restaurants = {r:Chef.query.filter_by(restaurant_id=r.id).all() for r in restaurants}

    return render_template("all_restaurants.html",restaurants = restaurants)

@app.route("/school_form")
def school_form():
    form = SchoolForm()
    return render_template("school_form.html",form=form)

@app.route("/school_results",methods=["GET"])
def school_results():
    if request.method == 'GET':
        form = SchoolForm(request.args)
        if form.validate():
            try:
                name = request.args.get("school","")
                base_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
                params = {"key":api_key,"fields":"formatted_address,name","input":name,"inputtype":"textquery"}
                data = requests.get(base_place_url,params)
                data = json.loads(data.text)
                address = data["candidates"][0]["formatted_address"]
                name = data["candidates"][0]["name"]
            except:
                flash("Internet connection issues. Please make sure you have valid internet connection.")
                return redirect("/school_form")
            return render_template("school_results.html",name=name,address=address)
    error_list = [error for error in form.errors.values()]
    if len(error_list) > 0:
        flash("Error in form submission!" + str(error_list))
    return render_template("school_form.html",form = form)




## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True,debug=True)
