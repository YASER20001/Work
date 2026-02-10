"""Pydantic models for the P&ID Analyzer API."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    session_id: str
    question: str


class UploadResponse(BaseModel):
    status: str
    session_id: str
    filename: str
    message: str


class AnalysisProgress(BaseModel):
    current_phase: int
    total_phases: int
    phase_name: Optional[str] = None


class StatusResponse(BaseModel):
    session_id: str
    status: str
    progress: Optional[AnalysisProgress] = None
    has_results: bool


class QueryResponse(BaseModel):
    question: str
    answer: str
    session_id: str


class PhaseResult(BaseModel):
    result: Any
    raw: str
    timestamp: str


class AnalysisResults(BaseModel):
    phases: Dict[str, PhaseResult]
    statistics: Dict[str, int]
    errors: List[Dict[str, str]]
    confidence: int
    start_time: str
    end_time: Optional[str] = None
