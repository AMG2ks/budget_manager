#!/bin/bash
"""
Installation script for Smart Budget Manager
"""

set -e  # Exit on any error

echo "🚀 Installing Smart Budget Manager..."
echo "================================="

# Check if Python 3.8+ is available
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.8+ required. Found: $(python3 --version 2>&1 || echo 'Python not found')"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python version OK: $(python3 --version)"

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "📦 Installing budget manager..."
pip install -e .

# Initialize the application
echo "🔧 Initializing budget manager..."
python -m budget_manager init

# Run tests to ensure everything works
echo "🧪 Running tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v
    echo "✅ All tests passed!"
else
    echo "⚠️ pytest not found, skipping tests"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your monthly salary:"
echo "   budget-manager salary set 5000"
echo ""
echo "3. Set your savings goal:"
echo "   budget-manager goal set 1000"
echo ""
echo "4. Add your first expense:"
echo "   budget-manager expense add 25.50 'Lunch' --category food"
echo ""
echo "5. Get your daily recommendation:"
echo "   budget-manager recommend"
echo ""
echo "6. Check your budget status:"
echo "   budget-manager status"
echo ""
echo "7. Launch the web interface:"
echo "   streamlit run app.py"
echo ""
echo "8. Run the demo to see all features:"
echo "   python demo.py"
echo ""
echo "📚 For more commands, run:"
echo "   budget-manager --help"
echo ""
echo "🌐 Web Interface: streamlit run app.py"
echo "💻 CLI Interface: budget-manager --help"
echo ""
echo "Happy budgeting! 💰" 