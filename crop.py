import cv2
import numpy as np
from numpy.typing import NDArray
from Sudoku_Reader import Reader
# Warning: This function creates a lots of files

def get_sudoku_tiles(filename : str, save : bool = False, name : int = 6) -> None:
    '''Gets sudoku tiles from image.

    Args:
        filename (str): Name of file with type from which function will get tiles.
        save (bool, optional): Whether to save tiles to file. Defaults to False.
        name (int, optional): Which iteration of tiles it is. Defaults at 6.
    '''
    DELTA: int = 10
    img : np.ndarray = cv2.imread(filename)
    k : int = 0
    for i in range(1,10):
        for j in range(1,10):
            cropImg : np.ndarray = img[(i-1)*72+DELTA:i*72-DELTA, (j-1)*72+DELTA:j*72-DELTA]
            if save:
                cv2.imwrite("{}_{}.png".format(name,k),cropImg)
            k += 1
def get_sudoku_tiles_predefined(filename : str, save : bool = False, predef = NDArray[np.int64], rep: int = 1) -> None:
    '''Gets sudoku tiles from image.

    Args:
        filename (str): Name of file with type from which function will get tiles.
        save (bool, optional): Whether to save tiles to file. Defaults to False.
        name (int, optional): Which iteration of tiles it is. Defaults at 6.
    '''
    DELTA: int = 10
    Read: Reader = Reader()

    k : int = 0
    for l in range(rep):
        Read.show()
        img : np.ndarray = cv2.imread(filename)
        for i in range(1,10):
            for j in range(1,10):
                cropImg : np.ndarray = img[(i-1)*72+DELTA:i*72-DELTA, (j-1)*72+DELTA:j*72-DELTA]
                if save:
                    cv2.imwrite("C:\\Users\\gt\\Desktop\\Studbaza\\Sudoku_sol\\Training\\{}\\{}.png".format(predef[i-1,j-1],k),cropImg)
                k += 1

def main():
    predef: NDArray[np.int64] = np.array([[0,0,0,0,1,9,0,5,0],
                                                        [0,6,0,0,7,0,0,1,3],
                                                        [0,0,0,2,0,0,0,0,7],
                                                        [3,0,6,0,0,1,8,4,0],
                                                        [4,0,0,0,0,0,0,0,9],
                                                        [0,8,2,9,0,0,3,0,6],
                                                        [2,0,0,0,0,6,0,0,0],
                                                        [6,1,0,0,5,0,0,3,0],
                                                        [0,7,0,8,3,0,0,0,0]])
    get_sudoku_tiles_predefined("Sudoku.png", save=True, predef=predef, rep=1000)

if __name__ == "__main__":
    main()

