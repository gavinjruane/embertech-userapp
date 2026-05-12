# embertech-userapp
User-facing application for Embertech Automation fabrication table

## Environment setup

### Development environment setup

1. Clone the repository to your local machine.
    
    `git clone git@github.com:gavinjruane/embertech-userapp.git`
2. Navigate to the newly-created repository directory.

    `cd embertech-userapp`
3. Create a Python virtual environment to manage the dependencies for the project.

    `python -m venv .venv`
4. Activate the virtual environment.

    On *macOS/Linux*: `. .venv/bin/activate`

    On *Windows*: `.venv\Scripts\activate`
5. Install the required dependencies to run the project.

    `pip freeze > requirements.txt`

### Running the development server

1. Activate the virtual environment.
2. Navigate to the "flaskr" directory.
3. Run the following command to start the Flask development server.

    `flask --app main run`
4. Navigate to http://127.0.0.1:5000 in your web browser.

### Creating an .env file

Our .env (environment) file will store sensitive variables like our secret key and any API keys.
Because this file contains sensitive data, we cannot check it into git, so you will probably get some kind of
`FileNotFoundException` if you don't create your own first.
Thankfully, it is very simple to create, and there is a file called ".env.example" on which you can model it!

1. In the "flaskr" directory, create a file called ".env".

   `touch .env`
2. Generate a secret key.

   `python -c 'import secrets; print(secrets.token_hex())'`
3. Take note of the path to the database. (For me (Gavin), it's `/home/gavinruane/.../flaskr/database.sqlite3`)
4. In the ".env" file, write the following key-value pairs.

   ```dotenv
   SECRET_KEY='<your secret key>'
   DATABASE_PATH='<your database path>'
   ```

## Project structure

The repository is organized like a 
[typical Flask application](https://flask.palletsprojects.com/en/stable/tutorial/layout/) currently.

| File/Directory   | Meaning                                                                          |
|------------------|----------------------------------------------------------------------------------|
| flaskr           | This is the root of the project. All project files should be stored in here.     |
| static           | This is where all *static* files like CSS stylesheets or fonts should be stored. |
| templates        | This is where all Jinja templates should be stored.                              |
| main.py          | Root of the Flask app                                                            |
| \_\_init\_\_.py  | File to make pip and the Python interpreter happy                                |
| pyproject.toml   | Configuration file for project                                                   |
| requirements.txt | File with information about modules required for the project                     |

## Database

I think it makes the most sense to use `sqlite` for this project, especially since our database is going to be very simple.

### Creating a database

I believe `sqlite3` should be installed on the Raspberry Pi already since it comes with many Linux distributions; however, it is easily installable if not.

1. Navigate to the directory containing the SQL files.
2. Create the database using the schema file.

   `sqlite3 new-database.db < schema.sql`
3. (Optional) Load the sample data into the database.

    `sqlite3 new-database.db < sample-data.sql`

I also made a file called `useful-queries.sql` that might be helpful when we write our queries in Python.
