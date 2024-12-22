# Robotics Final Project

This project is a robotics control system built using Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-SocketIO, and Alembic. The system manages navigation and restocking tasks for a robot in a warehouse environment.

The code for navigation is located in another repository: [robotics_project](https://github.com/QuantumSpawner/robotics_project).

## Project Structure
```
.
├── api.py
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       ├── 1fe733dfb696_rename_to_restock_and_modify_navigation_.py
│       ├── 8580834e811c_rename_product_type_to_user_name.py
│       └── d83274593e7e_remove_pickup_location.py
├── navigation.py
├── README.md
├── requirements.txt
├── server.py
├── shared.py
├── static/
│   ├── css/
│   │   └── task_completion.css
│   └── js/
│       └── functions.js
├── templates/
│   ├── base.html
│   ├── components.html
│   ├── enter_password.html
│   ├── home.html
│   ├── navigation.html
│   └── restock.html
└── ui.py
```
## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Database Migrations

1. Initialize the migration environment:
    ```sh
    flask db init
    ```

2. Create a new migration:
    ```sh
    flask db migrate -m "Initial migration."
    ```

3. Apply the migration:
    ```sh
    flask db upgrade
    ```

## Running the Application

1. Start the UI server:
    ```sh
    python ui.py
    ```

2. Start the navigation server:
    ```sh
    python navigation.py
    ```

3. Start the main server:
    ```sh
    python server.py
    ```

## Project Components

- **api.py**: Contains shared functions and data structures used across the project.
- **ui.py**: Implements the Flask application for the user interface, handling routes for navigation and restocking tasks.
- **server.py**: Manages the server-side logic for handling tasks and communicating with the navigation service.
- **navigation.py**: Handles the robot's navigation logic.
- **shared.py**: Contains shared utilities and data structures.
- **migrations/**: Contains database migration scripts managed by Alembic.
- **static/**: Contains static files such as CSS and JavaScript.
- **templates/**: Contains HTML templates for rendering the web pages.