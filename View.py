import customtkinter as ctk
import tkinter as tk
from typing import List, Any
import numpy as np
from numpy.typing import NDArray
import threading
from PIL import Image

# Global variables
ORANGE: str = "#cf6e32"
DARK_ORANGE: str = "#613317"
BUTTON_FG_COLOR: str = "#2CC985"
ENTRY_FG_COLOR: str = "#343638"
IMG_SIZE: int = 25
RETURN_COMBOBOX_TEXT: List[str] = ["Integer programming", "Programowanie całkowitoliczbowe"]
CHECK_TEXT: List[str] = ["Check", "Sprawdź"]
SOLVE_TEXT: List[str] = ["Solve", "Rozwiąż"]
TRY_TEXT: List[str] = ["Try", "Spróbuj"]
SCAN_TEXT: List[str] = ["Scan sudoku", "Skanuj sudoku"]
RETURN_TEXT: List[str] = ['Return', 'Wróć']
RESET_TEXT: str = "Reset"
SOLVE_METHODS: List[List[str]] = [["Brute force", "Linear programming", "Integer programming"],["Rozwiązanie siłowe", "Programowanie liniowe", "Programowanie całkowitoliczbowe"]]
EMPTY_SOLVE_BOX: List[str] = ["Choose method","Wybierz metodę"]
TEXTBOX_TEXT: List[str] = ["Welcome to Sudoku solver!\n\nHere you can solve your Sudoku by inserting numbers in correct boxes or by scanning your sudoku. You can try to solve it by yourself or just get correct answer by clicking 'Solve' button.",
                        "Witaj w solverze Sudoku!\n\nTutaj możesz rozwiązać sudoku poprzez wprowadzenie liczb w odpowiednie pola lub poprzez zeskanowanie twojego sudoku. Możesz spróbować je rozwiązać lub po prostu otrzymać poprawną odpowiedź klikając przycisk 'Rozwiąż'."]
DISCLAIMER_TEXT: List[str] = ["Disclaimer: Sudoku solver can solve sudoku with at least one number but it does not guarantee same results as yours. Linear programming solutions can be incorrect due to nature of the problem.",
                        "Uwaga: Sudoku solver może rozwiązać sudoku z co najmniej jedną liczbą, ale nie zapewnia takiego samego rezultatu jak twój. Rozwiązania z programowania liniowego mogą być niepoprawne przez naturę problemu."] 
CONGRATULATION_TEXT: List[str] = ["Congratulation!!!\n You solved sudoku!!!", "Gratulacje!!!\n Sudoku zostało rozwiązane!!!"]
CONGRATULATION_LABEL: List[str] = ["Congratulation!!!", "Gratulacje!!!"]
PLACEHOLDER_ID: List[str] = ["Input sudoku ID", "Podaj numer sudoku"] 
ID_TEXT: List[str] = ["Load","Załaduj"]
DISCLAIMER_LABEL: List[str] = ["Disclaimer", "Uwaga"]

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("green") 

