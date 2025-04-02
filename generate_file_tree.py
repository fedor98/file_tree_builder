#!/usr/bin/env python3
import os

def load_list(env_value):
    """
    If env_value is a path to an existing file, read its lines as a set.
    Otherwise, assume it's a comma-separated list and split accordingly.
    """
    if not env_value:
        return set()
    if os.path.isfile(env_value):
        with open(env_value, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    return {item.strip() for item in env_value.split(',') if item.strip()}

def build_tree_string(root, hide_folders):
    """Recursively builds a tree-like string from the given root,
    skipping any directory whose name is in hide_folders."""
    tree_lines = []
    
    def _walk(dir_path, prefix=""):
        try:
            entries = sorted(os.listdir(dir_path))
        except Exception as e:
            tree_lines.append(f"{prefix}[Error reading directory: {e}]")
            return
        # Filter out directories that should be hidden.
        filtered_entries = []
        for entry in entries:
            full_path = os.path.join(dir_path, entry)
            # If entry is a directory and its name is in hide_folders, skip it.
            if os.path.isdir(full_path) and entry in hide_folders:
                continue
            filtered_entries.append(entry)
        for i, entry in enumerate(filtered_entries):
            full_path = os.path.join(dir_path, entry)
            connector = "└── " if i == len(filtered_entries) - 1 else "├── "
            tree_lines.append(f"{prefix}{connector}{entry}")
            if os.path.isdir(full_path):
                extension = "    " if i == len(filtered_entries) - 1 else "│   "
                _walk(full_path, prefix + extension)
    
    tree_lines.append(root)
    _walk(root)
    return "\n".join(tree_lines)

def process_files(root, private_files, exclude_folders, hide_folders):
    """
    Recursively processes files under root.
    For each file, it outputs the relative path and:
      - If any folder in its path is in exclude_folders or hide_folders,
        it outputs “[Content is excluded]”.
      - Otherwise, if the file is in private_files, it outputs “[Content is private]”.
      - Else, it outputs the file's content.
    """
    file_contents = []
    for current_dir, _, files in os.walk(root):
        for file in sorted(files):
            file_path = os.path.join(current_dir, file)
            relative_path = os.path.relpath(file_path, root)
            file_contents.append(f"\n{relative_path}:\n")
            
            # Check if any folder in the file's relative path is in exclude_folders or hide_folders.
            folder_components = os.path.dirname(relative_path).split(os.sep)
            if any(comp in exclude_folders or comp in hide_folders for comp in folder_components if comp):
                file_contents.append("[Content is excluded]\n")
            elif file in private_files or file_path in private_files:
                file_contents.append("[Content is private]\n")
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents.append(f.read() + "\n")
                except Exception as e:
                    file_contents.append(f"[Error reading file: {e}]\n")
    return "\n".join(file_contents)

def main():
    # Read configuration from environment variables.
    folder = os.environ.get("FOLDER")
    private_list_env = os.environ.get("PRIVATE_LIST")
    exclude_folders_env = os.environ.get("EXCLUDE_FOLDERS")
    hide_folders_env = os.environ.get("HIDE_FOLDERS")
    output_path = os.environ.get("OUTPUT", "output.txt")
    
    if not folder:
        print("Error: FOLDER environment variable not set.")
        exit(1)
    
    if not os.path.isdir(folder):
        print(f"Error: The folder '{folder}' does not exist or is not a directory.")
        exit(1)
    
    private_files = load_list(private_list_env)
    exclude_folders = load_list(exclude_folders_env)
    hide_folders = load_list(hide_folders_env)
    
    # Generate the file tree (hiding folders specified in HIDE_FOLDERS).
    tree_str = build_tree_string(folder, hide_folders)
    # Process file contents.
    contents_str = process_files(folder, private_files, exclude_folders, hide_folders)
    
    # Combine both outputs into one file.
    with open(output_path, 'w', encoding='utf-8') as out_file:
        out_file.write("FILE TREE:\n")
        out_file.write(tree_str)
        out_file.write("\n\nFILE CONTENTS:\n")
        out_file.write(contents_str)
    
    print(f"Output written to {output_path}")

if __name__ == '__main__':
    main()
