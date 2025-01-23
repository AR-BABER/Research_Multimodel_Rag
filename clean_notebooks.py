import json
import re
import glob
import nbformat

def clean_api_keys(notebook_path):
    """Clean API keys from Jupyter notebook and replace with env vars."""
    
    # Common API key patterns
    api_key_patterns = [
        (r'api_key\s*=\s*["\']sk-[a-zA-Z0-9]{48}["\']', 'api_key=os.getenv("OPENAI_API_KEY")'),
        (r'api_key\s*:\s*["\']sk-[a-zA-Z0-9]{48}["\']', 'api_key: os.getenv("OPENAI_API_KEY")'),
        (r'["\']sk-[a-zA-Z0-9]{48}["\']', 'os.getenv("OPENAI_API_KEY")')
    ]
    
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Track if we made any changes
    changes_made = False
    env_vars_added = False
    
    # Process each cell
    for cell in notebook.cells:
        if cell.cell_type == "code":
            original_source = cell.source
            modified_source = cell.source
            
            # Apply each pattern
            for pattern, replacement in api_key_patterns:
                if re.search(pattern, modified_source):
                    modified_source = re.sub(pattern, replacement, modified_source)
                    changes_made = True
            
            # If we made changes and haven't added env vars import
            if changes_made and not env_vars_added:
                # Add imports if they don't exist
                imports = "import os\nfrom dotenv import load_dotenv\n\nload_dotenv()  # Load environment variables\n\n"
                if "import os" not in modified_source and "from dotenv" not in modified_source:
                    modified_source = imports + modified_source
                    env_vars_added = True
            
            cell.source = modified_source
    
    if changes_made:
        # Save the modified notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
        print(f"Cleaned API keys from {notebook_path}")
        return True
    
    print(f"No API keys found in {notebook_path}")
    return False

def process_all_notebooks(directory="."):
    """Process all notebooks in the given directory."""
    notebooks = glob.glob(f"{directory}/**/*.ipynb", recursive=True)
    cleaned_count = 0
    
    for notebook_path in notebooks:
        if clean_api_keys(notebook_path):
            cleaned_count += 1
    
    print(f"\nProcessed {len(notebooks)} notebooks, cleaned {cleaned_count} files")

# Run the script
if __name__ == "__main__":
    print("Starting API key cleanup...")
    process_all_notebooks()
    print("\nDone! Don't forget to:")
    print("1. Create a .env file with your API keys")
    print("2. Add .env to your .gitignore")