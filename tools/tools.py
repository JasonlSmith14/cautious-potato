from langchain_tavily import TavilySearch
from langchain_community.tools import DuckDuckGoSearchRun


class Tools:
    def __init__(self):
        pass

    @staticmethod
    def tavily_search_tool(
        max_results,
        topic,
        country,
        include_answer=False,
        include_raw_content=False,
        include_images=False,
        include_image_descriptions=False,
        search_depth="basic",
        time_range="day",
        include_domains=None,
        exclude_domains=None,
    ):
        tavily_search_tool = TavilySearch(
            max_results=max_results,
            topic=topic,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
            include_image_description=include_image_descriptions,
            search_depth=search_depth,
            time_range=time_range,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            country=country,
        )

        return tavily_search_tool

    @staticmethod
    def duck_duck_go_tool(description):
        return DuckDuckGoSearchRun(description=description)
