# Due Process AI Installation Guide

This guide provides step-by-step instructions for setting up the Due Process AI application on a new system.

## Prerequisites

Before beginning the installation, ensure you have:

1. Python 3.11 or newer
2. PostgreSQL 15 or newer
3. Required API keys (OpenAI, Anthropic, Stripe)
4. 1GB+ of available storage (for application files, evidence uploads, and database)

## Step 1: Clone or Download Application

Either clone from your repository or download and extract the application files to your preferred location.

## Step 2: Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
# Install required packages
pip install -r project_requirements.txt
```

## Step 4: Configure PostgreSQL Database

```bash
# Create a PostgreSQL database
createdb due_process_ai

# If restoring from a backup:
psql -d due_process_ai -f due_process_ai_backup.sql
```

## Step 5: Set Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/due_process_ai
PGDATABASE=due_process_ai
PGHOST=localhost
PGUSER=your_username
PGPASSWORD=your_password
PGPORT=5432

# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Optional API Keys
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token  
TWILIO_PHONE_NUMBER=your_twilio_phone_number
SENDGRID_API_KEY=your_sendgrid_api_key
```

## Step 6: Set Up Database

Initialize the database schema:

```bash
# Set up database migrations 
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## Step 7: Create Upload Directories

Ensure upload directories exist with proper permissions:

```bash
mkdir -p uploads
chmod 755 uploads
```

## Step 8: Create Admin User

Run the admin user creation script:

```bash
python create_admin.py your_admin_email your_username your_password
```

## Step 9: Populate Legal Terms Database

Populate the legal terms database:

```bash
python populate_legal_terms.py
```

## Step 10: Run the Application

For development:

```bash
flask run
```

For production:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

## Step 11: Verify Installation

Visit http://localhost:5000 in your web browser. You should see the Due Process AI login page.

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check PostgreSQL is running: `pg_isready`
2. Verify connection details in your `.env` file
3. Ensure the database exists: `psql -l`
4. Run `python reset_db_connection.py` to test and reset the database connection

### Missing Files or Folders

If you see errors about missing files or folders:

1. Ensure all directory paths exist
2. Check permissions on the directories
3. Verify `uploads` directory is writeable

### API Integration Issues

If AI analysis features aren't working:

1. Verify API keys are correctly set in environment variables
2. Check for API rate limit issues
3. Ensure internet connectivity for external API calls

## Backup and Maintenance

### Regular Backups

Schedule regular database backups:

```bash
pg_dump -U $PGUSER -h $PGHOST -p $PGPORT $PGDATABASE > due_process_ai_backup_$(date +%Y%m%d).sql
```

### Evidence Storage

Evidence files are stored in the `uploads` directory. Ensure regular backups of this directory as well:

```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```