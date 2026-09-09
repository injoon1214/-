import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
import random

st.set_page_config(page_title="오목 게임", layout="centered")
st.title("오목 게임")

# 19x19 정식 바둑판 설정
GRID_SIZE = 19
BOARD_IMG_PATH = "board.png"
BLACK_IMG_PATH = "black.png"
WHITE_IMG_PATH = "white.png"

def crop_to_square(img):
    """돌 이미지 구겨짐 방지: 중앙 기준 1:1 정사각형 자르기"""
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    return img.crop((left, top, left + min_dim, top + min_dim))

@st.cache_data
def load_assets():
    board_img = Image.open(BOARD_IMG_PATH).convert("RGBA")
    black_img = Image.open(BLACK_IMG_PATH).convert("RGBA")
    white_img = Image.open(WHITE_IMG_PATH).convert("RGBA")
    
    black_img = crop_to_square(black_img)
    white_img = crop_to_square(white_img)
    
    return board_img, black_img, white_img

try:
    base_board, black_stone, white_stone = load_assets()
except Exception:
    st.error("⚠️ 이미지 파일(board.png, black.png, white.png)을 확인해 주세요.")
    st.stop()

# 상단 모드 선택 라디오 버튼
mode = st.radio("🎮 게임 모드 선택", ["🤖 AI 대전 (혼자하기)", "👥 2인 대전 (친구와 같이)"], horizontal=True)
game_mode = "AI" if "AI" in mode else "PVP"

# 게임 상태 초기화 및 모드 변경 시 리셋
if "board_state" not in st.session_state or st.session_state.get("prev_mode") != game_mode:
    st.session_state.board_state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1  # 1: 흑돌, 2: 백돌
    st.session_state.winner = None
    st.session_state.last_click = None
    st.session_state.prev_mode = game_mode

def reset_game():
    st.session_state.board_state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1
    st.session_state.winner = None
    st.session_state.last_click = None

def check_win(board, r, c, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        for step in (1, -1):
            nr, nc = r + dr * step, c + dc * step
            while 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == player:
                count += 1
                nr += dr * step
                nc += dc * step
        if count >= 5:
            return True
    return False

# --- AI 가중치 계산 로직 ---
def evaluate_position(board, r, c, player):
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        consecutive = 1
        open_ends = 0

        # 정방향
        nr, nc = r + dr, c + dc
        while 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == player:
            consecutive += 1
            nr += dr; nc += dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == 0:
            open_ends += 1

        # 역방향
        nr, nc = r - dr, c - dc
        while 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == player:
            consecutive += 1
            nr -= dr; nc -= dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and board[nr][nc] == 0:
            open_ends += 1

        if consecutive >= 5:
            score += 100000
        elif consecutive == 4:
            score += 10000 if open_ends == 2 else 1000
        elif consecutive == 3:
            score += 1000 if open_ends == 2 else 100
        elif consecutive == 2:
            score += 100 if open_ends == 2 else 10
    return score

def get_ai_move(board):
    best_score = -1
    best_moves = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == 0:
                ai_attack = evaluate_position(board, r, c, 2)
                human_defense = evaluate_position(board, r, c, 1)
                score = ai_attack * 1.2 + human_defense
                if score > best_score:
                    best_score = score
                    best_moves = [(r, c)]
                elif score == best_score:
                    best_moves.append((r, c))
    if best_moves:
        return random.choice(best_moves)
    return (9, 9)

# 보드 이미지 생성
def generate_board_image():
    rendered = base_board.copy()
    w, h = rendered.size
    
    margin = w * 0.038
    cell_size = (w - (2 * margin)) / (GRID_SIZE - 1)
    stone_size = int(cell_size * 0.95)
    
    stone_b = black_stone.resize((stone_size, stone_size), Image.Resampling.LANCZOS)
    stone_w = white_stone.resize((stone_size, stone_size), Image.Resampling.LANCZOS)

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            stone_type = st.session_state.board_state[r][c]
            if stone_type != 0:
                center_x = margin + c * cell_size
                center_y = margin + r * cell_size
                top_left_x = int(center_x - stone_size / 2)
                top_left_y = int(center_y - stone_size / 2)
                
                stone_img = stone_b if stone_type == 1 else stone_w
                rendered.paste(stone_img, (top_left_x, top_left_y), stone_img)
                
    return rendered, margin, cell_size

current_img, margin, cell_size = generate_board_image()

# 승리 및 상태 표시 메시지
if st.session_state.winner:
    if game_mode == "AI":
        winner_name = "당신(흑돌)" if st.session_state.winner == 1 else "AI(백돌)"
    else:
        winner_name = "흑돌(●)" if st.session_state.winner == 1 else "백돌(○)"
    st.success(f"🎉 {winner_name} 승리!")
else:
    if game_mode == "AI":
        turn_name = "흑돌(●) - 당신의 차례입니다"
    else:
        turn_name = "흑돌(●) 차례입니다" if st.session_state.current_player == 1 else "백돌(○) 차례입니다"
    st.info(f"현재 상태: {turn_name}")

# 마우스 클릭 위치 감지
coords = streamlit_image_coordinates(current_img, key="omok_board")

# 클릭 처리
if coords and coords != st.session_state.last_click and not st.session_state.winner:
    st.session_state.last_click = coords
    click_x, click_y = coords["x"], coords["y"]
    
    col = int(round((click_x - margin) / cell_size))
    row = int(round((click_y - margin) / cell_size))
    
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        board = st.session_state.board_state
        current_p = st.session_state.current_player
        
        if board[row][col] == 0:
            # 플레이어 착수
            board[row][col] = current_p
            
            if check_win(board, row, col, current_p):
                st.session_state.winner = current_p
            else:
                if game_mode == "AI":
                    # AI 모드: 플레이어 착수 후 AI가 즉시 수비/공격 위치에 착수
                    ai_r, ai_c = get_ai_move(board)
                    board[ai_r][ai_c] = 2
                    if check_win(board, ai_r, ai_c, 2):
                        st.session_state.winner = 2
                    else:
                        st.session_state.current_player = 1
                else:
                    # 2인 대전 모드: 턴 교대
                    st.session_state.current_player = 3 - current_p
                    
            st.rerun()

# 리셋 버튼
if st.button("🔄 게임 다시 시작"):
    reset_game()
    st.rerun()