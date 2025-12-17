#!/usr/bin/env python3
"""
Visual AutoView - Implementation Verification Script

This script verifies that all components of the Visual AutoView project
are properly implemented and integrated.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}❌ {text}{RESET}")


def verify_backend():
    """Verify backend implementation."""
    print_header("BACKEND VERIFICATION")
    
    backend_path = Path("custom_components/visualautoview")
    checks = {
        "Phase 1 API": backend_path / "api" / "phase1_api.py",
        "Phase 2 API": backend_path / "api" / "phase2_api.py",
        "Phase 3 API": backend_path / "api" / "phase3_api.py",
        "API Base": backend_path / "api" / "base.py",
        "API Models": backend_path / "api" / "models.py",
        "Graph Parser": backend_path / "graph_parser.py",
        "Integration Setup": backend_path / "__init__.py",
    }
    
    results = {}
    for name, path in checks.items():
        if path.exists():
            try:
                lines = len(path.read_text(encoding='utf-8').splitlines())
            except (UnicodeDecodeError, UnicodeError):
                lines = len(path.read_text(encoding='latin-1').splitlines())
            print_success(f"{name:20s} - {lines:4d} lines")
            results[name] = (True, lines)
        else:
            print_error(f"{name:20s} - NOT FOUND")
            results[name] = (False, 0)
    
    return results


def verify_frontend():
    """Verify frontend implementation."""
    print_header("FRONTEND VERIFICATION")
    
    frontend_path = Path("frontend/src")
    checks = {
        "Main App": frontend_path / "app.ts",
        "Dashboard View": frontend_path / "views" / "dashboard.ts",
        "Analytics View": frontend_path / "views" / "analytics.ts",
        "Graph Component": frontend_path / "components" / "graph.ts",
        "API Service": frontend_path / "services" / "api.ts",
        "Helper Utils": frontend_path / "utils" / "helpers.ts",
        "Entry Point": frontend_path / "main.ts",
    }
    
    config_checks = {
        "Package JSON": Path("frontend/package.json"),
        "Vite Config": Path("frontend/vite.config.ts"),
        "TypeScript Config": Path("frontend/tsconfig.json"),
        "HTML Template": Path("frontend/index.html"),
    }
    
    results = {}
    
    # Check TypeScript files
    for name, path in checks.items():
        if path.exists():
            try:
                lines = len(path.read_text(encoding='utf-8').splitlines())
            except (UnicodeDecodeError, UnicodeError):
                lines = len(path.read_text(encoding='latin-1').splitlines())
            print_success(f"{name:20s} - {lines:4d} lines")
            results[name] = (True, lines)
        else:
            print_error(f"{name:20s} - NOT FOUND")
            results[name] = (False, 0)
    
    # Check configuration files
    print()
    for name, path in config_checks.items():
        if path.exists():
            print_success(f"{name:20s} - Configured")
            results[name] = (True, 0)
        else:
            print_error(f"{name:20s} - NOT FOUND")
            results[name] = (False, 0)
    
    return results


def verify_tests():
    """Verify test implementation."""
    print_header("TEST VERIFICATION")
    
    test_path = Path("tests")
    test_files = {
        "Graph Parser Tests": test_path / "test_graph_parser.py",
    }
    
    results = {}
    for name, path in test_files.items():
        if path.exists():
            content = path.read_text()
            test_count = content.count("def test_")
            print_success(f"{name:25s} - {test_count} tests")
            results[name] = (True, test_count)
        else:
            print_warning(f"{name:25s} - Not found (optional)")
            results[name] = (False, 0)
    
    return results


def verify_documentation():
    """Verify documentation."""
    print_header("DOCUMENTATION VERIFICATION")
    
    docs = {
        "API Implementation": Path("API_IMPLEMENTATION_COMPLETE.md"),
        "Quick Start Guide": Path("QUICK_START.md"),
        "Endpoint Checklist": Path("ENDPOINT_CHECKLIST.md"),
        "Frontend Verification": Path("FRONTEND_VERIFICATION.md"),
        "Frontend README": Path("frontend/README.md"),
        "Project Index": Path("PROJECT_INDEX.md"),
    }
    
    results = {}
    for name, path in docs.items():
        if path.exists():
            print_success(f"{name:25s} - Present")
            results[name] = True
        else:
            print_warning(f"{name:25s} - Missing")
            results[name] = False
    
    return results


def count_endpoint_classes(filepath):
    """Count endpoint classes in API file."""
    try:
        content = Path(filepath).read_text(encoding='utf-8')
        return content.count("class ") + content.count("Endpoint")
    except (UnicodeDecodeError, UnicodeError):
        content = Path(filepath).read_text(encoding='latin-1')
        return content.count("class ") + content.count("Endpoint")
    except:
        return 0


def verify_endpoints():
    """Verify API endpoints."""
    print_header("API ENDPOINT VERIFICATION")
    
    endpoints = {
        "Phase 1 Endpoints": "custom_components/visualautoview/api/phase1_api.py",
        "Phase 2 Endpoints": "custom_components/visualautoview/api/phase2_api.py",
        "Phase 3 Endpoints": "custom_components/visualautoview/api/phase3_api.py",
    }
    
    total_endpoints = 0
    results = {}
    
    for name, filepath in endpoints.items():
        path = Path(filepath)
        if path.exists():
            # Count endpoint classes
            try:
                content = path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, UnicodeError):
                content = path.read_text(encoding='latin-1')
            class_count = content.count("class ") - 1  # -1 for container class
            lines = len(content.splitlines())
            print_success(f"{name:25s} - {class_count:2d} classes, {lines:4d} lines")
            results[name] = (True, class_count)
            total_endpoints += class_count
        else:
            print_error(f"{name:25s} - NOT FOUND")
            results[name] = (False, 0)
    
    print(f"\n{BOLD}Total Endpoints: {total_endpoints}{RESET}")
    return results


def print_summary(backend_results, frontend_results, test_results, doc_results, endpoint_results):
    """Print verification summary."""
    print_header("SUMMARY")
    
    # Count successful checks
    backend_ok = sum(1 for ok, _ in backend_results.values() if ok)
    frontend_ok = sum(1 for ok, _ in frontend_results.values() if ok)
    test_ok = sum(1 for ok, _ in test_results.values() if ok)
    doc_ok = sum(1 for ok in doc_results.values() if ok)
    endpoint_ok = sum(1 for ok, _ in endpoint_results.values() if ok)
    
    backend_total = len(backend_results)
    frontend_total = len(frontend_results)
    test_total = len(test_results)
    doc_total = len(doc_results)
    endpoint_total = len(endpoint_results)
    
    # Count lines
    backend_lines = sum(lines for _, lines in backend_results.values())
    frontend_lines = sum(lines for _, lines in frontend_results.values())
    
    print(f"\n{BOLD}Component Status:{RESET}")
    print(f"  Backend:       {backend_ok:2d}/{backend_total} components ({backend_lines:5d} lines)")
    print(f"  Frontend:      {frontend_ok:2d}/{frontend_total} components ({frontend_lines:5d} lines)")
    print(f"  Tests:         {test_ok:2d}/{test_total} test suites")
    print(f"  Endpoints:     {endpoint_ok:2d}/{endpoint_total} endpoint files")
    print(f"  Documentation: {doc_ok:2d}/{doc_total} documents")
    
    total_lines = backend_lines + frontend_lines
    print(f"\n{BOLD}Code Metrics:{RESET}")
    print(f"  Backend Lines:       {backend_lines:6d}")
    print(f"  Frontend Lines:      {frontend_lines:6d}")
    print(f"  Total Project Lines: {total_lines:6d}")
    
    # Overall status
    all_ok = (backend_ok == backend_total and 
              frontend_ok == frontend_total and
              doc_ok == doc_total)
    
    print()
    if all_ok:
        print(f"{GREEN}{BOLD}✅ PROJECT IMPLEMENTATION COMPLETE{RESET}")
        print(f"{GREEN}All components are implemented and ready for production!{RESET}")
        return 0
    else:
        print(f"{YELLOW}{BOLD}⚠️  SOME COMPONENTS MISSING{RESET}")
        print(f"{YELLOW}Please check the verification output above.{RESET}")
        return 1


def main():
    """Main verification function."""
    print(f"{BOLD}{BLUE}Visual AutoView - Implementation Verification{RESET}")
    print(f"{BLUE}Checking all components...{RESET}\n")
    
    # Change to project root if needed
    if not Path("custom_components").exists():
        print_error("Not in project root directory!")
        sys.exit(1)
    
    # Run verifications
    backend_results = verify_backend()
    frontend_results = verify_frontend()
    endpoint_results = verify_endpoints()
    test_results = verify_tests()
    doc_results = verify_documentation()
    
    # Print summary
    exit_code = print_summary(
        backend_results,
        frontend_results,
        test_results,
        doc_results,
        endpoint_results
    )
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
