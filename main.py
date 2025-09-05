import json
import datetime
import hashlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


# ------------------- Pomocnicze -------------------
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ------------------- Wiersz edytowalny -------------------
class EditableRow(BoxLayout):
    def _init_(self, parent_list, parent_layout, name="Nowa pozycja", value="", **kwargs):
        super()._init_(orientation="horizontal", spacing=10, size_hint_y=None, height=70, **kwargs)

        self.parent_list = parent_list
        self.parent_layout = parent_layout

        # Nazwa
        self.name_input = TextInput(text=name, multiline=False, font_size=45, size_hint_x=0.45)
        self.add_widget(self.name_input)

        # Kwota
        self.value_input = TextInput(text=value, multiline=False, input_filter="float",
                                     font_size=45, size_hint_x=0.35)
        self.add_widget(self.value_input)

        # Usuń
        btn_delete = Button(text="❌", size_hint_x=0.2,
                            background_color=(0.8, 0.2, 0.2, 1), font_size=45)
        btn_delete.bind(on_press=self.remove_self)
        self.add_widget(btn_delete)

    def get_name(self):
        return self.name_input.text.strip()

    def get_value(self):
        try:
            return float(self.value_input.text)
        except:
            return 0.0

    def remove_self(self, instance):
        if self in self.parent_list:
            self.parent_list.remove(self)
        self.parent_layout.remove_widget(self)


