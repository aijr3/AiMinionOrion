"""Entry point — starts the Miro Strategy App backend."""
import uvicorn

from app.config import settings
from app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=settings.strategy_port,
        reload=(settings.environment == "development"),
        log_level="info",
    )
