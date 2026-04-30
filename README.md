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