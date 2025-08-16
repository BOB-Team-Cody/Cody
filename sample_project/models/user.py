"""User model for the sample application"""

class User:
    """Represents a user in the system"""
    
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
        self._id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the user"""
        return f"user_{hash(self.name) % 10000}"
    
    def get_info(self) -> dict:
        """Get user information as dictionary"""
        return {
            "id": self._id,
            "name": self.name,
            "age": self.age,
            "category": self.get_age_category()
        }
    
    def get_age_category(self) -> str:
        """Categorize user by age"""
        if self.age < 20:
            return "young"
        elif self.age < 65:
            return "adult"
        else:
            return "senior"
    
    def update_age(self, new_age: int):
        """Update user's age"""
        self.age = new_age
    
    def __str__(self) -> str:
        return f"User({self.name}, {self.age})"
    
    def __repr__(self) -> str:
        return self.__str__()

class AdminUser(User):
    """Administrative user with special privileges"""
    
    def __init__(self, name: str, age: int, permissions: list = None):
        super().__init__(name, age)
        self.permissions = permissions or ["read", "write"]
    
    def has_permission(self, permission: str) -> bool:
        """Check if admin has specific permission"""
        return permission in self.permissions
    
    def add_permission(self, permission: str):
        """Add a new permission"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def get_admin_info(self) -> dict:
        """Get admin-specific information"""
        info = self.get_info()
        info["permissions"] = self.permissions
        info["is_admin"] = True
        return info

# This class is never used - dead code
class ObsoleteUser:
    """This class is obsolete and should be detected as dead code"""
    
    def __init__(self, name):
        self.name = name
    
    def old_method(self):
        """This method is never called"""
        return f"Old user: {self.name}"