import customtkinter as ctk
from Model import Model
from View import *
from Controller import Controller

class App(ctk.CTk):
    """Graphical user interface for sudoku solver. It allows to solve sudoku with various methods. 
        You can solve problem on your own or with some help. Project includes scanning sudoku grid with webcam and
        provides estimated time for solution."""
    def __init__(self) -> None:
        super().__init__()
        #Create window
        self.geometry("900x750")
        self.title("Sudoku")
        self.window = None

        #Load model
        self.model: Model = Model()

        #Create grid for frames
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)

        #Create frame for displaying sudoku
        self.sudoku_frame: ViewSudoku = ViewSudoku(self)
        self.sudoku_frame.grid(row=0, column=1, pady=50, padx=0)

        #Create frame for configuration
        self.config_frame: ViewConfig = ViewConfig(self)
        self.config_frame.grid(row=0, column=0, pady=50, padx=50)

        #Create frame for loading sudoku
        self.id_frame: ViewPredef = ViewPredef(self)
        self.id_frame.grid(row=1, column=1, pady=0, padx=0, sticky='ne')
        
        #Create controller and configure frames
        controller: Controller = Controller(self.config_frame, self.sudoku_frame, self.id_frame, self.model)
        self.config_frame.set_controller(controller)
        self.id_frame.set_controller(controller)


if __name__ == '__main__':
    app: App = App()
    app.mainloop()