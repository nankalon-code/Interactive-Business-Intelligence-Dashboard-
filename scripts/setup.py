# scripts/setup.py
import subprocess
import sys
import os
import shutil

def run_setup():
    """Complete setup for the BI dashboard project"""
    
    print("="*60)
    print("BI DASHBOARD SETUP")
    print("="*60)
    
    # Step 1: Install packages
    print("\n[1/5] Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("   Packages installed successfully")
    
    # Step 2: Create necessary directories
    print("\n[2/5] Creating directories...")
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('tests', exist_ok=True)
    print("   Directories created")
    
    # Step 3: Generate sample data
    print("\n[3/5] Generating sample data (6 sources)...")
    subprocess.check_call([sys.executable, "scripts/generate_data.py"])
    print("   Sample data generated")
    
    # Step 4: Create .env file if it doesn't exist
    print("\n[4/5] Creating configuration...")
    if not os.path.exists('.env'):
        shutil.copy('.env.example', '.env')
        print("   Created .env file from template")
    else:
        print("   .env file already exists")
    
    # Step 5: Run initial pipeline test
    print("\n[5/5] Testing pipeline...")
    result = subprocess.run([sys.executable, "-c", 
                            "from src.pipeline import BIPipeline; p = BIPipeline(); p.load_data(); print('   Pipeline test passed')"])
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nTo run the dashboard:")
    print("   python run.py")
    print("\nTo run tests:")
    print("   pytest tests/ -v")
    print("\nTo run performance benchmark:")
    print("   python src/performance.py")
    print("="*60)

if __name__ == "__main__":
    run_setup()
