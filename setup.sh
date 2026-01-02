#!/bin/bash

echo "=========================================="
echo "  599_cal - Quick Setup Script"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Get your key from: https://platform.openai.com/api-keys"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker is installed"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "   Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker Compose is installed"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo ""
echo "1) Start all services with Docker Compose"
echo "2) Test backend_chatbot locally (Python required)"
echo "3) View API documentation"
echo "4) Run demo script"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Starting all services..."
        echo "This may take a few minutes on first run..."
        echo ""
        read -p "Do you want to rebuild images? (y/N): " rebuild
        if [[ $rebuild =~ ^[Yy]$ ]]; then
            docker-compose up --build
        else
            docker-compose up
        fi
        ;;
    2)
        echo ""
        if ! command -v python3 &> /dev/null; then
            echo "❌ Python 3 is not installed"
            exit 1
        fi
        echo "Installing backend_chatbot dependencies..."
        cd backend_chatbot
        if pip install -r requirements.txt; then
            echo ""
            echo "✓ Dependencies installed successfully"
            echo ""
            echo "Running test script..."
            python3 test_services.py
            echo ""
            echo "Test complete! To start the server, run:"
            echo "  cd backend_chatbot && python3 main.py"
        else
            echo ""
            echo "❌ Failed to install dependencies"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "API Documentation will be available at:"
        echo ""
        echo "  Backend Chatbot (OpenAI GPT):"
        echo "    Swagger UI: http://localhost:8001/docs"
        echo "    ReDoc:      http://localhost:8001/redoc"
        echo ""
        echo "  Original Backend:"
        echo "    Swagger UI: http://localhost:8000/docs"
        echo "    ReDoc:      http://localhost:8000/redoc"
        echo ""
        echo "Start the services first with option 1"
        ;;
    4)
        echo ""
        if ! command -v python3 &> /dev/null; then
            echo "❌ Python 3 is not installed"
            exit 1
        fi
        echo "Make sure backend_chatbot is running on port 8001"
        echo "Then run:"
        echo "  cd backend_chatbot && python3 demo.py"
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
