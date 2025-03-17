from dependencies import get_state_machine, get_env, get_agent
from fastapi import APIRouter, Depends
import asyncio
from core.state_machine import State, StateMachine
from snake.snake_env import SnakeEnv
from snake.q_learning_agent import QLearningAgent

router = APIRouter()
training_task = None

# === Dépendances ===

state_machine = get_state_machine()
env = get_env()
agent = get_agent()

async def training_loop():
    state_machine.set_state(State.TRAINING)

    while state_machine.state == State.TRAINING and state_machine.current_episode < state_machine.max_episodes:
        if state_machine.state == State.PAUSED:
            await asyncio.sleep(0.1)
            continue

        state = tuple(env.get_state())
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, tuple(next_state))

        state_machine.current_reward += reward

        if done:
            env.reset()
            state_machine.current_episode += 1
            state_machine.total_reward += reward
            state_machine.num_episodes_completed += 1
            state_machine.current_reward = 0

        await asyncio.sleep(0.1)

    if state_machine.state != State.IDLE:
        state_machine.set_state(State.IDLE)

    agent.save_model("model.npy")
    print("Training completed or stopped")

@router.post("/training/start")
async def start_training():
    global training_task

    if state_machine.state == State.INFERENCING:
        return {"status": "Cannot start training while inference is running"}

    if state_machine.state != State.TRAINING:
        state_machine.reset()
        if training_task is None or training_task.done():
            training_task = asyncio.ensure_future(training_loop())

        return {"status": "Training started"}
    else:
        return {"status": "Training is already running"}

@router.post("/training/pause")
async def pause_training():
    if state_machine.state == State.TRAINING:
        state_machine.set_state(State.PAUSED)
        return {"status": "Training paused"}
    elif state_machine.state == State.PAUSED:
        state_machine.set_state(State.TRAINING)
        return {"status": "Training resumed"}
    else:
        return {"status": "Training is not running"}

@router.post("/training/stop")
async def stop_training():
    if state_machine.state in [State.TRAINING, State.PAUSED]:
        state_machine.set_state(State.IDLE)
        return {"status": "Training stopped"}
    else:
        return {"status": "Training is not running"}

@router.post("/training/save")
async def save_model():
    agent.save_model("model.npy")
    return {"status": "Model saved"}
