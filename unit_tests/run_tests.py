import unittest
import sys
import os
import json
from datetime import datetime
from typing import Optional

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class JSONTestResult(unittest.TestResult):
    """Custom TestResult class that creates a JSON-serializable result."""

    def __init__(self):
        super().__init__()
        self.start_time: Optional[datetime] = None
        self.test_results = []

    def startTest(self, test):
        self.start_time = datetime.now()
        super().startTest(test)

    def addSuccess(self, test):
        if self.start_time is not None:
            execution_time = datetime.now() - self.start_time
            self.test_results.append({
                'test_name': test.id(),
                'status': 'pass',
                'execution_time': str(execution_time),
                'timestamp': datetime.now().isoformat()
            })
        super().addSuccess(test)

    def addError(self, test, err):
        if self.start_time is not None and err[0] is not None:
            execution_time = datetime.now() - self.start_time
            self.test_results.append({
                'test_name': test.id(),
                'status': 'error',
                'error_type': err[0].__name__,
                'error_message': str(err[1]),
                'execution_time': str(execution_time),
                'timestamp': datetime.now().isoformat()
            })
        super().addError(test, err)

    def addFailure(self, test, err):
        if self.start_time is not None and err[0] is not None:
            execution_time = datetime.now() - self.start_time
            self.test_results.append({
                'test_name': test.id(),
                'status': 'fail',
                'error_type': err[0].__name__,
                'error_message': str(err[1]),
                'execution_time': str(execution_time),
                'timestamp': datetime.now().isoformat()
            })
        super().addFailure(test, err)

def save_test_results(results: JSONTestResult) -> str:
    """Save test results to a JSON file."""
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'test_results.json'
    )

    # Create test summary
    summary = {
        'total_tests': results.testsRun,
        'passed': len([t for t in results.test_results if t['status'] == 'pass']),
        'failed': len([t for t in results.test_results if t['status'] == 'fail']),
        'errors': len([t for t in results.test_results if t['status'] == 'error']),
        'timestamp': datetime.now().isoformat(),
        'test_cases': results.test_results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    return output_file

def run_tests() -> bool:
    """Run all unit tests and save results to JSON."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with custom result object
    result = JSONTestResult()
    suite.run(result)

    # Save results to JSON
    output_file = save_test_results(result)
    print(f"\nTest results saved to: {output_file}")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)