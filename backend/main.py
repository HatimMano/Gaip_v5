from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.training_routes import router as training_router
from routes.inference_routes import router as inference_router
from routes.status_routes import router as status_router

# === Initialize App ===
app = FastAPI()

# ✅ Correction CORS : spécifier l'origine et forcer le preflight
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplacer "*" par l'URL réelle du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Monter les routes ===
app.include_router(training_router)
app.include_router(inference_router)
app.include_router(status_router)
