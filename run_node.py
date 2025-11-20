import uvicorn

if __name__ == "__main__":
    print("--- STARTING ILC NODE DAEMON ---")
    print("API available at http://127.0.0.1:8000")
    print("Docs available at http://127.0.0.1:8000/docs")
    
    # Run the FastAPI app from the ilc_core.server module
    uvicorn.run("ilc_core.server:app", host="127.0.0.1", port=8000, reload=True)
