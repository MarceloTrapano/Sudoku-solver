from scipy.optimize import linprog
from numpy.typing import NDArray
import numpy as np
import pulp as plp
from scipy.optimize._optimize import OptimizeResult
from abc import ABC, abstractmethod
from time import time

class Sudoku(ABC):
    def __init__(self, puzzle: NDArray[np.float64]) -> None:
        self.puzzle: NDArray[np.float64] = puzzle.reshape(9, 9)
        self.unknown: int = np.count_nonzero(self.puzzle == 0)
    @abstractmethod
    def solve(self) -> NDArray[np.float64]:
        pass

    def __repr__(self) -> str:
        text: str = "|-------|-------|-------|\n"
        j: int = 0
        p: int = 0
        for i in self.puzzle:
            text += "| "
            for k in i:
                if k == 0:
                    text += "☐ "
                else:
                    text += f'{k} '
                j += 1
                if j%3 == 0:
                    text += "| "
            p += 1
            if p%3 == 0:
                text += "\n|-------|-------|-------|"
            j = 0
            text += f'\n'
        return text

def check(sudoku: Sudoku) -> bool:
    for i in sudoku.puzzle:
        array = list(range(1,10))
        for j in i:
            if j == 0:
                continue
            try:
                array.remove(j)
            except ValueError:
                return False
    for i in np.transpose(sudoku.puzzle):
        array = list(range(1,10))
        for j in i:
            if j == 0:
                continue
            try:
                array.remove(j)
            except ValueError:
                return False
    for i in np.arange(0, 9, 3):
         for j in np.arange(0, 9, 3):
            array = list(range(1,10))
            for m in sudoku.puzzle[i:i+3,j:j+3]:
                for n in m:
                    if n == 0:
                        continue
                    try:
                        array.remove(n)
                    except ValueError:
                        return False
    return True
    


class SudokuBruteForce(Sudoku):
    def solve(self) -> NDArray[np.float64]:
        if not check(self):
            raise ValueError
        if self.unknown == 0:
            return self.puzzle
        x: int = 0
        puzzle: NDArray[np.float64] = np.copy(self.puzzle)
        for i in self.puzzle:
            y: int = 0
            for j in i:
                if j == 0:
                    for k in range(1, 10):
                        puzzle[x, y] = k
                        sudoku: self = SudokuBruteForce(puzzle) 
                        try:
                            puzzle = sudoku.solve()
                        except ValueError:
                            if k == 9:
                                raise ValueError
                            continue
                        break
                y += 1
            x += 1
        return puzzle
        
class SudokuLP(Sudoku):
    def solve(self) -> NDArray[np.float64]:
        if not check(self):
            raise ValueError
        if self.unknown == 0:
            return self.puzzle
        if self.unknown == 1:
            b: int = 45
            for i in self.puzzle:
                if np.count_nonzero(i == 0) > 0:
                    for j in i:
                        if j > 0:
                            b -= j
                    puzzle: NDArray = np.copy(self.puzzle)
                    puzzle[puzzle == 0] = b
                    return puzzle
        coordinates: NDArray[np.float64] = np.array([])
        b_eq: NDArray[np.float64] = np.array([])
        A_eq: bool = False
        # Horizontal equations
        x: int = 0
        k: int = 0
        y: int = 0
        for i in self.puzzle:
            y = 0
            if np.count_nonzero(i == 0) > 0:
                b = 45
                for j in i:
                    if j == 0:
                        coordinates = np.append(coordinates, np.array([x, y]))
                    else:
                        b -= j
                    y += 1
                if isinstance(A_eq, bool):
                    A_eq = np.hstack((np.ones(int(len(coordinates)/2)), np.zeros(self.unknown - int(len(coordinates)/2))))
                else:
                    if k-1 == 0:
                        A_eq = np.vstack((A_eq, np.hstack((np.zeros(np.count_nonzero(A_eq)),
                                                                 np.hstack((np.ones(int(len(coordinates)/2)-np.count_nonzero(A_eq)),
                                                                np.zeros(self.unknown - int(len(coordinates)/2))))))))
                    else:
                        A_eq = np.vstack((A_eq, np.hstack((np.zeros(np.count_nonzero(A_eq[0:k])),
                                                                 np.hstack((np.ones(int(len(coordinates)/2)-np.count_nonzero(A_eq[0:k])),
                                                                np.zeros(self.unknown - int(len(coordinates)/2))))))))
                b_eq = np.append(b_eq, b)
                k += 1
            x += 1
        
        #Vertical equations
        coordinates = coordinates.reshape(int(len(coordinates)/2), 2)
        y = 0
        for i in np.transpose(self.puzzle):
            x = 0
            if np.count_nonzero(i == 0) > 0:
                equation: NDArray[np.float64] = np.zeros(self.unknown)
                b = 45
                for j in i:
                    if j == 0:
                        for m in range(self.unknown):
                            if coordinates[m][0] == x and coordinates[m][1] == y:
                                equation[m] = 1
                    b -= j
                    x += 1
                A_eq = np.vstack((A_eq, equation))
                b_eq = np.append(b_eq, b)
            y += 1
        
        #Box equations
        for i in np.arange(0, 9, 3):
            for j in np.arange(0, 9, 3):
                if np.count_nonzero(self.puzzle[i:i+3,j:j+3] == 0) > 0:
                    x = 0 + i
                    b = 45
                    equation: NDArray[np.float64] = np.zeros(self.unknown)
                    for m in self.puzzle[i:i+3,j:j+3]:
                        
                        y = 0 + j
                        for n in m:
                            if n == 0:
                                for p in range(self.unknown):
                                    if coordinates[p][0] == x and coordinates[p][1] == y:
                                        equation[p] = 1
                            y += 1
                            b -= n
                        x += 1
                    A_eq = np.vstack((A_eq, equation))
                    b_eq = np.append(b_eq, b)    
        res: OptimizeResult = linprog(np.zeros(self.unknown), A_eq=A_eq, b_eq=b_eq, method='highs', bounds=(1,9))
        puzzle = np.copy(self.puzzle)
        print(res)
        puzzle[puzzle == 0] = res['x']
        return puzzle
    
