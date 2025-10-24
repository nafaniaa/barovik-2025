import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation, getcontext


getcontext().prec = 20

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Финансовый калькулятор")

     
        info_text = "ФИО: Гуринович Татьяна Витальевна\nКурс: 4\nГруппа: 4\nГод: 2025"
        self.info_label = tk.Label(root, text=info_text, justify=tk.LEFT)
        self.info_label.pack(pady=10)


        self.num1_label = tk.Label(root, text="Первое число:")
        self.num1_label.pack()
        self.num1_entry = tk.Entry(root, width=30)
        self.num1_entry.pack()

        self.num2_label = tk.Label(root, text="Второе число:")
        self.num2_label.pack()
        self.num2_entry = tk.Entry(root, width=30)
        self.num2_entry.pack()

     
        self.operation_frame = tk.Frame(root)
        self.operation_frame.pack(pady=10)

        self.add_button = tk.Button(self.operation_frame, text="Сложение (+)", command=self.add_numbers)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.sub_button = tk.Button(self.operation_frame, text="Вычитание (-)", command=self.sub_numbers)
        self.sub_button.pack(side=tk.LEFT, padx=5)

        self.result_label = tk.Label(root, text="Результат:")
        self.result_label.pack()
        self.result_entry = tk.Entry(root, width=30, state='readonly')
        self.result_entry.pack()

        

    def parse_number(self, num_str):
       
        num_str = num_str.replace(',', '.')
        try:
            return Decimal(num_str)
        except InvalidOperation:
            raise ValueError("Некорректное число")

    def check_overflow(self, result):
        min_val = Decimal('-1000000000000.000000')
        max_val = Decimal('1000000000000.000000')
        if result < min_val or result > max_val:
            raise OverflowError("Переполнение")

    def perform_operation(self, operation):
        try:
            num1_str = self.num1_entry.get().strip()
            num2_str = self.num2_entry.get().strip()

            if not num1_str or not num2_str:
                messagebox.showerror("Ошибка", "Введите оба числа")
                return

            num1 = self.parse_number(num1_str)
            num2 = self.parse_number(num2_str)

            if operation == '+':
                result = num1 + num2
            elif operation == '-':
                result = num1 - num2
            else:
                raise ValueError("Неверная операция")

            self.check_overflow(result)

            
            result_str = format(result, 'f')  

            self.result_entry.config(state='normal')
            self.result_entry.delete(0, tk.END)
            self.result_entry.insert(0, result_str)
            self.result_entry.config(state='readonly')

        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {ve}")
        except OverflowError as oe:
            messagebox.showerror("Ошибка", f"Результат превышает диапазон: {oe}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def add_numbers(self):
        self.perform_operation('+')

    def sub_numbers(self):
        self.perform_operation('-')

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()