# ------------------- Ekran logowania -------------------
class LoginScreen(Screen):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)

        layout = GridLayout(cols=1, padding=20, spacing=20)

        # Tytuły
        layout.add_widget(Label(text="Organizer budżetu", font_size=70, color=(1, 1, 1, 1)))
        layout.add_widget(Label(text="Zarządzaj swoim budżetem mądrze,\na sukces sam cię znajdzie",
                                font_size=45, color=(1, 1, 1, 1)))

        # Pola login/hasło
        self.username_input = TextInput(hint_text="Login", multiline=False, font_size=45,
                                        size_hint_y=None, height=60)
        layout.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Hasło", multiline=False, password=True,
                                        font_size=45, size_hint_y=None, height=60)
        layout.add_widget(self.password_input)

        self.info_label = Label(text="", font_size=45, color=(1, 0.5, 0.5, 1))
        layout.add_widget(self.info_label)

        # Przyciski
        btn_login = Button(text="Zaloguj", size_hint_y=None, height=70,
                           background_color=(0.1, 0.6, 0.2, 1), font_size=45)
        btn_login.bind(on_press=self.login)
        layout.add_widget(btn_login)

        btn_register = Button(text="Zarejestruj", size_hint_y=None, height=70,
                              background_color=(0.2, 0.4, 0.8, 1), font_size=45)
        btn_register.bind(on_press=self.register)
        layout.add_widget(btn_register)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if username in users and users[username] == hash_password(password):
            self.manager.current = "budget"
            self.manager.get_screen("budget").set_user(username)
        else:
            self.info_label.text = "❌ Niepoprawny login lub hasło"

    def register(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.info_label.text = "⚠ Wpisz login i hasło!"
            return

        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if username in users:
            self.info_label.text = "⚠ Taki login już istnieje!"
            return

        users[username] = hash_password(password)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

        self.info_label.text = "✅ Konto utworzone! Możesz się zalogować."


# ------------------- Ekran budżetu -------------------
class BudgetScreen(Screen):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.username = None

        self.rows_balance, self.rows_income, self.rows_expense = [], [], []

        root = BoxLayout(orientation="vertical")
        scroll = ScrollView(size_hint=(1, 1))
        self.main_layout = GridLayout(cols=1, spacing=20, padding=20,
                                      size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter("height"))

        # Tytuł
        self.main_layout.add_widget(Label(text="💰 Budżet - Organizer",
                                          font_size=45, size_hint_y=None, height=70,
                                          color=(1, 1, 1, 1)))

        # Pasek wyloguj / zamknij
        top_bar = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=60)
        btn_logout = Button(text="Wyloguj", background_color=(0.7, 0.2, 0.2, 1), font_size=45)
        btn_logout.bind(on_press=self.logout)
        top_bar.add_widget(btn_logout)

        btn_exit = Button(text="Zamknij aplikację", background_color=(0.2, 0.2, 0.2, 1), font_size=45)
        btn_exit.bind(on_press=self.exit_app)
        top_bar.add_widget(btn_exit)

        self.main_layout.add_widget(top_bar)

        # Wybór miesiąca
        date_row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=60)
        date_row.add_widget(Label(text="Miesiąc:", font_size=45, color=(1, 1, 1, 1)))
        self.month_input = TextInput(text=str(datetime.datetime.now().month).zfill(2),
                                     multiline=False, font_size=45, size_hint_x=0.3)
        date_row.add_widget(self.month_input)

        date_row.add_widget(Label(text="Rok:", font_size=45, color=(1, 1, 1, 1)))
        self.year_input = TextInput(text=str(datetime.datetime.now().year),
                                    multiline=False, font_size=45, size_hint_x=0.4)
        date_row.add_widget(self.year_input)

        self.main_layout.add_widget(date_row)

        # Obecny stan
        self.main_layout.add_widget(Label(text="[b]Obecny stan budżetu[/b]", markup=True,
                                          font_size=45, size_hint_y=None, height=40,
                                          color=(1, 1, 0.5, 1)))

        self.balance_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.balance_layout.bind(minimum_height=self.balance_layout.setter("height"))
        self.main_layout.add_widget(self.balance_layout)

        self.add_balance_row("Na koncie")
        self.add_balance_row("W portfelu")

        btn_add_balance = Button(text="+ Dodaj pozycję ",
                                 size_hint_y=None, height=50,
                                 background_color=(0.3, 0.5, 0.8, 1), font_size=45)
        btn_add_balance.bind(on_press=lambda x: self.add_balance_row())
        self.main_layout.add_widget(btn_add_balance)

        # Dochody
        self.main_layout.add_widget(Label(text="[b]Planowane dochody[/b]", markup=True,
                                          font_size=45, size_hint_y=None, height=40,
                                          color=(0.5, 1, 0.5, 1)))

        self.income_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.income_layout.bind(minimum_height=self.income_layout.setter("height"))
        self.main_layout.add_widget(self.income_layout)

        self.add_income_row("Praca stała")
        self.add_income_row("Dodatkowe źródło")

        btn_add_income = Button(text="+ Dodaj źródło dochodu",
                                size_hint_y=None, height=50,
                                background_color=(0.2, 0.6, 0.2, 1), font_size=45)
        btn_add_income.bind(on_press=lambda x: self.add_income_row())
        self.main_layout.add_widget(btn_add_income)

        # Wydatki
        self.main_layout.add_widget(Label(text="[b]Planowane wydatki[/b]", markup=True,
                                          font_size=45, size_hint_y=None, height=40,
                                          color=(1, 0.5, 0.5, 1)))

        self.expense_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.expense_layout.bind(minimum_height=self.expense_layout.setter("height"))
        self.main_layout.add_widget(self.expense_layout)

        self.add_expense_row("Rachunki i czynsz")
        self.add_expense_row("Paliwo ")

        btn_add_expense = Button(text="+ Dodaj wydatek",
                                 size_hint_y=None, height=50,
                                 background_color=(0.6, 0.2, 0.2, 1), font_size=45)
        btn_add_expense.bind(on_press=lambda x: self.add_expense_row())
        self.main_layout.add_widget(btn_add_expense)

        # Wczytaj
        btn_load = Button(text="📂 Wczytaj budżet", size_hint_y=None, height=50,
                          background_color=(0.4, 0.6, 0.2, 1), font_size=45)
        btn_load.bind(on_press=self.load_data)
        self.main_layout.add_widget(btn_load)

        # Oblicz
        calc_button = Button(text="Oblicz budżet", size_hint_y=None, height=60,
                             background_color=(0.1, 0.4, 0.8, 1),
                             color=(1, 1, 1, 1), font_size=45)
        calc_button.bind(on_press=self.calculate)
        self.main_layout.add_widget(calc_button)

        # Wyniki
        self.result_label = Label(text="Wyniki pojawią się tutaj",
                                  font_size=45, size_hint_y=None,
                                  color=(1, 1, 1, 1),
                                  markup=True,
                                  halign="left", valign="top")
        self.result_label.bind(
            width=lambda *x: setattr(self.result_label, 'text_size', (self.result_label.width, None)),
            texture_size=lambda *x: setattr(self.result_label, 'height', self.result_label.texture_size[1] + 20)
        )
        self.main_layout.add_widget(self.result_label)

        scroll.add_widget(self.main_layout)
        root.add_widget(scroll)
        self.add_widget(root)

    # ustaw użytkownika
    def set_user(self, username):
        self.username = username

    # Wylogowanie
    def logout(self, instance):
        self.save_data()
        self.manager.current = "login"

    # Zamknięcie aplikacji
    def exit_app(self, instance):
        self.save_data()
        App.get_running_app().stop()
        Window.close()

    # Dodawanie wierszy
    def add_balance_row(self, name="Nowa pozycja", value=""):
        row = EditableRow(self.rows_balance, self.balance_layout, name, value)
        self.rows_balance.append(row)
        self.balance_layout.add_widget(row)

    def add_income_row(self, name="Nowe źródło", value=""):
        row = EditableRow(self.rows_income, self.income_layout, name, value)
        self.rows_income.append(row)
        self.income_layout.add_widget(row)

    def add_expense_row(self, name="Nowy wydatek", value=""):
        row = EditableRow(self.rows_expense, self.expense_layout, name, value)
        self.rows_expense.append(row)
        self.expense_layout.add_widget(row)

    # Plik dla użytkownika i miesiąca
    def get_filename(self):
        month = self.month_input.text.strip()
        year = self.year_input.text.strip()
        return f"{self.username}budzet{month}_{year}.json"

    # Zapis / wczytanie
    def save_data(self):
        data = {
            "balance": [(row.get_name(), row.value_input.text) for row in self.rows_balance],
            "income": [(row.get_name(), row.value_input.text) for row in self.rows_income],
            "expense": [(row.get_name(), row.value_input.text) for row in self.rows_expense],
        }
        with open(self.get_filename(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self, instance):
        try:
            with open(self.get_filename(), "r", encoding="utf-8") as f:
                data = json.load(f)

            # Czyścimy
            self.balance_layout.clear_widgets()
            self.income_layout.clear_widgets()
            self.expense_layout.clear_widgets()
            self.rows_balance, self.rows_income, self.rows_expense = [], [], []

            # Przywracamy
            for name, value in data.get("balance", []):
                self.add_balance_row(name, value)
            for name, value in data.get("income", []):
                self.add_income_row(name, value)
            for name, value in data.get("expense", []):
                self.add_expense_row(name, value)

            self.result_label.text = f"📂 Wczytano budżet: {self.get_filename()}"
        except FileNotFoundError:
            self.result_label.text = "⚠ Brak pliku dla wybranego miesiąca!"

    # Obliczenia
    def calculate(self, instance):
        saldo = sum(row.get_value() for row in self.rows_balance)
        dochody = sum(row.get_value() for row in self.rows_income)
        wydatki = sum(row.get_value() for row in self.rows_expense)
        suma_przychodow = saldo + dochody
        wynik = suma_przychodow - wydatki

        if wynik < 0:
            kolor = "ff0000"
            dopisek = "Zmniejsz wydatki lub podejmij dodatkową pracę !!!"
        elif wynik < 0.1 * suma_przychodow:
            kolor = "ffa500"
            dopisek = "Mogło by być lepiej"
        else:
            kolor = "00ff00"
            dopisek = "Bardzo dobrze"

        self.result_label.text = (
            f"[color=ffffff]Obecny stan: {saldo:.2f} zł\n"
            f"Planowane dochody: {dochody:.2f} zł\n"
            f"Planowane wydatki: {wydatki:.2f} zł\n"
            f"Suma (stan + dochody): {suma_przychodow:.2f} zł\n\n"
            f"➡ Pozostaje na koniec: [/color][color={kolor}]{wynik:.2f} zł - {dopisek}[/color]"
        )

    def on_leave(self):
        self.save_data()


# ------------------- Główna aplikacja -------------------
class BudgetApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(BudgetScreen(name="budget"))
        return sm


if _name_ == "_main_":
    BudgetApp().run()
