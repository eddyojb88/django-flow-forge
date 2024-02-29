import os

def count_lines_of_code(directory, file_extensions=('.py',)):
    total_lines = 0
    total_files = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extensions):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Count non-empty lines
                    non_empty_lines = [line for line in lines if line.strip()]
                    total_lines += len(non_empty_lines)
                    total_files += 1

    return total_files, total_lines

# Specify the root directory of your project
project_directory = '.'
total_files, total_lines = count_lines_of_code(project_directory)
print(f"Total files: {total_files}, Total lines of code: {total_lines}")
