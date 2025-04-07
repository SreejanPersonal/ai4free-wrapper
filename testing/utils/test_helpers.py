"""
test_helpers.py

Common utility functions for test scripts.
"""

def print_section_header(title: str):
    """
    Prints a decorative section header.
    
    Args:
        title (str): The title to display in the header
    """
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_separator():
    """
    Prints a separator line for readability.
    """
    print("\n" + "=" * 80 + "\n")

def print_test_case(test_name: str):
    """
    Prints a test case header.
    
    Args:
        test_name (str): The name of the test case
    """
    print("\n----- Test Case: " + test_name + " -----")
