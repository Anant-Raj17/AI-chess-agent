import chess
import chess.svg
import streamlit as st
from autogen import ConversableAgent, register_function
from dotenv import load_dotenv
import os
import time
import random  # Import for random move selection
import threading  # Import for timeout handling

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "made_move" not in st.session_state:
    st.session_state.made_move = False
if "board_svg" not in st.session_state:
    st.session_state.board_svg = None
if "move_history" not in st.session_state:
    st.session_state.move_history = []
if "move_logs" not in st.session_state:
    st.session_state.move_logs = []
if "game_status" not in st.session_state:
    st.session_state.game_status = "Not started"
if "is_game_over" not in st.session_state:
    st.session_state.is_game_over = False
if "game_in_progress" not in st.session_state:
    st.session_state.game_in_progress = False
if "current_move" not in st.session_state:
    st.session_state.current_move = None

# Setup page layout with columns
st.set_page_config(layout="wide")

# Create a two-column layout
col1, col2 = st.columns([2, 1])

with col1:
    st.title("AI Chess Game")

with col2:
    st.title("Move Log")

# Sidebar configuration
st.sidebar.title("Chess Agent Configuration")
st.sidebar.info("""
This AI chess game plays automatically until completion.
The AI controls both white and black pieces.
The game will end when there's a checkmate, stalemate, or insufficient material.
The move log shows all moves made during the game.
""")

def available_moves() -> str:
    available_moves = [str(move) for move in st.session_state.board.legal_moves]
    return "Available moves are: " + ",".join(available_moves)

def execute_move(move: str) -> str:
    try:
        # Start timing the move execution
        start_time = time.time()
        
        chess_move = chess.Move.from_uci(move)
        if chess_move not in st.session_state.board.legal_moves:
            # If move is invalid, make a random legal move instead
            random_move = make_quick_move()
            if random_move:
                return execute_move(random_move)
            return f"Invalid move: {move}. No legal moves available."
        
        # Get current turn
        current_side = "White" if st.session_state.board.turn == chess.WHITE else "Black"
        
        # Update board state
        st.session_state.board.push(chess_move)
        st.session_state.made_move = True
        
        # Store the current move to highlight it on the board
        st.session_state.current_move = chess_move

        # Track move count
        move_number = len(st.session_state.move_logs) // 2 + 1
        side_to_move = "White" if current_side == "White" else "Black"
        
        # Generate and store board visualization
        board_svg = chess.svg.board(st.session_state.board,
                                  arrows=[(chess_move.from_square, chess_move.to_square)],
                                  fill={chess_move.from_square: "gray"},
                                  size=400)
        st.session_state.board_svg = board_svg

        # Get piece information
        moved_piece = st.session_state.board.piece_at(chess_move.to_square)
        piece_unicode = moved_piece.unicode_symbol() if moved_piece else "?"
        piece_type_name = chess.piece_name(moved_piece.piece_type) if moved_piece else "unknown"
        piece_name = piece_type_name.capitalize() if moved_piece and piece_unicode.isupper() else piece_type_name
        
        # Generate move description
        from_square = chess.SQUARE_NAMES[chess_move.from_square]
        to_square = chess.SQUARE_NAMES[chess_move.to_square]
        move_desc = f"Move {move_number}: {current_side} moved {piece_name} from {from_square} to {to_square}"
        
        # Add move to logs
        st.session_state.move_logs.append(move_desc)
        
        # Check game status
        status_message = ""
        if st.session_state.board.is_checkmate():
            winner = 'White' if st.session_state.board.turn == chess.BLACK else 'Black'
            status_message = f"Checkmate! {winner} wins!"
            st.session_state.is_game_over = True
        elif st.session_state.board.is_stalemate():
            status_message = "Game ended in stalemate!"
            st.session_state.is_game_over = True
        elif st.session_state.board.is_insufficient_material():
            status_message = "Game ended - insufficient material to checkmate!"
            st.session_state.is_game_over = True
        elif st.session_state.board.is_check():
            status_message = "Check!"
        
        if status_message:
            st.session_state.move_logs.append(status_message)
            st.session_state.game_status = status_message
        
        # Log the time it took to process the move
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Move processed in {processing_time:.3f} seconds")
        
        return move_desc + (f". {status_message}" if status_message else "")
    except ValueError:
        # If there's an error, try a random legal move
        random_move = make_quick_move()
        if random_move:
            return execute_move(random_move)
        return f"Invalid move format: {move}. Please use UCI format (e.g., 'e2e4')."

def check_made_move(msg):
    if st.session_state.made_move:
        st.session_state.made_move = False
        return False  # Return False to continue the conversation
    else:
        return False

def check_game_over(msg):
    return st.session_state.is_game_over

# Function to make a quick random move if needed
def make_quick_move():
    """Select a random legal move from the current position."""
    if not st.session_state.board.is_game_over():
        legal_moves = list(st.session_state.board.legal_moves)
        if legal_moves:
            return str(random.choice(legal_moves))
    return None

