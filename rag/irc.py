import asyncio
import re
from asyncio import sleep
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterable, Final, List

from langchain_core.tools import BaseTool

NICK: Final[str] = "da_bot"
CHANNEL: Final[str] = "#ts"

@dataclass(frozen=True)
class Message:
    author: str
    message: str
    timestamp: datetime = datetime.now()

class IRCClient():
    def __init__(self) -> None:
        self.__backlog: Final[List[Message]] = []

    async def __send(self, message: str) -> None:
        self.__writer.write((message + '\r\n').encode())
        await self.__writer.drain()

    async def __recv(self) -> str:
        return (await self.__reader.readuntil(b'\r\n')).decode()

    async def connect(self) -> None:
        self.__reader, self.__writer = await asyncio.open_connection('127.0.0.1', 6667)
        await self.__recv()
        await self.__send(f'NICK {NICK}')
        await self.__recv()
        await self.__send(f'USER {NICK} {NICK} {NICK} {NICK}')
        await self.__recv()
        await self.__send(f'JOIN {CHANNEL}')
        await self.__recv()
        self.__task = asyncio.create_task(self.loop())

    async def loop(self) -> None:
        while True:
            msg: str = await self.__recv()
            if (match := re.match('PING :(?P<token>.*)', msg)) is not None:
                await self.__send(f'PONG :{match.group("token")}')
            await self.__writer.drain()
            if (match := re.match(':(?P<from>.*?) PRIVMSG (?P<to>.*?):(?P<message>.*)', msg)) is not None:
                self.__backlog.append(Message(author=match.group('from'), message=match.group('message')))

    async def ask(self, question: str) -> str:
        await self.__send(f'PRIVMSG {CHANNEL} :{question}')
        return (await self.__reader.readuntil(b'\r\n')).decode()

    @property
    def backlog(self) -> List[Message]:
        return self.__backlog

    async def new_messages(self) -> AsyncIterable[Message]:
        while True:
            await sleep(10)
            yield self.__backlog[-1]

# langchain_community.tools.HumanInputRun ?
class AskHuman(BaseTool):
    """Tool that asks user for input."""

    description = """You can ask a human for guidance when you think you got stuck or you are not sure what to do next. \
                     The input should be a question for the human."""

    def __init__(self, client: IRCClient):
        self.__client = client

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError()

    async def _arun(
        self, question: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the Human input tool."""
        return await self.__client.ask(question)