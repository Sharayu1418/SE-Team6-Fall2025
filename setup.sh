#!/bin/bash
# SmartCache AI - Setup Script

echo "🚀 Setting up SmartCache AI..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
./venv/bin/pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Install requirements
echo -e "${BLUE}Installing dependencies...${NC}"
./venv/bin/pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Run migrations
echo -e "${BLUE}Setting up database...${NC}"
python manage.py migrate

# Seed default data
echo -e "${BLUE}Loading sample content sources...${NC}"
python manage.py seed_defaults

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create a superuser: ${BLUE}python manage.py createsuperuser${NC}"
echo "2. Run the server: ${BLUE}python manage.py runserver${NC}"
echo "3. Visit: ${BLUE}http://localhost:8000${NC}"
echo ""
echo -e "${YELLOW}Optional (for background tasks):${NC}"
echo "- Install Redis: ${BLUE}brew install redis && brew services start redis${NC}"
echo "- Run Celery worker: ${BLUE}celery -A smartcache worker --loglevel=info${NC}"
echo ""

