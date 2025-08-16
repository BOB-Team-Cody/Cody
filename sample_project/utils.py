"""Utility functions for sample project."""


def calculate_sum(numbers):
    """Calculate sum of numbers in a list."""
    return sum(numbers)


def format_output(data, total):
    """Format output string with data and total."""
    return f"Processed {len(data)} items, total: {total}"


def helper_function(text):
    """Helper function for text processing."""
    return text.upper()


def unused_helper():
    """This helper is never used - dead code."""
    return "Never called"