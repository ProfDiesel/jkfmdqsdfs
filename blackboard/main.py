from .blackboard import BlackboardVar, Blackboard
from dataclasses import dataclass
from collections.abc import Sequence
from enum import Enum, auto

@dataclass
class Message:
    pass

class Component(Enum):
    comp0 = auto()
    comp1 = auto()

CONFIG: BlackboardVar[str | None] = BlackboardVar('config', None)
VERSION: BlackboardVar[str | None] = BlackboardVar('version', None)
COMPONENT: BlackboardVar[Component | None] = BlackboardVar('component', None)
MESSAGES: BlackboardVar[Sequence[Message]] = BlackboardVar('messages', [])

llm = None

def extract_config(blackboard: Blackboard):
    if blackboard[CONFIG]:
        return
    config = llm.extract(blackboard[MESSAGES])
    blackboard.apply(CONFIG(config))

def extract_version(blackboard: Blackboard):
    if not blackboard[CONFIG]:
        return
    if blackboard[VERSION]:
        return
    version = llm.extract(blackboard[MESSAGES])
    blackboard.apply(VERSION(version))

def extract_component(blackboard: Blackboard):
    if blackboard[COMPONENT]:
        return
    component = llm.extract(blackboard[MESSAGES])
    blackboard.apply(COMPONENT(component))

def consolidate(blackboard: Blackboard):
    if not blackboard[VERSION] or not blackboard[CONFIG]:
        return
    advice = llm.prompt(blackboard[MESSAGES])
    blackboard.apply()

def main():
    bb = Blackboard()
    
    for callback in (extract_config, extract_version, consolidate):
        bb.register(callback)

    bb.apply(MESSAGES(bb[MESSAGES] + "hello"))

