import cv2
import numpy as np
# Warning: This function creates a lots of files

def get_sudoku_tiles(filename : str, save : bool = False, name : int = 6) -> None:
    '''Gets sudoku tiles from image.

    Args:
        filename (str): Name of file with type from which function will get tiles.
        save (bool, optional): Whether to save tiles to file. Defaults to False.
        name (int, optional): Which iteration of tiles it is. Defaults at 6.
    '''
    img : np.ndarray = cv2.imread(filename)
    k : int = 0
    for i in range(1,10):
        for j in range(1,10):
            cropImg : np.ndarray = img[(i-1)*72:i*72, (j-1)*72:j*72]
            if save:
                cv2.imwrite("{}_{}.png".format(name,k),cropImg)
            k += 1

def main():
    get_sudoku_tiles("Sudoku.png")

if __name__ == "__main__":
    main()

