from fastapi import FastAPI, WebSocket, WebSocketDisconnect #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from snake.environment import SnakeEnv
from snake.agent import QLearningAgent
import asyncio

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SnakeEnv()
agent = QLearningAgent(4)

# Global state variables
is_training = False
is_inferencing = False
is_paused = False
current_episode = 0
max_episodes = 1000

async def training_loop():
    global is_training, is_paused, current_episode

    while is_training and current_episode < max_episodes:
        if is_paused:
            await asyncio.sleep(0.1)
            continue

        state = tuple(env.get_state())
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, tuple(next_state))

        if done:
            env.reset()
            current_episode += 1
            print(f"Episode {current_episode} completed")

        await asyncio.sleep(0.1)

    # Stop training and save the model
    is_training = False
    agent.save_model("model.npy")
    print("Training completed or stopped")

@app.post("/training/start")
async def start_training():
    global is_training, is_paused, current_episode, is_inferencing

    if is_inferencing:
        return {"status": "Cannot start training while inference is running"}

    if not is_training:
        is_training = True
        is_paused = False
        current_episode = 0
        asyncio.create_task(training_loop())
        return {"status": "Training started"}
    else:
        return {"status": "Training is already running"}

@app.post("/training/pause")
async def pause_training():
    global is_paused

    if is_training:
        is_paused = not is_paused
        status = "Paused" if is_paused else "Resumed"
        return {"status": status}
    else:
        return {"status": "Training is not running"}

@app.post("/training/stop")
async def stop_training():
    global is_training, is_paused

    if is_training:
        is_training = False
        is_paused = False
        return {"status": "Training stopped"}
    else:
        return {"status": "Training is not running"}

@app.post("/training/save")
async def save_model():
    global is_training

    print("🔎 First 5 terms in Q-table:")
    for i, (state, values) in enumerate(agent.q_table.items()):
        print(f"State {i + 1}: {state} -> Q-values: {values}")
        if i == 4:
            break

    agent.save_model("model.npy")

    if is_training:
        print("🛑 Stopping training after save...")
        is_training = False

    return {"status": "Model saved"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global is_inferencing


    if is_training:
        await websocket.close(code=1000)
        return {"status": "Cannot start inference while training is running"}

    await websocket.accept()
    is_inferencing = True
    env.reset()
    total_reward = 0

    try:
        while True:
            if is_paused:
                await asyncio.sleep(0.1)
                continue

            state = tuple(env.get_state())
            print({"state": state})
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)
            total_reward += reward

            agent.update(state, action, reward, tuple(next_state))

            await websocket.send_json({"state": next_state})
            await asyncio.sleep(0.1)

            if done:
                print({"Reward total": total_reward})
                env.reset()
                total_reward = 0

    except WebSocketDisconnect:
        print("🔴 WebSocket disconnected cleanly")
        is_inferencing = False

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        is_inferencing = False

@app.post("/inference/pause")
async def pause_inference():
    global is_paused
    is_paused = not is_paused
    status = "Paused" if is_paused else "Resumed"
    return {"status": status}