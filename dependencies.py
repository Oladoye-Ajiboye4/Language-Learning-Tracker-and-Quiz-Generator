import sys
import subprocess

def install_packages():
    """Ensure required packages are installed, with error handling."""
    required_packages = {
        'wordfreq': 'wordfreq',
        'nltk': 'nltk'
    }
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)  # Check if the package is installed
        except ImportError:
            print('Internet connection is required to install the programme dependencies\n')
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{package} installed successfully!\n")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install it manually using:")
                print(f"pip install {package}\n")
                sys.exit(1)  # Stop execution if installation fail
                
