# Due Process AI Database Schema

This document contains the database schema for the Due Process AI application. Use this information when setting up a new instance of the application.

## Tables
The database contains the following tables:
- ad_campaign
- ad_click
- alembic_version
- case
- case_evidence
- document
- evidence
- legal_analysis
- legal_term
- subscription
- user

## Schema Details

### User Table
```sql
CREATE TABLE "user" (
  id INTEGER PRIMARY KEY NOT NULL,
  username VARCHAR(64) NOT NULL,
  email VARCHAR(120) NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  role VARCHAR(20) NOT NULL,
  created_at TIMESTAMP
);
```

### Case Table
```sql
CREATE TABLE "case" (
  id INTEGER PRIMARY KEY NOT NULL,
  user_id INTEGER NOT NULL,
  title VARCHAR(100) NOT NULL,
  court_type VARCHAR(50) NOT NULL,
  issue_type VARCHAR(50) NOT NULL,
  description TEXT NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  ai_analysis TEXT,
  legal_strategy TEXT,
  precedent_cases TEXT,
  success_probability DOUBLE PRECISION,
  FOREIGN KEY (user_id) REFERENCES "user" (id)
);
```

### Evidence Table
```sql
CREATE TABLE "evidence" (
  id INTEGER PRIMARY KEY NOT NULL,
  filename VARCHAR(255),
  original_filename VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  evidence_type VARCHAR(20),
  link_url VARCHAR(512),
  platform VARCHAR(50),
  uploaded_at TIMESTAMP,
  transcript TEXT,
  transcript_status VARCHAR(50),
  transcript_analysis TEXT,
  analysis_status VARCHAR(50),
  processed_at TIMESTAMP
);
```

### Case Evidence Table (Junction Table)
```sql
CREATE TABLE "case_evidence" (
  case_id INTEGER NOT NULL,
  evidence_id INTEGER NOT NULL,
  PRIMARY KEY (case_id, evidence_id),
  FOREIGN KEY (case_id) REFERENCES "case" (id),
  FOREIGN KEY (evidence_id) REFERENCES "evidence" (id)
);
```

### Legal Analysis Table
```sql
CREATE TABLE "legal_analysis" (
  id INTEGER PRIMARY KEY NOT NULL,
  case_id INTEGER NOT NULL,
  analysis_type VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  "references" TEXT,
  generated_at TIMESTAMP,
  confidence_score DOUBLE PRECISION,
  success_probability DOUBLE PRECISION,
  probability_factors TEXT,
  probability_suggestions TEXT,
  FOREIGN KEY (case_id) REFERENCES "case" (id)
);
```

### Subscription Table
```sql
CREATE TABLE "subscription" (
  id INTEGER PRIMARY KEY NOT NULL,
  user_id INTEGER NOT NULL,
  is_active BOOLEAN,
  subscription_type VARCHAR(20),
  price DOUBLE PRECISION,
  fee_waiver BOOLEAN,
  fee_waiver_reason TEXT,
  fee_waiver_approved BOOLEAN,
  fee_waiver_reviewed_by INTEGER,
  payment_method VARCHAR(50),
  external_subscription_id VARCHAR(100),
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  last_payment_date TIMESTAMP,
  next_payment_date TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "user" (id),
  FOREIGN KEY (fee_waiver_reviewed_by) REFERENCES "user" (id)
);
```

### Document Table
```sql
CREATE TABLE "document" (
  id INTEGER PRIMARY KEY NOT NULL,
  case_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  doc_type VARCHAR(100) NOT NULL,
  state VARCHAR(2) NOT NULL,
  court_type VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  created_at TIMESTAMP,
  FOREIGN KEY (case_id) REFERENCES "case" (id),
  FOREIGN KEY (user_id) REFERENCES "user" (id)
);
```

### Legal Term Table
```sql
CREATE TABLE "legal_term" (
  id INTEGER PRIMARY KEY NOT NULL,
  term VARCHAR(100) NOT NULL,
  simple_explanation TEXT NOT NULL,
  fun_explanation TEXT NOT NULL,
  cartoon_description TEXT NOT NULL,
  ai_generated BOOLEAN,
  verified BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  search_count INTEGER
);
```

### Ad Campaign Table
```sql
CREATE TABLE "ad_campaign" (
  id INTEGER PRIMARY KEY NOT NULL,
  campaign_id VARCHAR(50) NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  created_at TIMESTAMP
);
```

### Ad Click Table
```sql
CREATE TABLE "ad_click" (
  id INTEGER PRIMARY KEY NOT NULL,
  campaign_id VARCHAR(50) NOT NULL,
  source VARCHAR(50),
  medium VARCHAR(50),
  content VARCHAR(50),
  ip_address VARCHAR(50),
  user_agent TEXT,
  timestamp TIMESTAMP,
  converted BOOLEAN,
  conversion_type VARCHAR(50),
  conversion_timestamp TIMESTAMP
);
```

### Alembic Version Table
```sql
CREATE TABLE "alembic_version" (
  version_num VARCHAR(32) NOT NULL,
  CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
```

## Implementation Notes

1. This database schema is designed for a PostgreSQL database but should be compatible with other SQL databases.
2. All tables include proper foreign key constraints to ensure data integrity.
3. The system uses Flask-Migrate (Alembic) for managing database migrations. The `alembic_version` table tracks migrations.
4. Date fields use the PostgreSQL TIMESTAMP type without time zone.
5. Text fields of variable length use TEXT type instead of VARCHAR for flexibility.
6. The database supports 75MB file uploads for evidence with proper storage and retrieval mechanisms.

## Re-creating the Database

To re-create this database structure from scratch:

1. Create a PostgreSQL database instance
2. Run the above DDL statements in order, ensuring the parent tables are created before tables with foreign key references
3. If using Flask-Migrate, initialize migrations with `flask db init` and create a migration from the models with `flask db migrate`
4. Run `flask db upgrade` to apply the migration and build the tables