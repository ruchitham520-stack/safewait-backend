from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from math import radians, sin, cos, sqrt, atan2

app = FastAPI(title="SafeWait Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DEMO DATA — replace with verified local records later.
PLACES = [
    {
        "id": 1,
        "name": "Central Bus Stop",
        "category": "Bus Stop",
        "latitude": 12.3375,
        "longitude": 76.6195,
        "cctv": "unknown",
        "streetlight": "unknown",
        "rating": None,
        "reports": 0,
        "data_label": "Demo data - not verified"
    },
    {
        "id": 2,
        "name": "Main Market",
        "category": "Market",
        "latitude": 12.3400,
        "longitude": 76.6200,
        "cctv": "unknown",
        "streetlight": "unknown",
        "rating": None,
        "reports": 0,
        "data_label": "Demo data - not verified"
    },
    {
        "id": 3,
        "name": "City Park",
        "category": "Park",
        "latitude": 12.3330,
        "longitude": 76.6250,
        "cctv": "unknown",
        "streetlight": "unknown",
        "rating": None,
        "reports": 0,
        "data_label": "Demo data - not verified"
    }
]

def distance_km(lat1, lon1, lat2, lon2):
    earth_radius = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )
    return earth_radius * 2 * atan2(sqrt(a), sqrt(1 - a))

@app.get("/")
def home():
    return {"message": "SafeWait backend is running"}

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/nearby")
def nearby(lat: float, lon: float, radius: int = 2000):
    results = []

    for place in PLACES:
        distance = distance_km(
            lat, lon,
            place["latitude"], place["longitude"]
        ) * 1000

        if distance <= radius:
            results.append({
                **place,
                "distance_m": round(distance)
            })

    return {
        "count": len(results),
        "places": results,
        "message": "Demo locations retrieved"
    }

@app.get("/places/{place_id}")
def place_details(place_id: int):
    for place in PLACES:
        if place["id"] == place_id:
            return place

    return {"error": "Place not found"}
    # ---------------- SAFETY REPORTS ----------------

SAFETY_REPORTS = []

@app.post("/report")
def submit_report(report: dict):
    required = ["place_id", "indicator", "status"]

    for field in required:
        if field not in report:
            raise HTTPException(
                status_code=400,
                detail=f"Missing field: {field}"
            )

    if report["indicator"] not in [
        "cctv", "streetlight", "safety_concern"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid indicator"
        )

    if report["status"] not in [
        "available", "unavailable", "reported"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    new_report = {
        "id": len(SAFETY_REPORTS) + 1,
        "place_id": report["place_id"],
        "indicator": report["indicator"],
        "status": report["status"],
        "description": report.get("description", ""),
        "verification": "pending"
    }

    SAFETY_REPORTS.append(new_report)

    return {
        "message": "Report submitted for admin verification",
        "report": new_report
    }


@app.get("/reports")
def get_reports():
    return SAFETY_REPORTS


@app.post("/reports/{report_id}/verify")
def verify_report(report_id: int):
    for report in SAFETY_REPORTS:
        if report["id"] == report_id:
            report["verification"] = "verified"
            return {
                "message": "Report verified",
                "report": report
            }

    raise HTTPException(
        status_code=404,
        detail="Report not found"
    )