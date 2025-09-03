# Facturación System

## Overview
The Facturación System is a FastAPI-based application designed to manage invoices, debit notes, credit notes, delivery orders, and retention receipts. It includes features for authentication, document generation, and audit logging.

## Features
- **Authentication**: OAuth2 integration with Authentik.
- **Document Management**: Create and manage invoices, debit notes, credit notes, delivery orders, and retention receipts.
- **PDF Generation**: Generate PDF documents using WeasyPrint.
- **Audit Logging**: Log all transactions for auditing purposes, now with enhanced serialization support.
- **Frontend Integration**: Serve HTML templates for user interaction.
- **Middleware for Group Validation**: Protect routes based on user groups, with fallback for unprotected routes.
- **Advanced Logging**: Custom logger with rotating file handlers and detailed request information.

## Recent Updates
- **Version 0.6.2**:
  - Added `limit` and `offset` parameters to multiple service functions for pagination support.
  - Updated routers to include query parameters for pagination in endpoints.
  - Standardized function names for clarity (e.g., `get_documentos_by_empresa_id` renamed to `get_facturas_by_empresa_id`).
  - Enhanced consistency across services and routers for better maintainability.

- **Version 0.6.1**:
  - Adjusted `subtotal_productos` to exclude discounts, aligning with the imprenta's expectations.
  - Updated JSON generation logic to include taxes in the `subtotal` field.
  - Improved validation for subtotal consistency in `calcular_totales_nota`.
  - Enhanced error handling for imprenta API responses.
  - Integrated SMART API for invoices, credit notes, and debit notes.
  - Adjusted parsing logic for better compatibility with SMART API.
  - Refined exception handling for API and database operations.

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
- `starlette`
- `requests`
- `apscheduler`
- `python-jose`

## Environment Variables
The application uses the following environment variables:
- `SQLALCHEMY_DATABASE_URL`: Database connection URL (e.g., `postgresql://user:password@db:5432/database_name`).
- `AUTHENTIK_URL`: Base URL for Authentik.
- `AUTHENTIK_CLIENT_ID`: Client ID for Authentik.
- `AUTHENTIK_CLIENT_SECRET`: Client secret for Authentik.
- `AUTHENTIK_REDIRECT_URI`: Redirect URI for OAuth.
- `AUTHENTIK_JWKS_URL`: JWKS URL for Authentik.
- `SESSION_SECRET_KEY`: Secret key for session management.
- `AUTHENTIK_LOGOUT_URL`: Logout URL for Authentik.
- `SEND_EMAIL_SMART`: Flag to send email via SMART.
- `POST_SMART`: Flag to enable SMART POST requests.
- `SMART_URL`: Base URL for SMART API.
- `SMART_API_TOKEN`: Token for SMART API authentication.
- `RESET_DB`: Flag to reset the database.

**Example:**
```env
SQLALCHEMY_DATABASE_URL=postgresql://user:password@db:5432/database_name
AUTHENTIK_URL=https://auth.example.com
AUTHENTIK_CLIENT_ID=example_client_id
AUTHENTIK_CLIENT_SECRET=example_client_secret
AUTHENTIK_REDIRECT_URI=http://localhost:8000/oauth/callback
AUTHENTIK_JWKS_URL=https://auth.example.com/application/jwks/
AUTHENTIK_LOGOUT_URL=https://auth.example.com/application/end-session/
SESSION_SECRET_KEY=example_secret_key
SEND_EMAIL_SMART=false
POST_SMART=true
SMART_URL=https://api.example.com/
SMART_API_TOKEN=example_token
RESET_DB=false
```

## Logger Configuration
- Logs are stored in the `logs/` directory.
- Log files rotate automatically when they reach 10 MB, keeping up to 5 backups.
- Each log entry includes detailed information such as user, IP, and device.

## Project Structure
- `core.py`: Initializes OAuth client and templates.
- `database.py`: Sets up the database connection and session management.
- `models.py`: Defines the database models.
- `schemas.py`: Defines Pydantic schemas for request validation and response serialization.
- `services.py`: Contains business logic for document management.
- `routers/`: Contains API route definitions.
- `loggers/`: Configures custom logging and routes for log management.
- `auth/`: Handles authentication and group-based route protection.
- `templates/`: HTML templates for the frontend.
- `static/`: Static files (CSS, JS).

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