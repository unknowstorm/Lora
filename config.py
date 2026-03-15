# --- НАЛАШТУВАННЯ ШЛЯХУ ---
SPRITE_DIR = 'assets'

# --- НАЛАШТУВАННЯ ДЛЯ ПРИВІТАННЯ ---
WELCOME_SPRITE = 'welcome/hello_01.png' # <<< Шлях до спрайту привітання
WELCOME_DURATION_MS = 3000 # Тривалість показу привітання: 3 секунди
# ------------------------------------

# --- НАЛАШТУВАННЯ АНІМАЦІЇ ---

# 1. IDLE: ОДИН статичний спрайт
IDLE_SPRITES = ['idle/idle_01.png'] 
ANIMATION_SPEED_MS = 10000 # Дуже повільна швидкість (10 сек), щоб animation_timer не спрацьовував у статичному режимі

# 4 кадри для анімації ходьбы праворуч (WALK)
WALK_SPRITES_RIGHT = [f'walk_right/walk_right_0{i}.png' for i in range(1, 5)] 

# 4 кадра для анімації ходьбы ліворуч (WALK)
WALK_SPRITES_LEFT = [f'walk_left/walk_left_0{i}.png' for i in range(1, 5)]

# --- НАЛАШТУВАННЯ МОРГАННЯ ---

# 2. BLINK: 7 кадрів для моргання (шляхи відносно папки 'assets/blink/')
BLINK_SPRITES = [f'blink/blink_0{i}.png' for i in range(1, 8)]
BLINK_FRAME_DURATION_MS = 30 # Прискорюємо кадри моргання для швидкого ефекту
BLINK_INTERVAL_MIN_SEC = 5 # Мінімальний інтервал моргання (секунди)
BLINK_INTERVAL_MAX_SEC = 15 # Максимальний інтервал моргання (секунди)

# --- НАЛАШТУВАННЯ ЛОГІКИ ПЕРЕМІЩЕННЯ ---

WALK_DECISION_INTERVAL_MS = 15000 # Помічник вирішує, чи йти, кожні 15 секунд
WALK_PIXELS_PER_STEP = 2 # Швидкість ходьби (2 пікселі за крок)
WALK_MAX_DISTANCE = 300 # Максимальна відстань для випадкової точки (пікселів)

PRESET_FILE = "presets.json" # Файл для збереження пресетів
