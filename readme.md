# Virtual Hospital

### I. Local Set Up Instructions
#### 1. Database Set Up

First of all, set up a PostgreSQL server on you local machine.

Use the following link to download the correct version for your operating system: https://www.postgresql.org/download/

Or if you are familiar with Docker, you could also refer to this link: https://hub.docker.com/_/postgres

Do remember to note down the username, password and database name of your local PostgreSQL instance.
#### 2. Dependency Installation
In order for your code to access PostgreSQL, one of these commands should be run in your terminal:

For Mac:
```
brew install postgresql
```
For Linux (Ubuntu/Debian):
```
apt-get install libpq-dev
```
Then set up and activate a Python virtual environment:
```
cd /path_to_your_project_directory/Virtual-Hospital
python3 -m pip venv env
source ./env/bin/activate
```
Install Python dependencies:
```
python3 -m pip install -r requirements.txt
```
#### 3. Environment Variable Configurations
Create a file call `.env` in your project root directory. Refer to `.env.example` for what values are needed.

This file will not be tracked by Git version control.
#### 4. Start Application
If you haven't initialized the tables in the database, run:
```
flask dbinit
```
Or if you want to drop existing tables before creating new ones:
```
flask dbinit --drop
```
Then simply run:
```
flask run
```
Open a browser and see the application running at http://localhost:5000