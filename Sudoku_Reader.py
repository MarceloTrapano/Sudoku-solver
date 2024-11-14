import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def camera_setting(setting: bool) -> bool:
    '''Information about camera status.

    Args:
        setting (bool): It takes boolean parameter.

    Returns:
        bool: Camera status.
    '''
    if setting:
        print('Camera is on.')
        return setting
    print('Camera is off.')
    return setting

def threshold_setting(setting: int) -> int:
    '''Information about threshold value.
    
    Args:
        setting (int): It takes integer parameter.

    Returns:
        int: Threshold value.
    '''
    print('Threshold value is {}'.format(setting))
    return setting
    

class Reader:
    '''This class can read picture from file or capture a video. Then it tries to find contours of sudoku grid and apply linear
    tranformation. With that this class isolates the sudoku from image and applies filters for better clairity. 
    '''
    HEIGHT: int = 648
    WIDTH: int = 648
    def __init__(self) -> None:
        self.vid: cv2.VideoCapture = cv2.VideoCapture(0)
        
        self.img: np.ndarray = np.zeros((self.WIDTH, self.HEIGHT))
        self.contourImg: np.ndarray = np.zeros((self.WIDTH, self.HEIGHT))
        self.imgGray: np.ndarray 
        self.finalImg: np.ndarray

        self.file: bool

        
    def findContour(self) -> bool:
        '''Find contours of sudoku grid and apply linear tranformation. 
        
        Returns:
            bool: If it found any contour.'''
        contours: cv2.Sequence[np.ndarray]
        biggest: np.ndarray
        contours, _ = cv2.findContours(self.finalImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        biggest, _ = self.biggestContour(contours)
        if biggest.size != 0:
            biggest = self.reorder(biggest)
            cv2.drawContours(self.finalImg, biggest, -1, (0,0,255),20)
            cv2.drawContours(self.finalImg, contours, -1, (0,0,255),10)
            wrappoints1 : np.ndarray = np.float32(biggest)
            wrappoints2 : np.ndarray = np.float32([[0, 0],[self.WIDTH, 0],[0, self.HEIGHT],[self.WIDTH, self.HEIGHT]])
            matrix : np.ndarray = cv2.getPerspectiveTransform(wrappoints1,wrappoints2)
            self.contourImg = cv2.warpPerspective(self.img, matrix, (self.WIDTH,self.HEIGHT))
            self.contourImg = cv2.resize(self.contourImg, (self.WIDTH,self.HEIGHT))
            self.contourImg = cv2.cvtColor(self.contourImg, cv2.COLOR_BGR2GRAY)
            self.contourImg = cv2.adaptiveThreshold(self.contourImg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,7,2)
            kernel = np.ones((3,3),np.uint8)
            self.contourImg = cv2.morphologyEx(self.contourImg, cv2.MORPH_OPEN, kernel)
            return True
        return False

    @staticmethod
    def reorder(points : np.ndarray) -> np.ndarray:
        '''Reorder points of contour. It is used to arrange found rectangle in correct order.

        Args:
            points (ndarray): Vertices of rectangle.

        Returns:
            ndarray: Correct points order.'''
        points = points.reshape((4, 2))
        newPoints : np.ndarray = np.zeros((4, 1, 2), dtype=np.int32)
        add : float =  points.sum(1)

        newPoints[0] = points[np.argmin(add)]
        newPoints[3] = points[np.argmax(add)]
        diff : np.ndarray = np.diff(points, axis=1)

        newPoints[1] = points[np.argmin(diff)]
        newPoints[2] = points[np.argmax(diff)]
        return newPoints
    @staticmethod
    def biggestContour(contours : np.ndarray) -> tuple[np.ndarray, float]:
        '''Find biggest contour of video capture or image.

        Args:
            contours (ndarray): Contours of sudoku grid.

        Returns:
            (ndarray): Biggest contour and its area.
        '''
        biggest : np.ndarray= np.array([])
        max_area : float = 0
        for i in contours:
            area : float = cv2.contourArea(i)
            if area > 5000:
                peri : float = cv2.arcLength(i, True)
                approx : np.ndarray = cv2.approxPolyDP(i, 0.02 * peri, True)
                if area > max_area and 4 == len(approx):
                    biggest = approx
                    max_area = area 
        return biggest, max_area

    def capture(self) -> None:
        '''
        Capture video from camera with filters.'''
        _, self.finalImg = self.vid.read()
        self.finalImg = cv2.resize(self.finalImg, (self.WIDTH, self.HEIGHT), fx = 0, fy = 0)
        self.finalImg = cv2.cvtColor(self.finalImg, cv2.COLOR_BGR2GRAY)
        self.finalImg = cv2.GaussianBlur(self.finalImg, (5, 5), 1)

    def show(self) -> None:
        '''Show result of reader class.'''
        cv2.namedWindow('image')
        cv2.namedWindow('image1')
        cv2.namedWindow('image2')
        self.capture()
        kernel : np.ndarray = np.ones((1,1))
        empty = []
        i = 0
        while True:
            
            _, webcam= self.vid.read()
            _, self.img = self.vid.read()
            self.img = cv2.resize(self.img, (self.WIDTH, self.HEIGHT), fx = 0, fy = 0,
                        interpolation = cv2.INTER_CUBIC)
            cv2.imshow('image', webcam)
            self.capture()
            
            
            key : int = cv2.waitKey(10)
            if 27 == key:
                break
            self.finalImg = cv2.Canny(self.finalImg,0,77)
            kernel : np.ndarray = np.ones((1,1))
            self.finalImg = cv2.morphologyEx(self.finalImg, cv2.MORPH_CLOSE, kernel)
            contourCheck : bool = self.findContour()
            
            if contourCheck:
                kernel = np.ones((2,2))
                self.finalImg = self.contourImg
                #self.finalImg = cv2.erode(self.contourImg,kernel)
                kernel = np.ones((1,1))
                #self.finalImg = cv2.dilate(self.finalImg,kernel)
                #self.finalImg = cv2.blur(self.finalImg,(3,3))
                #_, self.finalImg = cv2.threshold(self.finalImg,127,255,cv2.THRESH_BINARY)
                if cv2.countNonZero(self.finalImg) < 380000:
                    if 15 < i:
                        empty.append(self.finalImg)
                    i += 1
                    if 20 == i:
                        dst = empty[0]
                        for j in range(len(empty)):
                            if j == 0:
                                pass
                            else:
                                alpha = 1.0/(j + 1)
                                beta = 1.0 - alpha
                                dst = cv2.addWeighted(empty[j], alpha, dst, beta, 0.0)
                        self.file = cv2.imwrite("Sudoku.png", dst)
                        break
        correct = cv2.imread("Sudoku.png", cv2.IMREAD_GRAYSCALE)
        correct = cv2.medianBlur(correct, 1)
        correct = cv2.morphologyEx(correct, cv2.MORPH_CLOSE, kernel)
        _, correct = cv2.threshold(correct,150,255,cv2.THRESH_BINARY)
        cv2.imwrite("Sudoku.png", correct)
        cv2.destroyAllWindows()
    def getFile(self) -> bool:
        '''Check if file was saved.
        
        Returns:
            bool: True if file was saved, False otherwise.'''
        return self.file


def main() -> None:
    red: Reader = Reader()
    red.show()
    file: bool = red.getFile()

if __name__ == '__main__':
    main()