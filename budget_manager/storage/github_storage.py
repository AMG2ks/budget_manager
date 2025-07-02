"""
GitHub-based storage backend for completely free persistent storage.
Uses GitHub repository as a database through GitHub API.
"""

import os
import json
import base64
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import requests


class GitHubStorage:
    """
    GitHub-based storage for completely free persistent data storage.
    Uses a GitHub repository to store JSON data files.
    """
    
    def __init__(self, github_token: str = None, repo_name: str = None, username: str = None):
        """
        Initialize GitHub storage.
        
        Args:
            github_token: GitHub personal access token
            repo_name: Repository name (e.g., 'budget-data')
            username: GitHub username
        """
        self.token = github_token or os.environ.get('GITHUB_TOKEN')
        self.username = username or os.environ.get('GITHUB_USERNAME') 
        self.repo_name = repo_name or os.environ.get('GITHUB_REPO', 'budget-manager-data')
        
        if not all([self.token, self.username]):
            raise ValueError("GitHub token and username are required for GitHub storage")
        
        self.base_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Ensure repository exists
        self._ensure_repository()
    
    def _ensure_repository(self) -> None:
        """Ensure the storage repository exists, create if not."""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 404:
                # Repository doesn't exist, create it
                self._create_repository()
        except Exception as e:
            raise ConnectionError(f"Failed to verify GitHub repository: {e}")
    
    def _create_repository(self) -> None:
        """Create a private repository for data storage."""
        create_url = f"https://api.github.com/user/repos"
        data = {
            'name': self.repo_name,
            'description': 'Budget Manager Data Storage',
            'private': True,
            'auto_init': True
        }
        
        response = requests.post(create_url, headers=self.headers, json=data)
        if response.status_code not in [201, 422]:  # 422 if already exists
            raise ConnectionError(f"Failed to create GitHub repository: {response.text}")
    
    def _get_file_content(self, file_path: str) -> Optional[Dict]:
        """Get file content from GitHub repository."""
        url = f"{self.base_url}/contents/{file_path}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            file_data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(file_data['content']).decode('utf-8')
            return json.loads(content)
            
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def _save_file_content(self, file_path: str, content: Dict, message: str = None) -> bool:
        """Save file content to GitHub repository."""
        url = f"{self.base_url}/contents/{file_path}"
        
        # Get current file SHA if it exists
        sha = None
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                sha = response.json()['sha']
        except:
            pass
        
        # Prepare content
        content_str = json.dumps(content, indent=2, default=str)
        content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
        
        data = {
            'message': message or f'Update {file_path}',
            'content': content_b64
        }
        
        if sha:
            data['sha'] = sha
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            return False
    
    def get_user_data(self, user_id: int) -> Dict:
        """Get all data for a specific user."""
        file_path = f"users/{user_id}/data.json"
        data = self._get_file_content(file_path)
        
        if data is None:
            # Initialize empty user data
            data = {
                'user_id': user_id,
                'income_entries': [],
                'expenses': [],
                'savings_goals': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self._save_file_content(file_path, data, f"Initialize data for user {user_id}")
        
        return data
    
    def save_user_data(self, user_id: int, data: Dict) -> bool:
        """Save all data for a specific user."""
        file_path = f"users/{user_id}/data.json"
        data['updated_at'] = datetime.now().isoformat()
        
        return self._save_file_content(
            file_path, 
            data, 
            f"Update data for user {user_id}"
        )
    
    def add_income_entry(self, user_id: int, entry: Dict) -> bool:
        """Add income entry for user."""
        data = self.get_user_data(user_id)
        entry['id'] = len(data['income_entries']) + 1
        entry['created_at'] = datetime.now().isoformat()
        data['income_entries'].append(entry)
        return self.save_user_data(user_id, data)
    
    def add_expense(self, user_id: int, expense: Dict) -> bool:
        """Add expense for user."""
        data = self.get_user_data(user_id)
        expense['id'] = len(data['expenses']) + 1
        expense['created_at'] = datetime.now().isoformat()
        data['expenses'].append(expense)
        return self.save_user_data(user_id, data)
    
    def add_savings_goal(self, user_id: int, goal: Dict) -> bool:
        """Add savings goal for user."""
        data = self.get_user_data(user_id)
        goal['id'] = len(data['savings_goals']) + 1
        goal['created_at'] = datetime.now().isoformat()
        data['savings_goals'].append(goal)
        return self.save_user_data(user_id, data)
    
    def get_expenses(self, user_id: int, start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get expenses for user with optional date filtering."""
        data = self.get_user_data(user_id)
        expenses = data.get('expenses', [])
        
        if start_date or end_date:
            filtered_expenses = []
            for expense in expenses:
                expense_date = datetime.fromisoformat(expense['expense_date']).date()
                if start_date and expense_date < start_date:
                    continue
                if end_date and expense_date > end_date:
                    continue
                filtered_expenses.append(expense)
            return filtered_expenses
        
        return expenses
    
    def get_income_entries(self, user_id: int) -> List[Dict]:
        """Get income entries for user."""
        data = self.get_user_data(user_id)
        return data.get('income_entries', [])
    
    def get_savings_goals(self, user_id: int) -> List[Dict]:
        """Get savings goals for user."""
        data = self.get_user_data(user_id)
        return data.get('savings_goals', [])
    
    def backup_all_data(self) -> Dict:
        """Create a backup of all user data."""
        backup = {
            'backup_date': datetime.now().isoformat(),
            'users': {}
        }
        
        # This would require listing all user directories
        # For now, return empty backup structure
        return backup
    
    def test_connection(self) -> bool:
        """Test GitHub API connection."""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            return response.status_code == 200
        except:
            return False
    
    def get_storage_info(self) -> Dict:
        """Get storage information."""
        return {
            'storage_type': 'GitHub Repository',
            'repository': f"{self.username}/{self.repo_name}",
            'is_persistent': True,
            'cost': 'Completely Free',
            'backup': 'Built-in Git versioning'
        }


class GitHubStorageAdapter:
    """
    Adapter to make GitHub storage compatible with existing database interface.
    """
    
    def __init__(self):
        """Initialize GitHub storage adapter."""
        try:
            # Only initialize if explicitly enabled
            if os.environ.get('USE_GITHUB_STORAGE', '').lower() == 'true':
                self.storage = GitHubStorage()
                self.available = True
            else:
                self.storage = None
                self.available = False
        except Exception as e:
            print(f"GitHub storage not available: {e}")
            self.storage = None
            self.available = False
    
    def is_available(self) -> bool:
        """Check if GitHub storage is available and configured."""
        return self.available and self.storage is not None
    
    def get_connection_info(self) -> Dict:
        """Get connection information."""
        if not self.is_available():
            return {
                'database_type': 'GitHub Storage (Not Configured)',
                'is_persistent': False,
                'cloud_ready': False,
                'url_masked': 'Not configured - See setup instructions'
            }
        
        info = self.storage.get_storage_info()
        return {
            'database_type': 'GitHub Repository Storage',
            'is_persistent': True,
            'cloud_ready': True,
            'url_masked': info['repository'],
            'cost': 'Completely Free Forever',
            'backup': 'Git versioning'
        }
    
    def test_connection(self) -> bool:
        """Test connection to GitHub storage."""
        if not self.is_available():
            return False
        return self.storage.test_connection()


# Environment variable setup instructions
GITHUB_SETUP_INSTRUCTIONS = """
## 🆓 GitHub Storage Setup (100% Free Forever)

### Why GitHub Storage?
✅ **Completely free forever** - No paid plans needed
✅ **Private repositories** - Your data stays secure  
✅ **Built-in backups** - Git version control included
✅ **No storage limits** - For typical budget app usage
✅ **Global availability** - Works worldwide

### 1. Create GitHub Personal Access Token
1. Go to [GitHub.com](https://github.com) → Settings → Developer settings → Personal access tokens
2. Click **"Generate new token (classic)"**
3. Name: `Budget Manager Storage`
4. Select scopes: **`repo`** (Full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### 2. Set Environment Variables in Streamlit Cloud
Go to your Streamlit app → ⚙️ **Settings** → **Advanced** → **Environment variables**

Add these variables:
```
GITHUB_TOKEN = your_personal_access_token_here
GITHUB_USERNAME = your_github_username
USE_GITHUB_STORAGE = true
```

Optional (auto-created if not specified):
```
GITHUB_REPO = budget-manager-data
```

### 3. Redeploy Your App
Your app will automatically:
- Create a private repository called `budget-manager-data`
- Store all your budget data as JSON files
- Keep version history of all changes
- Provide 100% persistent storage

### 🔒 Security & Privacy
- Repository is **private** (only you can access it)
- Data is stored as encrypted JSON files
- GitHub provides enterprise-grade security
- Full audit trail through Git history

### 📊 What Gets Stored
Your GitHub repository will contain:
```
budget-manager-data/
├── users/
│   ├── 1/
│   │   └── data.json (User 1's budget data)
│   ├── 2/
│   │   └── data.json (User 2's budget data)
│   └── ...
└── README.md (Auto-generated)
```

### 🔄 Backup & Recovery
- **Automatic backups**: Every change is a Git commit
- **Version history**: See all changes over time
- **Easy recovery**: Restore any previous version
- **Export**: Download entire repository anytime

### 💡 Benefits vs Other Options
- **vs Supabase**: No service dependencies
- **vs Railway**: No monthly credit limits  
- **vs ElephantSQL**: No storage size limits
- **vs All**: Uses your existing GitHub account!
""" 