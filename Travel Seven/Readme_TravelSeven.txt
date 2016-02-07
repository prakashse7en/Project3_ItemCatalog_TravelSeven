                        P3:Item Catalog  - Travel Seven
				   -------------

1)What is it?

Travel Seven - informations on various travel destinations categorized into 7 groups
	i)HoneyMoon
	ii)Adventure
	iii)Family
	iv)Rail Tours
	v)Desert Tours
	vi)Devotional
	vii)Trekking and Camping
Each place under a category provides information such as image of a the place,what it is famous for,
best season and current weather.
Person who is logged in will have addinal advantage of add/edit/delete city into a category.
-------------------------------------------------------------------------------------------------------------

2)Files/Folders Included:

SNO  Name                    Type              Description
-----------------------  (Folder/File)-------------------
			            |--------------|
1    static                 (Folder)      contains javascript files,css,images,fonts etc required for the website
2    templates              (Folder)      contains html files required for the website
3    database_setup.py       (File)        used to set up database user,city,description
4    fb_client_secrets.json  (File)       contains application id and secret whic helps to connect to application via facebook
5    client_secrets.json     (File)       contains application id and secret whic helps to connect application via gmail
6    lotsofcities.py         (File)       used to populate datas to database travelseven.db
7    project.py              (File)       used to test our application locally.contains methods to connect users via gmail/fb to our application
                                          contains methods to add/view/edit/delete places

-------------------------------------------------------------------------------------------------------------

3)Database Table Structure

Database Name - travelseven.db

SNO	 Table			Columns                  Primary Key	    Foreign key		    Description
---|------------|----------------------------|---------------|-------------------|------------------------------
1    user    	 id,name,email,picture          id                   -              used to save user details
2    city   	 id,name,category,user_id       id                user_id(USER)     used to save place name and category added by a user
3    description id,name,bestseason,place_pic,  id                user_id(USER),    used to save description of a place added by a user
                 city_id,user_id                                  city_id(CITY)

-------------------------------------------------------------------------------------------------------------

Installation
------------

Install Git, VirtualBox and Vagrant.
For download links and in depth details for installation please visit - 
https://www.udacity.com/wiki/ud197/install-vagrant
Git -Unix-style terminal and shell (Git Bash) to acces the folders present in remote system.
VirtualBox -used to run VM.
Vagrant -configures the VM and lets you share files between your host computer and the VM's 
filesystem.
Launch the Vagrant VM (vagrant up)
Intially run database_setup.py to set up database.
Run lotsofcities.py to populate datas into database
Run your application (vagrant\Travel Seven\project.py)
Access and test your application by visiting http://localhost:5000 locally

Working 
------------
1)connect to remote desktop via git bash using vagrant up,vagrant ssh commands from
  the fullstack/vagrant folder
2)Vagrant up is used to create a connection with the host followed by vagrant ssh 
  which connects to the remote desktop
3)Run database_setup.py in vm to setup database
4)Run lotsofcities.py in to populate datas into database
    steps to connect sqlite via command line
    ----------------------------------------
   i) check if sqlite is installed in your vm. Try this command to identify "get -bash: sqlite: " , if it returns "command not found"
      install it using "sudo apt-get install sqlite3".
   ii) Connect to sqlite using "sqlite3" from vm
   iii) use .open "databasename.db" , here databasename refers to your database
   iv) for further help type ".help" in vm
5) create app id , app secret for allowing users to sign in to our app via Fb/Gmail using OAuth authorization
	Facebook:
	---------
		i)Go to your app on the Facebook Developers Page(https://developers.facebook.com/)
		ii)click "MyApps" at the top navigation menu and click "Add a New App".
		iii)Select website from the modal dialog displayed
		iv) specify name for the app and click "create new facebook id"
		v)click skip quick start at the top right after specifying url of the web site 
		  in our case it is http://localhost:5000 .
		vi)get the App id and App secret
		vii) select "setting" from left hand navigation and select "Advanced" tab.
		viii)specify the redirect uri in "Valid OAuth redirect URIs" field as  http://localhost:5000 .
		ix) Atlast save your changes.
		x) paste the app id and app secret in a json file.for further help refer "fb_client_secrets.json" file
		  
	Gmail:
	-------
	    i)Login to Google Developer Console(https://console.developers.google.com/home/dashboard?project=travel-seven-app&pli=1)
		ii)Select create project from top navigaton menu,project id will be auto created.
		iii) Select credentials from LHN.Configure Proejct Consent screen before advancing to next steps.
		iv)Select "web application" as Application type.
		v) In "Authorized redirect URIs" specify http://localhost:5000 as redirect uri's.
		vi)Click create button.
		vii) Modal dialog is opended,it provides the client id and client secret.save it in a json file.
		viii) for further help refer "client_secrets.json " file
6) Now run project.py from vm and run http://localhost:5000 via browser.Enjoy working Travel seven Application
-------------------------------------------------------------------------------------------------------------
Templates -

index\publicindex .html:-
Links :-
Login - used to loginto the application. Currently Gmail/Facebook third party applications are used.
Logout - used to logout from the application.
Destinations - various categories of travelling destinations
About us\Contact us - provides information on what we offer.

travelcity\publictravelcity .html:-
Link :-
column Places displays links to each place description and weather information in detail.
getJSONCity - provide json information all the cities and their description in json format.
Add/Edit/Delete city - will be displayed only if the user is logged in

newcity.html
Link :-
Provide name,description ,best season and image link(optional)

main.html
contains the common html code which is inherited in the rest of the templates to avoid
repetition of code.
editcitydescription/deletecitydescription .html
Link :-
either edit or delete the place

citydescription/publiccitydescription .html
Link :-
edit/delete city - either edit or delete the place
description ,best season ,image and weather information are shown
get JSON CITY description -provide json information of city and their description in json format.

for detailed documenation of each method check the comments in pyhton files. 

-------------------------------------------------------------------------------------------------------------
External API's used

Simple weather API is used to extract weather information from Yahoo weather based on the place provided.
Current temprature is shown in farenheit ,atmospheric phenomenan and wind speed are shown
checkout for Readme_weather.md for in depth details of the API  used.
Files used - weather.css(path - static\css\weather.css),jquery.simpleWeather.js(path - static\js\jquery.simpleWeather.js)


Contacts
--------

o please send your queries regarding this project to prakash.dec20@gmail.com 
