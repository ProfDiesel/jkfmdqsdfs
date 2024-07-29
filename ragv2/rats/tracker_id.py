from datetime import datetime
from uuid import uuid4
from contextlib import contextmanager
from pathlib import Path
import json
import asyncio

from contextvars import ContextVar, Token
from typing import NewType, Any, cast, Final, Callable, Awaitable

TrackerId = NewType('TrackerId', str)

TRACKER_ID: Final[ContextVar[TrackerId | None]] = ContextVar[TrackerId | None]('trackerid', default=None)

def get_current_trackerid() -> TrackerId:
    if (trackerid := TRACKER_ID.get()) is None:
        raise RuntimeError('trackerid not set')
    return trackerid

@contextmanager
def trackerid(origin: Event):
    trackerId: TrackerId = cast(TrackerId, f'{origin.type}_{datetime.now():%Y%M}_{uuid4().hex}')
    token: Token[TrackerId | None] = TRACKER_ID.set(trackerId)
    try:
        yield
    finally:
        TRACKER_ID.reset(token)


def tap(name: str, data: Any) -> None:
    Path(f'{get_current_trackerid()}_{name}.json').write_text(json.dumps(data))


async def wrap(handle: Callable[[Event], Awaitable[T]]) -> Callable[[Event], Awaitable[T]]:
    async def result(origin: Event):
        async def task():
            with trackerid(origin):
                await handle(origin)
        await asyncio.create_task(task())
    return result
