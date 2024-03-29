import cv2 as cv
import numpy as np
import pytesseract  
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def display_image(image):
    # cv.rectangle(image, (x,y),(x+w, y+h),(0,255,255),2) 
    # image = cv.resize(image, (1200,540)) 
    # Display the original image with the rectangle around the match.
    cv.imshow('output',image) 
    # The image is only displayed if we call this
    cv.waitKey(0) 

def get_grayscale(image):
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

#TODO, threshold value needs work
def get_binary(image):
    # (thresh, blackAndWhiteImage) = cv.threshold(image, 180, 255, cv.THRESH_BINARY_INV) 
    # ADAPTIVE_THRESH_MEAN_C
    blackAndWhiteImage = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,11,2) 
    return blackAndWhiteImage


def draw_text(src, x, y, w, h, text):
    cFrame = np.copy(src)
    cv.rectangle(cFrame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv.putText(cFrame, "text: " + text, (50, 50), cv.FONT_HERSHEY_SIMPLEX,  
               2, (0, 0, 0), 5, cv.LINE_AA)
    
    return cFrame



def is_vertical(line):
    return line[0]==line[2]

def is_horizontal(line):
    return line[1]==line[3]
    
def overlapping_filter(lines, sorting_index):
    filtered_lines = []
    
    lines = sorted(lines, key=lambda lines: lines[sorting_index])
    
    for i in range(len(lines)):
            l_curr = lines[i]
            if(i>0):
                l_prev = lines[i-1]
                if ( (l_curr[sorting_index] - l_prev[sorting_index]) > 5):
                    filtered_lines.append(l_curr)
            else:
                filtered_lines.append(l_curr)
                
    return filtered_lines
               
def detect_lines(image, title='default', rho = 1, theta = np.pi/180, threshold = 50, minLinLength = 290, maxLineGap = 6, display = False, write = False, resize = (0, 0)):
    # Check if image is loaded fine
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    if gray is None:
        print ('Error opening image!')
        return -1

    # TODO mean = mean of gray image
    # min_threshold = 0.66 * mean
    # max_threshold = 1.33 * mean
    dst = cv.Canny(gray, 50, 200, None, 3) 
    
    # Copy edges to the images that will display the results in BGR
    cImage = np.copy(image) 

    #linesP = cv.HoughLinesP(dst, 1 , np.pi / 180, 50, None, 290, 6)
    linesP = cv.HoughLinesP(dst, rho , theta, threshold, None, minLinLength, maxLineGap)
    
    horizontal_lines = []
    vertical_lines = []
    
    if linesP is not None:
        #for i in range(40, nb_lines):
        for i in range(0, len(linesP)):
            l = linesP[i][0]

            if (is_vertical(l)):
                vertical_lines.append(l)
                
            elif (is_horizontal(l)):
                horizontal_lines.append(l)
        
        horizontal_lines = overlapping_filter(horizontal_lines, 1)
        vertical_lines = overlapping_filter(vertical_lines, 0)
            
    if (display):
        for i, line in enumerate(horizontal_lines):
            cv.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,255,0), 3, cv.LINE_AA)
            
            cv.putText(cImage, str(i) + "h", (line[0] + 5, line[1]), cv.FONT_HERSHEY_SIMPLEX,  
                       1, (0, 0, 0), 1, cv.LINE_AA)   
            
        for i, line in enumerate(vertical_lines):
            cv.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,0,255), 3, cv.LINE_AA)
            cv.putText(cImage, str(i) + "v", (line[0], line[1] + 5), cv.FONT_HERSHEY_SIMPLEX,  
                       1, (0, 0, 0), 1, cv.LINE_AA) 
 

        # cv.namedWindow('Source', cv.WINDOW_NORMAL)  
        cImage = cv.resize(cImage, resize) if (resize[0] and resize[1]) else cImage
        dst = cv.resize(dst, resize) if (resize[0] and resize[1]) else dst

        cv.imshow("Source", cImage)  
        cv.imshow("Canny", dst)
        cv.waitKey(0)
        cv.destroyAllWindows()
        
    if (write):
        cv.imwrite("../Images/" + title + ".png", cImage);
        
    return (horizontal_lines, vertical_lines)

def get_cropped_image(image, x, y, w, h):
    cropped_image = image[ y:y+h , x:x+w ]
    return cropped_image
    
def get_ROI(image, horizontal, vertical, left_line_index, right_line_index, top_line_index, bottom_line_index, offset=4):
    x1 = vertical[left_line_index][2] + offset
    y1 = horizontal[top_line_index][3] + offset
    x2 = vertical[right_line_index][2] - offset
    y2 = horizontal[bottom_line_index][3] - offset
    
    w = x2 - x1
    h = y2 - y1
    
    cropped_image = get_cropped_image(image, x1, y1, w, h)
    
    return cropped_image, (x1, y1, w, h)

def detect(cropped_frame, column = '', psm = 1):
    # config_num = ('-l eng --oem 3 --psm 6 -c tessedit_char_whitelist=0123456789%') 

    config_general = '-l eng --oem 3 --psm '+str(psm)
    config_item = config_general + " -c tessedit_char_whitelist=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz \\'(45-)\""
    config_wish = config_general + ' -c tessedit_char_whitelist=" -2CENPWacehimnoprstv"'
    config_wish = config_general
    config_time = config_general #+ ' -c tessedit_char_whitelist=" 0123456789-:"'  
    # columns = ['item_type', 'item_name', 'wish_type', 'time']


    if(column == 'item_name'):
        config = config_item
    elif(column == "wish_type"):
        config = config_wish
    elif(column == "time"):
        config = config_time
    else:
        config = config_general

    text = pytesseract.image_to_string(cropped_frame, lang = 'eng', config = (config))         
        
    # print(column, text)
    return text
