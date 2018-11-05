http://localhost:5000/ -> base.html

http://localhost:5000/names -> name_example.html

http://localhost:5000/restaurant_form -> restaurant_form.html

http://localhost:5000/all_restaurants -> all_restaurants.html

http://localhost:5000/school_form -> school_form.html

http://localhost:5000/school_results -> school_results.html

My app queries the Google Places API, I have forms set up to store chef names and data queried from the Google Places API on any valid restaurant in respective database tables. This code takes place within /restaurant_form route. I also have code to query my databases and return all the restaurants and chefs within my databases. This code takes place within /all_restaurants route.My app also queries the Google Places API from a form submission and shows data on any valid school or university. This code takes place within /school_form and /school_results routes.

Code for my extra credit takes place within /restaurant_form route, where I ensure that any given chef or restaurant is not currently in the databases.
