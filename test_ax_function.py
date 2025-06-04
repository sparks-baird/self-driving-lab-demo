#!/usr/bin/env python3
"""
Test specifically the ax_bayesian_optimization function changes
without importing the full package.
"""

import sys
import os
import types

# Mock dependencies
def mock_module(name, attrs=None):
    mock = types.ModuleType(name)
    if attrs:
        for attr, value in attrs.items():
            setattr(mock, attr, value)
    sys.modules[name] = mock
    return mock

numpy_mock = mock_module('numpy', {'floor': lambda x: int(x)})
sklearn_mock = mock_module('sklearn')
sklearn_model_selection_mock = mock_module('sklearn.model_selection', {
    'ParameterGrid': lambda x: [x]
})
sklearn_mock.model_selection = sklearn_model_selection_mock

print("Testing ax_bayesian_optimization function directly...")

# Load and test the search.py file directly
search_file = os.path.join(os.path.dirname(__file__), 'src', 'self_driving_lab_demo', 'utils', 'search.py')

try:
    with open(search_file, 'r') as f:
        search_code = f.read()
    
    # Create a namespace and execute the code
    namespace = {}
    exec(search_code, namespace)
    
    print("✓ search.py executes successfully")
    
    # Test the function signature
    ax_func = namespace['ax_bayesian_optimization']
    import inspect
    sig = inspect.signature(ax_func)
    params = list(sig.parameters.keys())
    expected = ['sdl', 'num_iter', 'objective_name']
    
    if params == expected:
        print("✓ Function signature is correct")
    else:
        print(f"✗ Function signature wrong: {params} != {expected}")
        sys.exit(1)
    
    # Test that calling the function triggers ax import
    class MockSDL:
        def __init__(self):
            self.bounds = {"R": [0, 255], "G": [0, 255], "B": [0, 255]}
        def evaluate(self, params):
            return {"frechet": 0.5, "rmse": 0.3, "mae": 0.2}
    
    try:
        sdl = MockSDL()
        result = ax_func(sdl, 2)
        print("✗ Expected ImportError for ax, but function succeeded")
        sys.exit(1)
    except ImportError as e:
        if "ax" in str(e):
            print(f"✓ Ax import properly deferred: {e}")
        else:
            print(f"✗ Wrong import error: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)
    
    print("✓ All tests passed for ax_bayesian_optimization!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)