import cv2
import numpy as np
import matplotlib.pyplot as plt

cap = cv2.VideoCapture('solidWhiteRight.mp4')

def gray(imgscr):
    return cv2.cvtColor(imgscr, cv2.COLOR_BGR2GRAY)

def blur(imgscr):
    return cv2.GaussianBlur(imgscr, (5,5), 0)

def canny(imgscr):
    return cv2.Canny(blur, 100, 180)

def mask():
    mask = np.zeros(gray.shape, np.uint8)
    pts = np.array([[0, rows],[cols, rows],[cols/2 + 20,((rows/2) + 35)],
                   [cols/2 - 20,((rows/2) + 35)]], np.int32)
    mask = cv2.fillPoly(mask, [pts], (255,255,255))
    return mask

def blankspace():
    blank_space = np.copy(image)*0
    return blank_space
    

def houghlines(imgsrc):
    hough_lines = cv2.HoughLinesP(imgsrc, 2, np.pi/180, 120, np.array([]), 1, 20)    
    return hough_lines

def curvefit(hough_lines):
## defining array of points for curve fitting left and right lines
    x_lefts = []
    y_lefts = []
    x_rights = []
    y_rights = []
    ##drawing lines based on hough transform on blank space
    for line in hough_lines:
        for x1,y1,x2,y2 in line:
            slope = ((y2-y1)/(x2-x1))

            ## classifying right and left lanes using slopes
            if (slope < 0):
                x_lefts += [x1,x2]
                y_lefts += [y1,y2]


            if (slope > 0):
                x_rights += [x1,x2]
                y_rights += [y1,y2]



    ## curve fitting to obtain 2 lanes
    ## np.polyfits returns m, b in (y = mx+b)
    ## np.polyfit(x-points, y-points, degree of polynomial)
    ## exception added to pass the empty frames
    try:
        mb_left = np.polyfit(x_lefts,y_lefts,1)
        mb_right = np.polyfit(x_rights,y_rights,1)

    except Exception as e:
        pass

    ##np.poly1D does (y = mx + b) for a given m and b
    y_lefts = np.poly1d(mb_left)
    y_rights = np.poly1d(mb_right)

    return mb_left,mb_right,y_lefts,y_rights

    
def x_equ(yl, yr):
    xl = (yl - mb_left[1]) / mb_left[0]
    xr = (yr - mb_right[1]) / mb_right[0]
    return xl, xr

def lane_attr():
    left_down = (0 , np.uint32(y_lefts(0)))
    left_up = (np.uint32(xl(330)),330)

    right_down = (960, np.uint32(y_rights(960)))
    right_up = (np.uint32(xr(330)), 330)
    return left_down,left_up,right_down,right_up
    
def lanes():
    l_lane = cv2.line(blank_space, left_down, left_up, 
                      (0,0,255), 10)

    r_lane = cv2.line(blank_space, right_down, right_up,
                      (0,0,255), 10)

def output():
    ## converting binary --> 3 channel binary
    chnled_mask = np.dstack((masked, masked, masked))

    ##combining hough lines with the canny edge
    final = cv2.addWeighted(img, 0.8, blank_space, 1, 0)
    cv2.imshow('final',final)    
    


while True:
    ret, image = cap.read()
    img = np.copy(image)

    x = gray(img)
    print(x)
    cv2.imshow('x',x)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
























    
    


