"""Data processing service with various class methods."""

from typing import List, Dict, Any
from models.user import User


class DataProcessor:
    """Main data processing service."""
    
    def __init__(self):
        """Initialize data processor."""
        self.processed_count = 0
        self.cache = {}
        self.validator = DataValidator()
    
    def process_users(self, users: List[User]) -> List[Dict[str, Any]]:
        """Process a list of users."""
        results = []
        for user in users:
            if self.validator.validate_user(user):
                processed = self._process_single_user(user)
                results.append(processed)
                self.processed_count += 1
        
        return results
    
    def _process_single_user(self, user: User) -> Dict[str, Any]:
        """Process a single user (private method)."""
        user_info = user.get_info()
        enhanced_info = self._enhance_user_data(user_info)
        return enhanced_info
    
    def _enhance_user_data(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance user data with additional processing."""
        enhanced = user_info.copy()
        enhanced['processed_timestamp'] = self._get_timestamp()
        enhanced['risk_score'] = self._calculate_risk_score(user_info)
        return enhanced
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _calculate_risk_score(self, user_info: Dict[str, Any]) -> float:
        """Calculate risk score for user."""
        age = user_info.get('age', 0)
        if age < 18:
            return 0.1
        elif age > 65:
            return 0.3
        else:
            return 0.5
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'processed_count': self.processed_count,
            'cache_size': len(self.cache)
        }
    
    def clear_cache(self):
        """Clear processing cache."""
        self.cache.clear()


class DataValidator:
    """Validator for data processing."""
    
    def __init__(self):
        """Initialize validator."""
        self.validation_rules = self._load_validation_rules()
    
    def validate_user(self, user: User) -> bool:
        """Validate user data."""
        if not self._validate_name(user.name):
            return False
        if not self._validate_age(user.age):
            return False
        return True
    
    def _validate_name(self, name: str) -> bool:
        """Validate user name."""
        return isinstance(name, str) and len(name.strip()) > 0
    
    def _validate_age(self, age: int) -> bool:
        """Validate user age."""
        return isinstance(age, int) and 0 <= age <= 150
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules."""
        return {
            'min_age': 0,
            'max_age': 150,
            'required_fields': ['name', 'age']
        }


class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self, connection_string: str = "sqlite://memory"):
        """Initialize database manager."""
        self.connection_string = connection_string
        self.connection = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to database."""
        try:
            # Simulate database connection
            self.connection = f"Connected to {self.connection_string}"
            self.is_connected = True
            return True
        except Exception:
            return False
    
    def disconnect(self):
        """Disconnect from database."""
        self.connection = None
        self.is_connected = False
    
    def save_user(self, user: User) -> bool:
        """Save user to database."""
        if not self.is_connected:
            self.connect()
        
        try:
            # Simulate saving user
            user_data = user.get_info()
            return self._execute_query("INSERT", user_data)
        except Exception:
            return False
    
    def _execute_query(self, query_type: str, data: Dict[str, Any]) -> bool:
        """Execute database query."""
        # Simulate query execution
        if query_type == "INSERT":
            return self._insert_data(data)
        elif query_type == "UPDATE":
            return self._update_data(data)
        return False
    
    def _insert_data(self, data: Dict[str, Any]) -> bool:
        """Insert data into database."""
        # Simulate insert operation
        return len(data) > 0
    
    def _update_data(self, data: Dict[str, Any]) -> bool:
        """Update data in database."""
        # Simulate update operation
        return 'id' in data


class APIClient:
    """API client for external services."""
    
    def __init__(self, base_url: str, api_key: str = None):
        """Initialize API client."""
        self.base_url = base_url
        self.api_key = api_key
        self.session = self._create_session()
    
    def _create_session(self):
        """Create HTTP session."""
        # Simulate session creation
        return {
            'headers': {'Authorization': f'Bearer {self.api_key}' if self.api_key else None},
            'timeout': 30
        }
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from external API."""
        endpoint = f"/users/{user_id}"
        return self._make_request("GET", endpoint)
    
    def update_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user data via external API."""
        endpoint = f"/users/{user_id}"
        response = self._make_request("PUT", endpoint, data)
        return response.get('success', False)
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        # Simulate API call
        if method == "GET":
            return self._simulate_get_response(endpoint)
        elif method == "PUT":
            return self._simulate_put_response(data)
        
        return {}
    
    def _simulate_get_response(self, endpoint: str) -> Dict[str, Any]:
        """Simulate GET response."""
        return {
            'id': endpoint.split('/')[-1],
            'data': 'simulated_data',
            'status': 'success'
        }
    
    def _simulate_put_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate PUT response."""
        return {
            'success': True,
            'updated_fields': list(data.keys()) if data else []
        }


def unused_function_outside_class():
    """This function is never called - dead code."""
    processor = DataProcessor()
    return processor.get_statistics()