import uvicorn
import sys
from pathlib import Path

# Ensure absolute import directories are properly resolved
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
workspace_root = backend_dir.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

if __name__ == "__main__":
    print("Starting Diyargezen Web Backend on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
