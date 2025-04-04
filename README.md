# Facturación System

## Overview
The Facturación System is a FastAPI-based application designed to manage invoices, debit notes, credit notes, delivery orders, and retention receipts. It includes features for authentication, document generation, and audit logging.

## Features
- **Authentication**: OAuth2 integration with Authentik.
- **Document Management**: Create and manage invoices, debit notes, credit notes, delivery orders, and retention receipts.
- **PDF Generation**: Generate PDF documents using WeasyPrint.
- **Audit Logging**: Log all transactions for auditing purposes.
- **Frontend Integration**: Serve HTML templates for user interaction.

## Dependencies
The project requires the following Python packages:
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg2-binary`
- `python-dotenv`
- `weasyprint`
- `jinja2`
- `authlib`
- `PyJWT`
- `httpx`
- `itsdangerous`
- `watchgod`

## Environment Variables
The application uses the following environment variables:
- `SQLALCHEMY_DATABASE_URL`: Database connection URL.
- `AUTHENTIK_URL`: Base URL for Authentik.
- `AUTHENTIK_CLIENT_ID`: Client ID for Authentik.
- `AUTHENTIK_CLIENT_SECRET`: Client secret for Authentik.
- `AUTHENTIK_REDIRECT_URI`: Redirect URI for OAuth.
- `AUTHENTIK_JWKS_URL`: JWKS URL for Authentik.
- `SESSION_SECRET_KEY`: Secret key for session management.

## Running the Project Without Docker
To run the project without Docker, follow these steps:

1. **Install Python**
   Ensure you have Python 3.8 or later installed on your system.

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/MacOS
   venv\Scripts\activate   # On Windows
   ```

3. **Install Dependencies**
   Install the required Python packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the project root and add the required environment variables:
   ```env
   SQLALCHEMY_DATABASE_URL=your_database_url
   AUTHENTIK_URL=your_authentik_url
   AUTHENTIK_CLIENT_ID=your_client_id
   AUTHENTIK_CLIENT_SECRET=your_client_secret
   AUTHENTIK_REDIRECT_URI=your_redirect_uri
   AUTHENTIK_JWKS_URL=your_jwks_url
   SESSION_SECRET_KEY=your_secret_key
   ```

5. **Run Database Migrations**
   Ensure the database is set up and migrations are applied. You can use the `Base.metadata.create_all(bind=engine)` in the `main.py` file to initialize the database.

6. **Start the Application**
   Run the application using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the Application**
   Open your browser and navigate to `http://127.0.0.1:8000` to access the application.

## Running the Project with Docker
To run the project using Docker, follow these steps:

1. **Install Docker and Docker Compose**
   Ensure Docker and Docker Compose are installed on your system.

2. **Set Up Environment Variables**
   Create a `.env` file in the project root and add the required environment variables:
   ```env
   SQLALCHEMY_DATABASE_URL=postgresql://rdus:28325882@db:5432/facturacion
   AUTHENTIK_URL=your_authentik_url
   AUTHENTIK_CLIENT_ID=your_client_id
   AUTHENTIK_CLIENT_SECRET=your_client_secret
   AUTHENTIK_REDIRECT_URI=your_redirect_uri
   AUTHENTIK_JWKS_URL=your_jwks_url
   SESSION_SECRET_KEY=your_secret_key
   ```

3. **Build and Start Services**
   Run the following command to build and start the services:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**
   Open your browser and navigate to `http://127.0.0.1:8000`.

5. **Stop Services**
   To stop the services, use:
   ```bash
   docker-compose down
   ```

## Project Structure
- `core.py`: Initializes OAuth client and templates.
- `database.py`: Sets up the database connection and session management.
- `models.py`: Defines the database models.
- `schemas.py`: Defines Pydantic schemas for request validation and response serialization.
- `services.py`: Contains business logic for document management.
- `routers/`: Contains API route definitions.
- `loggers/`: Configures custom logging.
- `templates/`: HTML templates for the frontend.
- `static/`: Static files (CSS, JS).