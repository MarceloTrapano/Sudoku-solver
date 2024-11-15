from numpy import dtype, signedinteger
from numpy._typing import _64Bit
from numpy._typing._array_like import NDArray
from Sudoku_solve import SudokuBruteForce, SudokuLP, SudokuIP
from Sudoku_Reader import Reader
from typing import List, Any, Literal
from View import *
from Model import Model
import View

class Controller:
    """Controller function for MVC method. It joins views with model.
    """
    def __init__(self, config, sudoku, predef, model) -> None:
        self.config: ViewConfig = config
        self.sudoku: ViewSudoku = sudoku
        self.predef: ViewPredef = predef
        self.model: Model = model
        self.in_try: bool = False
        self.color: bool = True
    @staticmethod
    def change_language(list_of_elements: List[Any], list_of_prompts: List[str], state: bool) -> None:
        """Configure elements for language change.
        
        Args: 
            list_of_elements(List[Any]): List of configurable buttons.
            list_of_prompts(List[str]): List of labels for buttons.
            state(bool): 0-English, 1-Polish.
        """
        for (element, prompt) in zip(list_of_elements, list_of_prompts):
            element.configure(text=prompt[state])
    def switch_event(self, state: bool) -> None:
        """Change language.

        Args:
            state (bool): 0-English, 1-Polish.
        """
        self.change_language([self.config.scan_button, self.predef.id_button], 
                             [View.SCAN_TEXT, View.ID_TEXT], state)
        self.config.combobox.set(View.EMPTY_SOLVE_BOX[state])
        self.predef.id_entry.configure(placeholder_text=View.PLACEHOLDER_ID[state])
        self.config.set_textbox(View.TEXTBOX_TEXT)
        if self.config.in_try:
            self.change_language([self.config.try_button, self.config.check_button, self.config.solve_button],
                                 [View.RETURN_TEXT, View.CHECK_TEXT, View.SOLVE_TEXT], state)
            self.config.combobox.configure(values=View.SOLVE_METHODS[state], state="normal")
            self.config.combobox.set(View.RETURN_COMBOBOX_TEXT[state])
            self.config.combobox.configure(state="disabled")
        else:
            self.config.try_button.configure(text=View.TRY_TEXT[state])
            self.config.combobox.configure(values=View.SOLVE_METHODS[state])
            self.config.solve_button.configure(text=View.SOLVE_TEXT[state], fg_color="gray", state='disabled')
    def reset_sudoku(self, state: bool) -> None:
        """Reset sudoku grid.

        Args:
            state (bool): 0-Reset all grid, 1-Reset only active tiles.
        """
        self.sudoku.reset_grid(not state)
    def try_callable(self) -> None:
        """Try to solve sudoku:
        """
        if not self.in_try: # Lock filled tiles
            self.sudoku.lock_grid(state=False)
            self.in_try = True
            return
        self.sudoku.lock_grid(state=True) # Unlock all tiles
        self.in_try = False
    def solve_sudoku(self, name: str, state: bool) -> None | bool:
        """Solve sudoku and diplay it.

        Args:
            name (str): Name of method to solve sudoku.
            state (bool): 0-Don't show sudoku, 1-Show sudoku.

        Returns:
            None | bool: Return False if error occurres.
        """
        solution: NDArray[np.int64]
        time: np.float64
        try:
            sudoku: NDArray[np.int64] = self.sudoku.read()
            solution, time = self.model.solve_sudoku(sudoku, name)
        except ValueError:
            solve_error: List[str] = ["Solve Error: Your sudoku is invalid.", "Błąd w rozwiązywaniu: Twoje sudoku jest błędne."]
            self.config.set_textbox(solve_error)
            self.sudoku.lock_grid(state=True)
            return False
        if not state:
            text: List[str] =  [f"Solved in {time:0.4f} s.", f"Rozwiązano w {time:0.4f} s."]
            self.config.set_textbox(text)
            self.sudoku.insert(solution)
            self.sudoku.lock_grid(state=False)
            return
    def scan_sudoku(self) -> None:
        """Scan sudoku.
        """
        self.sudoku.insert(self.model.scan())
    def check_sudoku(self) -> None:
        """Check your solution.
        """
        try:
            sudoku: NDArray[np.int64] = self.sudoku.read() # Read sudoku from entry
        except ValueError:
            check_error: List[str] = ["Check Error: Value is invalid.", "Błąd w sprawdzeniu: Wartość jest błędna."]
            self.config.set_textbox(check_error)
            return
        check: NDArray[np.float64] = sudoku - self.model.solution # Check difference between solution and entry solution
        if not check.any():
            self.config.pop_up_window(View.CONGRATULATION_LABEL, View.CONGRATULATION_TEXT, 24)
        if self.color:
            self.sudoku.highlight(check) # Highlight sudoku grid with green and red
            self.color = False
            return
        self.sudoku.highlight(check, true_color=View.ENTRY_FG_COLOR, false_color=View.ENTRY_FG_COLOR)
        self.color = True
    def load_sudoku(self, id_num: int | str) -> None:
        """Load predefined sudoku

        Args:
            id_num (int | str): Id of sudoku
        """
        self.sudoku.reset_grid()
        try:
            array: NDArray[np.int64] = self.model.load(id_num)
        except ValueError:
            load_error: List[str] = ["Load Error: Invalid ID.", "Błąd w wczytywaniu: Nieprawidłowy ID."]
            self.config.set_textbox(load_error)
            return
        self.sudoku.insert(array)
    
