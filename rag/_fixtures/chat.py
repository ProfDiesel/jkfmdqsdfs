from pytest import fixture
from rag.datasources.chat import Chat, Message
from datetime import date, datetime
from rag.issue import IssueFeatures
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class Sample:
    chat: Chat
    features: IssueFeatures | None

SAMPLE0 = Sample(
    chat = Chat(date=date(2024, 4, 1),
                messages=[
                    Message(timestamp=datetime(2024, 4, 1, 10, 0, 0), author='client0', message='Drive ÜBERDRIVE ist kaput'),
                ]),
    features = IssueFeatures(config_name='ÜBERDRIVE', reporter='client0')
)

SAMPLES = (SAMPLE0,)