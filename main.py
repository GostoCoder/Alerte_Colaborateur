from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from crud_1 import (
    create_collaborateur,
    get_collaborateur,
    get_collaborateurs,
    update_collaborateur,
    delete_collaborateur,
    get_db
)
from models_1 import Collaborateur
from inspection_notifications_1 import check_inspection_dates
import threading
import schedule
import time
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI(
    title="Collaborateurs API",
    description="API for managing collaborateurs and sending notifications.",
    version="1.0.0"
)

# Allow CORS for all origins (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start daily notification scheduler in a background thread
def run_scheduler():
    def job():
        try:
            check_inspection_dates()
        except Exception as e:
            print(f"Scheduled notification error: {e}")

    # Schedule the job every day at 8:00 Europe/Paris time
    schedule.every().day.at("08:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(30)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Pydantic models
class CollaborateurBase(BaseModel):
    nom: str = Field(..., example="Dupont")
    prenom: str = Field(..., example="Jean")
    ifo: Optional[str] = Field(None, example="2025-01-01")
    caces: Optional[str] = Field(None, example="2025-01-01")
    airr: Optional[str] = Field(None, example="2025-01-01")
    hgo_bo: Optional[str] = Field(None, example="2025-01-01")
    visite_med: Optional[str] = Field(None, example="2025-01-01")
    brevet_secour: Optional[str] = Field(None, example="2025-01-01")

class CollaborateurCreate(CollaborateurBase):
    pass

class CollaborateurUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    ifo: Optional[str] = None
    caces: Optional[str] = None
    airr: Optional[str] = None
    hgo_bo: Optional[str] = None
    visite_med: Optional[str] = None
    brevet_secour: Optional[str] = None

class CollaborateurResponse(CollaborateurBase):
    id: int

    class Config:
        orm_mode = True

# Dependency for DB session
def get_db_dep():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

# Manual notification trigger endpoint
@app.post("/notifications/send", status_code=200)
def send_notifications():
    try:
        check_inspection_dates()
        return {"detail": "Notifications sent (if any were due)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification error: {e}")

# POST /collaborateurs : Add a collaborator
@app.post("/collaborateurs", response_model=CollaborateurResponse, status_code=status.HTTP_201_CREATED)
def add_collaborateur(collab: CollaborateurCreate, db: Session = Depends(get_db_dep)):
    try:
        db_collab = create_collaborateur(
            db,
            nom=collab.nom,
            prenom=collab.prenom,
            ifo=collab.ifo,
            caces=collab.caces,
            airr=collab.airr,
            hgo_bo=collab.hgo_bo,
            visite_med=collab.visite_med,
            brevet_secour=collab.brevet_secour
        )
        return db_collab
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collaborateur: {str(e)}")

# GET /collaborateurs : List collaborators
@app.get("/collaborateurs", response_model=List[CollaborateurResponse])
def list_collaborateurs(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    direction: str = "asc",
    db: Session = Depends(get_db_dep)
):
    try:
        collaborateurs = get_collaborateurs(db, skip, limit, search, sort_by, direction)
        return collaborateurs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing collaborateurs: {str(e)}")

# GET /collaborateurs/{id} : Get collaborator details
@app.get("/collaborateurs/{id}", response_model=CollaborateurResponse)
def get_collaborateur_detail(id: int, db: Session = Depends(get_db_dep)):
    db_collab = get_collaborateur(db, id)
    if not db_collab:
        raise HTTPException(status_code=404, detail="Collaborateur not found")
    return db_collab

# PUT /collaborateurs/{id} : Update a collaborator
@app.put("/collaborateurs/{id}", response_model=CollaborateurResponse)
def update_collaborateur_detail(id: int, collab: CollaborateurUpdate, db: Session = Depends(get_db_dep)):
    db_collab = update_collaborateur(
        db,
        collaborateur_id=id,
        nom=collab.nom,
        prenom=collab.prenom,
        ifo=collab.ifo,
        caces=collab.caces,
        airr=collab.airr,
        hgo_bo=collab.hgo_bo,
        visite_med=collab.visite_med,
        brevet_secour=collab.brevet_secour
    )
    if not db_collab:
        raise HTTPException(status_code=404, detail="Collaborateur not found")
    return db_collab

# DELETE /collaborateurs/{id} : Delete a collaborator
@app.delete("/collaborateurs/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collaborateur_detail(id: int, db: Session = Depends(get_db_dep)):
    success = delete_collaborateur(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Collaborateur not found")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})

# GET /notifications/send : Manually trigger notification sending
@app.get("/notifications/send")
def send_notifications():
    try:
        check_inspection_dates()
        return {"message": "Notifications sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending notifications: {str(e)}")
