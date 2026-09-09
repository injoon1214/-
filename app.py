import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="이미지 오목 게임", layout="centered")
st.title("🎯 고화질 이미지 오목 게임")

GRID_SIZE = 15
BOARD_IMG_PATH = "board.png"
BLACK_IMG_PATH = "black.png"
WHITE_IMG_PATH = "white.png"

# 이미지 불러오기
@st.cache_data
def load_assets():
    board_img = Image.open(BOARD_IMG_PATH).convert("RGBA")
    black_img = Image.open(BLACK_IMG_PATH).convert("RGBA")
    white_img = Image.open(WHITE_IMG_PATH).convert("RGBA")
    return board_img, black_img, white_img

try:
    base_board, black_stone, white_stone = load_assets()
except Exception:
    st.error("⚠️ 이미지 파일(board.png, black.png, white.png)을 찾을 수 없습니다. 깃허브에 업로드했는지 확인해 주세요.")
    st.stop()

# 게임 상태 초기화
if "board_state" not in st.session_state:
    st.session_state.board_state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1  # 1: 흑돌, 2: 백돌
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

# 이미지에 돌을 합성하여 그리는 함수
def generate_board_image():
    rendered = base_board.copy()
    w, h = rendered.size
    
    # 여백 및 격자 간격 계산
    margin = w * 0.05
    cell_size = (w - (2 * margin)) / (GRID_SIZE - 1)
    stone_size = int(cell_size * 0.9)
    
    stone_b = black_stone.resize((stone_size, stone_size))
    stone_w = white_stone.resize((stone_size, stone_size))

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

# 현재 보드 이미지 그리기
current_img, margin, cell_size = generate_board_image()

# 상단 상태 표시
if st.session_state.winner:
    winner_name = "흑돌(●)" if st.session_state.winner == 1 else "백돌(○)"
    st.success(f"🎉 {winner_name} 승리!")
else:
    turn_name = "흑돌(●)" if st.session_state.current_player == 1 else "백돌(○)"
    st.info(f"현재 차례: {turn_name} (바둑판 교차점을 클릭하세요)")

# 이미지 클릭 이벤트 감지
coords = streamlit_image_coordinates(current_img, key="omok_board")

if coords and not st.session_state.winner:
    click_x, click_y = coords["x"], coords["y"]
    
    # 클릭 위치를 바둑판 행/열(0~14) 좌표로 변환
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

# 재시작 버튼
if st.button("🔄 게임 다시 시작"):
    st.session_state.board_state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1
    st.session_state.winner = None
    st.rerun()