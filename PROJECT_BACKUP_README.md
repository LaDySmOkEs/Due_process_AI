# Due Process AI - Project Backup

## Project Overview
Due Process AI is a comprehensive legal assistance platform powered by AI, designed to simplify complex legal challenges through intelligent document analysis, strategic case management, and user-friendly legal tools.

## Key Features
- Case management system with evidence uploading (75MB file size limit)
- Document generation with auto-form filling
- AI-powered legal analysis (OpenAI with Anthropic fallback)
- Evidence suppression analysis using "fruit of the poisonous tree" doctrine
- Client interview questions to identify rights violations
- Court procedure scripts
- Legal jargon translator
- Premium subscription service via Stripe ($50/month)
- Fee waiver calculator for indigent users (100% poverty line)
- Ad campaign tracking system

## Directory Structure
- `/templates/` - HTML templates for the web interface
- `/static/` - CSS, JavaScript, and other static assets
- `/migrations/` - Database migration files
- `/uploads/` - Directory for uploaded evidence files

## Core Files
- `main.py` - Main application entry point
- `app.py` - Flask application configuration
- `models.py` - Database models
- `auth.py` - Authentication system
- `cases.py` - Case management
- `ai_helpers.py` - AI integration (OpenAI)
- `anthropic_helper.py` - Secondary AI integration (Anthropic)
- `ai_analysis.py` - AI analysis features
- `evidence_analysis.py` - Evidence processing
- `client_interview.py` - Client interview system
- `court_script.py` - Court procedure generation
- `stripe_integration.py` - Premium subscription handling
- `fee_waiver_calculator.py` - Fee waiver calculations

## Environment Variables Required
The following environment variables must be set when deploying this application:

### Database Configuration
- `DATABASE_URL` - PostgreSQL connection string
- `PGDATABASE` - PostgreSQL database name
- `PGHOST` - PostgreSQL host
- `PGUSER` - PostgreSQL username
- `PGPASSWORD` - PostgreSQL password
- `PGPORT` - PostgreSQL port

### API Keys
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `STRIPE_SECRET_KEY` - Stripe secret key

### Optional API Keys
- `TWILIO_ACCOUNT_SID` - Twilio account identifier (optional)
- `TWILIO_AUTH_TOKEN` - Twilio authentication token (optional)
- `TWILIO_PHONE_NUMBER` - Twilio phone number (optional)
- `SENDGRID_API_KEY` - SendGrid API key for email functionality (optional)

## Database Backup
To back up the database, use the following command:
```bash
pg_dump -U $PGUSER -h $PGHOST -p $PGPORT $PGDATABASE > due_process_ai_backup.sql
```

## Restoring the Project
1. Set up a new PostgreSQL database
2. Configure all environment variables
3. Install dependencies from pyproject.toml
4. Restore database from backup if available
5. Run migrations if needed

## Current Project Status
- All core features implemented
- Premium subscription system working with Stripe
- Document strategy generation system fixed
- Ad tracking system implemented
- Legal jargon database contains 81 comprehensive terms