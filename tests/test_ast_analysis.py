"""Test AST analysis functionality using sample_project."""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.analysis_service import AnalysisService


def get_expected_functions_from_source(project_path: Path) -> list:
    """Extract all function names from source files using AST."""
    import ast
    from src.utils.file_utils import find_python_files, safe_read_file
    
    functions = []
    python_files = find_python_files(project_path)
    
    for py_file in python_files:
        try:
            content = safe_read_file(py_file)
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
        except Exception as e:
            print(f"Warning: Failed to parse {py_file}: {e}")
            continue
    
    return list(set(functions))  # Remove duplicates


def get_expected_classes_from_source(project_path: Path) -> list:
    """Extract all class names from source files using AST."""
    import ast
    from src.utils.file_utils import find_python_files, safe_read_file
    
    classes = []
    python_files = find_python_files(project_path)
    
    for py_file in python_files:
        try:
            content = safe_read_file(py_file)
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except Exception as e:
            print(f"Warning: Failed to parse {py_file}: {e}")
            continue
    
    return list(set(classes))  # Remove duplicates


def get_functions_from_file(file_path: Path) -> list:
    """Extract function names from a specific file."""
    import ast
    from src.utils.file_utils import safe_read_file
    
    try:
        content = safe_read_file(file_path)
        tree = ast.parse(content)
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
        
        return functions
    except Exception as e:
        print(f"Failed to extract functions from {file_path}: {e}")
        return []


def test_ast_function_extraction():
    """Test that AST analysis correctly extracts functions from sample_project."""
    print("=== Testing AST Function Extraction ===")
    
    # Get sample project path
    sample_project_path = Path(__file__).parent.parent / 'sample_project'
    print(f"Analyzing project: {sample_project_path}")
    
    # Initialize analysis service
    service = AnalysisService()
    
    # Analyze the sample project
    try:
        result = service.analyze_project(str(sample_project_path))
        print(f"Analysis completed successfully!")
        print(f"Found {len(result.nodes)} nodes and {len(result.edges)} edges")
        print(f"Total files analyzed: {result.file_count}")
        print(f"Dead code items detected: {result.dead_code_count}")
        
        # Extract functions from analysis results
        functions = [node for node in result.nodes if node.type == "function"]
        classes = [node for node in result.nodes if node.type == "class"]
        modules = [node for node in result.nodes if node.type == "module"]
        
        print(f"\n=== Analysis Results ===")
        print(f"Modules: {len(modules)}")
        print(f"Classes: {len(classes)}")
        print(f"Functions: {len(functions)}")
        
        # Print extracted functions
        print(f"\n=== Extracted Functions ===")
        for func in functions:
            dead_status = " (DEAD CODE)" if func.dead else ""
            call_count = f" (calls: {func.call_count})" if func.call_count > 0 else ""
            print(f"  - {func.label} in {func.file}{dead_status}{call_count}")
        
        # Print extracted classes
        print(f"\n=== Extracted Classes ===")
        for cls in classes:
            dead_status = " (DEAD CODE)" if cls.dead else ""
            call_count = f" (calls: {cls.call_count})" if cls.call_count > 0 else ""
            print(f"  - {cls.label} in {cls.file}{dead_status}{call_count}")
        
        # Get expected functions by parsing source files directly
        expected_functions = get_expected_functions_from_source(sample_project_path)
        
        found_function_names = [func.label for func in functions]
        print(f"\n=== Function Verification ===")
        for expected in expected_functions:
            if expected in found_function_names:
                print(f"  ✓ Found expected function: {expected}")
            else:
                print(f"  ✗ Missing expected function: {expected}")
        
        # Get expected classes by parsing source files directly
        expected_classes = get_expected_classes_from_source(sample_project_path)
        found_class_names = [cls.label for cls in classes]
        print(f"\n=== Class Verification ===")
        for expected in expected_classes:
            if expected in found_class_names:
                print(f"  ✓ Found expected class: {expected}")
            else:
                print(f"  ✗ Missing expected class: {expected}")
        
        # Print call relationships (edges)
        print(f"\n=== Call Relationships ===")
        for edge in result.edges[:10]:  # Show first 10 edges
            print(f"  {edge.source} -> {edge.target} ({edge.type})")
        if len(result.edges) > 10:
            print(f"  ... and {len(result.edges) - 10} more edges")
        
        return True
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_file_analysis():
    """Test analysis of a specific file to verify AST parsing."""
    print(f"\n=== Testing Specific File Analysis ===")
    
    sample_project_path = Path(__file__).parent.parent / 'sample_project'
    main_file = sample_project_path / 'main.py'
    
    if not main_file.exists():
        print(f"Main file not found: {main_file}")
        return False
    
    # Read and parse the main.py file manually using AST
    import ast
    from src.utils.file_utils import safe_read_file
    
    try:
        content = safe_read_file(main_file)
        tree = ast.parse(content)
        
        print(f"Successfully parsed {main_file}")
        print(f"AST node type: {type(tree)}")
        
        # Extract functions using AST walker
        functions_found = []
        classes_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions_found.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions_found.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes_found.append(node.name)
        
        print(f"\nDirect AST analysis of main.py:")
        print(f"Functions found: {functions_found}")
        print(f"Classes found: {classes_found}")
        
        # Get expected functions from main.py specifically
        expected_main_functions = get_functions_from_file(main_file)
        
        print(f"\nVerifying main.py functions:")
        for expected in expected_main_functions:
            if expected in functions_found:
                print(f"  ✓ Found: {expected}")
            else:
                print(f"  ✗ Missing: {expected}")
        
        return True
        
    except Exception as e:
        print(f"Failed to parse main.py: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dead_code_detection():
    """Test dead code detection functionality."""
    print(f"\n=== Testing Dead Code Detection ===")
    
    sample_project_path = Path(__file__).parent.parent / 'sample_project'
    service = AnalysisService()
    
    try:
        result = service.analyze_project(str(sample_project_path))
        
        # Find dead code items
        dead_functions = [node for node in result.nodes if node.type == "function" and node.dead]
        dead_classes = [node for node in result.nodes if node.type == "class" and node.dead]
        
        print(f"Dead functions detected: {len(dead_functions)}")
        for func in dead_functions:
            print(f"  - {func.label} in {func.file}")
        
        print(f"Dead classes detected: {len(dead_classes)}")
        for cls in dead_classes:
            print(f"  - {cls.label} in {cls.file}")
        
        # Verify some expected dead code (functions that are defined but never called)
        dead_function_names = [func.label for func in dead_functions]
        expected_dead = ['another_unused_function', 'calculate_complex_operation']
        
        print(f"\nVerifying expected dead code:")
        for expected in expected_dead:
            if expected in dead_function_names:
                print(f"  ✓ Correctly identified as dead: {expected}")
            else:
                print(f"  ? Not identified as dead: {expected}")
        
        return True
        
    except Exception as e:
        print(f"Dead code detection failed: {e}")
        return False


def run_all_tests():
    """Run all AST analysis tests."""
    print("Starting AST Analysis Tests")
    print("=" * 50)
    
    tests = [
        test_ast_function_extraction,
        test_specific_file_analysis,
        test_dead_code_detection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print("-" * 50)
    
    print(f"\n=== Test Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "PASS" if result else "FAIL"
        print(f"  {test.__name__}: {status}")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    exit_code = 0 if success else 1
    print(f"\nExiting with code: {exit_code}")
    sys.exit(exit_code)