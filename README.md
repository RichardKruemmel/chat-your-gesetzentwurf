# Chat-Your-Gesetzentwurf

This project, Chat-Your-Gesetzentwurf, aims to provide an interactive platform to chat about Gesetzentwurf PDF documents and ask questions. It utilizes a PostgreSQL database for storing PDFs and their corresponding text embeddings, and a pgAdmin dashboard for database management.

## Prerequisites

Ensure you have Docker Desktop installed on your machine. [Docker Desktop](https://www.docker.com/products/docker-desktop)) is a comprehensive solution for running Docker on Windows and MacOS systems. It includes Docker Compose, which is required to orchestrate our multi-container application.

## Running Locally

### Clone the Project

Clone the project repository from GitHub:

```bash
git clone https://github.com/RichardKruemmel/chat-your-gesetzentwurf.git
```

### Set Environment Variables

A `.sample.env` file is included in the project repository as a template for your own `.env` file. Copy the `.sample.env` file and rename the copy to `.env`:

```bash
cp .sample.env .env
```

Edit the .env file to set your own environment variables, such as POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, PGADMIN_DEFAULT_EMAIL, and PGADMIN_DEFAULT_PASSWORD.

The .env file will be used by Docker Compose to set environment variables for your services.

### Start Service

To start all services, run:

```bash
docker-compose up
```

### Running the Backend Independently (Optional)

*Note*: Running the backend by itself won't establish a connection with the database. Make sure to run the database service separately or together with the backend for full functionality.

We are using [poetry]https://python-poetry.org/) for dependency management and [uvicorn](https://www.uvicorn.org/) for server implementation. Follow these commands:

One-time Setup

- Install Python 3.9 or higher
- Install [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

Every time you run the backend

```bash
  # Create a virtual environment
  $ poetry shell
  # Install all packages
  $ poetry install
  # Start API server on port 8000
  $ poetry run uvicorn app.main:app --reload
```

### Running the Frontend Service Independently (Optional)

Navigate to the frontend directory and install the dependencies:

```bash
cd frontend
npm install
```

```bash
npm run dev
```

### Access to pgAdmin Dashboard

Once the services are up and running, open your web browser and navigate to <http://localhost:5050>. Log in using the email and password you specified in the .env file.

### Connect to PostgreSQL Server

In the pgAdmin dashboard, you'll need to add a new server connection to connect to your PostgreSQL container. Use the following details:

- Host: postgres
- Port: 5432
- Username: As per your .env file
- Password: As per your .env file

You should now see the tables (documents and embeddings) that were created through the init.sql file.

### Stop the Service

To stop all services and remove the containers, you can run:

```bash
docker-compose down
```

### Database Schema

The PostgreSQL database consists of two main tables:

- documents: Stores the PDF document data.
- embeddings: Stores the text embeddings associated with each document.

### License

This project is under the GNU General Public License. See LICENSE for more details.

The frontend template is based on the Horizon ChatGPT AI Template, which is open-source under the MIT license. Credits to [Horizon UI](https://horizon-ui.com/pro) for their work.

### Future Development

This project is under development. Future releases will include backend and frontend services for a more interactive experience.
