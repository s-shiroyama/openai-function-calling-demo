# openai-function-calling-demo

これは OpenAI API の function calling 機能のデモ用リポジトリです。
モデルは gpt-4-turbo が使用されています。

## requirements
- Python 3.11
- pip
- OpenAI API key

## setup
OPENAI_API_KEY の環境変数に API キーを設定してください。
```bash
export OPENAI_API_KEY=<your api key>
```

python パッケージをインストールしてください。
```bash
pip install -r requirements.txt
```

## usage
```bash
python chatbot.py --msg "<input message>"
```
