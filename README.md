# FlexiBot

## Introduction
FlexiBot is an AI-powered chatbot framework that utilizes LINE Message API, ChatGPT, and Azure Functions as a Service (FaaS). This project showcases a flexible approach that can be adapted for various domains such as debunking misinformation, business customer service, and more. The core functionality involves analyzing user intentions with GPT, scraping information from specified sources, filtering and summarizing the information, and providing the final response back to the user.

## Features
- Analyzes user intentions using ChatGPT
- Scrapes information from specified sources
- Filters and summarizes information for accurate responses
- Flexible architecture to adapt to various domains
- Uses Python with a router-like structure similar to Flask for handling intents

![structure](/images/structure.png)

## Installation
### Prerequisites
- Python 3.x
- LINE Message API credentials
- Azure Functions setup

### Installation Steps
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/FlexiBot.git
   ```
2. Navigate to the project directory:
   ```
   cd FlexiBot
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Set up environment variables for LINE API and Azure Functions credentials.
2. Define your intents and handlers similar to Flask routers. For example:
   ```
   @handler.intent('Inquire About Fraudulent TEL')
   def search_tel(event, intent):
       ...
   ```
3. Modify the scraping API calls and GPT prompts as needed for your specific domain.
4. Deploy your Azure Functions.
5. Run the chatbot:
   ```
   python app.py
   ```

## Contact Information
If you have any questions, please submit an issue.
