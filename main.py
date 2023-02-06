import sys
import json
import cv2 as cv
import os
import pytesseract 
import logging
from image_processing import get_cropped_image, detect_lines, get_ROI, get_grayscale, get_binary, detect, draw_text 
from output import wish2json, wish2excel, json2excel, data_verification
from wish import Wish
import argparse

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_text(text, column): 
    # ['item_type', 'item_name', 'wish_type', 'time'] 

    text = text.strip().replace("\n"," ").strip()
    text = text.replace("- ", "-").replace(" -", "-")
    text = text.replace("Wis!", "Wish")
    if(column=='time'):
        text=text.strip(")")

    return text

def find_files(path):
    file_list = []
    for file in os.listdir(path): 
        file_list.append(os.path.join(path,file))
    return file_list

def get_wish(info):
    # ['item_type', 'item_name', 'wish_type', 'time'] unparsed
    item_type = info[0]
    item_name = info[1].replace('(4-Star)',"").replace('(5-Star)',"").strip()
    if('4-Star' in info[1]): 
        rarity=4
    elif('5-Star' in info[1]):
        rarity=5
    else:
        rarity=3 
    # character, character2, weapon, standard, beginner

    wish_type = info[2]
    time = info[3]
    wish = Wish(item_type, item_name, wish_type, time, rarity)
    return wish 
def parse_wish(filename, display = False, psm=1):
    '''
    Parse wish from a file
    '''
    src = cv.imread(cv.samples.findFile(filename))
    # find the wish table

    # https://stackoverflow.com/questions/7853628/how-do-i-find-an-image-contained-within-an-image
    item_type_image = cv.imread("item_type.jpg")
    result = cv.matchTemplate(item_type_image, src, cv.TM_SQDIFF_NORMED)
    # Find coords
    _,_,(x0,y0),_ = cv.minMaxLoc(result) 
    w0,h0 = item_type_image.shape[:2] 

    scroll_bottom_image = cv.imread('scroll_bottom.jpg')
    result = cv.matchTemplate(scroll_bottom_image, src, cv.TM_SQDIFF_NORMED)
    _,_,(x1,y1),_ = cv.minMaxLoc(result) 
    w1,h1 = scroll_bottom_image.shape[:2] 

    x, y = x0-10, y0+w0-10 # start of box
    w, h = x1+h1//2-x, y1+w1//2-y # end of box 
 
    src = get_cropped_image(src, x, y, w, h) 
 
    # Tweak canny edge detector if lines not found properly
    # Loads an image
    horizontal, vertical = detect_lines(src, display = display, resize = (w//2, h//2)) 

    # ensure number of lines are correct
    if(len(horizontal) != 6 or len(vertical)!=5):
        logging.error("Error: box parsing incorrect")
        logging.debug(f'Horizontal lines {len(horizontal)}, Expected: 6')
        logging.debug(f'Vertical lines {len(vertical)}, Expected: 5') 
        return -1

    # Image preprocessing
    cropped_image, _ = get_ROI(src, horizontal, vertical, 0, -1, 0, -1)
    gray = get_grayscale(cropped_image) #grayscale
    bw = get_binary(gray) #blackwhite 
 
    # parse each box in table
    columns = ['item_type', 'item_name', 'wish_type', 'time']
    counter = 0
    wishes = list()
    # iterate by row
    for i in range(0, len(horizontal)-1):
        texts = list()

        for j in range(0, len(vertical)-1):
            column = columns[j]
            counter += 1
 
            left_line_index, right_line_index = j, j+1 
            top_line_index, bottom_line_index = i, i+1 
            
            # get boxed image
            cropped_image, (x,y,w,h) = get_ROI(bw, horizontal, vertical, left_line_index, right_line_index, top_line_index, bottom_line_index)
            
            # detect and clean text
            text = detect(cropped_image, column = column, psm = psm)  
            text = clean_text(text, column)
            texts.append(text)
            
            if(display):
                image_with_text = draw_text(src, x, y, w, h, text) 
                # cv.imshow("detect", image_with_text)
                cv.imshow(text, cropped_image)
                cv.waitKey(0)
                cv.destroyAllWindows() 
        # parse text and convert to wish type
        wish = get_wish(texts)
        logging.info(wish)
        wishes.append(wish)


    return wishes

def batch(folder_path = "wish/", json_path = "wishes.json", src_excel = None, dst_excel = None, display = False):   
    '''
    Process a batch of screenshot specified in the folder_path
    '''
    # TODO, support video 
    # TODO, read wish page number for order arrangement (low priority)

    # pics are taken in order of wish history page (most recent to oldest)
    file_list = find_files(folder_path)
    file_list = sorted(file_list)
    
    wishes = list()
    logging.info(f'Begin parsing wishes in {folder_path}')
    for i,file in enumerate(file_list):
        result = parse_wish(file, display = display)
        if(result == -1):
            logging.error(f"Error parsing {file}")
        wishes += result
    wishes.reverse() 

    wishes = data_verification(wishes)
 
    wish2json(wishes, name = json_path)

    if(src_excel and dst_excel):
        json2excel(json_path, src_excel, dst_excel)
 
if __name__ == "__main__":

    parser = argparse.ArgumentParser()  
    parser.add_argument("-f", "--folder_path", help="folder path", nargs='?', type=str, default="wish")  
    parser.add_argument("-json", "--json_path", help="json path", nargs='?', type=str, default="wishes.json")  
    parser.add_argument("-src", "--src_excel", help="src excel", nargs='?', type=str, const="src.xlsx") 
    parser.add_argument("-dst", "--dst_excel", help="dst excel", nargs='?', type=str, const="dst.xlsx")
    parser.add_argument("-d", "--display", help="display",action="store_true")
    args = parser.parse_args()
 
    logging.basicConfig(level=logging.DEBUG) 
    batch(folder_path = args.folder, json_path = args.json_path, 
        src_excel = args.src_excel, dst_excel = args.dst_excel,
        display = args.display)
 
