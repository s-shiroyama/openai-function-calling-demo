from openai import OpenAI
import click
import json
import os


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], max_retries=1)

GPT_MODEL = "gpt-4-turbo"


def get_current_weather(location: str):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"}
        )
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


# 関数定義
FUNCTIONS = {
    "get_current_weather": {
        "call": get_current_weather,
        "json_schema": {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                    },
                    "required": ["location"],
                },
            },
        },
    },
}


@click.command()
@click.option("--msg", "-m", type=str, required=True, help="Input message for chatbot")
def main(msg: str):
    messages: list[dict] = [{"role": "user", "content": msg}]

    # 関数定義を含めてメッセージを送信
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        # see https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools
        tools=[f["json_schema"] for f in FUNCTIONS.values()],
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    response_message = response.choices[0].message
    if not response_message.tool_calls:
        # 呼び出す関数が指定されていない場合、そのまま返信メッセージを表示して終了
        print("=================== answer without function call ===================")
        print(response_message.content)
        return

    messages.append(response_message)
    for tool_call in response_message.tool_calls:
        # 指定された関数を呼び出す
        print("=================== debug message ===================")
        print(
            f"call function: {tool_call.function.name}, with arguments: {tool_call.function.arguments}"
        )
        function_response = FUNCTIONS[tool_call.function.name]["call"](
            **json.loads(tool_call.function.arguments)
        )
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": function_response,
            }
        )

    # 関数の呼び出し結果を含めたメッセージで再度送信し、最終的な返信メッセージを取得
    second_response = client.chat.completions.create(model=GPT_MODEL, messages=messages)

    print("=================== answer with function call ===================")
    print(second_response.choices[0].message.content)


if __name__ == "__main__":
    main()
