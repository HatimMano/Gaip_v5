from fastapi import APIRouter
from dependencies import get_state_machine

router = APIRouter()
state_machine = get_state_machine()

@router.get("/training/status")
async def get_training_status():
    if state_machine.num_episodes_completed > 0:
        average_reward = state_machine.total_reward / state_machine.num_episodes_completed
    else:
        average_reward = 0
    
    return {
        "current_episode": state_machine.current_episode,
        "average_reward": average_reward,
        "current_reward": state_machine.current_reward,
        "status": state_machine.state.value
    }
