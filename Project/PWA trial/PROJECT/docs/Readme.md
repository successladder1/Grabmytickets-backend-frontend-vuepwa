# GrabMyTickets Application
GrabMyTickets is a web-based application built on Python Flask and SQLite database. It allows users to search and book tickets for various events such as movies, concerts, and sports events.

## Installation
Follow the below steps to install and run the application:

### Prerequisites
* Python 3.8 or higher version installed on your system.
* pip package installer.

### Backend Installation and set up:
### Install the following dependencies:
* Install the dependencies listed in requirements.txt file in the backend folder.

### Configure the Application
The application can be configured using the config.json file. Edit the file and set the desired configuration parameters for admin username and password of your choice so that you can login as admin using those credentials.
Configure the redis server ports to be used as backend, message broker and cache in the application.

### Initialize the Database
The database can be initialized using the following command:  

```
python database.py 
```

### Start the Application
Go inside the Backend directory.
Start the application using the following command:
```
python restapp.py
```
The below commands require a linux environment and thus install wsl if on windows.
Start redis server. (use wsl on windows).

```
redis-server
```
Start the celery workers.
```
celery -A restapp.celery worker -l info
```
Start celery beat on a different terminal.
```
celery -A restapp.celery beat --max-interval 1 -l info
```
Start mailhog server in a new terminal.
```
mailhog
```


## Access the Backend Application
Open your web browser and go to http://localhost:5000 to access the application.

### Frontend Installation
```
npm install vue/cli
vue init pwa vuepwa
cd 'vuepwa'
npm install
npm run dev
```
## Access the Frontend Application
Open your web browser and go to http://localhost:8080 to access the application.
## Directory Structure
Inside the project root directory:  

BACKEND: 
* restapp.py - The main application to run.
* config.json - To configure admin parameters.
* ticketshow.db - SQLite database.
* templates - containing all the HTML files.
* static - containing a css folder that contains css file - signin.css.
* application - folder that contains the following Python files.
  * controllers
    * controllers.py - containing all the Flask route controllers.
    * apis.py - contains flask restful apis returning json.
    * webhooks.py- contains webhook for testing purpose.
  * data
    * cached_functions.py - containing the functions which have been cached for faster performance.
    * ccache.py - contains initialisation of flask cache.
    * models.py - containing all the models of the database.
    * database.py - to establish the connection with the SQLite database.
  * jobs
    * tasks.py - contains celery tasks.
    * workers.py - initialisation of celery workers to execute tasks.
  * utils
    * validation.py - containing the user-defined exceptions for APIs.  

docs - folder that contains the following file.
* Openapi.yaml - the OpenAPI developed using Swagger.
* Report.pdf - Project report as a PDF.
* Readme.md - Markdown file describing the installation of the application.

FRONTEND\vuepwa:
* build -  contains files to build the vue cli environment.
* config - contains vue cli configuration files
* node_modules - heavy folder containing node packages.
* src 
  * assets
    * logo.png - default vue logo.
  * components - Multiple vue components wrapping html, css and js in a one file.
  * router
    * index.js - containing vue routes in the application.
  * App.vue - root component of the pwa.
  * main.js - initialisation of the main vue instance contaning all the components.
* static
  * image\icons:  default icons for installing the app.
  * manifest.json - used for installing the app locally.
* babelrc - compiler for conversions among js versions.
* .gitignore
* .postcssrc.js
* index.html - containing imports for frontend development.
* package.json - containing node package dependencies.
* package-lock.json - containing node package dependencies.
* README.md - for installing the npm environment.



## Conclusion
Follow the above steps to install and run the GrabMyTickets application. 