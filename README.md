
# 4h XAUUSD Prop Firm AI Strategy Generator

  

## Hey There, Meet PropBot!

Welcome to **PropBot**, your AI-powered trading strategist! Built for the Topcoder Llama 3 Challenge, PropBot crafts Prop Firm-compliant XAUUSD trading strategies for 4-hour candles using Llama 3 via AWS Bedrock. No backtesting—just pure AI-generated plans and a chat feature to dig deeper. Perfect for traders who want quick, creative strategies tailored to their style.

  

### What’s the Big Idea?

PropBot whips up XAUUSD 4h strategies that keep drawdowns low (under 5%) and profits steady, all while meeting prop firm rules. Feed it your preferences, and it delivers a detailed plan in markdown—entry, exit, stop-loss, and take-profit rules included. Got questions? Chat with PropBot to clarify anything. It’s fast, simple, and built to spark ideas.

  

## How PropBot Uses Llama 3

PropBot leans on Llama 3 in two slick ways:

-  **Strategy Generator**: Input your risk level, style, and indicators—Llama 3 crafts a custom XAUUSD 4h strategy with real examples.

-  **Chat Buddy**: Ask PropBot anything about your strategy—it answers in markdown, fast.

-  **Open Source**: Llama 3 is public, so we’re 100% challenge-compliant—no proprietary tricks here!

  

## What PropBot Can Do

-  **Custom Inputs**: Choose Conservative, Moderate, or Aggressive risk; Swing, Day, or Scalping style; 1 month to 2 years of data; plus news and indicators (MA, RSI, ATR, ADX).

-  **AI Strategies**: Get a markdown plan with specific rules and price examples based on recent XAUUSD data.

-  **Chat Feature**: Query your strategy—e.g., “Why use RSI?”—and get clear, formatted answers.

-  **Lightweight**: No backtesting—just raw AI output, ready to use or tweak.

  

## Setting It Up

Try PropBot on your machine (tested on macOS 10.15):

### What You’ll Need

- Python 3.7+

- AWS CLI (for Bedrock access)

- AWS Bedrock access (Llama 3 model)

- Terminal and browser

  

### Install the Basics

```pip  install  flask  flask-cors  pandas  boto3  pytz  awscli```

### Configure AWS CLI with your credentials
```bash
aws configure
```
Replace `<region>` (e.g., `us-east-1`) and `<aws-account-id>` with your AWS details in `app.py` modelId.

It should looks like this:
```
bedrock = boto3.client('bedrock-runtime', region_name='<region>')
```

```
`modelId="arn:aws:bedrock:<region>:<aws-account-id>:inference-profile/us.meta.llama3-3-70b-instruct-v1:0"`
```