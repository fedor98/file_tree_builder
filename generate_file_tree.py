#!/usr/bin/env python3
import os

def load_private_list(env_value):
    """
    If env_value is a path to a file, read and return its contents as a set.
    Otherwise, assume it is a comma-separated list of file names and return that as a set.
    """
    if not env_value:
        return set()
    if os.path.isfile(env_value):
        with open(env_value, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    # Split the string by commas and strip extra whitespace.
    return {item.strip() for item in env_value.split(',') if item.strip()}

def build_tree_string(root):
    """Recursively builds a tree-like string from the given root."""
    tree_lines = []
    
    def _walk(dir_path, prefix=""):
        entries = sorted(os.listdir(dir_path))
        for i, entry in enumerate(entries):
            path = os.path.join(dir_path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            tree_lines.append(f"{prefix}{connector}{entry}")
            if os.path.isdir(path):
                extension = "    " if i == len(entries) - 1 else "│   "
                _walk(path, prefix + extension)
    
    tree_lines.append(root)
    _walk(root)
    return "\n".join(tree_lines)

def process_files(root, private_files):
    """
    Walks through the folder recursively.
    For each file, appends its relative path and either the file's content or a private placeholder.
    """
    file_contents = []
    for current_dir, _, files in os.walk(root):
        for file in sorted(files):
            file_path = os.path.join(current_dir, file)
            relative_path = os.path.relpath(file_path, root)
            file_contents.append(f"\n{relative_path}:\n")
            # If the file name (or full path) is in the private list, mark as private.
            if file in private_files or file_path in private_files:
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
    output_path = os.environ.get("OUTPUT", "output.txt")
    
    if not folder:
        print("Error: FOLDER environment variable not set.")
        exit(1)
    
    if not os.path.isdir(folder):
        print(f"Error: The folder '{folder}' does not exist or is not a directory.")
        exit(1)
    
    private_files = load_private_list(private_list_env)
    
    # Generate the file tree and file content outputs.
    tree_str = build_tree_string(folder)
    contents_str = process_files(folder, private_files)
    
    # Combine both outputs into one file.
    with open(output_path, 'w', encoding='utf-8') as out_file:
        out_file.write("FILE TREE:\n")
        out_file.write(tree_str)
        out_file.write("\n\nFILE CONTENTS:\n")
        out_file.write(contents_str)
    
    print(f"Output written to {output_path}")

if __name__ == '__main__':
    main()
