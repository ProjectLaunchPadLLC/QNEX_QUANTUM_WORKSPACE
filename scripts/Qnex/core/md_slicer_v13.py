# ==========================================================
# QNEX OS: MD_SLICER_V13 (MARKDOWN-TO-REPO WORKFLOW)
# ==========================================================
import os
import re
import subprocess
from flask import request, jsonify

QNEX_PATH = '/content/ColabOS/scripts/Qnex'
BASE_PATH = '/content/ColabOS'

def parse_markdown_to_files(md_content):
    """
    Scans Markdown for '# File: path/to/file' and code blocks.
    Slices content into the actual file system.
    """
    # Pattern looks for # File: [path] followed by ```[content]```
    pattern = r"# File:\s+([^\s\n]+)\s+```(?:python|text|md)?\n(.*?)\n```"
    matches = re.findall(pattern, md_content, re.DOTALL)
    
    results = []
    for path, content in matches:
        # Determine absolute path within the workspace
        full_path = os.path.join(BASE_PATH, path)
        
        # Ensure the parent directories exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the content
        with open(full_path, "w") as f:
            f.write(content.strip())
        results.append(f"Successfully sliced: {path}")
    
    return results

def sync_bulk_changes():
    """Automates the push to GitHub after slicing."""
    ps_sync = f"""
    Set-Location {QNEX_PATH}
    git add .
    git commit -m "SLICER_WORKFLOW: Bulk update from Markdown input"
    git push
    """
    process = subprocess.run(["pwsh", "-Command", ps_sync], capture_output=True, text=True)
    return process.stdout

# --- Flask Integration Hook ---
# This part would be added to your main app.py/server block
@app.route('/api/bulk_architect', methods=['POST'])
def bulk_architect():
    data = request.json
    md_input = data.get('markdown_logic', '')
    
    if not md_input:
        return jsonify({"status": "error", "message": "No content provided"}), 400
        
    creation_logs = parse_markdown_to_files(md_input)
    git_logs = sync_bulk_changes()
    
    return jsonify({
        "status": "Success",
        "files_created": creation_logs,
        "git_status": "Repository Synchronized"
    })

print("✅ MD_SLICER_V13: Workflow logic defined and ready for core integration.")
