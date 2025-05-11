#!/bin/bash

set -e

# 1. Install npm dependencies
echo "Installing npm dependencies..."
npm install

# 2. Check for PostgreSQL (psql) and install/start if needed
echo "Checking for PostgreSQL (psql)..."
if ! command -v psql &> /dev/null
then
    echo "psql could not be found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install postgresql
        brew services start postgresql
    else
        echo "Homebrew not found. Please install Homebrew or PostgreSQL manually."
        exit 1
    fi
else
    echo "psql found."
fi

# Try to start PostgreSQL if not running (macOS Homebrew)
if command -v brew &> /dev/null; then
    if ! pg_isready &> /dev/null; then
        echo "Attempting to start PostgreSQL service via Homebrew..."
        brew services start postgresql
        sleep 3
    fi
fi

# 3. Always auto-detect PostgreSQL credentials and overwrite .env
ENV_FILE=".env"
POSTGRES_PASSWORD="mysecretpassword"
echo "Detecting working PostgreSQL credentials (ignoring any existing .env)..."
# Try current user and DB
PGUSER=$(whoami)
PGPASSWORD=""
PGDATABASE="$PGUSER"
PGHOST="localhost"
PGPORT="5432"
# Try to connect
if psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -c "\q" 2>/dev/null; then
    echo "Connected to PostgreSQL as user '$PGUSER' with database '$PGDATABASE'."
else
    # Try postgres superuser
    PGUSER="postgres"
    PGDATABASE="postgres"
    if psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -c "\q" 2>/dev/null; then
        echo "Connected to PostgreSQL as user 'postgres' with database 'postgres'."
    else
        echo "Could not connect to PostgreSQL with default credentials."
        echo "Please create a user and database or update the script with valid credentials."
        exit 1
    fi
fi

# Set postgres user password and update env
if [ "$PGUSER" = "postgres" ]; then
    echo "Setting password for user 'postgres'..."
    psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -c "ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';" || true
    PGPASSWORD="$POSTGRES_PASSWORD"
    echo "Password for user 'postgres' set to '$POSTGRES_PASSWORD'."
fi

cat > "$ENV_FILE" <<EOF
PGUSER=$PGUSER
PGPASSWORD=$PGPASSWORD
PGDATABASE=$PGDATABASE
PGHOST=$PGHOST
PGPORT=$PGPORT
EOF
echo ".env file created with detected credentials and password."

# Load the values for use in the rest of the script
export PGUSER PGPASSWORD PGDATABASE PGHOST PGPORT

# 4. Ensure user exists (attempt to create if not)
echo "Checking if PostgreSQL user $PGUSER exists..."
USER_EXISTS=$(PGPASSWORD="$PGPASSWORD" psql -U postgres -h "$PGHOST" -p "$PGPORT" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$PGUSER';" || echo "0")
if [ "$USER_EXISTS" != "1" ]; then
    echo "User $PGUSER does not exist. Creating..."
    PGPASSWORD="$PGPASSWORD" psql -U postgres -h "$PGHOST" -p "$PGPORT" -c "CREATE USER $PGUSER WITH PASSWORD '$PGPASSWORD' CREATEDB;" || true
else
    echo "User $PGUSER exists."
fi

# 5. Create DB if it doesn't exist
echo "Checking if database $PGDATABASE exists..."
DB_EXISTS=$(PGPASSWORD="$PGPASSWORD" psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -lqt | cut -d \| -f 1 | grep -w "$PGDATABASE" | wc -l)
if [ "$DB_EXISTS" -eq "0" ]; then
    echo "Database $PGDATABASE does not exist. Creating..."
    PGPASSWORD="$PGPASSWORD" createdb -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" "$PGDATABASE"
else
    echo "Database $PGDATABASE exists."
fi

# 6. Grant privileges (just in case)
echo "Granting all privileges on database $PGDATABASE to $PGUSER..."
PGPASSWORD="$PGPASSWORD" psql -U postgres -h "$PGHOST" -p "$PGPORT" -c "GRANT ALL PRIVILEGES ON DATABASE $PGDATABASE TO $PGUSER;" || true

# 7. Apply migrations
echo "Applying migrations from migrations/001_init.sql..."
MIGRATION_FILE="migrations/001_init.sql"
if [ -f "$MIGRATION_FILE" ]; then
    PGPASSWORD="$PGPASSWORD" psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -f "$MIGRATION_FILE"
    echo "Migration applied successfully."
else
    echo "Migration file $MIGRATION_FILE not found. Skipping DB migration."
fi

echo "\nSetup complete!"
echo "- To start your app: node src/app.js or use nodemon for auto-reload."
echo "- Database and tables are ready."
