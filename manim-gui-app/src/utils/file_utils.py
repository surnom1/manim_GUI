def load_project_file(file_path):
    """Load a project file and return its contents."""
    with open(file_path, 'r') as file:
        return file.read()

def save_project_file(file_path, content):
    """Save content to a project file."""
    with open(file_path, 'w') as file:
        file.write(content)

def list_files_in_directory(directory_path):
    """Return a list of files in the specified directory."""
    import os
    return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

def create_directory(directory_path):
    """Create a directory if it does not exist."""
    import os
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)