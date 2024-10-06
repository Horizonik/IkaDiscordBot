import os

from utils.constants import BASE_DIR


def concat_files_in_directory(directory, exclude_dirs: set, exclude_files: set):
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to exclude unwanted directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        files[:] = [f for f in files if f not in exclude_files]

        for file_name in files:
            file_path = os.path.join(root, file_name)
            folder_hierarchy = file_path.replace(directory, '').lstrip(os.sep)

            # Check if the file is empty
            if os.path.getsize(file_path) == 0:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f"File: {folder_hierarchy}")
                    print("-" * 50)
                    print(f.read())
            except UnicodeDecodeError:
                # Skip non-UTF-8 files silently (no output)
                continue
            except Exception as e:
                print(f"An error occurred while reading {folder_hierarchy}: {e}")
            print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    concat_files_in_directory(
        BASE_DIR,
        {'venv', 'data', '__pycache__', '.git', 'utils', 'actions', '.github', '.idea'},
        {'.gitignore', 'LICENSE', 'file_concat.py', 'help.py'}
    )
