from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware  # Importer le middleware CORS
from snake.environment import SnakeEnv
from snake.agent import QLearningAgent
import asyncio
import os
import pickle

app = FastAPI()

# ✅ Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Autoriser uniquement le frontend
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

env = SnakeEnv()
agent = QLearningAgent(4)

# ✅ Variables globales pour gérer le training et l'inférence
is_training = False
is_inferencing = False  # Nouvelle variable pour gérer l'inférence
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

        await asyncio.sleep(0.1)  # Pour éviter de surcharger le CPU

    # Arrêt du training une fois terminé
    is_training = False
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
    model_path = os.path.join("snake", "model.pkl")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(agent.get_model(), f)

    return {"status": "Model saved"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global is_inferencing

    if is_training:
        await websocket.close(code=1000)  # Fermer la connexion WebSocket si le training est en cours
        return {"status": "Cannot start inference while training is running"}

    await websocket.accept()
    is_inferencing = True  # Définir l'état de l'inférence
    env.reset()
    print('Init')

    try:
        while True:
            if is_paused:
                await asyncio.sleep(0.1)
                continue

            state = tuple(env.get_state())
            print({'state': state})
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, tuple(next_state))

            await websocket.send_json({"state": next_state})
            await asyncio.sleep(0.1)

            if done:
                print({'Reward total': reward})
                env.reset()
    finally:
        is_inferencing = False  # Réinitialiser l'état de l'inférence


@app.post("/inference/pause")
async def pause_inference():
    global is_paused
    is_paused = not is_paused
    status = "Paused" if is_paused else "Resumed"
    return {"status": status}