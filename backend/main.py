from fastapi import FastAPI #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from routes.training_routes import router as training_router
from routes.inference_routes import router as inference_router
from routes.status_routes import router as status_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(training_router)
app.include_router(inference_router)
app.include_router(status_router)
