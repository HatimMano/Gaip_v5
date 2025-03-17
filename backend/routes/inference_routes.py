import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.state_machine import StateMachine, State
from snake.snake_env import SnakeEnv
from snake.q_learning_agent import QLearningAgent

router = APIRouter()
state_machine = StateMachine()
env = SnakeEnv()
agent = QLearningAgent(4)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if state_machine.state == State.TRAINING:
        await websocket.close(code=1000)
        return {"status": "Cannot start inference while training is running"}

    await websocket.accept()
    state_machine.set_state(State.INFERENCING)
    env.reset()
    state_machine.total_reward = 0

    try:
        agent._load_model()  # Si Q-Learning

        while True:
            if state_machine.state == State.PAUSED:
                await asyncio.sleep(0.1)
                continue

            state = tuple(env.get_state())
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)
            state_machine.total_reward += reward

            agent.update(state, action, reward, tuple(next_state))

            await websocket.send_json({"state": next_state})
            await asyncio.sleep(0.01)

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
async def pause_inference():
    if state_machine.state == State.INFERENCING:
        state_machine.set_state(State.PAUSED)
        return {"status": "Inference paused"}
    elif state_machine.state == State.PAUSED:
        state_machine.set_state(State.INFERENCING)
        return {"status": "Inference resumed"}
    else:
        return {"status": "Inference is not running"}
