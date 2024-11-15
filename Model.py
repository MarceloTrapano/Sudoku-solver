from io import TextIOWrapper
from Sudoku_solve import SudokuBruteForce, SudokuLP, SudokuIP
from Sudoku_Reader import Reader
from crop import get_sudoku_tiles
from typing import Any, List
from numpy.typing import NDArray
import time
import keras
import numpy as np
import cv2

IMG_SIZE: int = 25
class Model:
    """Model for MVC app organization. It contains methods needed to work with data."""
    def __init__(self) -> None:
        self.solution: NDArray[np.int64]|None = None
        self.est: np.float64 = 0
        self.model: Any = keras.models.load_model("sudoku_solver.h5") # Load model for number recognition
        self.open_predefined_sudoku: TextIOWrapper = open("predefined_sudoku.txt", 'r') # Load predefined sudoku
        exec(self.open_predefined_sudoku.read())
    def solve_sudoku(self, array: NDArray[np.int64], name: str) -> tuple[NDArray[np.int64], np.float64]:
        """Solve sudoku using given method.

        Args:
            array (NDArray[np.int64]): Sudoku array.
            name (str): Name of method.
        Returns:
            tuple[NDArray[np.int64], np.float64]: Solved sudoku and estimated solution time.
        """
        match name:
            case "Brute force" | "Rozwiązanie siłowe":
                tic: float = time.perf_counter()
                self.solution = SudokuBruteForce(array).solve()
                toc: float = time.perf_counter()
            case "Linear programming" | "Programowanie liniowe":
                tic: float = time.perf_counter()
                self.solution = SudokuLP(array).solve()
                toc: float = time.perf_counter()
            case "Integer programming" | "Programowanie całkowitoliczbowe":
                tic: float = time.perf_counter()
                self.solution = SudokuIP(array).solve()
                toc: float = time.perf_counter()
        return self.solution, toc-tic
    def scan(self) -> List[np.int64]:
        """Scan sudoku and read tiles with neural network.
        
        Returns:
            List[np.int64]: Scanned sudoku."""
        reader: Reader = Reader()
        reader.show() # Read sudoku from camera
        get_sudoku_tiles('Sudoku.png', name="scan", save=True) # Crop sudoku to many tiles
        sudoku_array: List[Any] = []
        for i in range(81): # Load every tile to array
            sudoku_tile = cv2.resize(cv2.imread(f"scan_{i}.png", cv2.IMREAD_GRAYSCALE), (IMG_SIZE, IMG_SIZE))
            sudoku_array.append(sudoku_tile.reshape(-1, IMG_SIZE, IMG_SIZE, 1))
        sudoku_grid: List[Any] = []
        for scan in sudoku_array:
            sudoku_grid.append(self.model.predict(scan)) # Predict which tile each one is
        scan_grid = []     
        for line in sudoku_grid:
            number = np.where(line[0]>0.5)[0][0] # Connect prediction with value
            scan_grid.append(number)
        return scan_grid
    def load(self, entry: str) -> NDArray[np.float64]:
        """Get predefined sudoku or its solution

        Args:
            entry (str): id of sudoku

        Returns:
            NDArray[np.float64]: Sudoku or solved sudoku.
        """
        if str(entry).lower() == "debug": # Special debug option to return solved sudoku
            sudoku_id = np.random.randint(0,99999)
            sudoku = self.predefined_sudoku[(sudoku_id)%len(self.predefined_sudoku)]
            sudoku = np.reshape(sudoku, (9,9))
            sudoku_IP = SudokuIP(sudoku)
            return sudoku_IP.solve()
        
        sudoku_id: int = int(entry) 
        return self.predefined_sudoku[(sudoku_id+1)%len(self.predefined_sudoku)]

def main():
    model = Model()
    print(model.scan())
if __name__ == "__main__":
    main()
       
            
            
            