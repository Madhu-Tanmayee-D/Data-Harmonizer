import os
import re

def find_model_initialization():
    print(f"--- Searching for SentenceTransformer initialization ---\n")
    found = False
    
    # Pattern to find 'SentenceTransformer(' followed by the model name
    pattern = re.compile(r"SentenceTransformer\s*\(\s*['\"]([^'\"]+)['\"]")
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for match in matches:
                            print(f"FOUND: Model '{match}' initialized in file: {path}")
                            found = True
                except Exception:
                    pass
    
    if not found:
        print("No SentenceTransformer initialization found. The model might be loaded via a dynamic config or API call.")

if __name__ == "__main__":
    find_model_initialization()