class ViewSudoku(ctk.CTkFrame):
    """Create view for sudoku grid.
    """
    def __init__(self, master) -> None:
        super().__init__(master, width= 550, height=550)
        self.entry_list: List[Any] = []
        k: int = 0
        bias_x: int = 0
        bias_y: int = 0
        for i in range(9): # Create sudoku grid with entries
            for j in range(9):
                self.entry_list.append(ctk.CTkEntry(master=self, 
                                                        width=44, 
                                                        height=44, 
                                                        font=('Calibri',30), 
                                                        justify='center',
                                                        max_length=0))
                self.entry_list[k].place(relx=0.1*(i+1)+bias_x, rely=0.1*(j+1)+bias_y, anchor=tk.CENTER)
                if j%3 == 2: # Biases are calculated for sudoku style tiles spacing
                    bias_y += 0.01
                k += 1
            bias_y = 0
            if i%3 == 2:
                bias_x += 0.01

    def reset_grid(self, state: bool=True) -> None:
        """Reset sudoku grid.

        Args:
            state (bool, optional): 1-Reset all tiles, 0-Reset only active ones. Defaults to True.
        """
        if state:
            for entry in self.entry_list:
                entry.configure(state="normal", placeholder_text="", fg_color=ENTRY_FG_COLOR)
                entry.delete(-1, "end")
            return
        for entry in self.entry_list:
            entry.configure(fg_color=ENTRY_FG_COLOR)
            if entry.cget("state") == "normal":
                entry.delete(-1, "end")

    def insert(self, array: NDArray[np.int64], state='normal') -> None:
        """Insert array into sudoku grid.

        Args:
            array (NDArray[np.int64]): 9 by 9 array. 0-empty space.
            state (str, optional): Choose configuration state for entry when inserting. Defaults to 'normal'.
        """
        self.reset_grid() # Reset grid before inserting
        array = np.reshape(array, (9,9))
        array = array.transpose() # Transpose array because entry list was created from up to bottom
        array = np.reshape(array, (81,1))
        k = 0
        for i in array:
            if 0 == i:
                k += 1
                continue
            self.entry_list[k].insert(0, str(i[0]))
            self.entry_list[k].configure(state=state)
            k += 1
    
    def lock_grid(self, state=True) -> None:
        """Lock or unlock filled grid tiles.

        Args:
            state (bool, optional): 1-Lock grid, 0-Unlock grid. Defaults to True.
        """
        if not state: 
            for entry in self.entry_list:
                if entry.get() != "":
                    entry.configure(state="disabled")
            return
        for entry in self.entry_list:
            entry.configure(state="normal")

    def read(self) -> NDArray[np.int64]:
        """Read from sudoku entries.

        Raises:
            ValueError: When input is not int from range 1 through 9 or empty string.
            ValueError: When array is empty.

        Returns:
            NDArray[np.int64]: Read array.
        """
        error = True
        array: List[int] = []
        for entry in self.entry_list:
            if entry.get() == "":
                array.append(0)
            elif int(entry.get()) in range(1,10):
                error = False
                array.append(int(entry.get()))
            else:
                raise ValueError
        if error:
            raise ValueError
        return np.transpose(np.reshape(np.array(array),(9,9)))
    
    def highlight(self, array: NDArray[np.float64], true_color="green", false_color="red") -> None:
        """Highlight sudoku grid based on given array.

        Args:
            array (NDArray[np.float64]): Input 9 by 9 array.
            true_color (str, optional): 0 value in array interprets as correct and highlight with given color. Defaults to "green".
            false_color (str, optional): Non zero value in array interprets as incorrect and highlight with given color. Defaults to "red".
        """
        array = np.transpose(array)
        array = np.reshape(array,(81,1))
        for i, entry in zip(range(81),self.entry_list):
            if entry.cget('state')=='normal':
                if array[i]:
                    entry.configure(fg_color=false_color)
                else:
                    entry.configure(fg_color=true_color)

