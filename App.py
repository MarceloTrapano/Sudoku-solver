import tkinter
import time
import tkinter.messagebox
import customtkinter
import numpy as np
from PIL import Image, ImageTk
from numpy.typing import NDArray
from typing import List, Any
from Sudoku_solve import SudokuBruteForce, SudokuLP, SudokuIP

customtkinter.set_appearance_mode("Dark") 
customtkinter.set_default_color_theme("green") 

class App(customtkinter.CTk):
    """Graphical user interface for sudoku solver. It allows to solve sudoku with various methods. 
    You can solve problem on your own or with some help. Project includes scanning sudoku grid with webcam and
    provides estimated time for solution."""
    ORANGE: str = "#cf6e32"
    DARK_ORANGE: str = "#613317"
    def __init__(self) -> None:
        super().__init__()

        #Configure window
        self.geometry("900x650")
        self.title("Sudoku")

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

        #Create buttons and switches
        self.disclaimer = customtkinter.CTkButton(master=self.config_frame, text="!", command=self.disclaimer)
        self.disclaimer.configure(fg_color='red', hover_color='#5c0d03', width=30, height=30)
        self.disclaimer.place(relx=0.75, rely=0.8, anchor=tkinter.CENTER)

        self.switch = customtkinter.CTkSwitch(master=self.config_frame, text="EN/PL", command=self.switch_event, onvalue=1, offvalue=0)
        self.switch.configure(fg_color=self.ORANGE, progress_color=self.ORANGE)
        self.switch.place(relx=0.40, rely=0.8, anchor=tkinter.CENTER)    

        self.reset_button = customtkinter.CTkButton(master=self.config_frame, text=self.reset_text, command=self.reset_sudoku)
        self.reset_button.configure(state='disabled', fg_color='gray')
        self.reset_button.place(relx=0.5, rely=0.65, anchor=tkinter.CENTER)

        self.solve_button = customtkinter.CTkButton(master=self.config_frame, text=self.solve_text[self.switch.get()], command=self.solve_sudoku)
        self.solve_button.configure(state='disabled',fg_color='gray')
        self.solve_button.place(relx=0.5, rely=0.95, anchor=tkinter.CENTER)

        self.try_button = customtkinter.CTkButton(master=self.config_frame, text=self.try_text[self.switch.get()], command=self.try_callable)
        self.try_button.configure(fg_color=self.ORANGE, hover_color=self.DARK_ORANGE)
        self.try_button.place(relx=0.5, rely=0.88, anchor=tkinter.CENTER)
        
        #Create button with image
        scan_img = ImageTk.PhotoImage(Image.open("scan1.png"))
        self.scan_button = customtkinter.CTkButton(master=self.config_frame, 
                                            text=self.scan_text[self.switch.get()], 
                                            command=self.scan,
                                            image=scan_img,
                                            compound=tkinter.LEFT)
        self.scan_button.place(relx=0.5, rely=0.72, anchor=tkinter.CENTER)

        self.button_fg_color: Any = self.scan_button.cget('fg_color')
        self.entry_fg_color: Any = self.entry_list[1].cget('fg_color')

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

        self.disclaimer_window = None
        self.check_button = None
        self.in_try: bool = False
        self.check_press: bool = True

    def reset_sudoku(self) -> None:
        '''Funtion responsible for resetting sudoku grid.'''
        if not self.in_try:
            for entry in self.entry_list:
                entry.configure(state="normal", placeholder_text="", fg_color=self.entry_fg_color)
                entry.delete(-1, "end")
            self.reset_button.configure(state='disabled', fg_color='gray')
        else:
            for entry in self.entry_list:
                entry.configure(fg_color=self.entry_fg_color)
                if entry.cget("state") == "normal":
                    entry.delete(-1, "end")

    def switch_event(self) -> None:
        '''Function responsible for changing language.'''
        if self.switch.get():
            print("Język polski wybrany")
        else:
            print("Language changed to English")
        self.scan_button.configure(text=self.scan_text[self.switch.get()])
        self.combobox.set(self.empty_solve_box[self.switch.get()])
        self.textbox.configure(state='normal')
        self.textbox.delete(0.0, "end")
        self.textbox.insert(0.0, self.textbox_text[self.switch.get()])
        self.textbox.configure(state='disabled')
        if self.in_try:
            self.try_button.configure(text=self.return_text[self.switch.get()])
            self.combobox.configure(values=self.solve_methods[self.switch.get()], state="normal")
            self.combobox.set(self.return_combobox_text[self.switch.get()])
            self.combobox.configure(state="disabled")
            self.check_button.configure(text=self.check_text[self.switch.get()])
            self.solve_button.configure(text=self.solve_text[self.switch.get()])
        else:
            self.try_button.configure(text=self.try_text[self.switch.get()])
            self.combobox.configure(values=self.solve_methods[self.switch.get()])
            self.solve_button.configure(text=self.solve_text[self.switch.get()], fg_color="gray", state='disabled')
        self.update()

    def solve_sudoku(self) -> NDArray[np.float64] | bool:
        '''Function responsible for solving sudoku'''
        sudoku: List[int] = []
        for entry in self.entry_list:
            if entry.get():
                try:
                    sudoku_input: int = int(entry.get())
                except ValueError:
                    solve_error: List[str] = ["Solve Error: Your sudoku numbers must be integer.", "Błąd w rozwiązywaniu: Twoje sudoku musi być całkowitoliczbowe"]
                    self.textbox.configure(state='normal')
                    self.textbox.delete(0.0, "end")
                    self.textbox.insert(0.0, solve_error[self.switch.get()])
                    self.textbox.configure(state='disabled')
                    return False
                sudoku.append(sudoku_input)
            else:
                sudoku.append(0)
        if not any(sudoku):
            solve_error: List[str] = ["Solve Error: Your sudoku cannot be empty.", "Błąd w rozwiązywaniu: Twoje sudoku nie może być puste."]
            self.textbox.configure(state='normal')
            self.textbox.delete(0.0, "end")
            self.textbox.insert(0.0, solve_error[self.switch.get()])
            self.textbox.configure(state='disabled')
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
            self.textbox.configure(state='normal')
            self.textbox.delete(0.0, "end")
            self.textbox.insert(0.0, solve_error[self.switch.get()])
            self.textbox.configure(state='disabled')
            return False
        solve_time: List[str] = [f"Solved in {toc - tic:0.4f} s.", f"Rozwiązano w {toc - tic:0.4f} s."]
        self.textbox.configure(state='normal')
        self.textbox.delete(0.0, "end")
        self.textbox.insert(0.0, solve_time[self.switch.get()])
        self.textbox.configure(state='disabled')
        solution = np.reshape(np.transpose(solution),(81,1))
        i: int = 0
        for entry in self.entry_list:
            entry.configure(placeholder_text=f"{int(solution[i])}", placeholder_text_color='white')
            entry.configure(state='disabled')
            i += 1
        self.reset_button.configure(state='normal', fg_color='green')
        self.update()
        return solution
    def solve(self):
        '''Another function responsible for solving sudoku'''
        sudoku: List[int] = []
        for entry in self.entry_list:
            if entry.get():
                try:
                    sudoku_input: int = int(entry.get())
                except ValueError:
                    solve_error: List[str] = ["Solve Error: Your sudoku numbers must be integer.", "Błąd w rozwiązywaniu: Twoje sudoku musi być całkowitoliczbowe"]
                    self.textbox.configure(state='normal')
                    self.textbox.delete(0.0, "end")
                    self.textbox.insert(0.0, solve_error[self.switch.get()])
                    self.textbox.configure(state='disabled')
                    return False
                sudoku.append(sudoku_input)
            else:
                sudoku.append(0)
        if not any(sudoku):
            solve_error: List[str] = ["Solve Error: Your sudoku cannot be empty.", "Błąd w rozwiązywaniu: Twoje sudoku nie może być puste."]
            self.textbox.configure(state='normal')
            self.textbox.delete(0.0, "end")
            self.textbox.insert(0.0, solve_error[self.switch.get()])
            self.textbox.configure(state='disabled')
            return False
        sudoku = np.transpose(np.reshape(sudoku, (9,9)))
        sudoku_solver: SudokuIP = SudokuIP(sudoku)
        try:
            solution: NDArray[np.float64] = sudoku_solver.solve()
        except ValueError:
            solve_error: List[str] = ["Solve Error: Your sudoku is invalid.", "Błąd w rozwiązywaniu: Twoje sudoku jest błędne."]
            self.textbox.configure(state='normal')
            self.textbox.delete(0.0, "end")
            self.textbox.insert(0.0, solve_error[self.switch.get()])
            self.textbox.configure(state='disabled')
            return False
        solution = np.reshape(np.transpose(solution),(81,1))
        return solution
    def disclaimer(self) -> None:
        '''Function to display the disclaimer.'''
        text: List[str] = ["Disclaimer", "Uwaga"]
        if self.disclaimer_window is None or not self.disclaimer_window.winfo_exists():
            self.disclaimer_window = customtkinter.CTkToplevel(self) 
        else:
            self.disclaimer_window.focus() 
        self.disclaimer_window.geometry("300x200")
        self.disclaimer_window.title(text[self.switch.get()])
        disclaimer_frame = customtkinter.CTkFrame(self.disclaimer_window, width=250, height=175)
        disclaimer_frame.pack(padx=10, pady=10)
        disclaimer_label = customtkinter.CTkLabel(disclaimer_frame, text=text[self.switch.get()])
        disclaimer_label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)
        disclaimer_textbox = customtkinter.CTkTextbox(master=self.disclaimer_window, width=220, height=110)
        disclaimer_textbox.insert(0.0, self.disclaimer_text[self.switch.get()])
        disclaimer_textbox.configure(state='disabled', font=("Calibri",12), wrap='word')
        disclaimer_textbox.place(relx=0.5, rely=0.50, anchor=tkinter.CENTER)
    def combobox_callback(self, args) -> None:
        '''Method that allows solve button to be pressed.'''
        self.solve_button.configure(state='normal', fg_color=self.ORANGE, hover_color=self.DARK_ORANGE)

    def try_callable(self) -> None:
        '''Funtion that allows user to solve sudoku by him\herself.'''
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
            self.combobox.configure(state='normal')
            self.scan_button.configure(state="normal", fg_color=self.button_fg_color)
            self.try_button.configure(text=self.try_text[self.switch.get()])
            for entry in self.entry_list:
                entry.configure(fg_color=self.entry_fg_color)
                if entry.get():
                    entry.configure(state='normal')
    def check(self) -> None:
        '''Function that checks if the solution is correct'''
        if self.check_press:
            i: int = 0
            for entry in self.entry_list:
                if entry.get():
                    if int(entry.get()) != self.solution[i]:
                        entry.configure(fg_color='red')
                    else:
                        entry.configure(fg_color=self.entry_fg_color)
                else:
                    entry.configure(fg_color='red')
                i += 1
            self.check_press = False
        else:
            self.check_press = True
            for entry in self.entry_list:
                entry.configure(fg_color=self.entry_fg_color)
    def scan(self) -> None:
        '''Function that allows user to scan sudoku grid. (To implement)'''
        pass
    
if __name__ == '__main__':
    app: App = App()
    app.mainloop()