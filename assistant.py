import webbrowser
import sys
import os
import subprocess
import random
import json

REMINDER_FILE = "reminders.json"
PRESET_FILE = "presets.json"

# -----------------------------------------------------------
# --- ФУНКЦІЯ АВТОВСТАНОВЛЕННЯ ЗАЛЕЖНОСТЕЙ ---
# -----------------------------------------------------------

def install_dependencies():
    """Перевіряє та встановлює залежності, перелічені в requirements.txt."""
    try:
        # 1. Строго перевіряємо, не викликаючи виключення
        import PyQt5.QtWidgets 
        return True # Встановлено
    except ImportError:
        print("Бібліотеку PyQt5 не знайдено. Запуск встановлення...")
        
        # ... (логіка пошуку requirements.txt) ...
        requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
        
        if not os.path.exists(requirements_path):
            # ... (обробка помилки, якщо requirements.txt не знайдено) ...
            return False 

        try:
            # Виконуємо команду: pip install -r requirements.txt
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            
            print("--- Встановлення завершено ---")
            print("\n✅ Налаштування PyQt5 завершено. Будь ласка, перезапустіть програму.")
            sys.exit(0) # Успішно встановили, завершуємо скрипт
            
        except subprocess.CalledProcessError:
            print("\n!!! КРИТИЧНА ПОМИЛКА ВСТАНОВЛЕННЯ !!!")
            print("Не вдалося встановити залежність. Переконайтеся, що 'pip' доступний.")
            sys.exit(1)
        except Exception as e:
            print(f"\nНевідома помилка під час встановлення: {e}")
            sys.exit(1)

# -----------------------------------------------------------
#--- ЗАПУСК ПЕРЕВІРКИ ---
# -----------------------------------------------------------

if not install_dependencies():
    # Якщо install_dependencies повернула False (наприклад, не знайшла requirements.txt), 
    # ми не можемо продовжувати, і sys.exit(1) вже був викликаний.
    pass 

# -----------------------------------------------------------
# --- ІМПОРТИ PyQt5 І КОНСТАНТ ---
# -----------------------------------------------------------

# Тепер, коли ми впевнені, що PyQt5 встановлена, імпортуємо її
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QAction, QMenu, QMessageBox, 
    QDesktopWidget,
    QDialog, QTextEdit,
    QVBoxLayout, QHBoxLayout,
    QPushButton,
    QLabel, QTimeEdit, QDateTimeEdit,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QFileDialog
)
from PyQt5.QtGui import QPixmap, QIntValidator

from PyQt5.QtCore import (
    Qt, QTime, QTimer, QDate, QDateTime, QPoint, QRect, QSize, QCoreApplication
)

# Імпортуємо всі константи з файлу config.py
from config import (
    SPRITE_DIR, IDLE_SPRITES, ANIMATION_SPEED_MS, 
    WALK_SPRITES_RIGHT, WALK_SPRITES_LEFT, WALK_DECISION_INTERVAL_MS, WALK_PIXELS_PER_STEP, WALK_MAX_DISTANCE,
    BLINK_SPRITES, BLINK_FRAME_DURATION_MS, BLINK_INTERVAL_MIN_SEC,
    BLINK_INTERVAL_MAX_SEC,
    PRESET_FILE,
    WELCOME_SPRITE,
    WELCOME_DURATION_MS
)

class NoteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 Нова Замітка")
        self.setGeometry(150, 150, 400, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Створюємо елементи інтерфейсу

        # Розміщуємо елементи у вертикальному макеті
        layout = QVBoxLayout()

        # 1. Поле для Заголовка (НОВЕ)
        layout.addWidget(QLabel("**Заголовок Замітки (опціонально):**"))
        self.title_edit = QLineEdit(self)
        layout.addWidget(self.title_edit)

        # 2. Поле для Тексту
        layout.addWidget(QLabel("\n**Текст Замітки:**"))
        self.text_editor = QTextEdit(self)
        layout.addWidget(self.text_editor)


        # --- Прапорець активації нагадування ---
        self.reminder_checkbox = QCheckBox("⏰ Увімкнути нагадування", self)
        self.reminder_checkbox.setChecked(False) # За замовчуванням вимкнено
        self.reminder_checkbox.stateChanged.connect(self.toggle_datetime_editor) # Підключення логіки
        layout.addWidget(self.reminder_checkbox)

        # --- Поле для нагадування ---
        # reminder_label = QLabel("⏰ Час Нагадування (опціонально):") # Видаляємо, бо є прапорець

        self.datetime_edit = QDateTimeEdit(self)
        self.datetime_edit.setCalendarPopup(True)

        # Встановлюємо поточний час як мінімальне значення за замовчуванням
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(60)) # Поточний час + 1 хвилина
        self.datetime_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.datetime_edit.setEnabled(False) # <<< ВИМКНЕНО ЗА ЗАМОВЧУВАННЯМ
        layout.addWidget(self.datetime_edit)

        # --- Кнопка Зберегти ---
        self.save_button = QPushButton("✅ Зберегти", self)
        self.save_button.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.save_button)

        # self.save_button.clicked.connect(self.accept) # Закриваємо діалог та повертаємо дані
        
        
        self.setLayout(layout)

    
    def validate_and_accept(self):
        """Перевіряє наявність тексту перед закриттям діалогу."""
        if not self.text_editor.toPlainText().strip() and not self.title_edit.text().strip():
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть заголовок або текст для нотатки.")
            return

            # Якщо текст є, викликаємо accept()
        self.accept()

    # <<< НОВИЙ МЕТОД ДЛЯ УПРАВЛІННЯ СТАНОМ QDateTimeEdit

    def toggle_datetime_editor(self, state):
        """Активація/деактивація поля QDateTimeEdit відповідно до прапорця."""
        self.datetime_edit.setEnabled(state == Qt.Checked) # Використовуймо Qt.Checked для ясності

        # state == 2 означає checked, state == 0 означає unchecked
        # self.datetime_edit.setEnabled(state == 2)

    def get_data(self):
        """Повертає текст нотатки, час нагадування та стан активації."""
        return {
            'title': self.title_edit.text().strip(),             
            'text': self.text_editor.toPlainText().strip(),
            'datetime': self.datetime_edit.dateTime(),
            'is_reminder_active': self.reminder_checkbox.isChecked()
        }

class ReminderSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗓️ Налаштування Нагадування/Звички")
        self.setGeometry(100, 100, 450, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # Прибираємо кнопку "?"
        self.radio_group = QButtonGroup(self)

        # --- Елементи інтерфейсу ---
        layout = QVBoxLayout()
        
        # 1. Поле для назви / тексту
        layout.addWidget(QLabel("**Назва Звички/Текст Нагадування:**"))
        self.title_edit = QLineEdit(self)
        layout.addWidget(self.title_edit)
        
        # 2. Час першого спрацювання (для одноразового чи першого повтору)
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("**Перше спрацювання (Дата/Час):**"))
        self.datetime_edit = QDateTimeEdit(self)
        self.datetime_edit.setCalendarPopup(True)
        # Поточний час + 1 хвилина за замовчуванням
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.datetime_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        time_layout.addWidget(self.datetime_edit)
        layout.addLayout(time_layout)

        # 3. Налаштування періодичності (Радіокнопки)
        layout.addWidget(QLabel("\n**Періодичність:**"))
        
        self.repetition_layout = QHBoxLayout()
        
        # Створюємо QRadioButton
        self.radio_once = QRadioButton("Одноразово")
        self.radio_once.setChecked(True) # За замовчуванням
        self.radio_daily = QRadioButton("Щоденно")
        self.radio_hourly = QRadioButton("Щогодинно")
        self.radio_custom = QRadioButton("Кожні X хвилин")

        # Згрупувати їх (для гарантії вибору одного)
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_once)
        self.radio_group.addButton(self.radio_daily)
        self.radio_group.addButton(self.radio_hourly)
        self.radio_group.addButton(self.radio_custom)
        
        self.repetition_layout.addWidget(self.radio_once)
        self.repetition_layout.addWidget(self.radio_daily)
        self.repetition_layout.addWidget(self.radio_hourly)
        self.repetition_layout.addWidget(self.radio_custom)
        
        layout.addLayout(self.repetition_layout)
        
        # 4. Поле для кастомного інтервалу
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Інтервал (хв):"))
        self.custom_interval_edit = QLineEdit("60")
        self.custom_interval_edit.setValidator(QIntValidator(1, 1440)) # Від 1 хв до 24 годин
        custom_layout.addWidget(self.custom_interval_edit)
        custom_layout.addStretch()
        layout.addLayout(custom_layout)

        # Логіка активації полів
        self.radio_custom.toggled.connect(lambda state: self.custom_interval_edit.setEnabled(state))
        self.custom_interval_edit.setEnabled(False) 
        
        # 5. Кнопка Зберегти
        self.save_button = QPushButton("Зберегти Нагадування")
        self.save_button.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)

    def validate_and_accept(self):
        """Перевіряє наявність тексту та валідність інтервалу."""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть назву для нагадування.")
            return

        if self.radio_custom.isChecked():
            try:
                interval = int(self.custom_interval_edit.text())
                if interval <= 0 or interval > 1440:
                    QMessageBox.warning(self, "Помилка", "Інтервал має бути від 1 до 1440 хвилин.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Помилка", "Некоректний інтервал.")
                return

        self.accept()

    def get_data(self):
        """Повертає всі дані, необхідні для планування."""
        repetition = 'once'
        interval_ms = 0
        
        if self.radio_daily.isChecked():
            repetition = 'daily'
        elif self.radio_hourly.isChecked():
            repetition = 'hourly'
        elif self.radio_custom.isChecked():
            repetition = 'custom'
            try:
                # Конвертуємо хвилини в мілісекунди
                interval_ms = int(self.custom_interval_edit.text()) * 60 * 1000
            except:
                pass # Помилка вже була оброблена у validate_and_accept

        return {
            'text': self.title_edit.text().strip(),
            'datetime': self.datetime_edit.dateTime(),
            'repetition': repetition,
            'interval_ms': interval_ms
        }

