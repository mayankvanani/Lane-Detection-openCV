import cv2
import numpy as np 
import matplotlib.pyplot as plt

cap = cv2.VideoCapture('solidYellowLeft.mp4')

while True:
    
    ret, image = cap.read()
    img = np.copy(image)
    blank_space = np.copy(image)*0
    rows, cols, channels = img.shape

    ## bluring the image once for image processing
    blur = cv2.GaussianBlur(img, (5,5), 0)

    ##yellow channel masking by converting to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    ##setting the yellow limit
    lower_yellow = np.array([0,100,100])
    upper_yellow = np.array([70,300,300])
    ##yellow masking
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    ##cv2.imshow('yellow_mask',yellow_mask)

    ##white channel masking by thresholding
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    ret, white_thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    ## creating mask
    mask = np.zeros(gray.shape,np.uint8)
    pts = np.array([[0, rows],[cols, rows],[cols/2 + 20,((rows/2) + 35)],
                   [cols/2 - 20,((rows/2) + 35)]], np.int32)
    mask = cv2.fillPoly(mask, [pts], (255,255,255))
    ##cv2.imshow('mask', mask)
    ##applying mask on white channel
    white_thresh = cv2.bitwise_and(white_thresh,white_thresh, mask = mask)
    ##cv2.imshow('white_thresh',white_thresh)

    ##combining masking
    comb_mask = yellow_mask + white_thresh
    ##cv2.imshow('comb_mask',comb_mask)

    ##canny edge detection
    canny = cv2.Canny(comb_mask, 90, 150)
    ##cv2.imshow('canny',canny)

    ##applying hough transform
    hough = cv2.HoughLinesP(canny, 1, np.pi/180, 100, np.array([]), 5, 20)

    ##separating left and right lane points
    xl_pts = []
    yl_pts = []
    xr_pts = []
    yr_pts = []
    for line in hough:
        for x1,y1,x2,y2 in line:
            slope = (y2-y1)/(x2-x1)

            if (slope < 0):
                 xl_pts += [x1,x2]
                 yl_pts += [y1,y2]

            if (slope > 0):
                xr_pts += [x1,x2]
                yr_pts += [y1,y2]

    ##polyfitting left and right segregated coordinates
    ## exception arises in case of empty frames
    try:
        left_mb = np.polyfit(xl_pts, yl_pts, 1)
        right_mb = np.polyfit(xr_pts, yr_pts, 1)

    except Exception as e:
        pass

    ##constructing equation of line (y = mx + b)
    y_left = np.poly1d(left_mb)
    y_right = np.poly1d(right_mb)

    ##defining equation as (x = (y-b)/m )
    def x_left(y):
        x = (y - left_mb[1]) / (left_mb[0])
        return x

    def x_right(y):
        x = (y - right_mb[1]) / (right_mb[0])
        return x

    ## calculating lower and upper points of left and right lane
    ## length of left lane = length of right lane
    left_down = (0 , np.uint32(y_left(0)))
    left_up = (np.uint32(x_left(330)),330)

    right_down = (960, np.uint32(y_right(960)))
    right_up = (np.uint32(x_right(330)), 330)

    ##drawing lanes
    l_lane = cv2.line(blank_space, left_down, left_up, (0,0,255), 10)

    r_lane = cv2.line(blank_space, right_down, right_up, (0,0,255), 10)

    ## final output image
    final = cv2.addWeighted(image, 0.8, blank_space, 1, 0)
    cv2.imshow('final',final)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()


