class ViewConfig(ctk.CTkFrame):
    """Create view for configuration panel.
    """
    def __init__(self, master) -> None:
        super().__init__(master, width=200, height=550)

        # Create label
        self.label = ctk.CTkLabel(master=self, text="Sudoku solver", font=('Calibri',30))
        self.label.place(relx=0.075, rely=0)

        # Create switch for language change
        self.switch = ctk.CTkSwitch(master=self, text="EN/PL", command=self.switch_event, onvalue=1, offvalue=0)
        self.switch.configure(fg_color=ORANGE, progress_color=ORANGE)
        self.switch.place(relx=0.40, rely=0.8, anchor=tk.CENTER)

        # Create buttons with images
        disclaimer_img = ctk.CTkImage(light_image=Image.open("Images\\disclaimer.png"), dark_image=Image.open("Images\\disclaimer.png"))
        self.disclaimer = ctk.CTkButton(master=self,
                                                   text="", 
                                                   command= lambda: self.pop_up_window(DISCLAIMER_LABEL, DISCLAIMER_TEXT),
                                                   image=disclaimer_img)
        self.disclaimer.configure(fg_color='red', hover_color='#5c0d03', width=30, height=30)
        self.disclaimer.place(relx=0.75, rely=0.8, anchor=tk.CENTER)

        reset_img = ctk.CTkImage(light_image=Image.open("Images\\reset.png"), dark_image=Image.open("Images\\reset.png"))
        self.reset_button = ctk.CTkButton(master=self,
                                                     text=RESET_TEXT,
                                                     command=self.reset_sudoku,
                                                     image=reset_img,
                                                     compound=tk.LEFT)
        self.reset_button.configure(fg_color='green')
        self.reset_button.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        solve_img = ctk.CTkImage(light_image=Image.open("Images\\solve.png"), dark_image=Image.open("Images\\solve.png"))
        self.solve_button = ctk.CTkButton(master=self,
                                                    text=SOLVE_TEXT[self.switch.get()],
                                                    command=self.solve,
                                                    image=solve_img,
                                                    compound=tk.LEFT)
        self.solve_button.configure(state='disabled',fg_color='gray')
        self.solve_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        self.try_button = ctk.CTkButton(master=self, text=TRY_TEXT[self.switch.get()], command=self.try_callable)
        self.try_button.configure(fg_color=ORANGE, hover_color=DARK_ORANGE)
        self.try_button.place(relx=0.5, rely=0.88, anchor=tk.CENTER)

        scan_img = ctk.CTkImage(light_image=Image.open("Images\\scan.png"), dark_image=Image.open("Images\\scan.png"))
        self.scan_button = ctk.CTkButton(master=self, 
                                            text=SCAN_TEXT[self.switch.get()], 
                                            command=self._start_scan_thread,
                                            image=scan_img,
                                            compound=tk.LEFT)
        self.scan_button.place(relx=0.5, rely=0.72, anchor=tk.CENTER)

        #Create combobox
        self.combobox = ctk.CTkComboBox(master=self, values=SOLVE_METHODS[self.switch.get()],
                                            command=self.combobox_callback)
        self.combobox.set(EMPTY_SOLVE_BOX[self.switch.get()])
        self.combobox.place(relx=0.5, rely=0.10, anchor=tk.CENTER)

        #Create textbox
        self.textbox = ctk.CTkTextbox(master=self, width=160)
        self.textbox.insert(0.0, TEXTBOX_TEXT[self.switch.get()])
        self.textbox.configure(state='disabled', font=("Calibri",12), wrap='word')
        self.textbox.place(relx=0.5, rely=0.34, anchor=tk.CENTER)

        # Helper variables
        self.check_button = None
        self.in_try: bool = False
        self.check_press: bool = True
        self.window = None

        # Add controller for view
        self.controller: Any|None = None
    
    def _start_scan_thread(self) -> None:
        """Start scanning function on different thread.
        """
        text: List[str] = ["Scanning...","Skanowanie..."]
        self.scan_button.configure(state="disabled", text=text[self.switch.get()]) # Disable button during scaning
        self._scan_thread = threading.Thread(target=self.scan)
        self._scan_thread.start()
        self._monitor_scan_thread()

    def _monitor_scan_thread(self) -> None:
        """Monitor thread until task ends. 
        """
        if self._scan_thread and self._scan_thread.is_alive():
            self.after(100, self._monitor_scan_thread)
        else:
            self.scan_button.configure(state="normal", text=SCAN_TEXT[self.switch.get()])

    def set_controller(self, controller: Any) -> None:
        """Set controller for view.

        Args:
            controller (Controller):  controller to set.
        """
        self.controller = controller

    def pop_up_window(self, label: List[str], text: List[str], font_size: int = 12)  -> None:
        '''Display pop up window.
        
        Args:
            label(List[str]): Label to display
            text(List[str]): Text to display
            font_size(int, optional): Size of the font'''
        if self.window is None or not self.window.winfo_exists():
            self.window = ctk.CTkToplevel(self) 
        else:
            self.window.focus() 
        self.window.geometry("300x200")
        self.window.title(label[self.switch.get()])
        frame = ctk.CTkFrame(self.window, width=250, height=175)
        frame.pack(padx=10, pady=10)
        window_label = ctk.CTkLabel(frame, text=label[self.switch.get()])
        window_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        textbox = ctk.CTkTextbox(master=self.window, width=220, height=110)
        textbox.tag_config("center", justify="center")
        textbox.insert(0.0, text[self.switch.get()])
        textbox.tag_add("center", 1.0, "end")
        textbox.configure(state='disabled', font=("Calibri",font_size), wrap='word')
        textbox.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
    
    def switch_event(self) -> None:
        """Switch language.
        """
        if self.controller:
            self.controller.switch_event(self.switch.get())

    def reset_sudoku(self) -> None:
        """Reset sudoku.
        """
        if self.controller:
            self.controller.reset_sudoku(self.in_try)

    def try_callable(self) -> None:
        """Try to solve sudoku by yourself
        """
        if not self.in_try:
            self.scan_button.configure(state="disabled", fg_color="gray")
            self.combobox.set(RETURN_COMBOBOX_TEXT[self.switch.get()])
            self.combobox.configure(state="disabled")
            self.solve_button.configure(state="normal", fg_color=ORANGE, hover_color=DARK_ORANGE)

            self.check_button = ctk.CTkButton(self, text=CHECK_TEXT[self.switch.get()], command=self.check)
            self.check_button.configure(fg_color=ORANGE, hover_color=DARK_ORANGE)
            self.check_button.place(relx=0.5, rely=0.58, anchor=tk.CENTER)

            self.in_try = True

            self.solve()
            if self.controller:
                self.controller.try_callable()
            self.try_button.configure(text=RETURN_TEXT[self.switch.get()])
        else:
            self.check_button.destroy()
            self.in_try = False
            if self.controller:
                self.controller.try_callable()
            self.solve_button.configure(state='normal', fg_color=ORANGE)
            self.combobox.configure(state='normal')
            self.scan_button.configure(state="normal", fg_color=BUTTON_FG_COLOR)
            self.try_button.configure(text=TRY_TEXT[self.switch.get()])

    def combobox_callback(self, args) -> None:
        '''Method that allows solve button to be pressed.'''
        self.solve_button.configure(state='normal', fg_color=ORANGE, hover_color=DARK_ORANGE)

    def set_textbox(self, text: List[str]) -> None:
        """Method to set the textbox
        
        Args: 
            text(List[str]): Text provided with both languages"""
        self.textbox.configure(state='normal')
        self.textbox.delete(0.0, "end")
        self.textbox.insert(0.0, text[self.switch.get()])
        self.textbox.configure(state='disabled')

    def solve(self) -> None:
        if self.controller:
            self.controller.solve_sudoku(self.combobox.get(), self.in_try)

    def scan(self) -> None:
        if self.controller:
            self.controller.scan_sudoku()

    def check(self) -> None:
        if self.controller:
            self.controller.check_sudoku()

class ViewPredef(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=550, height=50)
        self.id_entry = ctk.CTkEntry(master=self,
                                                width=300,
                                                height=20, 
                                                font=('Calibri',20), 
                                                justify='left', 
                                                placeholder_text=PLACEHOLDER_ID[0],
                                                max_length=4)
        self.id_entry.place(relx=0.33, rely=0.5, anchor=tk.CENTER)

        id_img = ctk.CTkImage(light_image=Image.open("Images\\load.png"), dark_image=Image.open("Images\\load.png"))
        self.id_button = ctk.CTkButton(master=self, 
                                                 text=ID_TEXT[0], 
                                                 command=self.load_callable,
                                                 image=id_img,
                                                 compound=tk.LEFT
                                                 )
        self.id_button.configure(fg_color=ORANGE, hover_color=DARK_ORANGE, width=100, height=25)
        self.id_button.place(relx=0.87, rely=0.5, anchor=tk.CENTER)
        self.controller = None
    def set_controller(self, controller):
        self.controller = controller
    def load_callable(self):
        if self.controller:
            self.controller.load_sudoku(self.id_entry.get())
        self.id_entry.delete(0, "end")