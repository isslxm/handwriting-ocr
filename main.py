import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
import os

class HandwrittenOCR:
    def __init__(self, root):
        self.root = root
        self.root.title("Handwritten Recognition System - OCR")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Переменные
        self.original_image = None
        self.processed_image = None
        self.image_path = None
        
        # Создаем интерфейс
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="📝 Handwritten Recognition System",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#f0f0f0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - изображение
        left_frame = tk.Frame(main_container, bg="white", relief=tk.RIDGE, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_frame,
            text="Изображение",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=10)
        
        # Canvas для изображения
        self.image_canvas = tk.Canvas(left_frame, bg="#e0e0e0", highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Правая панель - результат
        right_frame = tk.Frame(main_container, bg="white", relief=tk.RIDGE, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="Распознанный текст",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=10)
        
        # Текстовое поле с прокруткой
        text_frame = tk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            yscrollcommand=scrollbar.set
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
        
        # Панель управления
        control_frame = tk.Frame(self.root, bg="#ecf0f1", height=100)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Кнопки
        button_frame = tk.Frame(control_frame, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        buttons = [
            ("📁 Загрузить изображение", self.load_image, "#3498db"),
            ("🔍 Распознать текст", self.recognize_text, "#2ecc71"),
            ("🎨 Обработать изображение", self.preprocess_image, "#e67e22"),
            ("💾 Сохранить текст", self.save_text, "#9b59b6"),
            ("🗑️ Очистить", self.clear_all, "#e74c3c")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=("Arial", 10, "bold"),
                bg=color,
                fg="white",
                width=20,
                height=2,
                relief=tk.RAISED,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
            
        # Параметры обработки
        params_frame = tk.LabelFrame(
            control_frame,
            text="Параметры обработки",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        )
        params_frame.pack(pady=5)
        
        tk.Label(params_frame, text="Язык:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
        self.lang_var = tk.StringVar(value="rus+eng")
        lang_combo = ttk.Combobox(
            params_frame,
            textvariable=self.lang_var,
            values=["rus", "eng", "rus+eng"],
            width=15,
            state="readonly"
        )
        lang_combo.grid(row=0, column=1, padx=5, pady=5)
        
    def load_image(self):
        """Загрузка изображения"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = cv2.imread(file_path)
                self.processed_image = self.original_image.copy()
                self.display_image(self.original_image)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, "✓ Изображение загружено. Нажмите 'Распознать текст' для OCR.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def display_image(self, cv_image):
        """Отображение изображения на canvas"""
        # Конвертируем BGR в RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Масштабируем под размер canvas
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            pil_image.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(pil_image)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=self.photo,
            anchor=tk.CENTER
        )
    
    def preprocess_image(self):
        """Предобработка изображения для улучшения распознавания"""
        if self.original_image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return
        
        try:
            # Конвертируем в оттенки серого
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            
            # Применяем гауссово размытие для уменьшения шума
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Адаптивная бинаризация
            thresh = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Морфологические операции для очистки
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            # Конвертируем обратно в BGR для отображения
            self.processed_image = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            self.display_image(self.processed_image)
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "✓ Изображение обработано. Теперь можно распознать текст.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке:\n{str(e)}")
    
    def recognize_text(self):
        """Распознавание текста с помощью Tesseract"""
        if self.processed_image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return
        
        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "⏳ Распознавание текста...\n")
            self.root.update()
            
            # Конфигурация Tesseract
            custom_config = r'--oem 3 --psm 6'
            lang = self.lang_var.get()
            
            # Распознавание
            text = pytesseract.image_to_string(
                self.processed_image,
                lang=lang,
                config=custom_config
            )
            
            self.result_text.delete(1.0, tk.END)
            
            if text.strip():
                self.result_text.insert(1.0, f"✓ Распознавание завершено!\n\n{text}")
            else:
                self.result_text.insert(1.0, "⚠️ Текст не распознан. Попробуйте:\n"
                                           "1. Обработать изображение\n"
                                           "2. Использовать более качественное изображение\n"
                                           "3. Проверить язык распознавания")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка распознавания:\n{str(e)}")
    
    def save_text(self):
        """Сохранение распознанного текста"""
        text = self.result_text.get(1.0, tk.END).strip()
        
        if not text or text.startswith("✓") or text.startswith("⏳"):
            messagebox.showwarning("Внимание", "Нет текста для сохранения!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Успех", "Текст успешно сохранен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def clear_all(self):
        """Очистка всех данных"""
        self.original_image = None
        self.processed_image = None
        self.image_path = None
        self.image_canvas.delete("all")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "Все очищено. Загрузите новое изображение.")

def main():
    root = tk.Tk()
    app = HandwrittenOCR(root)
    root.mainloop()

if __name__ == "__main__":
    main()