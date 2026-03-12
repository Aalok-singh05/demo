from fastapi import FastAPI

app = FastAPI(
    title="Nexus Event AI System",
    version="1.0"
)


@app.get("/")
def root():
    return {"message": "Nexus backend running"}