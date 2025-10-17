"""
Simple script to run the FastAPI application
Usage: python3 run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7878,
        reload=True,
    )
