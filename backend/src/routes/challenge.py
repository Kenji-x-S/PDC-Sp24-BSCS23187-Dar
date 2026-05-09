from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_generator import generate_challenge_with_ai
from database.db import (
    get_challenge_quota,
    create_challenge,
    create_challenge_quota,
    reset_quota_if_needed,
    get_user_challenges
)
from utils import authenticate_and_get_user_details
from database.models import get_db
import json
from datetime import datetime

router = APIRouter()

class ChallengeRequest(BaseModel):
    difficulty: str

    class Config:
        json_schema_extra = {"example": {"difficulty": "easy"}}

@router.post("/generate-challenge")
async def generate_challenge(request: ChallengeRequest, request_obj: Request, db: Session = Depends(get_db)):

    breaker = request_obj.app.state.llm_breaker

    if not breaker.check_state():
        raise HTTPException(
            status_code=503, 
            detail="Fallback: AI Service is temporarily overloaded. Please try again later."
        )


    # --- TEMPORARILY BYPASSED FOR VIDEO DEMO ---
    user_id = "test_demo_user"
    
    """
    try:
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = user_details.get("user_id")

        quota = get_challenge_quota(db, user_id)
        if not quota:
            quota = create_challenge_quota(db, user_id)

        quota = reset_quota_if_needed(db, quota)

        if quota.quota_remaining <= 0:
            raise HTTPException(status_code=429, detail="Quota exhausted")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth/Quota Error: {str(e)}")
    """


    try:
        # TEMPORARILY COMMENTED OUT THE REAL CALL:
        # challenge_data = generate_challenge_with_ai(request.difficulty)
        
        # ADDED THIS TO FAKE A CRASH:
        raise Exception("Simulated AI API Timeout")
        
        breaker.record_success()
        
    except Exception as llm_error:
        breaker.record_failure()
        raise HTTPException(
            status_code=503, 
            detail="External AI API is unresponsive."
        )

    try:
        new_challenge = create_challenge(
            db=db,
            difficulty=request.difficulty,
            created_by=user_id,
            title=challenge_data["title"],
            options=json.dumps(challenge_data["options"]),
            correct_answer_id=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"]
        )

        quota.quota_remaining -= 1
        db.commit()

        return {
            "id": new_challenge.id,
            "difficulty": request.difficulty,
            "title": new_challenge.title,
            "options": json.loads(new_challenge.options),
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explanation,
            "timestamp": new_challenge.date_created.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-history")
async def my_history(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")

    challenges = get_user_challenges(db, user_id)
    return {"challenges": challenges}


@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")

    quota = get_challenge_quota(db, user_id)
    if not quota:
        return {
            "user_id": user_id,
            "quota_remaining": 0,
            "last_reset_date": datetime.now()
        }

    quota = reset_quota_if_needed(db, quota)
    return quota