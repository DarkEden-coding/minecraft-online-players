import subprocess
import time


def run_target_file(file_path):
    try:
        # Attempt to run the target Python file
        subprocess.run(['python', file_path], check=True)
    except Exception as e:
        # If an error occurs, print the error message and rerun the target file
        print(f"Error occurred: {e}")
        print("Rerunning the target file...")
        time.sleep(2)  # Optional: Add a delay before rerunning to avoid rapid retries
        run_target_file(file_path)


# Replace 'your_target_file.py' with the actual name of your Python file
target_file_path = 'main.py'

# Run the target file
run_target_file(target_file_path)
