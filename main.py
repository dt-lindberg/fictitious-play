import os
import subprocess

def main():
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, "outputs")
    mega_parquet_path = os.path.join(outputs_dir, "mega.parquet")
     
    # Launch the dashboard
    print("Launching the interactive dashboard...")
    try:
        subprocess.run([
            "python", 
            os.path.join(script_dir, "gui", "app.py"), 
            "--output_file", mega_parquet_path
        ])
    except Exception as e:
        print(f"Error launching dashboard: {e}"
              "Try to run the following command:"
              "python gui/app.py --output_file 'outputs/mega.parquet'")

if __name__ == "__main__":
    main()