if GROQ_API_KEY:
    try:
        # Configure AutoGen to use Groq's API through the OpenAI compatibility layer
        agent_config_list = [
            {
                "model": "llama-3.3-70b-versatile",
                "api_key": GROQ_API_KEY,
                "base_url": "https://api.groq.com/openai/v1",
                "api_type": "openai",
                "timeout": 1.0,  # 1-second timeout for API calls
                "max_tokens": 100  # Limit token generation for faster responses
            },
        ]

        # Define a wrapper for agent responses to handle timeouts
        def response_with_timeout(agent, recipient, message, timeout=1.0):
            """Call the agent with a timeout and fall back to a quick move if needed."""
            result = None
            
            def target():
                nonlocal result
                try:
                    # Try to get the AI response
                    result = agent.initiate_chat(recipient=recipient, message=message)
                except Exception as e:
                    print(f"Error in agent response: {e}")
            
            # Start thread to handle the AI response
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout)
            
            # If we timed out, force a move
            if thread.is_alive():
                print("Agent response timed out, making random move")
                # If we're waiting for a move, make a random one
                quick_move = make_quick_move()
                if quick_move:
                    execute_move(quick_move)
                return None
            
            return result

        agent_white = ConversableAgent(
            name="Agent_White",  
            system_message="You are a chess player playing as white. "
            "First call available_moves() to get legal moves. "
            "Then immediately call execute_move(move) with a valid move. "
            "Respond very quickly with minimal thinking. "
            "Any move is better than no move. "
            "Continue playing until the game ends in checkmate, stalemate, or draw.",
            llm_config={"config_list": agent_config_list, "cache_seed": None},
        )

        agent_black = ConversableAgent(
            name="Agent_Black",  
            system_message="You are a chess player playing as black. "
            "First call available_moves() to get legal moves. "
            "Then immediately call execute_move(move) with a valid move. "
            "Respond very quickly with minimal thinking. "
            "Any move is better than no move. "
            "Continue playing until the game ends in checkmate, stalemate, or draw.",
            llm_config={"config_list": agent_config_list, "cache_seed": None},
        )

        game_master = ConversableAgent(
            name="Game_Master",  
            llm_config=False,
            is_termination_msg=lambda msg: check_game_over(msg),
            default_auto_reply="Please make a move.",
            human_input_mode="NEVER",
        )

        register_function(
            execute_move,
            caller=agent_white,
            executor=game_master,
            name="execute_move",
            description="Call this tool to make a move.",
        )

        register_function(
            available_moves,
            caller=agent_white,
            executor=game_master,
            name="available_moves",
            description="Get legal moves.",
        )

        register_function(
            execute_move,
            caller=agent_black,
            executor=game_master,
            name="execute_move",
            description="Call this tool to make a move.",
        )

        register_function(
            available_moves,
            caller=agent_black,
            executor=game_master,
            name="available_moves",
            description="Get legal moves.",
        )

        # Configure White's response to Black
        agent_white.register_nested_chats(
            trigger=agent_black,
            chat_queue=[
                {
                    "sender": game_master,
                    "recipient": agent_white,
                    "summary_method": "last_msg",
                }
            ],
        )

        # Configure Black's response to White
        agent_black.register_nested_chats(
            trigger=agent_white,
            chat_queue=[
                {
                    "sender": game_master,
                    "recipient": agent_black,
                    "summary_method": "last_msg",
                }
            ],
        )

        # Main board display
        with col1:
            st.info("""
    This chess game is played automatically between two AI agents:
    - **Agent White**: A LLaMA 3 70B powered chess player controlling white pieces
    - **Agent Black**: A LLaMA 3 70B powered chess player controlling black pieces

    The game will continue until checkmate, stalemate, or insufficient material.
    """)

            # Create a placeholder for the chess board
            board_placeholder = st.empty()
            
            # Display the initial board
            if st.session_state.board_svg:
                board_placeholder.image(st.session_state.board_svg, caption="Current Board Position", use_column_width=True)
            else:
                initial_board_svg = chess.svg.board(st.session_state.board, size=400)
                board_placeholder.image(initial_board_svg, caption="Current Board Position", use_column_width=True)

            # Game status display
            status_placeholder = st.empty()
            if st.session_state.game_status != "Not started":
                if st.session_state.is_game_over:
                    status_placeholder.success(st.session_state.game_status)
                else:
                    status_placeholder.info(st.session_state.game_status)

            # Add the start game button
            start_button = st.empty()
            
            if not st.session_state.game_in_progress and not st.session_state.is_game_over:
                if start_button.button("Start New Game"):
                    # Reset game state
                    st.session_state.board.reset()
                    st.session_state.made_move = False
                    st.session_state.move_logs = []
                    st.session_state.board_svg = chess.svg.board(st.session_state.board, size=400)
                    st.session_state.game_status = "Game in progress"
                    st.session_state.is_game_over = False
                    st.session_state.game_in_progress = True
                    st.session_state.current_move = None
                    
                    # Update the status display
                    status_placeholder.info("Game in progress - AIs are playing...")
                    
                    # Start a new thread for the game to avoid blocking the UI
                    st.rerun()
            
            # If game is in progress but not over, continue the game
            if st.session_state.game_in_progress and not st.session_state.is_game_over:
                status_placeholder.info("Game in progress - AIs are playing...")
                
                try:
                    # Start the game with White's turn
                    initial_message = "Let's play chess! Make your move as white."
                    
                    # Start the game with our timeout mechanism
                    game_start_time = time.time()
                    
                    # Main game loop - continue until game is over
                    while not st.session_state.is_game_over:
                        # White's turn
                        if st.session_state.board.turn == chess.WHITE:
                            # Get white's move with timeout fallback
                            white_start = time.time()
                            white_move_result = response_with_timeout(
                                agent_black,  # Agent initiating the chat
                                agent_white,  # Agent making the move
                                initial_message if st.session_state.board.fullmove_number == 1 else "Make your move as white.",
                                timeout=1.0
                            )
                            print(f"White's move took {time.time() - white_start:.3f} seconds")
                            
                            # If game ended during white's move, break
                            if st.session_state.is_game_over:
                                break
                                
                            # If we timed out and made a random move, the turn would have changed
                            if st.session_state.board.turn == chess.BLACK:
                                # Update UI after each move
                                st.rerun()
                        
                        # Black's turn
                        else:
                            # Get black's move with timeout fallback
                            black_start = time.time()
                            black_move_result = response_with_timeout(
                                agent_white,  # Agent initiating the chat
                                agent_black,  # Agent making the move
                                "Make your move as black.",
                                timeout=1.0
                            )
                            print(f"Black's move took {time.time() - black_start:.3f} seconds")
                            
                            # If game ended during black's move, break
                            if st.session_state.is_game_over:
                                break
                                
                            # If we timed out and made a random move, the turn would have changed
                            if st.session_state.board.turn == chess.WHITE:
                                # Update UI after each move
                                st.rerun()
                        
                        # If no progress was made (neither player moved), make a random move
                        if time.time() - game_start_time > 5.0 and not st.session_state.is_game_over:
                            print("Game appears stuck, making random move")
                            random_move = make_quick_move()
                            if random_move:
                                execute_move(random_move)
                            else:
                                # If no random moves are available, the game is over
                                st.session_state.is_game_over = True
                                if not st.session_state.game_status.startswith("Game ended"):
                                    st.session_state.game_status = "Game ended in a draw - no legal moves"
                            
                            # Update UI
                            st.rerun()
                    
                    # Update game state after completion
                    st.session_state.game_in_progress = False
                    
                    # Update the game status based on the final board state
                    if st.session_state.board.is_checkmate():
                        winner = 'White' if st.session_state.board.turn == chess.BLACK else 'Black'
                        st.session_state.game_status = f"Checkmate! {winner} wins!"
                    elif st.session_state.board.is_stalemate():
                        st.session_state.game_status = "Game ended in stalemate!"
                    elif st.session_state.board.is_insufficient_material():
                        st.session_state.game_status = "Game ended - insufficient material to checkmate!"
                    else:
                        st.session_state.game_status = f"Game ended after {len(st.session_state.move_logs)} moves"
                    
                    # Refresh the UI
                    st.rerun()
                    
                except Exception as game_error:
                    st.error(f"Game error: {str(game_error)}")
                    st.session_state.game_in_progress = False
            
            # Reset button appears after the game is over
            if st.session_state.is_game_over:
                status_placeholder.success(st.session_state.game_status)
                if st.button("Start New Game"):
                    # Reset game state
                    st.session_state.board.reset()
                    st.session_state.made_move = False
                    st.session_state.move_logs = []
                    st.session_state.board_svg = chess.svg.board(st.session_state.board, size=400)
                    st.session_state.game_status = "Game in progress"
                    st.session_state.is_game_over = False
                    st.session_state.game_in_progress = True
                    st.session_state.current_move = None
                    
                    # Refresh the UI
                    st.rerun()
                
        # Move log display in the second column
        with col2:
            log_placeholder = st.empty()
            log_content = ""
            
            if st.session_state.move_logs:
                for i, log in enumerate(st.session_state.move_logs):
                    log_content += f"{i+1}. {log}\n"
                log_placeholder.text_area("Game Moves", log_content, height=500, key="move_log")
            else:
                log_placeholder.info("No moves made yet. Start a new game to see the move log.")
            
    except Exception as e:
        st.error(f"Error setting up the chess agents: {str(e)}")
else:
    st.error("GROQ API key not found. Please add it to your .env file.")