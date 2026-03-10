# agent_runtime/src/migrationmind_agents/contracts.py

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- Agent 1: Surveyor ---
class SurveyorOutput(BaseModel):
    applications: List[str]
    dependency_graph: Dict[str, Any]
    azure_regions_verified: List[str]
    total_current_monthly_cost_usd: float
    summary: str

# --- Agent 2: Architect ---
class Wave(BaseModel):
    wave_number: int
    name: str
    duration_days: int
    assets: List[str]
    reasoning: str

class ArchitectOutput(BaseModel):
    total_waves: int
    waves: List[Wave]
    critical_path: List[str]
    total_estimated_days: int
    summary: str

# --- Agent 3: Accountant ---
class WaveCost(BaseModel):
    wave_number: int
    current_monthly_cost: float
    projected_monthly_cost: float
    estimated_savings: float
    pricing_source: str

class TotalBusinessCase(BaseModel):
    roi_month: int
    three_year_npv: float

class AccountantOutput(BaseModel):
    per_wave_costs: List[WaveCost]
    total_business_case: TotalBusinessCase
    summary: str

# --- Agent 4: Risk Officer ---
class RiskCard(BaseModel):
    wave_number: int
    risk_type: str
    description: str
    is_blocking: bool
    remediation_plan: str

class RiskOfficerOutput(BaseModel):
    wave_risk_cards: List[RiskCard]
