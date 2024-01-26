# Edulution Technical Support
- Requires Python 3.6

## Local Development Set up

### 1. Set up the project
- Clone the repository

- Create a virtual environment (highly recommended) either using venv or virtualenvwrapper:
- To **create** virtual environment using venv:
    ```Shell
    $ python3 -m venv env_name # using Python's venv
    # or
    $ virtualenv env_name # using virtualenv
    ``` 
- To **activate** virtual environment (Linux/Mac OS):
    ```Shell
    $ source env_name/bin/activate
    ``` 

- Install all dependencies:
    ```Shell
    $ pip3 install -r requirements.txt
    ``` 

### 2. Set up environment variables
- Inside the techsupport_management directory, create a file called **.env**. Inside the file, insert the following environment variables.
```
TSUPPORT_SECRET_KEY=<your-value>
TSUPPORT_DATABASE_NAME=<your-value>
TSUPPORT_DATABASE_USER=<your-value>
TSUPPORT_DATABASE_PASSWORD=<your-value>
TSUPPORT_DATABASE_HOST=<your-value>
TSUPPORT_DATABASE_PORT=<your-value>
TSUPPORT_SITE_ID=<your-value>
DEBUG=<your-value>
EMAIL_BACKEND=<your-value>
EMAIL_HOST=<your-value>
EMAIL_PORT=<your-value>
EMAIL_USE_TLS=<your-value>
EMAIL_HOST_USER=<your-value>
EMAIL_HOST_PASSWORD=<your-value>
GOOGLE_CLIENT_ID=<your-value>
GOOGLE_CLIENT_SECRET=<your-value>
```


### 3. Run migrations and start the server
Inside the root directory of the project, run database migrartions and start the server:
```Shell
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
``` 

If everything works well, we should see an instance of this application running on this address — http://localhost:8000
