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
    version="2.0.0"
)

# Allow access from iOS app + HTML dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML/CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------------------
# Data Models
# -----------------------------------------------------
class Driver(BaseModel):
    id: int
    name: str
    current_location: Optional[str] = None
    phone: Optional[str] = None
    vehicle_type: Optional[str] = None


class DriverCreate(BaseModel):
    name: str
    current_location: Optional[str] = None
    phone: Optional[str] = None
    vehicle_type: Optional[str] = None


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


# -----------------------------------------------------
# In-Memory Data (Temporary Until DB Integration)
# -----------------------------------------------------
drivers = [
    Driver(id=1, name="John Doe", current_location="Seattle", phone="555-1234", vehicle_type="Box Truck"),
    Driver(id=2, name="Sarah Lee", current_location="Bellevue", phone="555-5678", vehicle_type="Dry Van"),
]

jobs = [
    Job(id=1, pickup_location="Amazon SODO", dropoff_location="Bellevue Downtown",
        load_description="Pallet of boxes", status="available"),
    Job(id=2, pickup_location="Port of Seattle Terminal 18", dropoff_location="Redmond Microsoft Campus",
        load_description="Electronics container", status="available"),
]

next_job_id = 3
next_driver_id = 3


# -----------------------------------------------------
# Routes / API Endpoints
# -----------------------------------------------------

@app.get("/")
def home():
    return {"message": "Last-Mile Logistics API is live!"}


# -----------------------------
# DRIVERS
# -----------------------------

@app.get("/drivers", response_model=List[Driver])
def get_drivers():
    return drivers


@app.post("/drivers", response_model=Driver)
def create_driver(driver: DriverCreate):
    global next_driver_id

    new_driver = Driver(
        id=next_driver_id,
        name=driver.name,
        current_location=driver.current_location or "Unknown",
        phone=driver.phone,
        vehicle_type=driver.vehicle_type
    )

    drivers.append(new_driver)
    next_driver_id += 1
    return new_driver


# -----------------------------
# JOBS
# -----------------------------

@app.get("/jobs", response_model=List[Job])
def get_jobs():
    return jobs


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


@app.post("/assign/{job_id}/{driver_id}")
def assign_driver(job_id: int, driver_id: int):
    for job in jobs:
        if job.id == job_id:
            job.status = "assigned"
            job.driver_id = driver_id
            return {"message": "Driver assigned", "job": job}

    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/complete/{job_id}")
def complete_job(job_id: int):
    for job in jobs:
        if job.id == job_id:
            job.status = "completed"
            return {"message": "Job completed", "job": job}

    raise HTTPException(status_code=404, detail="Job not found")


# -----------------------------------------------------
# HTML Dashboards
# -----------------------------------------------------

@app.get("/shipper")
def shipper_dashboard():
    return FileResponse("static/shipper_dashboard.html")


@app.get("/admin")
def admin_dashboard():
    return FileResponse("static/admin_dashboard.html")
