from openai import OpenAI
from .config import get_config
from .openai_utils import safe_openai_call


def get_stock_news_openai(query, start_date, end_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Social Media for {query} from {start_date} to {end_date}? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    if response and "output" in response:
        return response.output[1].content[0].text
    else:
        return f"Unable to fetch news for {query} due to API limitations. Please try again later."


def get_global_news_openai(curr_date, look_back_days=7, limit=5):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = safe_openai_call(
        client=client,
        method_name="responses.create",
        fallback_value={"output": [None, {"content": [{"text": f"Unable to fetch global news from {look_back_days} days before {curr_date} due to API limitations. Please try again later."}]}]},
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search global or macroeconomics news from {look_back_days} days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period. Limit the results to {limit} articles.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    if response and "output" in response:
        return response.output[1].content[0].text
    else:
        return f"Unable to fetch global news from {look_back_days} days before {curr_date} due to API limitations. Please try again later."


def get_fundamentals_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = safe_openai_call(
        client=client,
        method_name="responses.create",
        fallback_value={"output": [None, {"content": [{"text": f"Unable to fetch fundamental data for {ticker} due to API limitations. Please try again later or use Alpha Vantage data source."}]}]},
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    if response and "output" in response:
        return response.output[1].content[0].text
    else:
        return f"Unable to fetch fundamental data for {ticker} due to API limitations. Please try again later or use Alpha Vantage data source."