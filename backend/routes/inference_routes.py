import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect #type: ignore
from core.state_machine import State
from dependencies import get_state_machine, get_env, get_agent

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for inference.
    Accepts a 'game' query parameter to determine the game.
    """
    await websocket.accept()
    game = websocket.query_params.get("game", "pong")
    state_machine = get_state_machine(game)
    env = get_env(game)
    agent = get_agent(game)
    
    if state_machine.state == State.TRAINING:
        await websocket.close(code=1000)
        return

    state_machine.set_state(State.INFERENCING)
    env.reset()
    state_machine.total_reward = 0
    seq = 0

    try:
        agent._load_model()
        while True:
            if state_machine.state == State.PAUSED:
                await asyncio.sleep(0.1)
                continue

            state = env.get_state()
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)
            state_machine.total_reward += reward

            agent.update(state, action, reward, next_state)
            await websocket.send_json({"state": next_state.tolist(), "seq": seq})
            await asyncio.sleep(0.02)

            if done:
                env.reset()
                state_machine.total_reward = 0

    except WebSocketDisconnect:
        state_machine.set_state(State.IDLE)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        state_machine.set_state(State.IDLE)

@router.post("/inference/pause")
async def pause_inference(game: str = "pong"):
    """
    Toggle pause/resume for inference.
    """
    state_machine = get_state_machine(game)
    if state_machine.state == State.INFERENCING:
        state_machine.set_state(State.PAUSED)
        return {"status": "Inference paused"}
    elif state_machine.state == State.PAUSED:
        state_machine.set_state(State.INFERENCING)
        return {"status": "Inference resumed"}
    else:
        return {"status": "Inference is not running"}
