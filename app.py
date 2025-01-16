from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.api.api import router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIR = Path(__file__).parent
static_folder = DIR / "static"
app.mount("/static", StaticFiles(directory=static_folder, html=True), name="static")

app.include_router(router)


@app.get("/{full_path:path}")
async def serve_html(full_path: str):
    file_path = static_folder / full_path
    if file_path.exists() and file_path.is_file():
        return StaticFiles(directory=static_folder).lookup_path(file_path)
    return StaticFiles(directory=static_folder).lookup_path(static_folder / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
