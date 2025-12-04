import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN

getcontext().prec = 30


# Проверка корректности форматирования числа
def validate_number_format(num_str: str) -> str:
    s = num_str.strip().replace("\u00A0", " ")

    # Минусы
    if s.count('-') > 1 or ('-' in s and not s.startswith('-')):
        raise ValueError("Некорректный знак минуса")

    # Точки
    if s.count('.') > 1:
        raise ValueError("Слишком много точек")

    # Проверка пробелов (групп тысяч)
    if ' ' in s:
        if '.' in s:
            int_part, frac_part = s.split('.', 1)
        else:
            int_part, frac_part = s, ''

        # Двойные пробелы
        if "  " in int_part or "  " in frac_part:
            raise ValueError("Лишние пробелы")

        # Проверка правильности групп
        groups = int_part.split(' ')
        if len(groups[0].lstrip('-')) > 3:
            raise ValueError("Неправильная группировка разрядов")

        for g in groups[1:]:
            if len(g) != 3:
                raise ValueError("Неправильная группировка разрядов")

        if ' ' in frac_part:
            raise ValueError("Пробелы в дробной части недопустимы")

    return s.replace(' ', '')



def format_output(value: Decimal) -> str:
    s = f"{value:.6f}".rstrip('0').rstrip('.')

    if '.' in s:
        int_p, frac_p = s.split('.')
    else:
        int_p, frac_p = s, ''

    sign = ''
    if int_p.startswith('-'):
        sign = '-'
        int_p = int_p[1:]

    rev = int_p[::-1]
    groups = [rev[i:i+3] for i in range(0, len(rev), 3)]
    int_formatted = " ".join(g[::-1] for g in groups[::-1])

    return sign + int_formatted + ('.' + frac_p if frac_p else '')



class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Финансовый калькулятор — Полная версия")
        self.root.geometry("450x650")

        info = "ФИО: Гуринович Татьяна Витальевна\nКурс: 4\nГруппа: 4\nГод: 2025"
        tk.Label(root, text=info, justify=tk.LEFT, font=("Arial", 11)).pack(pady=10)

        # Контейнер для ввода
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10)

        self.entries = []

        # -------- Поля ввода чисел --------
        for i in range(1, 5):
            tk.Label(main_frame, text=f"Число {i}:", font=("Arial", 10)).pack()
            e = tk.Entry(main_frame, width=30, font=("Arial", 12))
            e.insert(0, "0")
            e.pack(pady=3)

            # Очистка поля при фокусе
            def clear_default(event, entry=e):
                if entry.get() == "0":
                    entry.delete(0, tk.END)

            e.bind("<FocusIn>", clear_default)

            self.entries.append(e)

        # -------- Блок выбора операций --------
        op_frame = tk.Frame(root)
        op_frame.pack(pady=10)

        self.ops = []
        for i in range(3):
            var = tk.StringVar(value="+")
            menu = tk.OptionMenu(op_frame, var, "+", "-", "*", "/")
            menu.config(width=5)
            menu.grid(row=0, column=i, padx=10)
            self.ops.append(var)

        tk.Button(root, text="Вычислить", command=self.calculate,
                  font=("Arial", 12), padx=10, pady=5).pack(pady=10)

        # -------- Результат --------
        tk.Label(root, text="Результат:", font=("Arial", 12)).pack()
        self.result = tk.Entry(root, width=40, state='readonly', font=("Arial", 12))
        self.result.pack(pady=5)

        # -------- Округление --------
        tk.Label(root, text="Выбор вида округления:", font=("Arial", 12)).pack(pady=10)

        self.round_var = tk.StringVar(value="math")
        frame_r = tk.Frame(root)
        frame_r.pack()

        tk.Radiobutton(frame_r, text="Математическое", variable=self.round_var,
                       value="math", command=self.apply_round).pack(anchor="w")
        tk.Radiobutton(frame_r, text="Бухгалтерское", variable=self.round_var,
                       value="bank", command=self.apply_round).pack(anchor="w")
        tk.Radiobutton(frame_r, text="Усечение", variable=self.round_var,
                       value="cut", command=self.apply_round).pack(anchor="w")

        tk.Label(root, text="Округленный до целых:", font=("Arial", 12)).pack(pady=10)

        self.rounded = tk.Entry(root, width=40, state="readonly", font=("Arial", 12))
        self.rounded.pack(pady=5)

        self.last_result = None

        # -------- Поддержка Ctrl+C / Ctrl+V --------
        root.bind_class("Entry", "<Control-c>", lambda e: e.widget.event_generate("<<Copy>>"))
        root.bind_class("Entry", "<Control-v>", lambda e: e.widget.event_generate("<<Paste>>"))
        root.bind_class("Entry", "<Control-C>", lambda e: e.widget.event_generate("<<Copy>>"))
        root.bind_class("Entry", "<Control-V>", lambda e: e.widget.event_generate("<<Paste>>"))


    # ---------------------------------------------
    def parse(self, s: str) -> Decimal:
        cleaned = validate_number_format(s)
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            raise ValueError("Некорректное число")

    # ---------------------------------------------
    def check_overflow(self, x: Decimal):
        MIN = Decimal("-1000000000000.0000000000")
        MAX = Decimal("1000000000000.0000000000")
        if x < MIN or x > MAX:
            raise OverflowError("Переполнение")

    # ---------------------------------------------
    def calculate(self):
        try:
            nums = [self.parse(e.get()) for e in self.entries]
            op = [o.get() for o in self.ops]

            def apply(a, oper, b):
                if oper == "+":
                    res = a + b
                elif oper == "-":
                    res = a - b
                elif oper == "*":
                    res = a * b
                elif oper == "/":
                    if b == 0:
                        raise ZeroDivisionError("Деление на ноль")
                    res = a / b
                else:
                    raise ValueError("Ошибка операции")

                res = res.quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP)
                return res

            mid = apply(nums[1], op[1], nums[2])
            self.check_overflow(mid)

            left = apply(nums[0], op[0], mid)
            self.check_overflow(left)

            final = apply(left, op[2], nums[3])
            self.check_overflow(final)

            final6 = final.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

            out = format_output(final6)
            self.last_result = final

            self.result.config(state="normal")
            self.result.delete(0, tk.END)
            self.result.insert(0, out)
            self.result.config(state="readonly")

            self.apply_round()

        except ZeroDivisionError as e:
            messagebox.showerror("Ошибка", str(e))
        except OverflowError:
            messagebox.showerror("Ошибка", "Переполнение диапазона")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")

    # ---------------------------------------------
    def apply_round(self):
        if self.last_result is None:
            return

        x = self.last_result
        mode = self.round_var.get()

        if mode == "math":
            y = x.to_integral_value(rounding=ROUND_HALF_UP)
        elif mode == "bank":
            y = x.to_integral_value(rounding=ROUND_HALF_EVEN)
        else:
            y = Decimal(int(x))

        self.rounded.config(state="normal")
        self.rounded.delete(0, tk.END)
        self.rounded.insert(0, str(y))
        self.rounded.config(state="readonly")


# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()
