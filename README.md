# Smart Budget Manager

A smart and flexible budget management application that helps you manage your salary, track daily expenses, and achieve monthly savings goals through intelligent daily spending recommendations.

🌐 **Now with a beautiful web interface!** Use either the command-line interface or the modern web UI for the best experience.

## Features

- **Salary Management**: Track your monthly income and set savings targets
- **Daily Expense Tracking**: Record and categorize daily expenses
- **Smart Recommendations**: Get intelligent daily spending limits to meet your savings goals
- **Monthly Planning**: Automatic budget planning with target achievement by the 3rd of each month
- **Analytics**: Visual reports and spending insights
- **Flexible Categories**: Customizable expense categories
- **Goal Tracking**: Monitor progress towards savings targets
- **Multi-Currency Support**: Choose from 21 supported currencies including USD, EUR, GBP, TND, and more
- **Customizable Formatting**: Adjust decimal places and thousands separators

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd budget_manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. **Quick Start with Web Interface:**
```bash
streamlit run app.py
```

5. **Or use the automated installer:**
```bash
chmod +x install.sh
./install.sh
```

## 🗄️ Persistent Storage for Cloud Deployment

**Important**: For Streamlit Cloud deployment, set up persistent storage to prevent data loss on redeployments.

### 🆓 Option 1: GitHub Storage (100% Free Forever)
**Best choice - Uses your existing GitHub account!**

1. **Create GitHub Token**: GitHub.com → Settings → Developer settings → Personal access tokens → Generate new token (classic)
2. **Select Scope**: Check `repo` (Full control of private repositories)  
3. **Add to Streamlit Cloud**: Settings → Advanced → Environment variables:
   - `GITHUB_TOKEN` = your_token_here
   - `GITHUB_USERNAME` = your_github_username
   - `USE_GITHUB_STORAGE` = true
4. **Redeploy**: Auto-creates private repository for data storage!

### 📊 Option 2: PostgreSQL Database (Free Tiers Available)

📖 **[Complete Setup Guide: PERSISTENT_STORAGE_GUIDE.md](PERSISTENT_STORAGE_GUIDE.md)**

**Quick Setup**: Create free database at [Supabase](https://supabase.com) → Add `DATABASE_URL` environment variable

### ✅ Benefits of Persistent Storage:
- ✅ **No data loss** on redeployments
- ✅ **Multi-user support** with proper data isolation
- ✅ **Professional reliability** for production use
- ✅ **Automatic backups** (especially with GitHub storage)

## Usage

### Choose Your Interface

**Option 1: Web Interface (Recommended)**
```bash
streamlit run app.py
```
The web interface provides:
- Beautiful dashboard with charts and graphs
- Interactive forms for adding income, expenses, and goals
- Real-time budget recommendations
- Visual analytics and reports
- Progress tracking with gauges and metrics
- Easy database reset with safety confirmations

**Option 2: Command Line Interface**

### Initialize the application
```bash
python -m budget_manager init
```

### Set your monthly salary and savings target
```bash
python -m budget_manager salary set 5000
python -m budget_manager goal set 1000
```

### Add daily expenses
```bash
python -m budget_manager expense add 25.50 "Lunch" --category food
python -m budget_manager expense add 8.00 "Coffee" --category food
```

### Get daily spending recommendation
```bash
python -m budget_manager recommend
```

### View budget status
```bash
python -m budget_manager status
```

### Generate reports
```bash
python -m budget_manager report monthly
python -m budget_manager report category
```

## Project Structure

```
budget_manager/
├── budget_manager/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py        # Data models
│   │   ├── database.py      # Database management
│   │   └── calculator.py    # Budget calculations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── budget_service.py
│   │   ├── expense_service.py
│   │   └── recommendation_service.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py      # CLI commands
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py
│       └── formatters.py
├── tests/
├── requirements.txt
└── README.md
```

## Development

### Quick Commands (using Makefile)
```bash
make install     # Install the application
make ui          # Launch web interface
make demo        # Run demo script
make test        # Run tests
make format      # Format code
make lint        # Run linting
make clean       # Clean up build artifacts
make reset       # Reset database (delete all data)
```

### Manual Commands

#### Running Tests
```bash
pytest tests/ -v --cov=budget_manager
```

#### Code Formatting
```bash
black budget_manager/
```

#### Type Checking
```bash
mypy budget_manager/
```

#### Launch Web Interface
```bash
streamlit run app.py
```

## Database Management

### Reset Database (Delete All Data)

If you want to start fresh with a clean database:

**Option 1: Web Interface**
- Go to Settings → Data Management → Reset Database
- Check both confirmation boxes
- Click 'RESET DATABASE' button

**Option 2: CLI Commands**
```bash
# Using the reset script
python reset_database.py

# Using Make
make reset

# Manual deletion
rm ~/.budget_manager/budget.db
```

**⚠️ Warning:** This will permanently delete all your data including income entries, expenses, savings goals, and historical records.

### Data Location
Your data is stored securely in: `~/.budget_manager/budget.db`

## Supported Currencies

The Smart Budget Manager supports 21 international currencies:

| Currency | Code | Symbol | Name |
|----------|------|--------|------|
| 🇺🇸 | USD | $ | US Dollar |
| 🇪🇺 | EUR | € | Euro |
| 🇬🇧 | GBP | £ | British Pound |
| 🇯🇵 | JPY | ¥ | Japanese Yen |
| 🇨🇦 | CAD | C$ | Canadian Dollar |
| 🇦🇺 | AUD | A$ | Australian Dollar |
| 🇨🇭 | CHF | ₣ | Swiss Franc |
| 🇨🇳 | CNY | ¥ | Chinese Yuan |
| 🇮🇳 | INR | ₹ | Indian Rupee |
| 🇧🇷 | BRL | R$ | Brazilian Real |
| 🇷🇺 | RUB | ₽ | Russian Ruble |
| 🇰🇷 | KRW | ₩ | South Korean Won |
| 🇲🇽 | MXN | $ | Mexican Peso |
| 🇿🇦 | ZAR | R | South African Rand |
| 🇸🇪 | SEK | kr | Swedish Krona |
| 🇳🇴 | NOK | kr | Norwegian Krone |
| 🇩🇰 | DKK | kr | Danish Krone |
| 🇵🇱 | PLN | zł | Polish Złoty |
| 🇹🇷 | TRY | ₺ | Turkish Lira |
| 🇹🇳 | TND | د.ت | Tunisian Dinar |
| 🇳🇿 | NZD | NZ$ | New Zealand Dollar |

### Changing Currency

**Web Interface:**
1. Go to Settings → Preferences
2. Select your preferred currency from the dropdown
3. Adjust decimal places (0-4) and thousands separator as needed
4. See the live preview of formatting

**Currency preferences are saved and persist across sessions.**

## License

MIT License 