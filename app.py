from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import boto3
import json
from datetime import datetime, timedelta
import pytz
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Replace with your own region
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

try:
    with open('xauusd_4h.json', 'r') as f:
        df = pd.DataFrame(json.load(f))
    df['time'] = pd.to_datetime(df['time'], utc=True)
    df.set_index('time', inplace=True)
    df = df[['open', 'high', 'low', 'close']].dropna()
except FileNotFoundError:
    logging.error("xauusd_4h.json not found")
    exit(1)
except json.JSONDecodeError:
    logging.error("Invalid JSON in xauusd_4h.json")
    exit(1)

try:
    with open('usd_high_impact_news.json', 'r') as f:
        news_df = pd.DataFrame(json.load(f))
    news_df['dateTime'] = pd.to_datetime(news_df['dateTime'], utc=True)
except FileNotFoundError:
    logging.error("usd_high_impact_news.json not found")
    exit(1)
except json.JSONDecodeError:
    logging.error("Invalid JSON in usd_high_impact_news.json")
    exit(1)

def call_llama3(prompt):
    try:
        response = bedrock.invoke_model(
            # Replace with your own region and AWS account ID
            modelId="arn:aws:bedrock:us-east-1:324037276468:inference-profile/us.meta.llama3-3-70b-instruct-v1:0",
            body=json.dumps({
                "prompt": prompt,
                "max_gen_len": 512,
                "temperature": 0.5,
                "top_p": 0.9
            }),
            contentType="application/json",
            accept="application/json"
        )
        return json.loads(response['body'].read())['generation']
    except Exception as e:
        logging.error(f"Bedrock error: {str(e)}")
        return f"Error calling Bedrock: {str(e)}"

def generate_strategy(risk_level, data_summary, news_summary, trading_style, indicators):
    ind_desc = ", ".join([f"{k} (period={v['period']})" for k, v in indicators.items() if v['enabled']]) if indicators else "no indicators"
    prompt = f"""
    I am PropBot, your agent for generating Prop Firm-compliant XAUUSD trading strategies using Llama 3.
    Using {data_summary}, news '{news_summary if news_summary else 'none'}', and indicators {ind_desc}, generate a Prop Firm-compliant XAUUSD trading strategy for 4h candles.
    The strategy must:
    - Limit max drawdown to 5% or less.
    - Target consistent profits (e.g., 1-2% for Conservative, 2-3% for Moderate, 3-5% for Aggressive).
    - Use strict risk management (e.g., stop-loss < 1% for Conservative, < 1.5% for Moderate, < 2% for Aggressive).
    - Incorporate enabled technical indicators (MA, RSI, ATR, ADX) and news impact if provided.
    Provide specific entry, exit, stop-loss, and take-profit rules in markdown format with example price levels based on recent data.
    Risk level: {risk_level}. Trading style: {trading_style}.
    Return the strategy as plain text without additional commentary.
    """
    return call_llama3(prompt)

def chat_response(strategy, question):
    prompt = f"PropBot here! Given this strategy: {strategy}, answer this question: {question}"
    return call_llama3(prompt)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is alive!'})

@app.route('/generate_strategy', methods=['POST'])
def generate_strategy_endpoint():
    try:
        risk_level = request.json.get('risk_level', 'Conservative')
        trading_style = request.json.get('trading_style', 'Swing')
        time_range = request.json.get('time_range', '1m')
        use_news = request.json.get('use_news', True)
        use_indicators = request.json.get('use_indicators', True)
        indicators = request.json.get('indicators', {
            'MA': {'enabled': True, 'period': 50},
            'MA_long': {'enabled': True, 'period': 200},
            'RSI': {'enabled': True, 'period': 14},
            'ATR': {'enabled': False, 'period': 14},
            'ADX': {'enabled': False, 'period': 14}
        })

        utc = pytz.utc
        end_date = datetime.now(utc)
        ranges = {'1m': 30, '3m': 90, '6m': 180, '1y': 365, '2y': 730}
        start_date = end_date - timedelta(days=ranges.get(time_range, 30))

        filtered_df = df[(df.index >= start_date) & (df.index <= end_date)].copy()
        filtered_news = news_df[(news_df['dateTime'] >= start_date) & (news_df['dateTime'] <= end_date)].to_dict('records') if use_news else []

        if filtered_df.empty:
            return jsonify({'error': 'No candle data available for the selected time range'}), 400

        rsi = filtered_df['close'].pct_change().rolling(14).mean().iloc[-1] if indicators['RSI']['enabled'] and use_indicators else 0
        summary = f"XAUUSD 4h: Last price {filtered_df['close'].iloc[-1]}, RSI {rsi:.2f}"
        news_summary = ", ".join([f"{n['event']} on {n['dateTime'].isoformat()}" for n in filtered_news[-5:]]) if filtered_news else ""

        strategy_text = generate_strategy(risk_level, summary, news_summary, trading_style, indicators if use_indicators else {})

        response = {
            'strategy': strategy_text,
            'news': filtered_news
        }
        return jsonify(response)
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    try:
        strategy = request.json.get('strategy', '')
        question = request.json.get('question', '')
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        response = chat_response(strategy, question)
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({'error': f'Chat error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)