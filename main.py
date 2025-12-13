import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pytesseract
import cv2
import numpy as np
import threading
import time


class SimpleCameraOCR:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera OCR System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#2c3e50")

        self.camera = None
        self.camera_active = False
        self.realtime_ocr = False
        self.current_frame = None

        # Проверяем Tesseract
        self.check_tesseract()

        # Создаем интерфейс
        self.create_widgets()

        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_tesseract(self):
        """Проверка Tesseract"""
        try:
            pytesseract.get_tesseract_version()
            print("✓ Tesseract OK")
        except:
            messagebox.showerror(
                "Ошибка",
                "Tesseract не найден!\n\n"
                "Установите:\n"
                "sudo pacman -S tesseract tesseract-data-eng tesseract-data-rus"
            )
            self.root.quit()

    def create_widgets(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg="#34495e", height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="📹 Camera OCR System",
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(pady=18)

        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#2c3e50")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Левая панель - камера
        left_frame = tk.Frame(main_container, bg="#34495e", relief=tk.FLAT)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        camera_label = tk.Label(
            left_frame,
            text="📷 Камера",
            font=("Arial", 16, "bold"),
            bg="#34495e",
            fg="white"
        )
        camera_label.pack(pady=10)

        # Canvas для камеры
        self.camera_canvas = tk.Canvas(
            left_frame,
            bg="#2c3e50",
            highlightthickness=0
        )
        self.camera_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Правая панель - текст
        right_frame = tk.Frame(main_container, bg="#34495e", relief=tk.FLAT)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        text_label = tk.Label(
            right_frame,
            text="📝 Распознанный текст",
            font=("Arial", 16, "bold"),
            bg="#34495e",
            fg="white"
        )
        text_label.pack(pady=10)

        # Текстовое поле
        text_container = tk.Frame(right_frame, bg="#34495e")
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=("Courier New", 12),
            bg="#ecf0f1",
            fg="#2c3e50",
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)

        # Панель управления
        control_frame = tk.Frame(self.root, bg="#34495e", height=100)
        control_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        control_frame.pack_propagate(False)

        button_container = tk.Frame(control_frame, bg="#34495e")
        button_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Кнопка камеры
        self.camera_btn = tk.Button(
            button_container,
            text="📹 Включить камеру",
            command=self.toggle_camera,
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            width=20,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#229954"
        )
        self.camera_btn.pack(side=tk.LEFT, padx=10)

        # Кнопка OCR
        self.ocr_btn = tk.Button(
            button_container,
            text="🔍 Распознать текст",
            command=self.recognize_once,
            font=("Arial", 13, "bold"),
            bg="#3498db",
            fg="white",
            width=20,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#2980b9",
            state=tk.DISABLED
        )
        self.ocr_btn.pack(side=tk.LEFT, padx=10)

        # Кнопка очистки
        clear_btn = tk.Button(
            button_container,
            text="🗑️ Очистить",
            command=self.clear_text,
            font=("Arial", 13, "bold"),
            bg="#e74c3c",
            fg="white",
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#c0392b"
        )
        clear_btn.pack(side=tk.LEFT, padx=10)

    def toggle_camera(self):
        """Включить/выключить камеру"""
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        """Запуск камеры"""
        try:
            self.camera = cv2.VideoCapture(0)

            if not self.camera.isOpened():
                messagebox.showerror("Ошибка", "Не удалось открыть камеру!")
                return

            # Настройки камеры для лучшей производительности
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            self.camera_active = True
            self.camera_btn.config(
                text="⏹️ Выключить камеру",
                bg="#e74c3c",
                activebackground="#c0392b"
            )
            self.ocr_btn.config(state=tk.NORMAL)

            # Запускаем поток для видео
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()

            print("✓ Камера запущена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить камеру:\n{str(e)}")

    def stop_camera(self):
        """Остановка камеры"""
        self.camera_active = False

        if self.camera:
            self.camera.release()
            self.camera = None

        self.camera_btn.config(
            text="📹 Включить камеру",
            bg="#27ae60",
            activebackground="#229954"
        )
        self.ocr_btn.config(state=tk.DISABLED)

        # Удаляем ID изображения
        if hasattr(self, 'canvas_image_id'):
            self.canvas_image_id = None

        self.camera_canvas.delete("all")

        print("✓ Камера остановлена")

    def video_loop(self):
        """Цикл захвата видео"""
        while self.camera_active:
            ret, frame = self.camera.read()

            if ret:
                # Отзеркаливаем
                frame = cv2.flip(frame, 1)
                self.current_frame = frame.copy()

                # Отображаем
                self.display_frame(frame)

            # Задержка для ~30 FPS
            time.sleep(0.033)

    def display_frame(self, frame):
        """Отображение кадра"""
        if not self.camera_active:
            return

        try:
            # BGR -> RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)

            # Получаем размеры canvas
            canvas_width = self.camera_canvas.winfo_width()
            canvas_height = self.camera_canvas.winfo_height()

            # Масштабируем, сохраняя пропорции
            if canvas_width > 1 and canvas_height > 1:
                # Вычисляем соотношение сторон
                img_ratio = pil_image.width / pil_image.height
                canvas_ratio = canvas_width / canvas_height

                if img_ratio > canvas_ratio:
                    # Ограничиваем по ширине
                    new_width = canvas_width - 20
                    new_height = int(new_width / img_ratio)
                else:
                    # Ограничиваем по высоте
                    new_height = canvas_height - 20
                    new_width = int(new_height * img_ratio)

                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Конвертируем для tkinter
            photo = ImageTk.PhotoImage(pil_image)

            # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: создаем изображение ОДИН раз, потом только обновляем
            if not hasattr(self, 'canvas_image_id') or self.canvas_image_id is None:
                # Первый кадр - создаем изображение
                self.canvas_image_id = self.camera_canvas.create_image(
                    canvas_width // 2,
                    canvas_height // 2,
                    image=photo,
                    anchor=tk.CENTER
                )
            else:
                # Последующие кадры - только обновляем
                self.camera_canvas.coords(
                    self.canvas_image_id,
                    canvas_width // 2,
                    canvas_height // 2
                )
                self.camera_canvas.itemconfig(self.canvas_image_id, image=photo)

            # Сохраняем ссылку чтобы изображение не удалилось
            self.camera_canvas.image = photo

        except Exception as e:
            print(f"Ошибка отображения: {e}")

    def recognize_once(self):
        """Распознать текст с текущего кадра"""
        if self.current_frame is None:
            return

        # Запускаем в отдельном потоке чтобы не тормозить интерфейс
        ocr_thread = threading.Thread(target=self.process_ocr, daemon=True)
        ocr_thread.start()

    def process_ocr(self):
        """Обработка OCR"""
        try:
            # Показываем процесс
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "⏳ Распознавание текста...\n")

            # Копируем кадр
            frame = self.current_frame.copy()

            # Предобработка
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Увеличиваем контраст
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Размытие для удаления шума
            blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

            # Бинаризация
            thresh = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Морфологическая очистка
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # OCR
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(
                processed,
                lang='rus+eng',
                config=custom_config
            )

            # Выводим результат
            self.result_text.delete(1.0, tk.END)

            if text.strip():
                self.result_text.insert(1.0, f"✅ Текст распознан:\n\n{text}")
                print(f"✓ Распознано {len(text)} символов")
            else:
                self.result_text.insert(1.0, "❌ Текст не обнаружен\n\n"
                                             "Советы:\n"
                                             "• Поднесите текст ближе к камере\n"
                                             "• Убедитесь в хорошем освещении\n"
                                             "• Держите камеру стабильно\n"
                                             "• Используйте четкий текст")

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"❌ Ошибка распознавания:\n\n{str(e)}")
            print(f"✗ Ошибка OCR: {e}")

    def clear_text(self):
        """Очистить текст"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "Текст очищен")

    def on_closing(self):
        """Закрытие приложения"""
        if self.camera_active:
            self.stop_camera()
        cv2.destroyAllWindows()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SimpleCameraOCR(root)
    root.mainloop()


if __name__ == "__main__":
    main()