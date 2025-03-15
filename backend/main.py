from fastapi import FastAPI, WebSocket
from snake.environment import SnakeEnv
from snake.agent import QLearningAgent
import asyncio

app = FastAPI()

env = SnakeEnv()
agent = QLearningAgent(4)

is_paused = False  # ✅ Variable d'état globale pour la pause


@app.post("/training/start")
async def start_training():
    for _ in range(1000):
        state = tuple(env.get_state())
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, tuple(next_state))
        if done:
            env.reset()
    return {"status": "Training complete"}

@app.post("/training/save")
async def save_model():
    agent.save_model("model.npy")
    return {"status": "Model saved"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    env.reset()
    print('Init')
    while True:
        
        if is_paused:
            await asyncio.sleep(0.1)
            continue

        state = tuple(env.get_state())
        print({'state':state})
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, tuple(next_state))

        # ✅ Envoyer l'état via WebSocket
        await websocket.send_json({"state": next_state})
        await asyncio.sleep(0.1)

        if done:
            print({'Reward total': reward})
            env.reset()


@app.post("/inference/pause")
async def pause_inference():
    global is_paused
    is_paused = not is_paused
    status = "Paused" if is_paused else "Resumed"
    return {"status": status}