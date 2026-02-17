import os
import csv

source_dir = 'dataset'
output_file = 'dataset.csv'

# Ensure the output file is not in the source directory to avoid reading it if we run this multiple times
# (though here source is 'dataset' and output is in current dir, so it's fine)

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'content'])

    # Get all files in the directory
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith('.md')]
    # Sort files to have a consistent order
    files.sort()

    for filename in files:
        filepath = os.path.join(source_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Remove extension for the name column
            name = os.path.splitext(filename)[0]
            
            writer.writerow([name, content])
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print(f"Successfully created {output_file}")
