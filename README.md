# ♜ AI vs AI: Animated Chess Game

An advanced Chess game system where two AI agents play chess against each other automatically until game completion. The system features animated moves, responsive display, and comprehensive move logging.

## Features

### Fully Autonomous Gameplay

- **Animated Game Display**: Chess pieces move on a single board with visual indicators for the latest move
- **Complete Autonomous Play**: AI plays both sides (white and black) until the game reaches its natural conclusion
- **Move Log**: Real-time display of all moves and game state changes

### Multi-Agent Architecture

- **Agent White**: Groq-powered chess master controlling white pieces using LLaMA 3 70B
- **Agent Black**: Groq-powered chess master controlling black pieces using LLaMA 3 70B
- **Game Master**: Validation agent for move legality and game state tracking

### Strategic Gameplay

- AI-powered position evaluation
- Dynamic strategy adaptation
- Complete chess ruleset implementation
- Game automatically continues until victory, stalemate, or insufficient material

### How to get Started?

1. Clone the GitHub repository

```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd ai_agent_tutorials/ai_chess_game
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Get your Groq API Key

- Sign up for a [Groq account](https://console.groq.com/) and obtain your API key.
- Create a `.env` file in the root directory and add your API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

4. Run the Streamlit App

```bash
streamlit run ai_chess_agent.py
```

5. Using the App

- Click "Start New Game" to begin an automated chess match
- Watch as the AI agents play against each other
- The move log on the right side records every move in real-time
- The game continues automatically until checkmate, stalemate, or insufficient material to win
