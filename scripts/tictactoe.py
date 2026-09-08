import sys
import json
import os
import random

STATE_FILE = "assets/tictactoe_state.json"
SVG_FILE = "assets/tictactoe.svg"
README_FILE = "README.md"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "board": [" "] * 9,
        "turn": "X",
        "status": "in_progress",
        "winner": null,
        "stats": {"community_wins": 0, "ai_wins": 0, "draws": 0, "total_games": 0},
        "last_player": "None",
        "last_move": None
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_winner(board):
    win_cond = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in win_cond:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    if " " not in board:
        return "Draw"
    return None

def minimax(board, depth, is_maximizing):
    result = check_winner(board)
    if result == "O": return 10 - depth
    elif result == "X": return depth - 10
    elif result == "Draw": return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = "O"
                score = minimax(board, depth + 1, False)
                board[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = "X"
                score = minimax(board, depth + 1, True)
                board[i] = " "
                best_score = min(score, best_score)
        return best_score

def best_move(board):
    # Minimax AI with 15% chance to make a suboptimal random move so humans can sometimes win!
    empty_spots = [i for i, v in enumerate(board) if v == " "]
    if random.random() < 0.15:
        return random.choice(empty_spots)
        
    best_score = -float('inf')
    move = empty_spots[0]
    for i in empty_spots:
        board[i] = "O"
        score = minimax(board, 0, False)
        board[i] = " "
        if score > best_score:
            best_score = score
            move = i
    return move

def render_svg(state):
    board = state["board"]
    stats = state["stats"]
    status_text = "⚡ YOUR TURN (X)"
    if state["status"] == "won_community": status_text = "🏆 YOU WON!"
    elif state["status"] == "won_ai": status_text = "🤖 MANAS-AI WON!"
    elif state["status"] == "draw": status_text = "🤝 DRAW!"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 320" width="600" height="320" font-family="ui-sans-serif,-apple-system,Segoe UI,Helvetica,sans-serif">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#0d1117" />
            <stop offset="100%" stop-color="#040711" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="neon_x">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur2" />
            <feMerge><feMergeNode in="blur2" /><feMergeNode in="blur1" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="neon_o">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur2" />
            <feMerge><feMergeNode in="blur2" /><feMergeNode in="blur1" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
    </defs>
    
    <rect width="600" height="320" rx="16" fill="url(#bg)" stroke="#30363d" stroke-width="2"/>
    
    <g transform="translate(40, 40)">
        <!-- Grid -->
        <line x1="80" y1="0" x2="80" y2="240" stroke="#1f242e" stroke-width="6" stroke-linecap="round"/>
        <line x1="160" y1="0" x2="160" y2="240" stroke="#1f242e" stroke-width="6" stroke-linecap="round"/>
        <line x1="0" y1="80" x2="240" y2="80" stroke="#1f242e" stroke-width="6" stroke-linecap="round"/>
        <line x1="0" y1="160" x2="240" y2="160" stroke="#1f242e" stroke-width="6" stroke-linecap="round"/>
        
        <!-- Cells -->
"""
    for i in range(9):
        x = (i % 3) * 80 + 40
        y = (i // 3) * 80 + 40
        val = board[i]
        if val == "X":
            svg_content += f"""
        <g transform="translate({x},{y})" filter="url(#neon_x)">
            <line x1="-20" y1="-20" x2="20" y2="20" stroke="#00f5d4" stroke-width="8" stroke-linecap="round"/>
            <line x1="-20" y1="20" x2="20" y2="-20" stroke="#00f5d4" stroke-width="8" stroke-linecap="round"/>
        </g>
"""
        elif val == "O":
            svg_content += f"""
        <circle cx="{x}" cy="{y}" r="22" fill="none" stroke="#7b2cbf" stroke-width="8" filter="url(#neon_o)"/>
"""
        else:
            svg_content += f"""
        <text x="{x}" y="{y+5}" font-size="12" fill="#30363d" text-anchor="middle" font-weight="bold">({i//3},{i%3})</text>
"""
            
    svg_content += f"""
    </g>

    <!-- Side Panel -->
    <g transform="translate(320, 40)">
        <text x="0" y="20" font-size="22" font-weight="900" fill="#ffffff" letter-spacing="1">PLAY VS MANAS-AI</text>
        <text x="0" y="45" font-size="14" fill="#8b949e">Minimax Agent Engine v2.4</text>
        
        <rect x="0" y="65" width="240" height="40" rx="6" fill="#161b22" stroke="#30363d" stroke-width="1"/>
        <text x="120" y="90" font-size="16" font-weight="bold" fill="{('#00f5d4' if state['status'] != 'won_ai' else '#7b2cbf')}" text-anchor="middle" filter="url(#glow)">{status_text}</text>

        <text x="0" y="140" font-size="14" font-weight="bold" fill="#c9d1d9">Global Match Record</text>
        
        <g transform="translate(0, 160)">
            <rect x="0" y="0" width="75" height="60" rx="6" fill="#161b22"/>
            <text x="37.5" y="25" font-size="20" font-weight="bold" fill="#00f5d4" text-anchor="middle">{stats['community_wins']}</text>
            <text x="37.5" y="45" font-size="10" fill="#8b949e" text-anchor="middle">Wins (X)</text>
            
            <rect x="82.5" y="0" width="75" height="60" rx="6" fill="#161b22"/>
            <text x="120" y="25" font-size="20" font-weight="bold" fill="#7b2cbf" text-anchor="middle">{stats['ai_wins']}</text>
            <text x="120" y="45" font-size="10" fill="#8b949e" text-anchor="middle">AI Wins (O)</text>
            
            <rect x="165" y="0" width="75" height="60" rx="6" fill="#161b22"/>
            <text x="202.5" y="25" font-size="20" font-weight="bold" fill="#e6edf3" text-anchor="middle">{stats['draws']}</text>
            <text x="202.5" y="45" font-size="10" fill="#8b949e" text-anchor="middle">Draws</text>
        </g>
        
        <text x="0" y="250" font-size="13" fill="#8b949e">Last Challenger:</text>
        <text x="0" y="270" font-size="15" font-weight="bold" fill="#58a6ff">@{state['last_player']}</text>
    </g>
</svg>"""

    with open(SVG_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)

def update_readme(state):
    board = state["board"]
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    start_marker = "<!-- TTT_START -->"
    end_marker = "<!-- TTT_END -->"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1: return

    base_url = "https://github.com/manas-shukla-101/manas-shukla-101/issues/new?title=ttt|play|{0}&body=Just+click+%27Submit+new+issue%27+to+play+at+index+{0}.+Manas-AI+will+counter-move+automatically!"
    
    grid = []
    for i in range(9):
        if board[i] == " ": grid.append(f"[ 🟦 Play ({i//3},{i%3}) ]({base_url.format(i)})")
        elif board[i] == "X": grid.append(" ❌ X")
        elif board[i] == "O": grid.append(" 🟣 O")

    reset_url = "https://github.com/manas-shukla-101/manas-shukla-101/issues/new?title=ttt|reset&body=Click+submit+to+start+a+new+match!"
    
    table_content = f"""
| Row 0 | Row 1 | Row 2 |
| :---: | :---: | :---: |
| {grid[0]} | {grid[1]} | {grid[2]} |
| {grid[3]} | {grid[4]} | {grid[5]} |
| {grid[6]} | {grid[7]} | {grid[8]} |

<div align="center">
  <br>
  <a href="{reset_url}"><img src="https://img.shields.io/badge/%F0%9F%94%84%20START%20NEW%20MATCH-0d1117?style=for-the-badge&logo=github&logoColor=00f5d4" alt="Reset Game"></a>
</div>
"""
    new_content = content[:start_idx + len(start_marker)] + "\n" + table_content + content[end_idx:]
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

def process_action(action, user):
    state = load_state()
    
    if "reset" in action.lower() or state["status"] != "in_progress":
        state["board"] = [" "] * 9
        state["status"] = "in_progress"
        state["last_player"] = user
        if "reset" in action.lower():
            state["stats"]["total_games"] += 1

    if "play" in action.lower() and state["status"] == "in_progress":
        try:
            idx = int(action.split("|")[-1])
            if 0 <= idx <= 8 and state["board"][idx] == " ":
                state["board"][idx] = "X"
                state["last_player"] = user
                
                win = check_winner(state["board"])
                if win == "X":
                    state["status"] = "won_community"
                    state["stats"]["community_wins"] += 1
                elif win == "Draw":
                    state["status"] = "draw"
                    state["stats"]["draws"] += 1
                else:
                    # AI Turn
                    ai_move = best_move(state["board"])
                    state["board"][ai_move] = "O"
                    win2 = check_winner(state["board"])
                    if win2 == "O":
                        state["status"] = "won_ai"
                        state["stats"]["ai_wins"] += 1
                    elif win2 == "Draw":
                        state["status"] = "draw"
                        state["stats"]["draws"] += 1
        except Exception as e:
            pass

    save_state(state)
    render_svg(state)
    update_readme(state)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, default="ttt|reset")
    parser.add_argument("--user", type=str, default="LocalUser")
    args = parser.parse_args()
    
    process_action(args.action, args.user)
