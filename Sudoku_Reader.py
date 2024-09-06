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
    def __init__(that) -> None:
        that.height : int = 648
        that.width : int = 648
        that.vid : cv2.VideoCapture = cv2.VideoCapture(0)
        
        that.img : np.ndarray = np.zeros((that.width, that.height))
        that.contourImg : np.ndarray
        that.imgGray : np.ndarray 
        that.finalImg : np.ndarray

        that.file : bool

        cv2.namedWindow('image')
        cv2.createTrackbar('Camera','image',0 ,1 ,camera_setting)

    def readImage(self, filename : str) -> None:
        ''' Read image from file.

        Args:
            filename (str): Name of the file to read with type.
        '''
        self.img = cv2.imread(filename)
        self.img = cv2.resize(self.img, (self.width, self.height))
        self.imgGray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.finalImg  = cv2.GaussianBlur(self.imgGray, (5, 5), 1)

    def findContour(self) -> bool:
        '''Find contours of sudoku grid and apply linear tranformation. 
        
        Returns:
            bool: If it found any contour.'''
        contours : cv2.Sequence[np.ndarray]
        biggest : np.ndarray
        contours, _ = cv2.findContours(self.finalImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        biggest, _ = self.biggestContour(contours)
        if biggest.size != 0:
            biggest = self.reorder(biggest)
            cv2.drawContours(self.img, biggest, -1, (0,0,255),20)
            cv2.drawContours(self.img, contours, -1, (0,0,255),10)
            wrappoints1 : np.ndarray = np.float32(biggest)
            wrappoints2 : np.ndarray = np.float32([[0, 0],[self.width, 0],[0, self.height],[self.width, self.height]])
            matrix : np.ndarray = cv2.getPerspectiveTransform(wrappoints1,wrappoints2)
            self.contourImg = cv2.warpPerspective(self.img, matrix, (self.width,self.height))
            #self.contourImg = self.contourImg[20:self.contourImg.shape[0]-20, 20:self.contourImg.shape[1]-20]
            self.contourImg = cv2.resize(self.contourImg, (self.width,self.height))
            self.contourImg = cv2.cvtColor(self.contourImg, cv2.COLOR_BGR2GRAY)
            self.contourImg = cv2.adaptiveThreshold(self.contourImg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,7,2)
            return True
        return False
    def setWidth(self, width : int) -> None:
        '''Set the width of screen
        
        Args:
            width (int): The width of the screen'''
        self.width = width

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

    def setHeight(self, height : int) -> None:
        '''Set height of the window.

        Args:
            height (int): Value for height.'''
        self.height = height

    def capture(self) -> None:
        '''
        Capture video from camera with filters.'''
        _, self.finalImg = self.vid.read()
        self.finalImg = cv2.resize(self.finalImg, (self.width, self.height), fx = 0, fy = 0)
        self.finalImg = cv2.cvtColor(self.finalImg, cv2.COLOR_BGR2GRAY)
        self.finalImg = cv2.GaussianBlur(self.finalImg, (5, 5), 1)

    def show(self) -> None:
        '''Show result of reader class.'''
        old_img : np.ndarray = self.finalImg
        raw_img : np.ndarray = self.img
        kernel : np.ndarray = np.ones((5,5))
        while True:
            #cameraSet = cv2.getTrackbarPos('Camera','image')
            cameraSet : bool = True
            cv2.imshow('image', self.finalImg)
            if not cameraSet:
                self.finalImg = old_img
                self.img = raw_img
            else:
                self.capture()
                _, self.img = self.vid.read()
                self.img = cv2.resize(self.img, (self.width, self.height), fx = 0, fy = 0,
                         interpolation = cv2.INTER_CUBIC)
            key : int = cv2.waitKey(10)
            if 27 == key:
                break
            self.finalImg = cv2.Canny(self.finalImg,0,77)
            self.finalImg = cv2.morphologyEx(self.finalImg, cv2.MORPH_CLOSE, kernel)
            contourCheck : bool = self.findContour()
            
            if contourCheck:
                kernel = np.ones((2,2))
                self.finalImg = cv2.erode(self.contourImg,kernel)
                kernel = np.ones((1,1))
                self.finalImg = cv2.dilate(self.finalImg,kernel)
                self.finalImg = cv2.blur(self.finalImg,(3,3))
                _, self.finalImg = cv2.threshold(self.finalImg,127,255,cv2.THRESH_BINARY)
                self.file = cv2.imwrite("Sudoku.png", self.finalImg)
        cv2.destroyAllWindows()
    def getFile(self) -> bool:
        '''Check if file was saved.
        
        Returns:
            bool: True if file was saved, False otherwise.'''
        return self.file


def main() -> None:
    red: Reader = Reader()
    red.readImage('shapes.jpg')
    red.show()
    file: bool = red.getFile()

if __name__ == '__main__':
    main()