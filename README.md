# ♜ AI Chess Agent

A Streamlit app where two AI agents play chess against each other automatically using Groq's LLM API.

## Features

- AI controls both white and black pieces
- Visual chess board with move highlighting
- Start, pause, and reset game controls
- Plays until checkmate, stalemate, or draw

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Groq API key: `GROQ_API_KEY=your_key_here`
4. Run: `streamlit run ai_chess_agent.py`

## Usage

- Click "Start New Game" to begin
- Watch the AI agents play against each other
- Use pause/resume to control the game flow
- Reset anytime to start over

## Tech Stack

- Python Chess library
- Streamlit
- AutoGen
- Groq API
