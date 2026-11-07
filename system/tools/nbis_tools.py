from pydantic import BaseModel
from pydantic_ai import FunctionToolset, RunContext
import requests
from bs4 import BeautifulSoup

nbis_tools = FunctionToolset()

class SearchResultEntry(BaseModel):
    url: str
    hitTitle: str
    hitSummary: str
    searchCategory: str


class SearchResult(BaseModel):
    hits: list[SearchResultEntry]


class Fact(BaseModel):
    description: str
    url: str


class Knowledge(BaseModel):
    facts: list[Fact]
    open_questions: list[str]


DepsType = list[Fact]
OutputType = Knowledge

@nbis_tools.tool_plain
def find_at_nbis(search: str) -> SearchResult:
    """Returns structured information about the NBIS organization

    Args:
        search: short topical sentence with what you are looking for
    """
    base_url = "https://nbis.se"
    try:
        print(f"Searching: {search}")
        params = {
            "q": search
        }
        response = requests.get(f"{base_url}/results/", params=params)
        response.raise_for_status()
        result = SearchResult.model_validate(response.json())
        for hit in result.hits:
            hit.url = f"{base_url}/{hit.url}"
        return result
    except requests.exceptions.HTTPError as e:
        return "Failed to get search result."


@nbis_tools.tool_plain
def get_text_from_url(url: str) -> str:
    """Returns the text content from a web page URL

    Args:
        url: a url from which to fetch text
    """
    try:
        print(f"Fetching: {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, features="html.parser")
        return soup.get_text()
    except requests.exceptions.HTTPError as e:
        return "Failed to get url result."


@nbis_tools.tool
def recall_previous_knowledge(ctx: RunContext[DepsType]) -> list[Fact]:
    """Recall current facts about the topic at hand
    
    Args:
        ctx: The AI context for this run
    """

    print("Recalling knowledge.")
    return ctx.deps
