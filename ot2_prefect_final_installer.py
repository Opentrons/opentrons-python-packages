#!/usr/bin/env python3
"""
OT-2 Prefect Partial Installation Script
Successfully installs Prefect v3.3.4 with BASIC flow/task functionality on OT-2

⚠️ LIMITATION: Only provides 3 of 15+ required wheels for FULL functionality
✅ ACHIEVEMENT: Resolves core compilation issues and enables basic Prefect workflows
"""

import subprocess
import sys
import os


def run_command(cmd, check=True):
    """Run command and return result"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Error: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if check:
            raise
        return e


def install_wheel(url, force=True, user=True):
    """Install a wheel with force and user flags"""
    cmd = [sys.executable, '-m', 'pip', 'install']
    
    if force:
        cmd.extend(['--force-reinstall', '--no-deps'])
    
    if user:
        cmd.append('--user')
    
    cmd.append(url)
    
    return run_command(cmd, check=False)


def set_pythonpath():
    """Set PYTHONPATH for OT-2 compatibility"""
    user_site = "/var/user-packages/root/.local/lib/python3.10/site-packages"
    current_path = os.environ.get('PYTHONPATH', '')
    new_path = f"{user_site}:{current_path}" if current_path else user_site
    os.environ['PYTHONPATH'] = new_path
    print(f"✅ PYTHONPATH set to: {new_path}")


def main():
    print("=== OT-2 BASIC PREFECT INSTALLATION ===")
    print("🎯 Installing Prefect v3.3.4 with basic workflow functionality")
    print("⚠️  Note: Only 3 of 15+ required wheels provided (see documentation)\n")
    
    # Set Python path for OT-2 compatibility
    set_pythonpath()
    
    # Base URL for pre-built wheels
    base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
    
    # Core wheels that resolve compilation issues
    wheels = [
        ("pendulum-3.1.0-cp310-cp310-linux_armv7l.whl", "Resolves Prefect's core dependency issue"),
        ("ujson-5.10.0-py3-none-linux_armv7l.whl", "Custom ARMv7l fallback for JSON processing"),
        ("prefect-3.3.4-py3-none-any.whl", "Basic Prefect workflow engine"),
    ]
    
    print("Phase 1: Installing core pre-built wheels...")
    for wheel, description in wheels:
        url = base_url + wheel
        print(f"\n📦 Installing {wheel}")
        print(f"   Purpose: {description}")
        result = install_wheel(url, force=True, user=True)
        if result.returncode == 0:
            print(f"✅ {wheel} installed successfully")
        else:
            print(f"❌ {wheel} failed to install")
    
    print("\nPhase 2: Installing additional dependencies...")
    
    # Install dependencies that need compilation resolution
    deps = [
        ("pydantic>=2.0", "Modern data validation (resolves v1->v2 conflicts)"),
        ("rich", "Terminal formatting for Prefect flows"),
        ("typing-extensions>=4.10.0", "Modern type hints"),
    ]
    
    for dep, description in deps:
        print(f"\n📦 Installing {dep}")
        print(f"   Purpose: {description}")
        cmd = [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', dep]
        result = run_command(cmd, check=False)
        if result.returncode == 0:
            print(f"✅ {dep} installed successfully")
        else:
            print(f"❌ {dep} failed to install")
    
    print("\nPhase 3: Testing complete Prefect installation...")
    
    # Test basic import
    print("\n🔍 Testing Prefect core import...")
    test_cmd = [sys.executable, '-c', "import prefect; print(f'Prefect version: {prefect.__version__}')"]
    result = run_command(test_cmd, check=False)
    if result.returncode == 0:
        print("✅ Prefect core import: SUCCESS")
    else:
        print("❌ Prefect core import: FAILED")
        return
    
    # Test flow/task imports
    print("\n🔍 Testing flow and task imports...")
    test_cmd = [sys.executable, '-c', "from prefect import flow, task; print('Flow/task imports: SUCCESS')"]
    result = run_command(test_cmd, check=False)
    if result.returncode == 0:
        print("✅ Flow/task imports: SUCCESS")
    else:
        print("❌ Flow/task imports: FAILED")
        return
    
    # Test complete flow functionality
    print("\n🔍 Testing complete flow execution...")
    flow_test = '''
from prefect import flow, task

@task
def say_hello(name: str):
    return f"Hello {name}!"

@flow 
def hello_flow(name: str = "OT-2"):
    message = say_hello(name)
    print(message)
    return message

if __name__ == "__main__":
    result = hello_flow()
    print(f"Flow result: {result}")
    print("🎉 PREFECT FULLY OPERATIONAL ON OT-2!")
'''
    
    test_cmd = [sys.executable, '-c', flow_test]
    result = run_command(test_cmd, check=False)
    if result.returncode == 0:
        print("✅ Complete flow execution: SUCCESS")
        print("\n🎉 BASIC INSTALLATION COMPLETE! 🎉")
        print("=" * 50)
        print("✅ Prefect v3.3.4 basic functionality working on OT-2")
        print("✅ Flow and task decorators functional")
        print("✅ Core compilation issues resolved")
        print("⚠️  Limited functionality - see docs for missing wheels")
        print("=" * 50)
    else:
        print("❌ Flow execution: FAILED")
        print("Manual troubleshooting may be required")
    
    print("\n📝 Usage Instructions:")
    print("1. Always set PYTHONPATH before using Prefect:")
    print('   export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"')
    print("2. Import and use Prefect normally:")
    print("   from prefect import flow, task")
    print("3. Create and run basic workflows")
    print("\n⚠️  LIMITATIONS:")
    print("   • Advanced database features may fail (missing asyncpg, cryptography)")
    print("   • Date parsing limited (missing dateparser, regex)")
    print("   • Performance may be reduced (missing orjson)")
    print("   • See WHEEL-BUILD-INSTRUCTIONS.md for complete wheel list")


if __name__ == "__main__":
    main()