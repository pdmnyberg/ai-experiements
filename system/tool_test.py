from pydantic import BaseModel, TypeAdapter
from openai import AsyncOpenAI
from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.output import ToolOutput
import requests
import functools
from bs4 import BeautifulSoup
from tools.nbis_tools import nbis_tools, Knowledge
from tools.pollen_tools import pollen_tools
import os


def get_config():
    base_url = os.environ["AI_BASE_URL"]
    api_key = os.environ["AI_API_KEY"]

    return {
        "base_url": base_url,
        "api_key": api_key,
    }


def main():
    config = get_config()
    client = AsyncOpenAI(
        **config,
    )

    model = OpenAIChatModel(
        "Qwen3-235B-A22B",
        provider=OpenAIProvider(openai_client=client),
    )

    agent = Agent(
        model,
        toolsets=[
            nbis_tools,
            pollen_tools,
        ],
        output_type=ToolOutput(Knowledge),
        instructions="Use the tools to find the information you are looking for. Answer with a list of facts and include any possibly open questions related to information you find.",
    )

    result = agent.run_sync("What is the current pollen count close around latitude: 59.83 and longitude: 17.63? Use only data available from tools to extrapolate a result.")
    print(result.output)


main()