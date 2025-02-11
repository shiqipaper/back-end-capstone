## PlantFinder Backend 🌱
A full-stack plant discovery platform with user authentication, plant management, and social features like commenting and saving plants to a personal list. This repository contains the backend service, built with Flask, SQLAlchemy, and Flask-JWT-Extended, providing RESTful endpoints for the frontend.

## Tech Stack 🛠️
- Python (v3.12+)
- Flask (Framework)
- Flask SQLAlchemy (ORM)
- Flask Migrate (Database migrations)
- Flask-JWT-Extended (Authentication / JWT)
- Bcrypt (Password hashing)
- boto3 (AWS S3 Cloud Storage interaction)
- PostgreSQL (SQLAlchemy-supported database)

## Setup Instructions ⚙️
1. Clone the repository. <br />
   git clone https://github.com/<your-username>/<repo-name>.git <br />
   cd <repo-name>
2. Create and activate a virtual environment <br />
   python3 -m venv venv <br />
   source venv/bin/activate
3. Install Python dependencies <br />
   pip install -r requirements.txt
4. Environment Setup <br />
   Create `.env` file in root directory:  
   SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://<username>:<password>@<hostname>:<port>/<dbname> <br />
   AWS_ACCESS_KEY_ID=&lt;your AWS access key ID&gt; <br />
   AWS_SECRET_ACCESS_KEY=&lt;your AWS secret access key&gt; <br />
   S3_BUCKET_NAME=&lt;your AWS S3 bucket name&gt; <br />
   AWS_DEFAULT_REGION=&lt;your AWS S3 region&gt; <br />
   For local development, replace URLs with your local database address
5. Database Setup <br />
   Run the following commands to create the database and apply migrations: <br />
   `flask db init` <br />
   `flask db migrate` <br />
   `flask db upgrade`
6. Run the application <br />
   `flask run`
