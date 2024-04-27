from jinja2 import Template
from langchain.output_parsers import BooleanOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable
from langchain_community.chat_models.fake import FakeListChatModel

from rag._fixtures.chat import SAMPLES
from rag.datasources.chat import Chat
from rag.environment import environment
from rag.issue import IssueFeatures, create_issue_extractor
from rag.playground import PlaygroundChatModel
from rag.prompts import load_prompt

import pytest


@pytest.mark.asyncio
async def test_detect_issue():
    llm: BaseLanguageModel = FakeListChatModel(responses=['YES'])
    issue_detector_chain: Runnable[dict, bool] = (
            load_prompt('detect_errors')
            | llm
            | BooleanOutputParser())
    template: Template = environment().get_template('embedding/chat.jinja2')
    
    async def detect(chat: Chat):
        return await issue_detector_chain.ainvoke({'chat_history': {template.render(chat=chat)}})

    for sample in SAMPLES:
        assert (await detect(sample.chat)) == (sample.features is not None)


@pytest.mark.asyncio
async def test_extract_issue_features():
    llm: BaseLanguageModel = FakeListChatModel(responses=['{"config_name": "ÜBERDRIVE"}'])
    issue_extractor_chain: Runnable[dict, IssueFeatures] = create_issue_extractor(load_prompt('extract'), llm)
    template: Template = environment().get_template('embedding/chat.jinja2')
    
    async def extract(chat: Chat):
        return await issue_extractor_chain.ainvoke({'chat_history': {template.render(chat=chat)}})

    for sample in SAMPLES:
        assert (await extract(sample.chat)) == sample.features