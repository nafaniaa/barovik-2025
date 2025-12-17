import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN

# ===================== НАСТРОЙКА DECIMAL =====================
getcontext().prec = 40

# ===================== ВАЛИДАЦИЯ ЧИСЕЛ =====================
def validate_number_format(num_str: str) -> str:
    s = num_str.strip().replace("\u00A0", " ")

    if 'e' in s.lower():
        return s.replace(' ', '').replace(',', '.')

    if ',' in s and '.' not in s:
        s = s.replace(',', '.')

    if s.count('-') > 1 or ('-' in s and not s.startswith('-')):
        raise ValueError("Некорректный знак минуса")

    if s.count('.') > 1:
        raise ValueError("Слишком много точек")

    if ' ' in s:
        int_part, *rest = s.split('.', 1)
        frac_part = rest[0] if rest else ''

        if "  " in int_part or "  " in frac_part:
            raise ValueError("Лишние пробелы")

        groups = int_part.split(' ')
        if len(groups[0].lstrip('-')) > 3:
            raise ValueError("Неправильная группировка разрядов")

        for g in groups[1:]:
            if len(g) != 3:
                raise ValueError("Неправильная группировка разрядов")

        if ' ' in frac_part:
            raise ValueError("Пробелы в дробной части недопустимы")

    return s.replace(' ', '')

# ===================== ФОРМАТ ВЫВОДА =====================
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
    groups = [rev[i:i + 3] for i in range(0, len(rev), 3)]
    int_formatted = " ".join(g[::-1] for g in groups[::-1])

    return sign + int_formatted + ('.' + frac_p if frac_p else '')

# ===================== ПРИЛОЖЕНИЕ =====================
class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Финансовый калькулятор — Полная версия")
        self.root.geometry("500x720")

        info = "ФИО: Гуринович Татьяна Витальевна\nКурс: 4\nГруппа: 4\nГод: 2025"
        tk.Label(root, text=info, justify=tk.LEFT, font=("Arial", 11)).pack(pady=10)

        main_frame = tk.Frame(root)
        main_frame.pack(pady=10)

        self.entries = []
        for i in range(1, 5):
            tk.Label(main_frame, text=f"Число {i}:", font=("Arial", 10)).pack()
            e = tk.Entry(main_frame, width=30, font=("Arial", 12))
            e.insert(0, "0")
            e.pack(pady=3)

            def clear_default(event, entry=e):
                if entry.get() == "0":
                    entry.delete(0, tk.END)

            e.bind("<FocusIn>", clear_default)
            self.enable_clipboard(e)
            self.entries.append(e)

        # Операции
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

        tk.Label(root, text="Результат:", font=("Arial", 12)).pack()
        self.result = tk.Entry(root, width=40, state='readonly', font=("Arial", 12))
        self.result.pack(pady=5)

        tk.Label(root, text="Выбор вида округления:", font=("Arial", 12)).pack(pady=10)
        self.round_var = tk.StringVar(value="math")
        frame_r = tk.Frame(root)
        frame_r.pack()
        tk.Radiobutton(frame_r, text="Математическое",
                       variable=self.round_var, value="math",
                       command=self.apply_round).pack(anchor="w")
        tk.Radiobutton(frame_r, text="Бухгалтерское",
                       variable=self.round_var, value="bank",
                       command=self.apply_round).pack(anchor="w")
        tk.Radiobutton(frame_r, text="Усечение",
                       variable=self.round_var, value="cut",
                       command=self.apply_round).pack(anchor="w")

        tk.Label(root, text="Округленный до целых:", font=("Arial", 12)).pack(pady=10)
        self.rounded = tk.Entry(root, width=40, state="readonly", font=("Arial", 12))
        self.rounded.pack(pady=5)

        self.last_result = None

    # ---------- буфер обмена ----------
    def enable_clipboard(self, widget):
        def copy(event):
            widget.event_generate("<<Copy>>")
            return "break"

        def paste(event):
            widget.event_generate("<<Paste>>")
            return "break"

        widget.bind("<Control-c>", copy)
        widget.bind("<Control-C>", copy)
        widget.bind("<Control-v>", paste)
        widget.bind("<Control-V>", paste)
        widget.bind("<Control-Insert>", copy)
        widget.bind("<Shift-Insert>", paste)

    # ---------- парсинг ----------
    def parse(self, s: str) -> Decimal:
        cleaned = validate_number_format(s)
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            raise ValueError("Некорректное число")

    # ---------- переполнение ----------
    def check_overflow(self, x: Decimal):
        LIM = Decimal("2000000000000")  # увеличенный лимит для тестов
        if x < -LIM or x > LIM:
            raise OverflowError("Переполнение")

    # ---------- вычисление ----------
    def calculate(self):
        try:
            nums = [self.parse(e.get()) for e in self.entries]
            ops = [o.get() for o in self.ops]

            a, b, c, d = nums
            op2 = ops[1]

            # 1. Приоритет второго и третьего числа (скобки)
            if op2 == "+":
                mid = (b + c).quantize(Decimal("0.0000000001"), ROUND_HALF_UP)
            elif op2 == "-":
                mid = (b - c).quantize(Decimal("0.0000000001"), ROUND_HALF_UP)
            elif op2 == "*":
                mid = (b * c).quantize(Decimal("0.0000000001"), ROUND_HALF_UP)
            elif op2 == "/":
                if c == 0:
                    raise ZeroDivisionError
                mid = (b / c).quantize(Decimal("0.0000000001"), ROUND_HALF_UP)
            self.check_overflow(mid)

            # 2. Создаем список для дальнейшего вычисления с приоритетом
            values = [a, mid, d]
            operations = [ops[0], ops[2]]  # первый и третий оператор

            # 3. Сначала умножение и деление
            i = 0
            while i < len(operations):
                if operations[i] in ("*", "/"):
                    if operations[i] == "*":
                        values[i] = (values[i] * values[i+1]).quantize(Decimal("0.0000000001"), ROUND_HALF_UP)
                    else:
                        if values[i+1] == 0:
                            raise ZeroDivisionError
                        values[i] = (values[i] / values[i+1]).quantize(Decimal("0.0000000001"), ROUND_HALF_UP)
                    del values[i+1]
                    del operations[i]
                else:
                    i += 1

            # 4. Затем сложение и вычитание
            result = values[0]
            for i, op in enumerate(operations):
                if op == "+":
                    result += values[i+1]
                else:
                    result -= values[i+1]
                result = result.quantize(Decimal("0.0000000001"), ROUND_HALF_UP)

            self.check_overflow(result)
            self.last_result = result

            # 5. Отображение точного результата
            out = format_output(result)
            self.result.config(state="normal")
            self.result.delete(0, tk.END)
            self.result.insert(0, out)
            self.result.config(state="readonly")

            # 6. Итоговое округление до целых
            self.apply_round()

        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "Деление на ноль")
        except OverflowError:
            messagebox.showerror("Ошибка", "Переполнение")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------- округление ----------
    def apply_round(self):
        if self.last_result is None:
            return

        x = self.last_result
        mode = self.round_var.get()

        if mode == "math":
            y = x.to_integral_value(rounding=ROUND_HALF_UP)
        elif mode == "bank":
            y = x.to_integral_value(rounding=ROUND_HALF_EVEN)
        else:  # усечение
            y = x.to_integral_value(rounding=ROUND_DOWN)

        self.rounded.config(state="normal")
        self.rounded.delete(0, tk.END)
        self.rounded.insert(0, format_output(y))
        self.rounded.config(state="readonly")


# ===================== ЗАПУСК =====================
if __name__ == "__main__":
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()
