try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - optional until deps are installed
    FastAPI = None

import uvicorn

from .api_models import (
    HealthResponse,
    MetadataResponse,
    ObservationResponse,
    ResetRequest,
    StepRequest,
)
from .environment import GeoAuditEnvironment
from .models import GeoAuditAction


env = GeoAuditEnvironment()

if FastAPI is not None:
    app = FastAPI(title="GEO Audit Environment", version="0.1.0")

    @app.get("/")
    def root() -> dict[str, object]:
        return {
            "name": "geo-audit-env",
            "status": "ok",
            "message": "GEO Audit Environment is running.",
            "routes": {
                "health": "/health",
                "metadata": "/metadata",
                "state": "/state",
                "reset": "/reset",
                "step": "/step",
                "docs": "/docs",
            },
        }

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="healthy")

    @app.get("/metadata", response_model=MetadataResponse)
    def metadata() -> MetadataResponse:
        return MetadataResponse(
            name="geo-audit-env",
            description="GEO webpage audit environment for reinforcement learning experiments",
            version="0.1.0",
            available_actions=env.AVAILABLE_ACTIONS,
            issue_types=env.ISSUE_TYPES,
            positive_types=env.POSITIVE_TYPES,
        )

    @app.get("/state", response_model=ObservationResponse)
    def state() -> ObservationResponse:
        observation = env.current_observation()
        return ObservationResponse.model_validate(env.observation_dict(observation))

    @app.post("/reset", response_model=ObservationResponse)
    def reset(payload: ResetRequest = ResetRequest()) -> ObservationResponse:
        observation = env.reset(task_difficulty=payload.task_difficulty)
        return ObservationResponse.model_validate(env.observation_dict(observation))

    @app.post("/step", response_model=ObservationResponse)
    def step(payload: StepRequest) -> ObservationResponse:
        action = GeoAuditAction(**payload.model_dump())
        observation = env.step(action)
        return ObservationResponse.model_validate(env.observation_dict(observation))
else:
    app = None


def main() -> None:
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
