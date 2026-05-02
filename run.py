# run.py
import sys
import subprocess
import os

def print_menu():
    print("="*50)
    print("BI DASHBOARD")
    print("="*50)
    print("\nOptions:")
    print("  1. Run Pipeline Only (generate data + calculate measures)")
    print("  2. Run Dashboard Only (show existing data)")
    print("  3. Run Performance Benchmark (test 40% improvement)")
    print("  4. Run Pipeline + Dashboard")
    print("  5. Run All Tests")
    print("  6. Exit")
    print("-"*50)

def run_pipeline():
    print("\nRunning pipeline...")
    subprocess.run([sys.executable, "-c", 
                    "from src.pipeline import BIPipeline; BIPipeline().run_complete_pipeline()"])

def run_dashboard():
    print("\nStarting dashboard...")
    print("Dashboard will open at http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/dashboard.py"])

def run_performance():
    print("\nRunning performance benchmark...")
    subprocess.run([sys.executable, "src/performance.py"])

def run_tests():
    print("\nRunning all tests...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])

def main():
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            run_pipeline()
        elif choice == '2':
            run_dashboard()
        elif choice == '3':
            run_performance()
        elif choice == '4':
            run_pipeline()
            print("\n" + "="*50)
            run_dashboard()
        elif choice == '5':
            run_tests()
        elif choice == '6':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter 1-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