class PresetDialog(QDialog):
    """Діалог для створення/редагування пресету."""
    def __init__(self, parent=None, preset_data=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Створення/Редагування Пресету")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        
        # 1. Назва Пресету
        layout.addWidget(QLabel("**Назва Пресету:**"))
        self.name_edit = QLineEdit(self)
        layout.addWidget(self.name_edit)

        # Створюємо горизонтальний макет для інструкції та кнопки
        path_instruction_layout = QHBoxLayout()
        
        # 2. Інструкція та Кнопка
        path_instruction_label = QVBoxLayout()
        layout.addWidget(QLabel("\n**Шляхи/Посилання (кожне з нового рядка):**"))
        layout.addWidget(QLabel("*(Приклад: C:\\Program Files\\app.exe або https://youtube.com)*"))

        path_instruction_layout.addLayout(path_instruction_label)
        
        # Кнопка "Обрати Файл"
        self.browse_button = QPushButton("... Обрати Файл/Програму")
        self.browse_button.setFixedWidth(200) # Фіксуємо ширину для кращого вигляду
        self.browse_button.clicked.connect(self.browse_file) # Підключення нового методу
        path_instruction_layout.addWidget(self.browse_button)
        
        # <<< НОВА КНОПКА
        self.program_list_button = QPushButton("📚 Обрати зі Списку") 
        self.program_list_button.setFixedWidth(200) 
        self.program_list_button.clicked.connect(self.show_program_selector)
        path_instruction_layout.addWidget(self.program_list_button)
        # КІНЕЦЬ НОВОЇ КНОПКИ >>>

        path_instruction_layout.addStretch() # Відсунути кнопку вправо
        
        layout.addLayout(path_instruction_layout) # Додаємо горизонтальний макет

        # 3. Поле для шляхів/посилань
        self.items_edit = QTextEdit(self)
        self.items_edit.setPlaceholderText("Введіть шляхи або посилання, або натисніть кнопку 'Обрати Файл'")
        layout.addWidget(self.items_edit)

        # 4. Логіка розміру (ЗАГЛУШКА, але збираємо дані)
        layout.addWidget(QLabel("\n**Налаштування Розміру (опціонально):**"))
        size_layout = QHBoxLayout()
        self.width_edit = QLineEdit("800")
        self.width_edit.setPlaceholderText("Ширина")
        self.width_edit.setValidator(QIntValidator(100, 10000))
        self.height_edit = QLineEdit("600")
        self.height_edit.setPlaceholderText("Висота")
        self.height_edit.setValidator(QIntValidator(100, 10000))
        size_layout.addWidget(self.width_edit)
        size_layout.addWidget(self.height_edit)
        size_layout.addStretch()
        layout.addLayout(size_layout)

        # 5. Кнопка Зберегти
        self.save_button = QPushButton("✅ Зберегти Пресет")
        self.save_button.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        
        # Завантажуємо дані, якщо режим редагування
        if preset_data:
            self.name_edit.setText(preset_data.get('name', ''))
            self.items_edit.setText('\n'.join(preset_data.get('items', [])))
            self.width_edit.setText(str(preset_data.get('width', 800)))
            self.height_edit.setText(str(preset_data.get('height', 600)))
        
    def browse_file(self):
        """Відкриває діалог вибору файлу та вставляє обраний шлях у поле."""
        # Фільтр для Windows-виконуваних файлів
        file_filter = "Виконувані файли (*.exe);;Всі файли (*)"
        
        # Виклик QFileDialog.getOpenFileName
        # self - батьківське вікно
        # "Оберіть виконуваний файл (.exe)" - заголовок діалогу
        # "" - початкова директорія (порожньо = поточна або остання використана)
        # file_filter - застосовуваний фільтр
        filepath, _ = QFileDialog.getOpenFileName(self, 
                                                  "Оберіть виконуваний файл/програму", 
                                                  "", 
                                                  file_filter)
        
        if filepath:
            # 1. Отримуємо поточний текст
            current_text = self.items_edit.toPlainText().strip()
            
            # 2. Визначаємо, чи потрібно додати перенесення рядка
            if current_text:
                # Якщо поле не порожнє, додаємо шлях з нового рядка
                self.items_edit.setText(current_text + '\n' + filepath)
            else:
                # Якщо поле порожнє, просто вставляємо шлях
                self.items_edit.setText(filepath)

    def show_program_selector(self):
        """Викликає діалог для вибору програми зі системних шляхів."""
        dialog = ProgramSelectorDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_path = dialog.get_selected_path()
            if selected_path:
                # Додаємо обраний шлях у текстове поле items_edit
                current_text = self.items_edit.toPlainText().strip()
                if current_text:
                    self.items_edit.setText(current_text + '\n' + selected_path)
                else:
                    self.items_edit.setText(selected_path)

    def validate_and_accept(self):
        """Перевіряє наявність назви та хоча б одного елемента."""
        name = self.name_edit.text().strip()
        items = self.items_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть назву пресету.")
            return

        if not items:
            QMessageBox.warning(self, "Помилка", "Будь ласка, додайте хоча б один шлях або посилання.")
            return

        self.accept()

    def get_data(self):
        """Повертає дані пресету."""
        return {
            'name': self.name_edit.text().strip(),
            'items': [item.strip() for item in self.items_edit.toPlainText().split('\n') if item.strip()],
            'width': int(self.width_edit.text()) if self.width_edit.text().isdigit() else 800,
            'height': int(self.height_edit.text()) if self.height_edit.text().isdigit() else 600,
        }

class ManagePresetsDialog(QDialog):
    """Діалог для керування (відкриття/видалення) пресетів."""
    def __init__(self, parent=None, presets=None):
        super().__init__(parent)
        self.setWindowTitle("📂 Керування Пресетами")
        self.setGeometry(200, 200, 350, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.presets = presets if presets is not None else []
        self.selected_preset_index = -1
        
        layout = QVBoxLayout()
        
        self.list_label = QLabel("Оберіть пресет для дії:")
        layout.addWidget(self.list_label)
        
        self.preset_list = QListWidget()
        for p in self.presets:
            self.preset_list.addItem(p['name'])
        layout.addWidget(self.preset_list)

        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("▶️ Відкрити")
        self.open_button.clicked.connect(lambda: self.select_action('open'))
        button_layout.addWidget(self.open_button)

        self.delete_button = QPushButton("🗑️ Видалити")
        self.delete_button.clicked.connect(lambda: self.select_action('delete'))
        button_layout.addWidget(self.delete_button)

        self.edit_button = QPushButton("✏️ Редагувати")
        self.edit_button.clicked.connect(lambda: self.select_action('edit'))
        button_layout.addWidget(self.edit_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def select_action(self, action):
        """Встановлює вибраний індекс та приймає діалог з кодом дії."""
        selected_items = self.preset_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть пресет.")
            return
            
        # Знаходимо індекс вибраного пресету
        self.selected_preset_index = self.preset_list.row(selected_items[0])

        self.done(self.Accepted + (1 if action == 'open' else 2 if action == 'delete' else 3))

        # self.done(self.Result.Accepted + (1 if action == 'open' else 2 if action == 'delete' else 3)) # 1=Open, 2=Delete, 3=Edit

    def get_selected_index(self):
        return self.selected_preset_index

class ProgramSelectorDialog(QDialog):
    """Діалог для вибору програм з поширених системних шляхів (частини PATH)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Швидкий Вибір Програми")
        self.setGeometry(200, 200, 450, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.selected_path = None

        layout = QVBoxLayout()

        self.label = QLabel("Оберіть програму зі списку (пошук у системних шляхах):")
        layout.addWidget(self.label)

        # ДОДАНО: Індикатор статусу
        self.status_label = QLabel("Очікування...")
        self.status_label.setStyleSheet("color: #0078d4; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Поле пошуку
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук за назвою...")
        self.search_edit.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_edit)

        # Список програм
        self.program_list = QListWidget()
        self.program_list.itemDoubleClicked.connect(self.select_and_accept)
        layout.addWidget(self.program_list)

        # Кнопки
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("✅ Обрати")
        self.select_button.clicked.connect(self.select_and_accept)
        self.cancel_button = QPushButton("❌ Скасувати")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.load_programs()

    def load_programs(self):
        """Збирає програми з поширених системних директорій."""
        self.program_list.clear()
        
        # 💡 ІНІЦІАЛІЗУЄМО СЛОВНИК ОДИН РАЗ НА ПОЧАТКУ
        found_programs = {} # {ім'я: повний_шлях}. Використовуємо словник для уникнення дублікатів та зберігання шляху

        self.status_label.setText("Початок сканування системних шляхів (PATH)...")
        QCoreApplication.processEvents() # Примусове оновлення GUI
        
        # 1. Збір шляхів для ПРОСТОГО сканування (PATH та Start Menu)
        system_paths_simple = os.environ.get('PATH', '').split(os.pathsep)
        
        # Додаткові шляхи для Windows (для .lnk чи .exe) - часто там знаходяться ярлики
        if os.name == 'nt':
            app_data = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            public_start = os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            system_paths_simple.extend([app_data, public_start])
        
        # 2. Збір шляхів для РЕКУРСИВНОГО сканування (Program Files)
        program_files_paths_recursive = []
        if os.name == 'nt':

            # 1. Основний Program Files (зазвичай x64)
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            
            # 2. Program Files (x86) для 32-бітних програм
            program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
            
            program_files_paths_recursive.extend([program_files, program_files_x86])

        

        # ----------------------------------------------------
        # 3. ПОШУК У PROGRAM FILES (РЕКУРСИВНИЙ)
        # ----------------------------------------------------
        self.status_label.setText("Сканування Program Files (може зайняти кілька секунд)...")
        QCoreApplication.processEvents() # Примусове оновлення GUI

        # Визначаємо, які розширення ми шукаємо (тільки EXE та LNK)
        EXECUTABLE_EXTENSIONS = ('.exe', '.lnk')

        for root_path in program_files_paths_recursive:
            if not os.path.isdir(root_path):
                continue
            
            try:
                # os.walk рекурсивно проходить по всіх підпапках
                for root, dirs, files in os.walk(root_path):
                    
                    # ОПТИМІЗАЦІЯ: Обмежуємо глибину сканування
                    # Програма не має бути глибше 4-5 рівнів
                    depth = root.count(os.sep) - root_path.count(os.sep)
                    if depth > 5: # Збільшуємо до 5, щоб захопити більше
                        dirs.clear() # Не заходимо далі
                        continue
                        
                    # ОПТИМІЗАЦІЯ: Пропускаємо системні папки з DLL та ті, що не потрібні
                    dirs[:] = [d for d in dirs if d not in ['Common Files', 'Reference Assemblies', 'InstallShield Installation Information']]

                    # ОПТИМІЗАЦІЯ: Пропускаємо системні папки з DLL
                    # if 'Common Files' in dirs:
                    #     dirs.remove('Common Files') 
                        
                    for filename in files:
                        full_path = os.path.join(root, filename)
                        
                        # Фільтр для виконуваних файлів
                        is_executable = filename.lower().endswith(EXECUTABLE_EXTENSIONS)
                        
                        if is_executable: # and os.access(full_path, os.X_OK):
                            name = os.path.splitext(filename)[0]
                            
                            # Ігноруємо службові файли
                            if name.lower() not in ['unins000', 'uninstall', 'setup', 'update', 'temp'] and name not in found_programs:
                                found_programs[name] = full_path
                                
            except PermissionError:
                continue
            except Exception:
                continue

        # ----------------------------------------------------
        # 4. ПОШУК У PATH ТА START MENU (НЕ-РЕКУРСИВНИЙ)
        # ----------------------------------------------------

        self.status_label.setText(f"Сканування PATH та ярликів. Знайдено {len(found_programs)} програм...")
        QCoreApplication.processEvents() # Примусове оновлення GUI

        for path in system_paths_simple:
            path = path.strip()
            if not os.path.isdir(path):
                continue
            
            try:
                for filename in os.listdir(path):
                    full_path = os.path.join(path, filename)

                    # Фільтруємо: Тільки файли І лише з потрібними розширеннями
                    is_executable = filename.lower().endswith(EXECUTABLE_EXTENSIONS)

                    # Фільтруємо лише виконувані файли (файли, а не директорії)
                    if os.path.isfile(full_path) and is_executable: # and os.access(full_path, os.X_OK):

                        # name = filename

                        # if os.name == 'nt':

                        # Прибираємо розширення тільки для Windows, щоб мати чисте ім'я

                        # На Windows: прибираємо .exe, .bat тощо для відображення
                        name = os.path.splitext(filename)[0]
                             
                        # Додаємо лише унікальні імена
                        if name not in found_programs:
                            found_programs[name] = full_path

            except PermissionError:
                # Ігноруємо шляхи, до яких немає доступу
                continue
            except Exception:
                continue

        # ----------------------------------------------------
        # 5. ВІДОБРАЖЕННЯ (без змін)
        # ----------------------------------------------------

        # Сортуємо та додаємо до списку
        for name in sorted(found_programs.keys()):
            # Використовуємо basename для більш чистого відображення повного шляху
            
            display_name = f"{name} ({os.path.basename(found_programs[name])})"
            
            self.program_list.addItem(display_name)

            # self.program_list.addItem(f"{name} ({os.path.basename(found_programs[name])})")
            
            # Шукаємо елемент, щоб додати до нього повний шлях
            # Зберігаємо повний шлях у QListWidgetItem через userData
            
            item = self.program_list.findItems(display_name, Qt.MatchExactly)

            if item:
                item[0].setData(Qt.UserRole, found_programs[name])

            # item = self.program_list.findItems(f"{name} ({os.path.basename(found_programs[name])})", Qt.MatchExactly)[0]
            # item.setData(Qt.UserRole, found_programs[name])

        self.all_items = [self.program_list.item(i) for i in range(self.program_list.count())]
        self.status_label.setText(f"Готово! Знайдено {len(found_programs)} унікальних програм.")

    def filter_list(self, text):
        """Фільтрує список програм відповідно до тексту пошуку."""
        search_text = text.lower()
        for i in range(self.program_list.count()):
            item = self.program_list.item(i)
            # Приховуємо/показуємо елемент
            item.setHidden(search_text not in item.text().lower())


    def select_and_accept(self):
        """Отримує обраний шлях і закриває діалог."""
        selected_items = self.program_list.selectedItems()
        if selected_items:
            # Отримуємо повний шлях, збережений у UserRole
            self.selected_path = selected_items[0].data(Qt.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть програму зі списку.")

    def get_selected_path(self):
        return self.selected_path

class VirtualAssistant(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- Стан анімації ---
        self.current_sprite_index = 0
        self.current_sprites = IDLE_SPRITES
        self.is_moving = False
        self.facing_right = True
        
        # --- СТАН ДЛЯ ПРИВІТАННЯ ---
        self.is_welcoming = True # <<< ФЛАГ ПРИВІТАННЯ

        # --- НОВИЙ СТАН ДЛЯ МОРГАННЯ ---
        self.is_blinking = False # Прапор: чи активна анімація моргання

        # --- НОВИЙ СТАН: Нагадування ---
        # self.reminders = [] # Список для зберігання QTimer та тексту нагадувань

        # --- СТАН: Нагадування (з ID та інформацією) ---
        # Зберігаємо тут об'єкти {id, timer, text, repetition}
        self.active_reminders = [] 
        self.reminder_id_counter = 1 # Унікальний ID для кожного нагадування

        # --- Пресети ---
        self.presets = [] # <--- СПИСОК ПРЕСЕТІВ

        # --- Ініціалізація Таймера ---
        self.active_countdown_timer = QTimer()
        self.active_countdown_timer.setSingleShot(True) # Одноразовий таймер
        self.active_countdown_timer_name = ""

        # ...
        ######################################
        
        # --- Стан руху ---
        self.target_pos = QPoint()
        self.direction = QPoint(0, 0) # Напрямок руху (dx, dy)
        
        # --- Режим руху ---
        self.move_mode = 'free' 
        
        # --- Режим сну ---
        self.is_sleeping = False

        self.initUI()

        # --- ТАЙМЕРИ ЗАПУСКАЮТЬСЯ ПІСЛЯ ПРИВІТАННЯ ---
        # self.start_timers() # ЦЕЙ ВИКЛИК ПЕРЕНОСИМО В end_welcome()

        # НОВИЙ ВИКЛИК: Завантажуємо нагадування та пресети при старті
        self.load_reminders()
        self.load_presets() # <--- НОВИЙ ВИКЛИК

        # 🌟 НОВИЙ ВИКЛИК ПРИВІТАННЯ 🌟
        self.show_welcome_animation()

    def initUI(self):
        # 1. Налаштування вікна для прозорості та відсутності рамки
        self.setWindowFlags(
            Qt.FramelessWindowHint |     
            Qt.WindowStaysOnTopHint |    
            Qt.Tool                     
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True) 
        
        # 2. Створення QLabel для відображення спрайтів
        self.label = QLabel(self)
        
        # Завантажуємо перший спрайт IDLE для ініціалізації розміру
        if not self.load_sprite(IDLE_SPRITES[0]):
             return 

        # Розміщуємо помічника у початковій точці (праворуч внизу)
        screen_geo = QDesktopWidget().availableGeometry()
        self.move(screen_geo.width() - self.width(), screen_geo.height() - self.height() - 50)
        
        self.show()

    # ----------------------------------------
    # --- МЕТОДИ ДЛЯ АНІМАЦІЇ ПРИВІТАННЯ ---
    # ----------------------------------------

    def show_welcome_animation(self):
        """Завантажує спрайт привітання та планує повернення до IDLE."""
        
        # 1. Завантажуємо спрайт "Махання рукою"
        if not self.load_sprite(WELCOME_SPRITE):
            # Якщо спрайту немає, переходимо одразу до стандартного запуску
            self.end_welcome()
            return
            
        # 2. Створюємо одноразовий таймер для завершення привітання
        self.welcome_timer = QTimer(self)
        self.welcome_timer.setSingleShot(True)
        self.welcome_timer.timeout.connect(self.end_welcome)
        self.welcome_timer.start(WELCOME_DURATION_MS)

    def end_welcome(self):
        """Завершує анімацію привітання та запускає основні таймери."""
        self.is_welcoming = False
        
        # 1. Повертаємо помічника до статичного IDLE-спрайта
        if not self.load_sprite(IDLE_SPRITES[0]):
             return 

        # 2. Запускаємо основні таймери (анімація, рух, моргання)
        self.start_timers()
        
    # ----------------------------------------

    # ... (load_sprite залишається без змін) ...
    def load_sprite(self, filename):
        """Завантажує та відображає спрайт, підганяючи розмір вікна під нього."""
        path = os.path.join(SPRITE_DIR, filename)
        
        if not os.path.exists(path):
            QMessageBox.critical(self, "Помилка Спрайту", 
                                 f"Спрайт не знайдено: {path}. Перевірте шляхи в config.py.")
            return False

        pixmap = QPixmap(path)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.size())
        self.resize(pixmap.size())
        return True
    # ----------------------------------------
    
    # --- СИСТЕМА ТАЙМЕРіВ ---

    def start_timers(self):
        """Запускає всі необхідні таймери: анімації та логіки руху."""
        
        # 1. Таймер для покадрової анімації (змінюватиме швидкість)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_sprite)
        self.animation_timer.start(ANIMATION_SPEED_MS) # Старт з 10000 мс (Static IDLE)
        
        # 2. Таймер для логіки прийняття рішень (рух)
        self.decision_timer = QTimer(self)
        self.decision_timer.timeout.connect(self.make_move_decision)
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)
        
        # 3. Таймер для плавної ходьби
        self.walk_timer = QTimer(self)
        self.walk_timer.timeout.connect(self.update_position)

        ### КОД ДЛЯ МОРГАННЯ ###
        # 4. Таймер для прийняття рішення про моргання (повільний, одноразовий)
        self.blink_decision_timer = QTimer(self)
        self.blink_decision_timer.setSingleShot(True)
        self.blink_decision_timer.timeout.connect(self.start_blink)
        self.schedule_next_blink() # Запускаємо першу перевірку
        ##############################

    ### НОВІ МЕТОДИ ДЛЯ МОРГАННЯ ###
    def schedule_next_blink(self):
        """Планує наступну анімацію моргання у випадковий час."""
        if not self.is_blinking: # Перевірка потрібна, якщо викликається з інших місць
            interval_sec = random.randint(BLINK_INTERVAL_MIN_SEC, BLINK_INTERVAL_MAX_SEC)
            self.blink_decision_timer.start(interval_sec * 1000)

    def start_blink(self):
        """Запускає анімацію моргання."""

        if self.is_sleeping: # <<< ПЕРЕВІРКА СТАНУ
            self.schedule_next_blink() # Потрібно перепланувати моргання на майбутнє
            return

        if self.is_moving:
            self.schedule_next_blink() # Якщо рухається, плануємо пізніше
            return

        if self.is_welcoming: # <<< ДОДАНО ПЕРЕВІРКУ
            self.schedule_next_blink() 
            return
            
        self.is_blinking = True
        
        # 1. Встановлюємо швидкість таймера для швидкої анімації моргання
        self.animation_timer.setInterval(BLINK_FRAME_DURATION_MS)
        
        # 2. Форсуємо перемикання на спрайти моргання
        self.current_sprites = BLINK_SPRITES
        self.current_sprite_index = -1 # Скидаємо на -1, щоб update_sprite почав з 0
        
        # 3. Викликаємо update_sprite, щоб негайно завантажити перший кадр
        self.update_sprite()

    def stop_blink(self):
        """Повертає помічника до статичного IDLE після моргання."""
        self.is_blinking = False
        
        # 1. Повертаємо швидкість таймера на Static IDLE (10000 мс)
        self.animation_timer.setInterval(ANIMATION_SPEED_MS)
        
        # 2. Форсуємо перемикання на статичний IDLE-спрайт
        self.current_sprites = IDLE_SPRITES
        self.current_sprite_index = 0 # Фіксуємо на першому (і єдиному) статичному кадрі
        
        # 3. Завантажуємо статичний спрайт негайно
        self.load_sprite(IDLE_SPRITES[0])
        
        # 4. Плануємо наступне моргання
        self.schedule_next_blink()
    ################################

   

    def _save_note_to_file(self, note_text):
        """Внутрішній метод для збереження нотатки."""
        try:
            timestamp = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm:ss")
            note_entry = f"--- Замітка від {timestamp} ---\n{note_text}\n\n"

            with open("notes.txt", "a", encoding="utf-8") as f:
                f.write(note_entry)
            
            # Не показуємо QMessageBox тут, оскільки ми це робимо в show_note_dialog

        except Exception as e:
            QMessageBox.critical(self, "Помилка Збереження", f"Не вдалося зберегти нотатку: {e}")

 
    def show_note_dialog(self):
        """Викликає діалог для створення нової замітки та зберігає її."""
        
        if self.is_moving:
            self.stop_moving()

        dialog = NoteDialog(self)
            
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            note_title = data['title'] if data['title'] else "Без заголовка"
            note_text = data['text']
            
            # Зберігаємо нотатку у файл
            self._save_note_to_file(f"=== {note_title} ===\n{note_text}\n\n")
            
            # 2. Планування нагадування
            if data['is_reminder_active']:
                reminder_dt = data['datetime']
                
                # Для нотаток з нагадуванням використовуємо простий 'once'
                self.schedule_flexible_reminder(
                    f"📝 Нагадування: {note_title or note_text}", # Текст, який буде відображено
                    reminder_dt,
                    'once' # Завжди 'once' для нотаток, створених через цей діалог
                )

                # Виводимо сповіщення про збереження та нагадування
                QMessageBox.information(
                    self,
                    "✅ Замітка Збережена та Запланована",
                    f"Замітка '{note_title}' успішно збережена. Нагадування встановлено на {reminder_dt.toString('dd.MM.yyyy HH:mm')}."
                )
            else:

                QMessageBox.information(
                    self,
                    "✅ Замітка Збережена",
                    f"Замітка '{note_title}' успішно збережена у файл."
                )
        
        # Відновлюємо рух після завершення діалогу
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)   



    def show_reminder_setup_dialog(self):
        """Створює та відображає діалогове вікно для налаштування нагадування."""
        
        if self.is_moving:
            self.stop_moving()

        dialog = ReminderSetupDialog(self)
            
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            note_text = data['text']
            reminder_dt = data['datetime']
            repetition = data['repetition']
            interval_ms = data['interval_ms']

            # Зберігаємо нотатку у файл (додатково)
            self._save_note_to_file(note_text)
            
            # Планування нагадування
            self.schedule_flexible_reminder(note_text, reminder_dt, repetition, interval_ms)
        
        # Після закриття діалогу
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)



    def schedule_flexible_reminder(self, text, start_dt, repetition, interval_ms=0, existing_id=None):
        """Планує нагадування з гнучкими налаштуваннями повторення."""
        
        # 1. Визначення ID та оновлення лічильника
        if existing_id is not None:
            # Випадок 1: Завантаження старого нагадування з файлу
            reminder_id = existing_id
        else:
            # Випадок 2: Створення нового нагадування через діалог
            reminder_id = self.reminder_id_counter
            # Збільшуємо лічильник для наступного нового нагадування
            self.reminder_id_counter += 1

        now = QDateTime.currentDateTime()
        
        if start_dt <= now and repetition == 'once':
            # Якщо це одноразове нагадування, і час минув, виводимо помилку (тільки для нових)
            if existing_id is None:
                QMessageBox.warning(self, "Помилка", "Час для одноразового нагадування вже минув.")
            return

        # 1. Обчислюємо інтервал до першого спрацювання (для всіх типів)
        first_interval_ms = now.msecsTo(start_dt)


        if first_interval_ms <= 0 and repetition != 'once': # Одноразові вже відсіяли:
            current_dt = start_dt # Починаємо з початкового часу

            # Якщо час вже минув, встановлюємо на наступний повтор (через 1 годину, 1 день або кастомний інтервал)
            # (Логіка коректна, оскільки start_dt в цьому випадку - це цільовий час доби/інтервал)
            
            if repetition == 'daily':
                # Щоденне: просто ставимо на той самий час завтра
                first_interval_ms = now.msecsTo(start_dt.addDays(1))

            
            elif repetition in ['hourly', 'custom']:
                # Визначаємо інтервал для додавання
                interval_to_add = interval_ms if repetition == 'custom' else 3600000 # 3600000 мс = 1 година

            # elif repetition == 'custom':
            #     first_interval_ms = now.msecsTo(start_dt.addMSecs(interval_ms))
            
            # Циклічно додаємо інтервал, поки не вийдемо в майбутнє
                while now.msecsTo(current_dt) <= 0:
                    current_dt = current_dt.addMSecs(interval_to_add)
                
                first_interval_ms = now.msecsTo(current_dt)

            # Перевірка безпеки
            if first_interval_ms <= 0:
                # Якщо навіть після корекції час все ще в минулому (або дуже близький), ставимо на 1 секунду
                first_interval_ms = 1000

            # if first_interval_ms <= 0:
                # Якщо навіть наступний повтор у минулому (малоймовірно), ставимо на 1 хвилину
                # first_interval_ms = 60000 
        
        # reminder_id = self.reminder_id_counter
        # self.reminder_id_counter += 1
        
        # 2. Створення таймера
        reminder_timer = QTimer(self)
        
        def _trigger_action():
            title = f"🔔 Нагадування #{reminder_id}!"
            message = f"**{text}**"
            QMessageBox.information(self, title, message)
            
            # Логіка для повторюваних нагадувань
            if repetition == 'once':
                # Одноразове нагадування завершено, видаляємо його
                reminder_timer.stop()
                # Видалення з активного списку
                self.active_reminders = [r for r in self.active_reminders if r['id'] != reminder_id]
                return
            
            # Для щоденного нагадування
            elif repetition == 'daily':
                # Встановлюємо інтервал 24 години (86,400,000 мс)
                # Якщо час спрацювання був обчислений точно, простіше ставити фіксований 1 день

                interval = 86400000 # 24 години в мс

                #next_dt = QDateTime(QDate.currentDate().addDays(1), start_dt.time())
                #interval = now.msecsTo(next_dt)

            # Для щогодинного нагадування
            elif repetition == 'hourly':
                interval = 3600000 # 1 година

            # Для кастомного нагадування
            elif repetition == 'custom':
                interval = interval_ms

            else:
                return # На всяк випадок

            # Перезапуск таймера на наступний інтервал
            if interval > 0:

                reminder_timer.stop() # Зупиняємо (якщо він ще працює)
                reminder_timer.setSingleShot(False) # Встановлюємо на циклічний режим
                reminder_timer.start(interval)


        reminder_timer.timeout.connect(_trigger_action)
        
        # Встановлюємо перший інтервал та запускаємо
        reminder_timer.setSingleShot(repetition == 'once')
        reminder_timer.start(first_interval_ms)
        
        # 3. Зберігаємо інформацію про нагадування
        self.active_reminders.append({
            'id': reminder_id,
            'timer': reminder_timer,
            'text': text,
            'repetition': repetition,

            # Зберігаємо ключові параметри для відновлення:
            'start_dt_str': start_dt.toString('dd.MM.yyyy HH:mm'), # Дата/час першого спрацювання (для Once)
            'start_time_str': start_dt.toString('HH:mm'),          # Час (для Daily)
            'interval_ms': interval_ms                             # Інтервал (для Custom/Hourly)
        })
        
        # Виводимо інформаційне повідомлення лише для нових нагадувань
        if existing_id is None:
            rep_text = {
                'once': f"одноразово {start_dt.toString('dd.MM.yyyy HH:mm')}",
                'daily': f"щоденно о {start_dt.toString('HH:mm')}",
                'hourly': "щогодини",
                'custom': f"кожні {interval_ms // 60000} хвилин"
            }.get(repetition, "невідомо")

            QMessageBox.information(self, "✅ Успіх", f"Нагадування **'{text}'** встановлено: **{rep_text}**.")



    def show_cancel_reminder_dialog(self):
        """Відображає список активних нагадувань і дозволяє їх скасувати."""
        
        if not self.active_reminders:
            QMessageBox.information(self, "Список Порожній", "Наразі немає активних запланованих нагадувань.")
            return

        # Створюємо список рядків для відображення у діалоговому вікні
        items = []
        for r in self.active_reminders:
            rep = {
                'once': ' (Одноразово)',
                'daily': ' (Щоденно)',
                'hourly': ' (Щогодинно)',
                'custom': ' (Кастомно)'
            }.get(r['repetition'], '')
            items.append(f"ID {r['id']}: {r['text']}{rep}")

        # Використовуємо QInputDialog для вибору
        item, ok = QInputDialog.getItem(
            self, 
            "🗑️ Скасувати Нагадування", 
            "Оберіть нагадування для скасування:", 
            items, 
            0, 
            False # Не дозволяти редагування тексту
        )
        
        if ok and item:
            # Витягуємо ID з вибраного рядка
            reminder_id = int(item.split(':')[0].replace('ID ', ''))
            
            self._cancel_reminder_by_id(reminder_id)

    def _cancel_reminder_by_id(self, reminder_id):
        """Внутрішній метод для зупинки таймера та видалення зі списку."""
        reminder_to_cancel = next((r for r in self.active_reminders if r['id'] == reminder_id), None)
        
        if reminder_to_cancel:
            reminder_to_cancel['timer'].stop()
            self.active_reminders.remove(reminder_to_cancel)
            QMessageBox.information(
                self, 
                "Скасовано", 
                f"Нагадування **'{reminder_to_cancel['text']}'** (ID {reminder_id}) успішно скасовано."
            )
        else:
            QMessageBox.warning(self, "Помилка", f"Нагадування з ID {reminder_id} не знайдено.")


    def save_reminders(self):
        """Зберігає активні нагадування у файл reminders.json."""
        data_to_save = []
        
        for r in self.active_reminders:
            data_to_save.append({
                # Зберігаємо лише необхідні для відновлення дані:
                'id': r['id'], 
                'text': r['text'],
                'repetition': r['repetition'],

                # 🔥 КРИТИЧНЕ ВИПРАВЛЕННЯ: Використовуємо .get() для запобігання KeyError
                'start_dt_str': r.get('start_dt_str'),    # Для Once
                'start_time_str': r.get('start_time_str'),  # Для Daily
                'interval_ms': r.get('interval_ms', 0),      # Для Custom/Hourly, Додаємо 0 як дефолт
                
                # Зберігаємо точку відліку для циклічних (для коректного відновлення)
                # Зберігаємо час, на який воно було вперше заплановано (QDateTime)
                # 'original_start_dt_str': r.get('start_dt_str'),

            })
                
        try:
            with open(REMINDER_FILE, "w", encoding="utf-8") as f:

                final_data = {
                'reminders': data_to_save,
                'max_id': self.reminder_id_counter
                }
                json.dump(final_data, f, indent=4)

                # json.dump(data_to_save, f, indent=4)

        except Exception as e:
            QMessageBox.critical(self, "Помилка Збереження", f"Не вдалося зберегти нагадування: {e}")
        

    def load_reminders(self, initial_load=True): # (initial_load - для уникнення діалогових вікон)
        """Завантажує та відновлює нагадування з файлу reminders.json і переплановує їх."""
        """Використовує якірний час (start_dt) для коректного відновлення циклічних графіків."""
        try:
            if not os.path.exists(REMINDER_FILE):
                # print("Файл нагадувань не знайдено, починаємо з чистого аркуша.")
                return
            
            with open(REMINDER_FILE, "r", encoding="utf-8") as f:
                data_from_file = json.load(f) # Перейменовуємо змінну для ясності

            reminders_data = data_from_file.get('reminders', []) # ✅ Отримуємо список нагадувань
            
            # Оскільки ми не зберігаємо таймери, ми повинні відновити їх.
            for r_data in reminders_data: # ✅ Ітеруємо по правильному списку
                
                text = r_data.get('text', 'Нагадування без тексту') # Безпечніше
                repetition = r_data.get('repetition')
                interval_ms = r_data.get('interval_ms', 0) # Ініціалізуємо тут
                start_dt = None # Ініціалізуємо якірний час

                    # A. Одноразові та циклічні нагадування (Hourly/Custom) використовують повну дату/час як якір
                if r_data.get('start_dt_str'):
                    start_dt = QDateTime.fromString(r_data['start_dt_str'], 'dd.MM.yyyy HH:mm')
                
                # B. Daily: Якщо є час доби, він перевизначає start_dt на сьогоднішню дату (це якір для Daily)
                if repetition == 'daily' and r_data.get('start_time_str'):
                    try:
                        time_to_use = QTime.fromString(r_data['start_time_str'], 'HH:mm')
                        start_dt = QDateTime(QDate.currentDate(), time_to_use)
                    except ValueError:
                        start_dt = None # Якщо формат часу невірний
                
                # --- ПЕРЕВІРКА ---

                # 1. Якщо ми не змогли отримати опорний час, пропускаємо нагадування
                if start_dt is None or not text:
                    continue 
                
                # 2. Обробка одноразових нагадувань, час яких минув
                if repetition == 'once' and start_dt <= QDateTime.currentDateTime():
                    continue

                existing_id = r_data.get('id') # <<< ДОДАТИ

                self.schedule_flexible_reminder(
                    text=text, 
                    start_dt=start_dt, # Передаємо якірний час для всіх типів, 
                    repetition=repetition, 
                    interval_ms=interval_ms,
                    existing_id=existing_id # <-- ПЕРЕДАЄМО ID
                )
                    


            max_id_saved = data_from_file.get('max_id', 0) # ✅ Використовуємо data_from_file
            self.reminder_id_counter = max_id_saved + 1

            # Оновлення списку нагадувань в інтерфейсі
            self.update_reminder_list_ui()

            # print(f"✅ Нагадування відновлено. Наступний ID встановлено на: {self.reminder_id_counter}")
        
        except json.JSONDecodeError as e: # Обробка помилки формату JSON
            print(f"Помилка декодування JSON: {e}")
            QMessageBox.critical(self, "Помилка Завантаження", f"Не вдалося декодувати файл нагадувань: {e}")
        except Exception as e:
            print(f"Помилка завантаження нагадувань: {e}")
            QMessageBox.critical(self, "Помилка Завантаження", f"Не вдалося завантажити нагадування: {e}")

    def update_reminder_list_ui(self):
        """
        Метод-заглушка для оновлення списку нагадувань у графічному інтерфейсі.
        TODO: Реалізувати логіку відображення self.active_reminders в ListWidget.
        """
        # print("Інформація: update_reminder_list_ui викликано, оновлюю список нагадувань...")
        pass

    def show_timer_setup_dialog(self):
        """Відображає діалогове вікно для встановлення зворотного таймера."""
        
        if self.is_moving:
            self.stop_moving()
            
        # 1. Запитуємо тривалість у хвилинах
        minutes, ok = QInputDialog.getInt(
            self,
            "⏱️ Встановити Таймер",
            "Введіть тривалість таймера у хвилинах (від 1 до 180):",
            1,  # Значення за замовчуванням
            1,  # Мінімальне значення
            180 # Максимальне значення
        )
        
        if not ok or minutes <= 0:
            self.decision_timer.start(WALK_DECISION_INTERVAL_MS)
            return

        # 2. Запитуємо назву таймера
        text, ok = QInputDialog.getText(
            self, 
            "⏱️ Встановити Таймер",
            "Назва таймера (наприклад, 'перерва', 'відпочинок'):",
            QLineEdit.Normal,
            f"Таймер на {minutes} хвилин"
        )

        if ok and minutes > 0:
            self.start_countdown_timer(minutes, text.strip())
        
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)

    def start_countdown_timer(self, minutes, name):
        """Запускає зворотний таймер на вказану кількість хвилин."""

        if self.active_countdown_timer.isActive():
            QMessageBox.warning(self, "Таймер Активний", "Уже запущено інший таймер. Зупиніть його або дочекайтеся завершення.")
            return

        # 1. Встановлюємо параметри
        duration_ms = minutes * 60 * 1000
        self.active_countdown_timer_name = name
        
        # 2. Підключаємо сигнал
        # Використовуємо lambda, щоб уникнути помилок, якщо виклик connect
        # відбудеться кілька разів
        try:
             self.active_countdown_timer.timeout.disconnect()
        except TypeError:
             pass # Ігноруємо, якщо сигнал ще не підключено

        self.active_countdown_timer.timeout.connect(self.timer_finished_alert)
        
        # 3. Запускаємо таймер
        self.active_countdown_timer.start(duration_ms)

        QMessageBox.information(
            self,
            "⏱️ Таймер Запущено",
            f"Таймер **'{name}'** запущено на **{minutes} хвилин**."
        )

    def timer_finished_alert(self):
        """Спрацьовує, коли таймер завершено."""
        
        name = self.active_countdown_timer_name
        self.active_countdown_timer.stop()
        self.active_countdown_timer.timeout.disconnect(self.timer_finished_alert)
        self.active_countdown_timer_name = ""

        QMessageBox.information(
            self,
            "🔔 Таймер Завершено!",
            f"Таймер **'{name}'** завершив зворотний відлік!"
        )

    def cancel_countdown_timer(self):
        """Зупиняє та скидає поточний зворотний таймер."""
        
        if self.active_countdown_timer.isActive():
            self.active_countdown_timer.stop()
            
            # 1. Від'єднуємо сигнал, щоб він не спрацював пізніше
            try:
                self.active_countdown_timer.timeout.disconnect(self.timer_finished_alert)
            except TypeError:
                pass # Ігноруємо, якщо сигнал вже відключено
            
            name = self.active_countdown_timer_name
            self.active_countdown_timer_name = ""
            
            QMessageBox.information(
                self,
                "⏱️ Таймер Скасовано",
                f"Таймер **'{name}'** був успішно скасований."
            )
        else:
            QMessageBox.information(
                self,
                "Таймер",
                "Наразі немає активних таймерів для скасування."
            )

    # ----------------------------------------------------
    # --- СИСТЕМА ПРЕСЕТІВ ---
    # ----------------------------------------------------

    def save_presets(self):
        """Зберігає список пресетів у файл."""
        try:
            with open(PRESET_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Помилка Збереження", f"Не вдалося зберегти пресети: {e}")

    def load_presets(self):
        """Завантажує пресети з файлу."""
        try:
            if os.path.exists(PRESET_FILE):
                with open(PRESET_FILE, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Помилка Завантаження", f"Не вдалося завантажити пресети: {e}")
            self.presets = []

    def show_create_preset_dialog(self, preset_data=None, index=None):
        """Показує діалог створення/редагування пресету."""
        if self.is_moving:
            self.stop_moving()
            
        dialog = PresetDialog(self, preset_data)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if index is not None:
                # Редагування існуючого
                self.presets[index] = data
                QMessageBox.information(self, "✅ Успіх", f"Пресет **'{data['name']}'** успішно оновлено.")
            else:
                # Створення нового
                self.presets.append(data)
                QMessageBox.information(self, "✅ Успіх", f"Пресет **'{data['name']}'** успішно створено.")
            
            self.save_presets()
            
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)
        
    def show_manage_presets_dialog(self):
        """Показує діалог для керування (відкриття/видалення/редагування) пресетами."""
        if not self.presets:
            QMessageBox.information(self, "Список Порожній", "Наразі немає збережених пресетів.")
            return

        dialog = ManagePresetsDialog(self, self.presets)
        result = dialog.exec_()
        
        index = dialog.get_selected_index()
        
        if result == QDialog.Accepted + 1: # Open
            self._open_preset(self.presets[index])
            
        elif result == QDialog.Accepted + 2: # Delete
            preset_name = self.presets[index]['name']
            del self.presets[index]
            self.save_presets()
            QMessageBox.information(self, "🗑️ Видалено", f"Пресет **'{preset_name}'** успішно видалено.")
            
        elif result == QDialog.Accepted + 3: # Edit
            self.show_create_preset_dialog(self.presets[index], index)
            
    def _open_preset(self, preset_data):
        """Відкриває програми та посилання з пресету."""
        
        name = preset_data['name']
        items = preset_data['items']
        width = preset_data['width']
        height = preset_data['height']
        
        open_count = 0
        
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            try:
                if item.startswith(('http://', 'https://')):
                    # 1. Відкриття посилання в браузері
                    webbrowser.open_new_tab(item)
                    open_count += 1
                else:
                    # 2. Запуск локальної програми
                    subprocess.Popen(item, shell=True) # shell=True може бути небезпечним, але необхідний для .lnk/.bat
                    open_count += 1
                    
                    # ЗМІНА РОЗМІРУ: Ця логіка є заглушкою! 
                    # Для зміни розміру потрібна стороння бібліотека
                    # QTimer.singleShot(2000, lambda: self._resize_application(item, width, height))
                    
            except Exception as e:
                QMessageBox.warning(self, "Помилка Запуску", f"Не вдалося запустити **'{item}'**: {e}")
                
        if open_count > 0:
            QMessageBox.information(self, "🚀 Запуск", f"Пресет **'{name}'** активовано. Запущено {open_count} елементів.")
            
    def _resize_application(self, app_path, width, height):
        """Заглушка для логіки зміни розміру вікна."""
        # Цей метод вимагає pygetwindow/pyautogui. 
        # Додамо його, коли будемо готові до додаткових залежностей.
        print(f"DEBUG: Спроба змінити розмір вікна {app_path} на {width}x{height}")
        pass
        
    # ----------------------------------------------------
    # --- КІНЕЦЬ БЛОКУ ПРЕСЕТІВ ---
    # ----------------------------------------------------

    def show_search_dialog(self):
        """Відображає діалогове вікно для введення пошукового запиту."""
        
        if self.is_moving:
            self.stop_moving()
            
        # Використовуємо QInputDialog для швидкого отримання тексту
        text, ok = QInputDialog.getText(
            self, 
            "🔎 Пошук в Інтернеті", 
            "Введіть пошуковий запит:", 
            QLineEdit.Normal, 
            ""
        )

        if ok and text:
            self.perform_search(text.strip())
            
        # Після закриття діалогу
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)

    def perform_search(self, query):
        """Відкриває результати пошуку в браузері за допомогою Google."""
        
        # Замінюємо пробіли на '+' для коректного URL-кодування
        safe_query = query.replace(' ', '+')
        
        search_url = f"https://www.google.com/search?q={safe_query}"
        
        try:
            # Відкриваємо URL у новому вікні/вкладці браузера
            webbrowser.open_new_tab(search_url)
            QMessageBox.information(
                self, 
                "🔎 Пошук Запущено", 
                f"Відкрито браузер з результатами для запиту: **{query}**"
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Помилка Браузера", 
                f"Не вдалося відкрити браузер. Перевірте встановлення: {e}"
            )

    def toggle_sleep_mode(self):
        """Вмикає або вимикає Режим сну, призупиняючи всю активність."""
        
        self.is_sleeping = not self.is_sleeping
        
        if self.is_sleeping:
            # 1. Сон: Зупиняємо всі таймери, пов'язані з рухом та анімацією
            if self.is_moving:
                self.stop_moving() # Зупиняє walk_timer
            
            # Додатково зупиняємо blink_decision_timer, якщо помічник заснув,
            # щоб він не намагався моргати під час сну    
            self.decision_timer.stop()
            self.blink_decision_timer.stop()
            self.animation_timer.stop()
            
            # 2. Встановлюємо спрайт сну
            #завантажуємо окремий спрайт "SLEEP_01".

            if not self.load_sprite("sleep/sleep_01.png"):
                # Якщо спрайт сну не знайдено, повертаємося до idle_01.png
                self.load_sprite(IDLE_SPRITES[0])
                QMessageBox.warning(self, "Помилка Спрайта", "Спрайт 'sleep_01.png' для режиму сну не знайдено. Використовую стандартний.")

            QMessageBox.information(self, "💤 Режим Сну", "Помічник заснув. Усі рухи призупинено.")
            
        else:
            # 1. Пробудження: Перезапускаємо таймери
            self.decision_timer.start(WALK_DECISION_INTERVAL_MS)
            self.animation_timer.start(ANIMATION_SPEED_MS)
            self.schedule_next_blink() # Плануємо моргання
            
            # 2. Повертаємо до статичного IDLE (забезпечуємо, що не застряг у BLINK/WALK)
            # Ми використовуємо stop_blink(), оскільки він вже містить логіку повернення до IDLE_SPRITES[0]
            self.stop_blink()
            
            QMessageBox.information(self, "☀️ Пробудження", "Помічник прокинувся і готовий до роботи!")

    # --- АНИМАЦИЯ ---

    def update_sprite(self):
        """Переключає поточний спрайт для створення анімації IDLE, WALK або BLINK."""
        
        target_sprites = None
        
        # 1. Визначаємо поточний набір спрайтів

        if self.is_moving:
            
            if self.facing_right:
                target_sprites = WALK_SPRITES_RIGHT
            else:
                target_sprites = WALK_SPRITES_LEFT

        elif self.is_blinking:
            target_sprites = BLINK_SPRITES

        else:
            # Static IDLE (коли помічник не рухається і не моргає)
            target_sprites = IDLE_SPRITES
            
            # Якщо ми в статичному IDLE, не потрібно оновлювати спрайт,
            # оскільки він завжди IDLE_01 і animation_timer дуже повільний.
            # Якщо цей метод викликається (що він буде робити кожні 10 сек),
            # він повинен вийти.
            if len(IDLE_SPRITES) == 1:
                return # Виходимо, якщо це статичний IDLE
        
        # 2. Логіка зміни набору спрайтів (при переході WALK <-> BLINK)
        if self.current_sprites != target_sprites:
            self.current_sprites = target_sprites
            # Скидаємо індекс. Для BLINK він вже скинутий у start_blink, 
            # але тут ми просто перестраховуємось.
            self.current_sprite_index = -1 
        
        # 3. Оновлюємо індекс та завантажуємо спрайт
        if self.current_sprites:
            # Обчислюємо наступний індекс
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.current_sprites)
            
            sprite_file = self.current_sprites[self.current_sprite_index]
            self.load_sprite(sprite_file)
            
            # 4. Логіка зупинки для одноразової анімації (BLINK)
            if self.current_sprites == BLINK_SPRITES and self.current_sprite_index == len(BLINK_SPRITES) - 1:
                # Анімація моргання завершена (останній кадр)
                self.stop_blink()
                return # Виходимо, оскільки stop_blink переключить на IDLE_01 та змінить швидкість таймера


    # --- ДОВІЛЬНЕ ПЕРЕМІЩЕННЯ ---
    
    def make_move_decision(self):
        """Вирішує, чи почати рух, і встановлює ціль."""
        
        if self.is_sleeping: # <<< ПЕРЕВІРКА СТАНУ
            return


        if random.random() < 0.7 and not self.is_moving: 
            # 70% шанс розпочати рух
            self.start_moving()
        elif self.is_moving:
            # З 30% шансом перервати рух (за умови, що start_moving не спрацював)
            self.stop_moving()


    def calculate_direction(self):
        """Визначає вектор напряму до мети з урахуванням режиму руху."""
        
        current_pos = self.pos()
        dx = self.target_pos.x() - current_pos.x()
        dy = self.target_pos.y() - current_pos.y()
        
        # За замовчуванням: вільний рух
        dir_x = 0
        dir_y = 0

        # --- Логіка руху X ---
        if self.move_mode in ['free', 'horizontal']:
            if abs(dx) > WALK_PIXELS_PER_STEP:
                dir_x = 1 if dx > 0 else -1

        # --- Логіка руху Y ---
        if self.move_mode in ['free', 'vertical']:
            if abs(dy) > WALK_PIXELS_PER_STEP:
                dir_y = 1 if dy > 0 else -1
                
        self.direction = QPoint(dir_x, dir_y)


    def start_moving(self):
        """Починає довільне переміщення."""
        
        ### Якщо моргає, зупиняємо моргання перед рухом ###
        if self.is_blinking:
            self.stop_blink()
            
        self.is_moving = True
        
        
        screen_geo = QDesktopWidget().availableGeometry()
        current_pos = self.pos()
        MIN_WALK_DISTANCE = 40 

        # Визначаємо межі доступної області
        min_x = screen_geo.left()
        max_x = screen_geo.right() - self.width()
        min_y = screen_geo.top()
        max_y = screen_geo.bottom() - self.height()
        
        # Обмежуємо максимальну відстань (WALK_MAX_DISTANCE з config.py)
        # та перевіряємо, що нова точка не надто близька (MIN_WALK_DISTANCE)
        while True:
            # Вибираємо випадкову точку на екрані в межах WALK_MAX_DISTANCE від поточної позиції
            rand_x = random.randint(
                max(min_x, current_pos.x() - WALK_MAX_DISTANCE),
                min(max_x, current_pos.x() + WALK_MAX_DISTANCE)
            )
            rand_y = random.randint(
                max(min_y, current_pos.y() - WALK_MAX_DISTANCE),
                min(max_y, current_pos.y() + WALK_MAX_DISTANCE)
            )
            
            new_target = QPoint(rand_x, rand_y)
            
            # Перевіряємо мінімальну відстань, щоб рух був помітний
            distance_sq = (new_target.x() - current_pos.x())**2 + (new_target.y() - current_pos.y())**2
            
            if distance_sq >= MIN_WALK_DISTANCE**2:
                self.target_pos = new_target
                break
        # -----------------------------------------------------------------
        
        # 2. Встановлюємо, куди дивитися
        current_x = self.pos().x()
        target_x = self.target_pos.x()
        
        if target_x > current_x:
            self.facing_right = True
        elif target_x < current_x:
            self.facing_right = False

        # Обчислюємо напрямок та запускаємо таймер ходьби
        self.calculate_direction()
        
        
        # 1. Прискорюємо анімаційний таймер для ходьби
        self.animation_timer.setInterval(80) 
        
        # 2. Форсуємо негайне перемикання на WALK-анімацію
        target_walk_sprites = WALK_SPRITES_RIGHT if self.facing_right else WALK_SPRITES_LEFT
        
        if self.current_sprites != target_walk_sprites:
            self.current_sprites = target_walk_sprites
            self.current_sprite_index = -1 # Скидаємо на -1
            self.update_sprite() # Негайно завантажуємо 1-й кадр
            
        # Запускаємо плавне переміщення
        self.walk_timer.start(20) # 20 мс = 50 кадрів/сек для плавного руху


    def stop_moving(self):
        """Зупиняє переміщення та перемикає на IDLE-анімацію."""
        self.is_moving = False
        self.walk_timer.stop()
        self.direction = QPoint(0, 0)
        
        
        # Повертаємо до статичного IDLE та плануємо моргання
        self.stop_blink() # <<< ВИКЛИК stop_blink, який фіксує IDLE_01 та планує наступне моргання

    
    def update_position(self):
        """Зміщує помічника на один крок у заданому напрямку."""
        if not self.is_moving:
            self.walk_timer.stop()
            return
            
        current_pos = self.pos()
        
        new_x = current_pos.x() + self.direction.x() * WALK_PIXELS_PER_STEP
        new_y = current_pos.y() + self.direction.y() * WALK_PIXELS_PER_STEP
        
        self.move(new_x, new_y)
        
        # Проверка, достигнута ли цель
        # Якщо обидва напрямки (x і y) дорівнюють 0, ціль досягнута або рух зупинено
        # Тут ми повинні перевірити, чи все ще є потреба в русі до цілі
        
        # Перераховуємо напрям до мети, що залишилася після кроку
        self.calculate_direction()
        
        if self.direction.x() == 0 and self.direction.y() == 0:
             self.stop_moving()
             return

    # --- Перемикає режим руху ---
    def toggle_move_mode(self):
        """Перемикає режим руху: free -> horizontal -> vertical -> free."""
        if self.move_mode == 'free':
            self.move_mode = 'horizontal'
        elif self.move_mode == 'horizontal':
            self.move_mode = 'vertical'
        else: # 'vertical'
            self.move_mode = 'free'
            
        # Зупиняємо поточний рух, щоб новий режим застосувався відразу
        if self.is_moving:
            self.stop_moving()
            # Перезапускаємо таймер рішення, щоб вона відразу почала новий рух
            self.decision_timer.start(WALK_DECISION_INTERVAL_MS)    

    # --- ВЗАЄМОДІЯ (КЛІК) ---

    def mousePressEvent(self, event):
        """Обробляє клік миші та перетягування/меню."""
        
        # 1. Обробка ЛІВОЇ кнопки миші (Drag/Перетягування)
        if event.button() == Qt.LeftButton:
            # При кліку на помічника зупиняємо його рух
            if self.is_moving:
                self.stop_moving()
            
            # Запам'ятовуємо зміщення (offset) курсора відносно вікна
            self.old_pos = event.globalPos() - self.pos()
            
        # 2. Обробка ПРАВОЇ кнопки миші (Меню)
        elif event.button() == Qt.RightButton: 
            self.show_dialog_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        """Обробляє перетягування вікна ЛКМ."""
        if event.buttons() == Qt.LeftButton:
            # Переміщуємо вікно на нову глобальну позицію курсора 
            # мінус збережене зміщення (offset)
            if hasattr(self, 'old_pos'): # Перевірка на всяк випадок
                self.move(event.globalPos() - self.old_pos)
            
    # --- МЕНЮ (Хмара діалогів) ---
    

    def show_dialog_menu(self, pos):
        """Створює та відображає контекстне меню."""

        # Зупиняємо рух на час взаємодії з меню
        if self.is_moving:
            self.stop_moving()

        menu = QMenu(self)
        
        # 1. НОВИЙ ПУНКТ: Створити Замітку
        note_action = QAction("📝 Створити Замітку", self)
        note_action.triggered.connect(self.show_note_dialog)
        menu.addAction(note_action) # <-- Додаємо новий пункт

        # --- НОВИЙ ГОЛОВНИЙ ПУНКТ ---
        reminder_action = QAction("➕ Створити Нагадування/Звичку", self)
        reminder_action.triggered.connect(self.show_reminder_setup_dialog)
        menu.addAction(reminder_action)
        
        # --- НОВИЙ ПУНКТ СКАСУВАННЯ ---
        cancel_action = QAction("🗑️ Скасувати Нагадування", self)
        cancel_action.triggered.connect(self.show_cancel_reminder_dialog)
        menu.addAction(cancel_action)
        
        # --- НОВИЙ ПУНКТ: ТАЙМЕР ---
        
        # 1. Дія ВСТАНОВИТИ ТАЙМЕР
        set_timer_text = "⏱️ Встановити Новий Таймер"
        set_timer_action = QAction(set_timer_text, self)
        set_timer_action.triggered.connect(self.show_timer_setup_dialog)
        
        if self.active_countdown_timer.isActive():
            # 2. Якщо таймер АКТИВНИЙ, додаємо дію СКАСУВАТИ
            cancel_timer_name = self.active_countdown_timer_name
            cancel_timer_action = QAction(f"❌ Скасувати: {cancel_timer_name}", self)
            cancel_timer_action.triggered.connect(self.cancel_countdown_timer)
            menu.addAction(cancel_timer_action)
            
            # Робимо дію 'Встановити' неактивною, поки працює інший таймер
            set_timer_action.setEnabled(False)

        menu.addAction(set_timer_action)
        # --- КІНЕЦЬ БЛОКУ ТАЙМЕРА ---

        menu.addSeparator()

        # 2. Секція Пресети
        # preset_menu = menu.addMenu("⚙️ Робочі Пресети (Workspaces)")
        
        create_preset_action = QAction("⚙️ Створити Новий Пресет", self)
        create_preset_action.triggered.connect(self.show_create_preset_dialog)
        menu.addAction(create_preset_action)

        manage_preset_action = QAction("📂 Керувати/Відкрити Пресети", self)
        manage_preset_action.triggered.connect(self.show_manage_presets_dialog)
        menu.addAction(manage_preset_action)

        menu.addSeparator()

        # --- Існуючі пункти ---
        menu.addSeparator() # Додаємо розділювач
        
        search_action = QAction("🔎 Пошук в Інтернеті", self)
        search_action.triggered.connect(self.show_search_dialog)
        menu.addAction(search_action)
        
        # Перемикання режиму руху (залишаємо)
        move_mode_text = {
            'free': 'Вільний',
            'horizontal': 'Горизонтальний',
            'vertical': 'Вертикальний'
        }.get(self.move_mode)
        move_action = QAction(f"➡️ Режим Руху: {move_mode_text}", self)
        move_action.triggered.connect(self.toggle_move_mode)
        menu.addAction(move_action)

        # Режим сну (залишаємо)
        sleep_action_text = "☀️ Прокинутися" if self.is_sleeping else "💤 Режим Сну"
        sleep_action = QAction(sleep_action_text, self)
        sleep_action.triggered.connect(self.toggle_sleep_mode)
        menu.addAction(sleep_action)
        
        # Вихід
        menu.addSeparator()
        exit_action = QAction("❌ Вихід", self)
        exit_action.triggered.connect(self.quit_assistant)

        # exit_action.triggered.connect(QApplication.instance().quit)

        menu.addAction(exit_action)
        
        menu.exec_(pos)

        # Після закриття меню відновлюємо логіку руху
        self.decision_timer.start(WALK_DECISION_INTERVAL_MS)

    def quit_assistant(self):
        """Коректно закриває помічника, викликаючи closeEvent."""
        self.close()

    def closeEvent(self, event):
        """Перехоплює подію закриття вікна для збереження даних."""
        
        # ДІАГНОСТИКА:
        # print(">>> ВИКЛИК: closeEvent - Починаю збереження нагадувань...")

        # 1. Зберігаємо всі активні нагадування
        self.save_reminders()
        
        # 2. !!! КЛЮЧОВИЙ МОМЕНТ: ЗУПИНКА ВСІХ ТАЙМЕРІВ !!!
        
        # Перевіряємо та зупиняємо таймер руху/анімації
        if hasattr(self, 'animation_timer') and self.animation_timer.isActive():
            self.animation_timer.stop()
            # print("Інформація: animation_timer зупинено.")
            
        if hasattr(self, 'walk_timer') and self.walk_timer.isActive():
            self.walk_timer.stop()
            # print("Інформація: walk_timer зупинено.")

        # Зупиняємо таймер перевірки нагадувань, якщо він є
        if hasattr(self, 'reminder_check_timer') and self.reminder_check_timer.isActive():
            self.reminder_check_timer.stop()
            # print("Інформація: reminder_check_timer зупинено.")

        # ЗУПИНКА decision_timer та blink_decision_timer
        if hasattr(self, 'decision_timer') and self.decision_timer.isActive():
            self.decision_timer.stop()
        if hasattr(self, 'blink_decision_timer') and self.blink_decision_timer.isActive():
            self.blink_decision_timer.stop()
        
        # !!! ЗУПИНКА ТАЙМЕРА ЗВОРОТНОГО ВІДЛІКУ !!!
        if hasattr(self, 'active_countdown_timer') and self.active_countdown_timer.isActive():
            self.active_countdown_timer.stop()
        # !!! КІНЕЦЬ БЛОКУ !!!

        # 3. !!! ЗУПИНКА ІНДИВІДУАЛЬНИХ ТАЙМЕРІВ НАГАДУВАНЬ !!!
        if hasattr(self, 'active_reminders') and self.active_reminders:

            # reminders_to_stop = []

            # Перебираємо словник нагадувань
            for data in self.active_reminders:

                # Шукаємо об'єкт QTimer всередині даних
                # 'data' тепер є словником, який містить 'timer'
                if 'timer' in data and isinstance(data['timer'], QTimer):
                    if data['timer'].isActive():
                        data['timer'].stop()


        event.accept()

        # 4. Гарантоване завершення додатку
        QCoreApplication.instance().quit()

# --- ЗАПУСК ДОДАТКА ---
if __name__ == '__main__':
    if not os.path.exists(SPRITE_DIR):
        print(f"Помилка: Папка '{SPRITE_DIR}' не знайдена. Створіть її та додайте спрайти!")
        sys.exit(1)

    app = QApplication(sys.argv)
    ex = VirtualAssistant()
    
    # Завершуємо, якщо не вдалося завантажити початковий спрайт
    if not ex.isVisible():
        sys.exit(1)
        
    sys.exit(app.exec_())