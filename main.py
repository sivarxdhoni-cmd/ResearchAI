import sys
import os

# Ensure the project root folder is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Expose the FastAPI ASGI application from our backend package
from backend.run import app

if __name__ == "__main__":
    import uvicorn
    # This enables running 'py main.py' from the project root directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
