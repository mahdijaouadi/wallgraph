from fastapi import APIRouter, HTTPException
from backend.src.adapters.outbound.agents.market_mind.workflow.graph import WorkFlow
from pydantic import BaseModel
router = APIRouter()



class MarketMindRequest(BaseModel):
    query: str

@router.post("/call_marketmind")
async def call_marketmind(request: MarketMindRequest):
    try:
        work_flow = WorkFlow(request=request)
        await work_flow(request=request)
        state_values = work_flow.workflow.get_state(work_flow.config).values
        return {
            "agent_response": state_values.get("final_response",""),
            "status": "success",   
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to launch workflow: {str(e)}"
        )
        