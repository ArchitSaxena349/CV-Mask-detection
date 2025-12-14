#!/usr/bin/env python3
"""
Check system compatibility for Mask Detection System
"""
import sys
import importlib.util

def check_package(package_name, min_version=None):
    """Check if a package is available and optionally check version"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            return False, f"❌ {package_name} not found"
        
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        
        if min_version and hasattr(module, '__version__'):
            from packaging import version as pkg_version
            if pkg_version.parse(version) < pkg_version.parse(min_version):
                return False, f"❌ {package_name} {version} < {min_version}"
        
        return True, f"✅ {package_name} {version}"
    except Exception as e:
        return False, f"❌ {package_name}: {e}"

def main():
    """Run compatibility checks"""
    print("🔍 Checking Mask Detection System Compatibility...")
    print("=" * 50)
    
    # Core dependencies
    checks = [
        ("flask", "3.0.0"),
        ("cv2", None),  # opencv
        ("numpy", "1.20.0"),
        ("PIL", None),  # Pillow
        ("tensorflow", "2.16.0"),
        ("waitress", "2.0.0"),
        ("psutil", "5.0.0"),
        ("requests", "2.25.0"),
    ]
    
    all_passed = True
    
    for package, min_ver in checks:
        passed, message = check_package(package, min_ver)
        print(message)
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All compatibility checks passed!")
        print("🚀 System ready for Mask Detection deployment!")
        return 0
    else:
        print("⚠️ Some compatibility issues found.")
        print("📋 Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())