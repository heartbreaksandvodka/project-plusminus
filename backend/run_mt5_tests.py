#!/usr/bin/env python
"""
Test runner for MT5 integration tests
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'authproject.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific MT5 tests
    failures = test_runner.run_tests(["mt5_integration.tests"])
    
    if failures:
        sys.exit(1)
    else:
        print("All MT5 tests passed!")
        sys.exit(0)
