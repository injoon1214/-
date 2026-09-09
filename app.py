import streamlit as st

st.title("🎮 파이썬 웹 오목 게임")

GRID_SIZE = 15

# 게임 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1  # 1: 흑돌, 2: 백돌
    st.session_state.winner = None

def check_win(r, c, player):
    board = st.session_state.board
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

def make_move(r, c):
    if st.session_state.board[r][c] == 0 and not st.session_state.winner:
        st.session_state.board[r][c] = st.session_state.current_player
        if check_win(r, c, st.session_state.current_player):
            st.session_state.winner = st.session_state.current_player
        else:
            st.session_state.current_player = 3 - st.session_state.current_player

if st.session_state.winner:
    winner_text = "흑돌(●)" if st.session_state.winner == 1 else "백돌(○)"
    st.success(f"🎉 {winner_text} 승리!")
else:
    turn_text = "흑돌(●)" if st.session_state.current_player == 1 else "백돌(○)"
    st.info(f"현재 차례: {turn_text}")

if st.button("게임 다시 시작"):
    st.session_state.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    st.session_state.current_player = 1
    st.session_state.winner = None
    st.rerun()

# 바둑판 출력 (버튼 그리드)
for r in range(GRID_SIZE):
    cols = st.columns(GRID_SIZE)
    for c in range(GRID_SIZE):
        cell = st.session_state.board[r][c]
        label = "⚫" if cell == 1 else ("⚪" if cell == 2 else "➕")
        cols[c].button(label, key=f"{r}_{c}", on_click=make_move, args=(r, c))