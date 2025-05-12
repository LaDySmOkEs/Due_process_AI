import os
import psycopg2

# Get database connection information from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

try:
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL)
    
    # Required for rolling back active transactions
    conn.autocommit = True
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Get list of active transactions
    cursor.execute("SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';")
    idle_transactions = cursor.fetchall()
    
    # Terminate idle transactions if any exist
    if idle_transactions:
        print(f"Found {len(idle_transactions)} idle transactions. Terminating...")
        for trans in idle_transactions:
            pid = trans[0]  # Process ID
            cursor.execute(f"SELECT pg_terminate_backend({pid});")
        print("All idle transactions terminated.")
    else:
        print("No idle transactions found.")
    
    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    print("Database connection reset successfully!")
    
except Exception as e:
    print(f"Error: {e}")