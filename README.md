# Plus One 🎫

A REST API for managing users, venues, events, and RSVPs. Users can view and manage events and RSVPs, with authentication and a PostgreSQL database backend.

The application can be deployed to AWS using Terraform. The cloud architecture separates the application layer from the database layer, with the FastAPI application running on an EC2 instance and PostgreSQL hosted on Amazon RDS.


## Project Overview

Plus One is a backend application developed using Python and FastAPI, with a PostgreSQL relational database. The API provides authenticated users with functionality to manage events and RSVPs, while organisers can manage events and view attendee and event statistics.

The project was developed to practise backend development, relational database design, SQL, authentication, testing and cloud deployment using infrastructure as code.

## Requirements

- Python 3.13+
- PostgreSQL 14+

## Local Setup

1. Clone the repo
2. Create and activate a venv in the root directory:
    
    `python -m venv .venv`
    
     `source .venv/bin/activate`
3. Install project requirements 

     `pip install -r requirements.txt`
4. Create a .env file and copy the contents of .env.example into it. Set the database URL to your local Postgres connection string. Generate a JWT secret key and copy it into .env as JWT_SECRET
5. Create the database 'nc_plus_one' by running the setup file

    `psql -f setup.sql`
6. Seed the database
    
    `python db/data/seed/seed.py`
7. Start the server
    
    `uvicorn main:app --reload`

The server is now running. Visit http://127.0.0.1:8000/docs for documentation.

## Cloud Deployment

To deploy the infrastructure:

1. Configure the AWS CLI with credentials for an AWS account.
2. Navigate to the Terraform directory:

    `cd terraform`

3. Initialise Terraform:

    `terraform init`

4. Review the infrastructure changes:

    `terraform plan`

5. Provision the AWS infrastructure:

    `terraform apply`

Terraform outputs the public IP address of the EC2 instance once deployment is complete.

The FastAPI application is then available through the EC2 instance, with the API documentation accessible at:

http://<EC2_PUBLIC_IP>:8000/docs