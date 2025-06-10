# constants.py

#화면 크기 관련 상수
TILE_SIZE = 100
UI_HEIGHT = 100
# WIDTH = None #main에서 모니터 크기에 따라 설정됨
# HEIGHT = None #main에서 모니터 크기에 따라 설정됨

# 플레이어 관련 상수
PLAYER_SIZE = TILE_SIZE
PLAYER_SPEED = 10
PLAYER_HP = 3
PLAYER_INVINCIBILITY = 5000 # 무적시간 5초
PLAYER_SPEED_INV = 10000 # 부스트 10초

# 키 아이템 관련 상수
KEY_SIZE = TILE_SIZE // 2

# 게임 타이머
GAME_TICK_MS = 33
GAME_DURATION = 60  # 게임 시간 (초)

POTION_SIZE = TILE_SIZE // 2
POTION_HEAL_AMOUNT = 1
POTION_COUNT_PER_PLAYER = 2  # 플레이어당 기본 포션 개수

OBSTACLE_SIZE = TILE_SIZE // 2