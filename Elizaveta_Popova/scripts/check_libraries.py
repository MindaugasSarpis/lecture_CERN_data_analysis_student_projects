import subprocess, sys

libs = ['pandas', 'matplotlib', 'numpy', 'requests']

print("Checking libraries...")
for lib in libs:
    try:
        __import__(lib)
        print(f"You already have {lib}, great...")
    except ImportError:
        print(f"Installing {lib} rn, please wait...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

print("Done, ready to go!")