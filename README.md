# ♜ AI Chess Agent

A Streamlit app where two AI agents play chess against each other automatically using various LLM providers.

## Features

- AI controls both white and black pieces
- Visual chess board with move highlighting
- Start, pause, and reset game controls
- Plays until checkmate, stalemate, or draw
- Support for multiple AI providers:
  - Groq (gemma2-9b-it)
  - OpenAI (o1-mini)
  - Anthropic (Claude 3.5 Sonnet)

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_key_here
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```
   (You only need to add the API key for the provider you want to use)
4. Run: `streamlit run ai_chess_agent.py`

## Usage

- Select your preferred AI provider from the sidebar
- Enter your API key if not already in the .env file
- Click "Start New Game" to begin
- Watch the AI agents play against each other
- Use pause/resume to control the game flow
- Reset anytime to start over

## Tech Stack

- Python Chess library
- Streamlit
- AutoGen
- Groq API
- OpenAI API
- Anthropic API
