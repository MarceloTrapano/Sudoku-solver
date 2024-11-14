from io import TextIOWrapper
import tkinter
import time
import tkinter.messagebox
import customtkinter
import numpy as np
import keras
import cv2
from PIL import Image, ImageTk
from numpy.typing import NDArray
from typing import List, Any
from Sudoku_solve import SudokuBruteForce, SudokuLP, SudokuIP
from Sudoku_Reader import Reader
from crop import get_sudoku_tiles

customtkinter.set_appearance_mode("Dark") 
customtkinter.set_default_color_theme("green") 

class App(customtkinter.CTk):
    """Graphical user interface for sudoku solver. It allows to solve sudoku with various methods. 
    You can solve problem on your own or with some help. Project includes scanning sudoku grid with webcam and
    provides estimated time for solution."""
    ORANGE: str = "#cf6e32"
    DARK_ORANGE: str = "#613317"
    BUTTON_FG_COLOR: str = "#2CC985"
    ENTRY_FG_COLOR: str = "#343638"
    IMG_SIZE: int = 25
    def __init__(self) -> None:
        super().__init__()

        #Configure window
        self.geometry("900x750")
        self.title("Sudoku")
        self.window = None

        #Configure grid
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        
        #Create sudoku grid
        self.sudoku_frame = customtkinter.CTkFrame(self, width=550, height=550)
        self.sudoku_frame.grid(row=0, column=1, pady=50, padx=0)
        self.entry_list: List[Any] = []
        k: int = 0
        bias_x: int = 0
        bias_y: int = 0
        for i in range(9):
            for j in range(9):
                self.entry_list.append(customtkinter.CTkEntry(master=self.sudoku_frame, 
                                                        width=44, 
                                                        height=44, 
                                                        font=('Calibri',30), 
                                                        justify='center',
                                                        max_length=0))
                self.entry_list[k].place(relx=0.1*(i+1)+bias_x, rely=0.1*(j+1)+bias_y, anchor=tkinter.CENTER)
                if j%3 == 2:
                    bias_y += 0.01
                k += 1
            bias_y = 0
            if i%3 == 2:
                bias_x += 0.01

        #Create cofiguration panel
        self.config_frame = customtkinter.CTkFrame(self, width=200, height=550)
        self.config_frame.grid(row=0, column=0, pady=50, padx=50)

        self.label = customtkinter.CTkLabel(master=self.config_frame, text="Sudoku solver", font=('Calibri',30))
        self.label.place(relx=0.075, rely=0)

        #Create string variables
        self.return_combobox_text: List[str] = ["Integer programming", "Programowanie całkowitoliczbowe"]
        self.check_text: List[str] = ["Check", "Sprawdź"]
        self.solve_text: List[str] = ["Solve", "Rozwiąż"]
        self.try_text: List[str] = ["Try", "Spróbuj"]
        self.scan_text: List[str] = ["Scan sudoku", "Skanuj sudoku"]
        self.return_text: List[str] = ['Return', 'Wróć']
        self.reset_text: str = "Reset"
        self.solve_methods: List[List[str]] = [["Brute force", "Linear programming", "Integer programming"],["Rozwiązanie siłowe", "Programowanie liniowe", "Programowanie całkowitoliczbowe"]]
        self.empty_solve_box: List[str] = ["Choose method","Wybierz metodę"]
        self.textbox_text: List[str] = ["Welcome to Sudoku solver!\n\nHere you can solve your Sudoku by inserting numbers in correct boxes or by scanning your sudoku. You can try to solve it by yourself or just get correct answer by clicking 'Solve' button.",
                                    "Witaj w solverze Sudoku!\n\nTutaj możesz rozwiązać sudoku poprzez wprowadzenie liczb w odpowiednie pola lub poprzez zeskanowanie twojego sudoku. Możesz spróbować je rozwiązać lub po prostu otrzymać poprawną odpowiedź klikając przycisk 'Rozwiąż'."]
        self.disclaimer_text: List[str] = ["Disclaimer: Sudoku solver can solve sudoku with at least one number but it does not guarantee same results as yours. Linear programming solutions can be incorrect due to nature of the problem.",
                                   "Uwaga: Sudoku solver może rozwiązać sudoku z co najmniej jedną liczbą, ale nie zapewnia takiego samego rezultatu jak twój. Rozwiązania z programowania liniowego mogą być niepoprawne przez naturę problemu."] 
        self.congratulation_text: List[str] = ["Congratulation!!!\n You solved sudoku!!!", "Gratulacje!!!\n Sudoku zostało rozwiązane!!!"]
        self.congratulation_label: List[str] = ["Congratulation!!!", "Gratulacje!!!"]
        self.placeholder_id: List[str] = ["Input sudoku ID", "Podaj numer sudoku"] 
        self.id_text: List[str] = ["Load","Załaduj"]
        self.disclaimer_label: List[str] = ["Disclaimer", "Uwaga"]
        #Create id frame
        self.id_frame = customtkinter.CTkFrame(self, width=550, height=50)
        self.id_frame.grid(row=1, column=1, pady=0, padx=0, sticky='ne')


        #Create buttons, entries and switches
        disclaimer_img = customtkinter.CTkImage(light_image=Image.open("disclaimer.png"), dark_image=Image.open("disclaimer.png"))
        self.disclaimer = customtkinter.CTkButton(master=self.config_frame,
                                                   text="", 
                                                   command= lambda: self.pop_up_window(self.disclaimer_label, self.disclaimer_text),
                                                   image=disclaimer_img)
        self.disclaimer.configure(fg_color='red', hover_color='#5c0d03', width=30, height=30)
        self.disclaimer.place(relx=0.75, rely=0.8, anchor=tkinter.CENTER)

        self.switch = customtkinter.CTkSwitch(master=self.config_frame, text="EN/PL", command=self.switch_event, onvalue=1, offvalue=0)
        self.switch.configure(fg_color=self.ORANGE, progress_color=self.ORANGE)
        self.switch.place(relx=0.40, rely=0.8, anchor=tkinter.CENTER)    

        self.id_entry = customtkinter.CTkEntry(master=self.id_frame,
                                                width=300,
                                                height=20, 
                                                font=('Calibri',20), 
                                                justify='left', 
                                                placeholder_text=self.placeholder_id[self.switch.get()],
                                                max_length=4)
        self.id_entry.place(relx=0.33, rely=0.5, anchor=tkinter.CENTER)

        reset_img = customtkinter.CTkImage(light_image=Image.open("reset.png"), dark_image=Image.open("reset.png"))
        self.reset_button = customtkinter.CTkButton(master=self.config_frame,
                                                     text=self.reset_text,
                                                     command=self.reset_sudoku,
                                                     image=reset_img,
                                                     compound=tkinter.LEFT)
        self.reset_button.configure(state='disabled', fg_color='gray')
        self.reset_button.place(relx=0.5, rely=0.65, anchor=tkinter.CENTER)

        solve_img = customtkinter.CTkImage(light_image=Image.open("solve.png"), dark_image=Image.open("solve.png"))
        self.solve_button = customtkinter.CTkButton(master=self.config_frame,
                                                    text=self.solve_text[self.switch.get()],
                                                    command=self.solve_sudoku,
                                                    image=solve_img,
                                                    compound=tkinter.LEFT)
        self.solve_button.configure(state='disabled',fg_color='gray')
        self.solve_button.place(relx=0.5, rely=0.95, anchor=tkinter.CENTER)

        self.try_button = customtkinter.CTkButton(master=self.config_frame, text=self.try_text[self.switch.get()], command=self.try_callable)
        self.try_button.configure(fg_color=self.ORANGE, hover_color=self.DARK_ORANGE)
        self.try_button.place(relx=0.5, rely=0.88, anchor=tkinter.CENTER)

        id_img = customtkinter.CTkImage(light_image=Image.open("load.png"), dark_image=Image.open("load.png"))
        self.id_button = customtkinter.CTkButton(master=self.id_frame, 
                                                 text=self.id_text[self.switch.get()], 
                                                 command=self.load_callable,
                                                 image=id_img,
                                                 compound=tkinter.LEFT
                                                 )
        self.id_button.configure(fg_color=self.ORANGE, hover_color=self.DARK_ORANGE, width=100, height=25)
        self.id_button.place(relx=0.87, rely=0.5, anchor=tkinter.CENTER)
        
        #Create button with an image
        scan_img = customtkinter.CTkImage(light_image=Image.open("scan1.png"), dark_image=Image.open("scan1.png"))
        
        self.scan_button = customtkinter.CTkButton(master=self.config_frame, 
                                            text=self.scan_text[self.switch.get()], 
                                            command=self.scan,
                                            image=scan_img,
                                            compound=tkinter.LEFT)
        self.scan_button.place(relx=0.5, rely=0.72, anchor=tkinter.CENTER)

        #Create combobox
        self.combobox = customtkinter.CTkComboBox(master=self.config_frame, values=self.solve_methods[self.switch.get()],
                                            command=self.combobox_callback)
        self.combobox.set(self.empty_solve_box[self.switch.get()])
        self.combobox.place(relx=0.5, rely=0.10, anchor=tkinter.CENTER)

        #Create textbox
        self.textbox = customtkinter.CTkTextbox(master=self.config_frame, width=160)
        self.textbox.insert(0.0, self.textbox_text[self.switch.get()])
        self.textbox.configure(state='disabled', font=("Calibri",12), wrap='word')
        self.textbox.place(relx=0.5, rely=0.34, anchor=tkinter.CENTER)

        self.check_button = None
        self.in_try: bool = False
        self.check_press: bool = True

        self.open_predefined_sudoku: TextIOWrapper[Any] = open("predefined_sudoku.txt", 'r')
        exec(self.open_predefined_sudoku.read())
        self.reader: Reader = Reader()
        self.model: Any = keras.models.load_model("sudoku_solver.h5")

    @staticmethod
    def disable_button(button) -> None:
        """Function that disables button

        Args: 
            button: Button to disable
        """
        button.configure(state='disabled', fg_color='gray')
    @staticmethod
    def change_language(list_of_elements: List[Any], list_of_prompts: List[str], state: bool) -> None:
        """Function that changes language from Polish to English and vice versa
        
        Args: 
            list_of_elements(List[Any]): List of configurable buttons
            list_of_prompts(List[str]): List of labels for buttons
            state(bool): 0-English, 1-Polish
        """
        for (element, prompt) in zip(list_of_elements, list_of_prompts):
            element.configure(text=prompt[state])
    def set_textbox(self, text: List[str]) -> None:
        """Method to set the textbox
        
        Args: 
            text(List[str]): Text provided with both languages"""
        self.textbox.configure(state='normal')
        self.textbox.delete(0.0, "end")
        self.textbox.insert(0.0, text[self.switch.get()])
        self.textbox.configure(state='disabled')
    def reset_sudoku(self) -> None:
        '''Funtion responsible for resetting sudoku grid.'''
        if not self.in_try:
            for entry in self.entry_list:
                entry.configure(state="normal", placeholder_text="", fg_color=self.ENTRY_FG_COLOR)
                entry.delete(-1, "end")
            self.disable_button(self.reset_button)
        else:
            for entry in self.entry_list:
                entry.configure(fg_color=self.ENTRY_FG_COLOR)
                if entry.cget("state") == "normal":
                    entry.delete(-1, "end")

    def switch_event(self) -> None:
        '''Function responsible for changing language.'''
        if self.switch.get():
            print("Język polski wybrany")
        else:
            print("Language changed to English")
        self.change_language([self.scan_button, self.id_button], 
                             [self.scan_text, self.id_text], self.switch.get())
        self.combobox.set(self.empty_solve_box[self.switch.get()])
        self.id_entry.configure(placeholder_text=self.placeholder_id[self.switch.get()])
        self.set_textbox(self.textbox_text)
        if self.in_try:
            self.change_language([self.try_button, self.check_button, self.solve_button],
                                 [self.return_text, self.check_text, self.solve_text], self.switch.get())
            self.combobox.configure(values=self.solve_methods[self.switch.get()], state="normal")
            self.combobox.set(self.return_combobox_text[self.switch.get()])
            self.combobox.configure(state="disabled")
        else:
            self.try_button.configure(text=self.try_text[self.switch.get()])
            self.combobox.configure(values=self.solve_methods[self.switch.get()])
            self.solve_button.configure(text=self.solve_text[self.switch.get()], fg_color="gray", state='disabled')
        self.update()

    def solve_sudoku(self) -> NDArray[np.float64] | bool:
        '''Function responsible for solving sudoku'''
        sudoku: List[int] = []
        for entry in self.entry_list:
            if entry.get() == "0":
                solve_error: List[str] = ["Solve Error: Your sudoku numbers must be natural.", "Błąd w rozwiązywaniu: Twoje sudoku musi mieć liczby naturalne"]
                self.set_textbox(solve_error)
                return False
            if entry.get():
                try:
                    sudoku_input: int = int(entry.get())
                except ValueError:
                    solve_error: List[str] = ["Solve Error: Your sudoku numbers must be natural.", "Błąd w rozwiązywaniu: Twoje sudoku musi mieć liczby naturalne"]
                    self.set_textbox(solve_error)
                    return False
                sudoku.append(sudoku_input)
            else:
                sudoku.append(0)
        if not any(sudoku):
            solve_error: List[str] = ["Solve Error: Your sudoku cannot be empty.", "Błąd w rozwiązywaniu: Twoje sudoku nie może być puste."]
            self.set_textbox(solve_error)
            return False
        sudoku = np.transpose(np.reshape(sudoku, (9,9)))
        if self.combobox.get() == "Brute force" or self.combobox.get() == "Rozwiązanie siłowe":
            sudoku_solver: SudokuBruteForce = SudokuBruteForce(sudoku)
        elif self.combobox.get() == "Linear programming" or self.combobox.get() == "Programowanie liniowe":
            sudoku_solver: SudokuLP = SudokuLP(sudoku)
        else:
            sudoku_solver: SudokuIP = SudokuIP(sudoku)
        try:
            tic: float = time.perf_counter()
            solution: NDArray[np.float64] = sudoku_solver.solve()
            toc: float = time.perf_counter()
        except ValueError:
            solve_error: List[str] = ["Solve Error: Your sudoku is invalid.", "Błąd w rozwiązywaniu: Twoje sudoku jest błędne."]
            self.set_textbox(solve_error)
            return False
        solve_time: List[str] = [f"Solved in {toc - tic:0.4f} s.", f"Rozwiązano w {toc - tic:0.4f} s."]
        self.set_textbox(solve_time)
        solution = np.reshape(np.transpose(solution),(81,1))
        i: int = 0
        for entry in self.entry_list:
            entry.configure(placeholder_text=f"{int(solution[i])}", placeholder_text_color='white')
            entry.configure(state='disabled')
            i += 1
        self.reset_button.configure(state='normal', fg_color='green')
        self.update()
        return solution
    def solve(self) -> NDArray[np.float64] | bool:
        '''Another function responsible for solving sudoku'''
        sudoku: List[int] = []
        for entry in self.entry_list:
            if entry.get() == "0":
                solve_error: List[str] = ["Solve Error: Your sudoku numbers must be natural.", "Błąd w rozwiązywaniu: Twoje sudoku musi mieć liczby naturalne"]
                self.set_textbox(solve_error)
                try:
                    self.disable_button(self.check_button)
                    self.disable_button(self.solve_button)
                    self.disable_button(self.reset_button)
                except Exception:
                    return False
                return False
            if entry.get():
                try:
                    sudoku_input: int = int(entry.get())
                except ValueError:
                    solve_error: List[str] = ["Solve Error: Your sudoku numbers must be natural.", "Błąd w rozwiązywaniu: Twoje sudoku musi mieć liczby naturalne"]
                    self.set_textbox(solve_error)
                    try:
                        self.disable_button(self.check_button)
                        self.disable_button(self.solve_button)
                        self.disable_button(self.reset_button)
                    except Exception:
                        return False
                    return False
                sudoku.append(sudoku_input)
            else:
                sudoku.append(0)
        if not any(sudoku):
            solve_error: List[str] = ["Solve Error: Your sudoku cannot be empty.", "Błąd w rozwiązywaniu: Twoje sudoku nie może być puste."]
            self.set_textbox(solve_error)
            try:
                self.disable_button(self.check_button)
                self.disable_button(self.solve_button)
                self.disable_button(self.reset_button)
            except Exception:
                return False
            return False
        sudoku = np.transpose(np.reshape(sudoku, (9,9)))
        sudoku_solver: SudokuIP = SudokuIP(sudoku)
        try:
            solution: NDArray[np.float64] = sudoku_solver.solve()
        except ValueError:
            solve_error: List[str] = ["Solve Error: Your sudoku is invalid.", "Błąd w rozwiązywaniu: Twoje sudoku jest błędne."]
            self.set_textbox(solve_error)
            try:
                self.disable_button(self.check_button)
                self.disable_button(self.solve_button)
                self.disable_button(self.reset_button)
            except Exception:
                return False
            return False
        solution = np.transpose(solution)
        solution = np.reshape(solution,(81,1))
        return solution
    def pop_up_window(self, label: List[str], text: List[str], font_size: int = 12)  -> None:
        '''Function for displaying pop up window
        
        Args:
            label(List[str]): Label to display
            text(List[str]): Text to display
            font_size(int, optional): Size of the font'''
        if self.window is None or not self.window.winfo_exists():
            self.window = customtkinter.CTkToplevel(self) 
        else:
            self.window.focus() 
        self.window.geometry("300x200")
        self.window.title(label[self.switch.get()])
        frame = customtkinter.CTkFrame(self.window, width=250, height=175)
        frame.pack(padx=10, pady=10)
        window_label = customtkinter.CTkLabel(frame, text=label[self.switch.get()])
        window_label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)
        textbox = customtkinter.CTkTextbox(master=self.window, width=220, height=110)
        textbox.tag_config("center", justify="center")
        textbox.insert(0.0, text[self.switch.get()])
        textbox.tag_add("center", 1.0, "end")
        textbox.configure(state='disabled', font=("Calibri",font_size), wrap='word')
        textbox.place(relx=0.5, rely=0.50, anchor=tkinter.CENTER)
    def combobox_callback(self, args) -> None:
        '''Method that allows solve button to be pressed.'''
        self.solve_button.configure(state='normal', fg_color=self.ORANGE, hover_color=self.DARK_ORANGE)

    def load_callable(self) -> None:
        '''Method for loading predefined sudoku grid'''
        if str(self.id_entry.get()).lower() == "debug":
            sudoku_id = np.random.randint(0,99999)
            self.reset_sudoku()
            sudoku: NDArray = self.predefined_sudoku[(sudoku_id)%len(self.predefined_sudoku)]
            sudoku = np.reshape(sudoku, (9,9))
            sudoku_IP = SudokuIP(sudoku)
            sudoku_solved: NDArray[np.float64] = sudoku_IP.solve()
            sudoku_solved = sudoku_solved.transpose()
            sudoku_solved = np.reshape(sudoku_solved, (81,1))
            k = 0
            for i in sudoku_solved:
                if 0 == i:
                    k += 1
                    continue
                self.entry_list[k].insert(0, str(i[0]))
                k += 1
            return
        try:
            sudoku_id: int = int(self.id_entry.get())
        except ValueError:
            id_error: List[str] = ["Id error: sudoku id must be integer", "Błąd klucza: klucz sudoku musi być całkowitoliczbowy"]
            self.set_textbox(id_error)
            return False
        self.reset_sudoku()
        sudoku: NDArray = self.predefined_sudoku[(sudoku_id+1)%len(self.predefined_sudoku)]
        sudoku = np.reshape(sudoku, (9,9))
        sudoku = sudoku.transpose()
        sudoku = np.reshape(sudoku, (81,1))
        k = 0
        for i in sudoku:
            if 0 == i:
                k += 1
                continue
            self.entry_list[k].insert(0, str(i[0]))
            k += 1
            

    def try_callable(self) -> None:
        '''Funtion that allows user to solve sudoku by him/herself.'''
        if not self.in_try:
            self.scan_button.configure(state="disabled", fg_color="gray")
            self.combobox.set(self.return_combobox_text[self.switch.get()])
            self.combobox.configure(state="disabled")
            self.solve_button.configure(state="normal", fg_color=self.ORANGE, hover_color=self.DARK_ORANGE)
            self.reset_button.configure(state="normal", fg_color='green')

            self.check_button = customtkinter.CTkButton(self.config_frame, text=self.check_text[self.switch.get()], command=self.check)
            self.check_button.configure(fg_color=self.ORANGE, hover_color=self.DARK_ORANGE)
            self.check_button.place(relx=0.5, rely=0.58, anchor=tkinter.CENTER)

            self.in_try = True

            self.solution: NDArray[np.float64] | bool = self.solve()

            for entry in self.entry_list:
                if entry.get():
                    entry.configure(state='disabled')
            self.try_button.configure(text=self.return_text[self.switch.get()])
        else:
            self.check_button.destroy()
            self.in_try = False
            self.reset_button.configure(state='disabled', fg_color='gray')
            self.solve_button.configure(state='normal', fg_color=self.ORANGE)
            self.combobox.configure(state='normal')
            self.scan_button.configure(state="normal", fg_color=self.BUTTON_FG_COLOR)
            self.try_button.configure(text=self.try_text[self.switch.get()])
            for entry in self.entry_list:
                entry.configure(fg_color=self.ENTRY_FG_COLOR)
                if entry.get():
                    entry.configure(state='normal')
    def check(self) -> None:
        '''Function that checks if the solution is correct'''
        congratulation = True
        if self.check_press:
            i: int = 0
            for entry in self.entry_list:
                if entry.get() and entry.cget("state")=="normal":
                    try: 
                        int(entry.get())
                    except ValueError:
                        entry.configure(fg_color='red')
                        congratulation = False
                        entry_error: List[str] = ['Entry error: Input cannot be interpreted as integer', 'Błąd wejścia: Musi zostać podana wartość liczbowa'] 
                        self.set_textbox(entry_error)
                        i += 1
                        continue
                    if int(entry.get()) != self.solution[i]:
                        entry.configure(fg_color='red')
                        congratulation = False
                    else:
                        entry.configure(fg_color='green')
                if not entry.get():
                    congratulation = False
                i += 1
            self.check_press = False
            if not congratulation:
                return
            for entry in self.entry_list:
                if entry.get() is None:
                    return
            self.pop_up_window(self.congratulation_label, self.congratulation_text, 24)
        else:
            self.check_press = True
            for entry in self.entry_list:
                entry.configure(fg_color=self.ENTRY_FG_COLOR)
    def scan(self) -> None:
        '''Function that allows user to scan sudoku grid.'''
        self.reset_sudoku()
        self.reader.show()
        get_sudoku_tiles('Sudoku.png', name="scan", save=True)
        sudoku_array: List[Any] = []
        for i in range(81):
            sudoku_tile = cv2.resize(cv2.imread(f"scan_{i}.png", cv2.IMREAD_GRAYSCALE), (self.IMG_SIZE, self.IMG_SIZE))
            sudoku_array.append(sudoku_tile.reshape(-1, self.IMG_SIZE, self.IMG_SIZE, 1))

        sudoku_grid: List[Any] = []
        for scan in sudoku_array:
            sudoku_grid.append(self.model.predict(scan))
        i = 0
        for line in sudoku_grid:
            number = np.where(line[0]>0.5)[0][0]
            print(line)
            print(number)
            if 0 == number:
                i += 9
                i = i%81
                if i < 9:
                    i += 1
                continue
            self.entry_list[i].insert(0, str(number))
            i += 9
            i = i%81
            if i < 9:
                i += 1

if __name__ == '__main__':
    app: App = App()
    app.mainloop()