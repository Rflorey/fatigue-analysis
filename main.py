from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Create FastAPI app
app = FastAPI(title="Fatigue Analysis API", version="1.0.0")

# Data models for requests/responses
class FatigueInput(BaseModel):
    stress_amplitude: float  # MPa
    mean_stress: float      # MPa
    cycles: int
    material: str           # e.g., "steel", "aluminum"
    safety_factor: Optional[float] = 2.0

class FatigueResult(BaseModel):
    cycles_to_failure: int
    safety_margin: float
    is_safe: bool
    analysis_method: str

# Simple fatigue analysis function (placeholder - replace with your actual analysis)
def analyze_fatigue(data: FatigueInput) -> FatigueResult:
    """
    Simple fatigue analysis using basic S-N curve approach
    Replace this with your actual fatigue analysis logic
    """
    
    # Basic material properties (simplified)
    material_props = {
        "steel": {"endurance_limit": 200, "fatigue_strength_coeff": 900},
        "aluminum": {"endurance_limit": 130, "fatigue_strength_coeff": 620}
    }
    
    if data.material.lower() not in material_props:
        raise ValueError(f"Material '{data.material}' not supported")
    
    props = material_props[data.material.lower()]
    
    # Simple Goodman correction for mean stress
    equivalent_stress = data.stress_amplitude / (1 - data.mean_stress / props["fatigue_strength_coeff"])
    
    # Basic S-N curve calculation (simplified)
    if equivalent_stress <= props["endurance_limit"]:
        cycles_to_failure = 10_000_000  # Infinite life
    else:
        # Simple power law relationship
        cycles_to_failure = int((props["fatigue_strength_coeff"] / equivalent_stress) ** 3 * 1000)
    
    safety_margin = cycles_to_failure / data.cycles
    is_safe = safety_margin >= data.safety_factor
    
    return FatigueResult(
        cycles_to_failure=cycles_to_failure,
        safety_margin=safety_margin,
        is_safe=is_safe,
        analysis_method="Simplified S-N Curve with Goodman Correction"
    )

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Fatigue Analysis API is running"}

@app.post("/analyze", response_model=FatigueResult)
async def run_fatigue_analysis(input_data: FatigueInput):
    """
    Run fatigue analysis on provided data
    """
    try:
        result = analyze_fatigue(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/supported_materials")
async def get_supported_materials():
    """
    Get list of supported materials
    """
    return {"materials": ["steel", "aluminum"]}

# Batch analysis endpoint
@app.post("/analyze_batch", response_model=List[FatigueResult])
async def run_batch_analysis(input_data: List[FatigueInput]):
    """
    Run fatigue analysis on multiple datasets
    """
    results = []
    for i, data in enumerate(input_data):
        try:
            result = analyze_fatigue(data)
            results.append(result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in dataset {i+1}: {str(e)}")
    
    return results

# Run the server
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)