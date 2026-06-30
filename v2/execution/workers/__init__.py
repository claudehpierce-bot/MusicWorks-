"""MusicWorks™ V4 — Worker package: AI provider interfaces."""
from .base_worker import BaseWorker, WorkerResult
from .claude_worker import ClaudeWorker
from .veo_worker import VeoWorker
from .hedra_worker import HedraWorker
from .elevenlabs_worker import ElevenLabsWorker
from .canva_worker import CanvaWorker

ALL_WORKERS: list[BaseWorker] = [
    ClaudeWorker(),
    VeoWorker(),
    HedraWorker(),
    ElevenLabsWorker(),
    CanvaWorker(),
]

WORKER_MAP: dict[str, BaseWorker] = {w.key: w for w in ALL_WORKERS}


def get_worker(key: str) -> BaseWorker | None:
    return WORKER_MAP.get(key)
