from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Shared state reflecting your keys ===
shared_state = {
    "mode": "NA",       # e.g., "idle", "training", "active"
    "section": "NA",    # e.g., "grabbing", "holding"
    "request": "NA"     # e.g., command/request to Arduino
}


# === POST endpoint to update mode ===
@app.post("/set_mode/{value}")
def set_mode(value: str):
    shared_state["mode"] = value
    return {"message": f"Mode set to '{value}'"}

# === POST endpoint to update section ===
@app.post("/set_section/{value}")
def set_section(value: str):
    shared_state["section"] = value
    return {"message": f"Section set to '{value}'"}

# === POST endpoint to update request ===
@app.post("/set_request/{value}")
def set_request(value: str):
    shared_state["request"] = value
    return {"message": f"Request set to '{value}'"}

# === POST endpoint to reset entire state ===
@app.post("/reset")
def reset_state():
    shared_state.update({
        "mode": "NA",
        "section": "NA",
        "request": "NA"
    })
    return {"message": "State reset to default"}

# === GET endpoint for a single variable ===
@app.get("/get/{variable}")
def get_variable(variable: str):
    if variable in shared_state:
        return {variable: shared_state[variable]}
    raise HTTPException(status_code=404, detail=f"Variable '{variable}' not found.")
