import os
import glob
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import tempfile
import shutil

def combine_parquet_files(batch_size=200):
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all parquet files matching the pattern
    pattern = os.path.join(current_dir, "*_game_*.parquet")
    all_parquet_files = glob.glob(pattern)
    
    if not all_parquet_files:
        print("No matching parquet files found.")
        return
    
    total_files = len(all_parquet_files)
    print(f"Found {total_files} parquet files to combine.")
    
    # Output file path
    output_file = os.path.join(current_dir, "mega.parquet")
    
    # Process files in batches to avoid memory issues
    processed_files = []
    for i in range(0, total_files, batch_size):
        batch_files = all_parquet_files[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"Processing batch {batch_num} ({len(batch_files)} files)...")
        
        # Read this batch of parquet files
        dfs = []
        for file_path in batch_files:
            try:
                df = pd.read_parquet(file_path)
                dfs.append(df)
                processed_files.append(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if not dfs:
            print("No valid parquet files in this batch.")
            continue
        
        # Combine dataframes for this batch
        batch_df = pd.concat(dfs, ignore_index=True)
        print(f"Batch {batch_num} combined shape: {batch_df.shape}")
        
        # Write or append to the output file
        if i == 0:  # First batch
            batch_df.to_parquet(output_file, compression="snappy")
            print(f"Created {output_file} with first batch")
        else:  # Subsequent batches
            # Create a temporary file for the new combined data
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Read existing data
                existing_df = pd.read_parquet(output_file)
                
                # Combine with new batch
                combined_df = pd.concat([existing_df, batch_df], ignore_index=True)
                
                # Write combined data to temp file
                combined_df.to_parquet(temp_path, compression="snappy")
                
                # Replace original with new combined file
                shutil.move(temp_path, output_file)
                
                print(f"Appended batch {batch_num} to {output_file}")
                
                # Free memory
                del existing_df, combined_df
            except Exception as e:
                print(f"Error while appending batch {batch_num}: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Free memory
        del dfs, batch_df
    
    # Delete processed files after successful combination
    print(f"Deleting {len(processed_files)} processed files...")
    for file_path in processed_files:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    
    print(f"Operation completed successfully. All data combined into {output_file}")

if __name__ == "__main__":
    combine_parquet_files(batch_size=200)