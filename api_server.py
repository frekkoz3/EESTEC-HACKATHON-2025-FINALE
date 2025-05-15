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
    "mode": "NA",
    "section": "detect",
    "requests": "NA",
    "data": "NA"
}

# === Outline of all possible variables one can access or edit and their possible values ===
#     "mode": "NA", "grab", "train"
#     "section": "NA", "detected", "holding", "released" 
#     "request": "NA", "begin", "release"
#     "data": many things, like images or strings, handled case by case


# === POST endpoint to update mode ===
@app.post("/mode/{value}")
def set_mode(value: str):
    shared_state["mode"] = value
    return {"message": f"Mode set to '{value}'"}

# === POST endpoint to update section ===
@app.post("/section/{value}")
def set_section(value: str):
    shared_state["section"] = value
    return {"message": f"Section set to '{value}'"}

# === POST endpoint to update request ===
@app.post("/request/{value}")
def set_request(value: str):
    shared_state["request"] = value
    return {"message": f"Request set to '{value}'"}

# === POST endpoint to update data ===
@app.post("/data/{value}")
def set_data(value: str):
    shared_state["data"] = value
    return {"message": f"Data has ben set"}


# === POST endpoint to reset entire state ===
@app.post("/reset")
def reset_state():
    shared_state.update({
        "mode": "NA",
        "section": "NA",
        "request": "NA",
        "data": "NA"
    })
    return {"message": "State reset to default"}

# === GET endpoint for a single variable ===
@app.get("/{variable}")
def get_variable(variable: str):
    if variable in shared_state:
        return {variable: shared_state[variable]}
    raise HTTPException(status_code=404, detail=f"Variable '{variable}' not found.")
