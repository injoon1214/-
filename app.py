import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="오목 게임", layout="centered")
st.title("오목 게임")

# 올려주신 이미지 기준 정식 19줄 바둑판 설정
GRID_SIZE = 19
BOARD_IMG_PATH = "board.png"
BLACK_IMG_PATH = "black.png"
WHITE_IMG_PATH = "white.png"

def crop_to_square(img):
    """이미지가 비정방형일 경우 중앙을 기준으로 1:1 비율 자르기"""
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
    
    # 구겨짐 방지: 돌 이미지를 1:1 비율 정사각형으로 보정
    black_img = crop_to_square(black_img)
    white_img = crop_to_square(white_img)
    
    return board_img, black_img, white_img

try:
    base_board, black_stone, white_stone = load_assets()
except Exception:
    st.error("⚠️ 이미지 파일(board.png, black.png, white.png)을 확인해 주세요.")
    st.stop()

# 게임 상태 초기화
if "board_state" not in st.session_state:
    st.session_state.board_state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1
    st.session_state.winner = None

def check_win(r, c, player):
    board = st.session_state.board_state
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

def generate_board_image():
    rendered = base_board.copy()
    w, h = rendered.size
    
    # 19줄 바둑판 정밀 여백 비율 계산
    margin = w * 0.038
    cell_size = (w - (2 * margin)) / (GRID_SIZE - 1)
    stone_size = int(cell_size * 0.95)
    
    # 고화질 리사이징(LANCZOS 필터) 적용
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

if st.session_state.winner:
    winner_name = "흑돌(●)" if st.session_state.winner == 1 else "백돌(○)"
    st.success(f"🎉 {winner_name} 승리!")
else:
    turn_name = "흑돌(●)" if st.session_state.current_player == 1 else "백돌(○)"
    st.info(f"현재 차례: {turn_name}")

coords = streamlit_image_coordinates(current_img, key="omok_board")

if coords and not st.session_state.winner:
    click_x, click_y = coords["x"], coords["y"]
    
    col = int(round((click_x - margin) / cell_size))
    row = int(round((click_y - margin) / cell_size))
    
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        if st.session_state.board_state[row][col] == 0:
            st.session_state.board_state[row][col] = st.session_state.current_player
            
            if check_win(row, col, st.session_state.current_player):
                st.session_state.winner = st.session_state.current_player
            else:
                st.session_state.current_player = 3 - st.session_state.current_player
            st.rerun()

if st.button("🔄 게임 다시 시작"):
    st.session_state.board_state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1
    st.session_state.winner = None
    st.rerun()