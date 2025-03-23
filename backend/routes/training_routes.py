import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect #type: ignore

from dependencies import get_state_machine, get_env, get_agent
from core.state_machine import State

router = APIRouter()

# Global task for training process
training_task = None

# Set of connected WebSocket clients for training visualization
training_ws_clients = set()


async def broadcast_training_state(game: str, data: dict) -> None:
    """
    Broadcast training updates to all connected WebSocket clients.

    Args:
        game (str): The game identifier.
        data (dict): The training update data.
    """
    for ws in list(training_ws_clients):
        try:
            await ws.send_json(data)
        except Exception as e:
            print("Error broadcasting training state:", e)
            training_ws_clients.remove(ws)


async def training_loop(game: str) -> None:
    """
    Main training loop. Executes training steps until the training is stopped or completed.

    Args:
        game (str): The game identifier.
    """
    state_machine = get_state_machine(game)
    env = get_env(game)
    agent = get_agent(game)
    state_machine.set_state(State.TRAINING)

    sequence = 0  # Sequence counter for updates

    while state_machine.state == State.TRAINING and state_machine.current_episode < state_machine.max_episodes:
        if state_machine.state == State.PAUSED:
            await asyncio.sleep(0.1)
            continue

        # Get current state and perform training step
        state = env.get_state()
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, next_state)

        state_machine.current_reward += reward
        sequence += 1

        # Prepare training update data
        training_update = {
            "current_episode": state_machine.current_episode,
            "current_reward": state_machine.current_reward,
            "average_reward": (state_machine.total_reward / state_machine.num_episodes_completed)
                              if state_machine.num_episodes_completed > 0 else 0,
            "state": next_state.tolist() if hasattr(next_state, 'tolist') else next_state,
            "seq": sequence
        }
        await broadcast_training_state(game, training_update)

        if done:
            env.reset()
            state_machine.current_episode += 1
            state_machine.total_reward += reward
            state_machine.num_episodes_completed += 1
            state_machine.current_reward = 0

        await asyncio.sleep(0.1)

    if state_machine.state != State.IDLE:
        state_machine.set_state(State.IDLE)

    print("Training completed or stopped")


@router.post("/training/start")
async def start_training(game: str = "pong") -> dict:
    """
    Start training if not already running.

    Args:
        game (str): The game identifier (default "pong").

    Returns:
        dict: Status message.
    """
    global training_task
    state_machine = get_state_machine(game)

    if state_machine.state == State.INFERENCING:
        return {"status": "Cannot start training while inference is running"}

    if state_machine.state != State.TRAINING:
        state_machine.reset()
        if training_task is None or training_task.done():
            training_task = asyncio.ensure_future(training_loop(game))
        return {"status": "Training started"}
    return {"status": "Training is already running"}


@router.post("/training/pause")
async def pause_training(game: str = "pong") -> dict:
    """
    Pause or resume training depending on current state.

    Args:
        game (str): The game identifier (default "pong").

    Returns:
        dict: Status message.
    """
    state_machine = get_state_machine(game)
    if state_machine.state == State.TRAINING:
        state_machine.set_state(State.PAUSED)
        return {"status": "Training paused"}
    elif state_machine.state == State.PAUSED:
        state_machine.set_state(State.TRAINING)
        return {"status": "Training resumed"}
    return {"status": "Training is not running"}


@router.post("/training/stop")
async def stop_training(game: str = "pong") -> dict:
    """
    Stop the training process.

    Args:
        game (str): The game identifier (default "pong").

    Returns:
        dict: Status message.
    """
    state_machine = get_state_machine(game)
    if state_machine.state == State.TRAINING:
        state_machine.set_state(State.IDLE)
        return {"status": "Training stopped"}
    return {"status": "Training is not running"}


@router.post("/training/save")
async def save_model(game: str = "pong") -> dict:
    """
    Save the current model.

    Args:
        game (str): The game identifier (default "pong").

    Returns:
        dict: Status message.
    """
    agent = get_agent(game)
    agent.save_model()
    return {"status": "Model saved"}


@router.websocket("/ws/training")
async def training_visualization_ws(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for training visualization.

    The endpoint accepts a 'game' query parameter to identify the game.
    The training updates are broadcasted from the training_loop.

    Args:
        websocket (WebSocket): The WebSocket connection.
    """
    await websocket.accept()
    # Extract the 'game' parameter from the query (unused in this endpoint but kept for future use)
    game = websocket.query_params.get("game", "pong")
    training_ws_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        training_ws_clients.remove(websocket)
    except Exception as e:
        print("Training visualization WS error:", e)
        training_ws_clients.remove(websocket)
