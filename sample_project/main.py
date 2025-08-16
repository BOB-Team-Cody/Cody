"""
Sample Python project for Code Weaver analysis
Main entry point with various code patterns
"""

from utils.helpers import calculate_sum, format_output
from models.user import User
from services.data_processor import DataProcessor

def main():
    """Main function that orchestrates the application"""
    print("Starting Code Weaver Sample Application...")
    
    # Create sample data
    users = [
        User("Alice", 25),
        User("Bob", 30),
        User("Charlie", 35)
    ]
    
    # Process data
    processor = DataProcessor()
    processed_data = processor.process_users(users)
    
    # Calculate and display results
    total_age = calculate_sum([user.age for user in users])
    output = format_output(processed_data, total_age)
    
    print(output)
    
    # Call some unused functions for dead code detection
    unused_function()
    
def unused_function():
    """This function is never called - should be detected as dead code"""
    return "This code is never executed"

def another_unused_function():
    """Another unused function for testing"""
    result = calculate_complex_operation(10, 20)
    return f"Complex result: {result}"

def calculate_complex_operation(a, b):
    """This is also unused"""
    return a * b + (a - b) ** 2

if __name__ == "__main__":
    main()