class SudokuIP(Sudoku):
    def solve(self) -> NDArray[np.float64]|None:
        if not check(self):
            raise ValueError
        if self.unknown == 0:
            return self.puzzle
        Boxes = [
            [(3 * i + k + 1, 3 * j + l + 1) for k in range(3) for l in range(3)]
            for i in range(3)
            for j in range(3)
        ]


        prob = plp.LpProblem("Sudoku Problem")

        choices = plp.LpVariable.dicts("Choice", (range(1,10), range(1,10), range(1,10)), cat="Binary")


        for r in range(1,10):
            for c in range(1,10):
                prob += plp.lpSum([choices[v][r][c] for v in range(1,10)]) == 1

        for v in range(1,10):
            for r in range(1,10):
                prob += plp.lpSum([choices[v][r][c] for c in range(1,10)]) == 1

            for c in range(1,10):
                prob += plp.lpSum([choices[v][r][c] for r in range(1,10)]) == 1

            for b in Boxes:
                prob += plp.lpSum([choices[v][r][c] for (r, c) in b]) == 1

        k = 0
        for i in self.puzzle:
            for j in i:
                
                col: int = k%9 + 1
                row: int = int(np.floor(k/9) + 1)
                if 0 == j:
                    k += 1
                    continue
                prob += choices[j][row][col] == 1
                k += 1
        prob.solve()

        if plp.LpStatus[prob.status] == 'Optimal':
            solution: list[list[int]] = [[0 for col in range(9)] for row in range(9)]
            for row in range(9):
                for col in range(9):
                    for value in range(1, 10):
                        if plp.value(choices[value][row+1][col+1]):
                            solution[row][col] = value 
            return np.array(solution)
        return False

def main() -> None:
    puzzle: NDArray = np.array([0,0,2,7,0,4,1,0,0,
                                6,0,0,0,3,0,0,0,5,
                                0,8,4,0,0,0,3,9,0,
                                0,0,6,0,0,0,7,0,0,
                                0,2,0,9,0,6,0,5,0,
                                0,0,9,0,0,0,6,0,0,
                                0,6,8,0,0,0,2,7,0,
                                3,0,0,0,8,0,0,0,1,
                                0,0,5,6,0,3,9,0,0])
    sudoku: SudokuLP = SudokuLP(puzzle)
    print(sudoku)
    solved: SudokuLP = SudokuLP(sudoku.solve())
    print(solved)
    sudoku: SudokuBruteForce = SudokuBruteForce(puzzle)
    print(sudoku)
    solved: SudokuBruteForce = SudokuBruteForce(sudoku.solve())
    print(solved)
    sudoku: SudokuIP = SudokuIP(puzzle)
    print(sudoku)
    solved: SudokuIP = SudokuIP(sudoku.solve())
    print(solved)
    
if __name__ == "__main__":
    main()