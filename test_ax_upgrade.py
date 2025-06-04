#!/usr/bin/env python3
"""
Comprehensive test of the ax-platform upgrade changes.
"""

import sys
import os
import types
import inspect

# Mock dependencies to enable testing without full install
def mock_module(name, attrs=None):
    mock = types.ModuleType(name)
    if attrs:
        for attr, value in attrs.items():
            setattr(mock, attr, value)
    sys.modules[name] = mock
    return mock

# Mock core dependencies
numpy_mock = mock_module('numpy', {
    'floor': lambda x: int(x),
    'linspace': lambda start, stop, num: [start + i*(stop-start)/(num-1) for i in range(num)],
    'round': lambda x: round(x),
    'random': lambda x: [0.5] * x if hasattr(x, '__iter__') else 0.5
})
numpy_mock.random = mock_module('numpy.random', {'random': lambda x: [0.5]*x})

sklearn_mock = mock_module('sklearn')
sklearn_model_selection_mock = mock_module('sklearn.model_selection', {
    'ParameterGrid': lambda x: [x]
})
sklearn_mock.model_selection = sklearn_model_selection_mock

# Add source path
repo_path = os.path.dirname(__file__)
src_path = os.path.join(repo_path, 'src')
sys.path.insert(0, src_path)

def test_api_compatibility():
    """Test that the updated functions maintain API compatibility."""
    print("Testing API compatibility...")
    
    try:
        from self_driving_lab_demo.utils.search import ax_bayesian_optimization, grid_search, random_search
        
        # Test function signatures
        ax_sig = inspect.signature(ax_bayesian_optimization)
        ax_params = list(ax_sig.parameters.keys())
        expected_ax_params = ['sdl', 'num_iter', 'objective_name']
        
        if ax_params == expected_ax_params:
            print("✓ ax_bayesian_optimization signature preserved")
        else:
            print(f"✗ ax_bayesian_optimization signature changed: {ax_params} != {expected_ax_params}")
            return False
        
        # Test that other functions are unchanged
        grid_sig = inspect.signature(grid_search)
        grid_params = list(grid_sig.parameters.keys())
        expected_grid_params = ['sdl', 'num_iter']
        
        if grid_params == expected_grid_params:
            print("✓ grid_search signature preserved")
        else:
            print(f"✗ grid_search signature changed: {grid_params} != {expected_grid_params}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing API compatibility: {e}")
        return False

def test_deferred_import():
    """Test that ax imports are properly deferred."""
    print("Testing deferred ax imports...")
    
    try:
        # This should succeed without importing ax
        from self_driving_lab_demo.utils.search import ax_bayesian_optimization
        print("✓ ax_bayesian_optimization imports without ax dependency")
        
        # Test that calling it fails with ax import error
        class MockSDL:
            def __init__(self):
                self.bounds = {"R": [0, 255], "G": [0, 255], "B": [0, 255]}
            def evaluate(self, params):
                return {"frechet": 0.5, "rmse": 0.3, "mae": 0.2}
        
        try:
            sdl = MockSDL()
            result = ax_bayesian_optimization(sdl, 2)
            print("✗ Expected ax import error, but function succeeded")
            return False
        except ImportError as e:
            if "ax" in str(e) or "AxClient" in str(e):
                print(f"✓ Ax import deferred correctly: {e}")
                return True
            else:
                print(f"✗ Unexpected import error: {e}")
                return False
        except Exception as e:
            print(f"✗ Unexpected error when calling function: {e}")
            return False
            
    except ImportError as e:
        if "ax" in str(e).lower():
            print(f"✗ Ax import not deferred: {e}")
            return False
        else:
            print(f"✗ Other import error: {e}")
            return False

def test_version_constraint():
    """Test that the version constraint has been updated correctly."""
    print("Testing version constraint update...")
    
    setup_cfg_path = os.path.join(os.path.dirname(__file__), 'setup.cfg')
    
    try:
        with open(setup_cfg_path, 'r') as f:
            setup_content = f.read()
        
        if 'ax-platform >= 0.5' in setup_content:
            print("✓ Version constraint updated to >= 0.5")
            return True
        elif 'ax-platform < 0.5' in setup_content:
            print("✗ Version constraint still < 0.5")
            return False
        else:
            print("✗ Cannot find ax-platform version constraint")
            return False
            
    except Exception as e:
        print(f"✗ Error checking version constraint: {e}")
        return False

def test_all_search_files():
    """Test that all search.py files have been updated."""
    print("Testing all search.py files...")
    
    search_files = [
        'src/self_driving_lab_demo/utils/search.py',
        'src/extra/self_driving_lab_demo_blinkt/utils/search.py'
    ]
    
    for search_file in search_files:
        file_path = os.path.join(os.path.dirname(__file__), search_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check that old import is removed
                if 'from ax import optimize' in content:
                    print(f"✗ {search_file} still has deprecated import")
                    return False
                
                # Check that new pattern is present
                if 'from ax.service.ax_client import AxClient' in content:
                    print(f"✓ {search_file} has new AxClient import inside function")
                else:
                    print(f"✗ {search_file} missing AxClient import")
                    return False
                    
            except Exception as e:
                print(f"✗ Error checking {search_file}: {e}")
                return False
        else:
            print(f"✗ {search_file} not found")
            return False
    
    return True

if __name__ == "__main__":
    print("Running comprehensive ax-platform upgrade tests...\n")
    
    tests = [
        test_version_constraint,
        test_all_search_files,
        test_deferred_import,
        test_api_compatibility,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print()
        except Exception as e:
            print(f"✗ Test {test_func.__name__} failed with exception: {e}\n")
            results.append(False)
    
    print("="*60)
    if all(results):
        print("✓ ALL TESTS PASSED! Ax-platform upgrade is ready.")
        print("Changes made:")
        print("  - Updated version constraint from < 0.5 to >= 0.5")
        print("  - Replaced deprecated 'optimize' function with AxClient API")
        print("  - Deferred ax imports to avoid top-level dependency issues")
        print("  - Maintained backward compatibility of function signatures")
        sys.exit(0)
    else:
        failed_tests = [test.__name__ for test, result in zip(tests, results) if not result]
        print(f"✗ {len(failed_tests)} test(s) failed: {failed_tests}")
        sys.exit(1)