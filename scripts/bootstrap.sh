# scripts/bootstrap.sh
#!/bin/bash
# Strive-Code AI Bootstrap Script
# Executes on Render.com during container build

set -euo pipefail

echo "STRIVE-CODE AI — BOOTSTRAP INITIATED"

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Validate installation
echo "Verifying core packages..."
python -c "import fastapi, uvicorn, gitpython, weasyprint, gtts; print('All core deps installed')"

# Initialize any required directories
mkdir -p /tmp/strive-output
chmod 777 /tmp/strive-output

# Run database migrations (placeholder for future)
# python -m app.db.migrate

echo "BOOTSTRAP COMPLETE. STRIVE-CODE AI IS READY."
