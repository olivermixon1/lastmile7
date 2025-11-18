from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


# -----------------------------------------------------
# FastAPI App Setup
# -----------------------------------------------------
app = FastAPI(
    title="Last-Mile Logistics API",
    description="Backend API for connecting autonomous trucking companies with local truckers.",
    version="1.0.0"
)

# Allow access from anywhere (iOS app, HTML dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve files in /static (HTML, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------------------
# Data Models
# -----------------------------------------------------
class Job(BaseModel):
    id: int
    pickup_location: str
    dropoff_location: str
    load_description: str
    status: str  # available, assigned, completed
    driver_id: Optional[int] = None

    # Optional job details
    weight: Optional[str] = None
    equipment_type: Optional[str] = None
    delivery_window: Optional[str] = None
    contact_phone: Optional[str] = None
    price_offered: Optional[float] = None


class JobCreate(BaseModel):
    pickup_location: str
    dropoff_location: str
    load_description: str
    weight: Optional[str] = None
    equipment_type: Optional[str] = None
    delivery_window: Optional[str] = None
    contact_phone: Optional[str] = None
    price_offered: Optional[float] = None


class Driver(BaseModel):
    id: int
    name: str
    current_location: str


# -----------------------------------------------------
# In-Memory Data
# -----------------------------------------------------
drivers = [
    Driver(id=1, name="John Doe", current_location="Seattle"),
    Driver(id=2, name="Sarah Lee", current_location="Bellevue"),
]

jobs = [
    Job(id=1, pickup_location="Amazon SODO", dropoff_location="Bellevue Downtown", load_description="Pallet of boxes", status="available"),
    Job(id=2, pickup_location="Port of Seattle Terminal 18", dropoff_location="Redmond Microsoft Campus", load_description="Electronics container", status="available"),
]

next_job_id = 3  # auto-increment ID for new jobs


# -----------------------------------------------------
# Routes / API Endpoints
# -----------------------------------------------------

@app.get("/")
def home():
    return {"message": "Last-Mile Logistics API is live!"}


# Get all jobs
@app.get("/jobs", response_model=List[Job])
def get_jobs():
    return jobs


# Create a new job
@app.post("/jobs", response_model=Job)
def create_job(job: JobCreate):
    global next_job_id

    new_job = Job(
        id=next_job_id,
        pickup_location=job.pickup_location,
        dropoff_location=job.dropoff_location,
        load_description=job.load_description,
        status="available",
        driver_id=None,
        weight=job.weight,
        equipment_type=job.equipment_type,
        delivery_window=job.delivery_window,
        contact_phone=job.contact_phone,
        price_offered=job.price_offered
    )

    jobs.append(new_job)
    next_job_id += 1

    return new_job


# Get all drivers
@app.get("/drivers", response_model=List[Driver])
def get_drivers():
    return drivers


# Assign a driver to a job
@app.post("/assign/{job_id}/{driver_id}")
def assign_driver(job_id: int, driver_id: int):
    for job in jobs:
        if job.id == job_id:
            job.status = "assigned"
            job.driver_id = driver_id
            return {"message": "Driver assigned", "job": job}

    raise HTTPException(status_code=404, detail="Job not found")


# Mark job as completed
@app.post("/complete/{job_id}")
def complete_job(job_id: int):
    for job in jobs:
        if job.id == job_id:
            job.status = "completed"
            return {"message": "Job completed", "job": job}

    raise HTTPException(status_code=404, detail="Job not found")


# Serve the shipper dashboard HTML form
@app.get("/shipper")
def shipper_dashboard():
    return FileResponse("static/shipper_dashboard.html")
