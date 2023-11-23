import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
import tkinter as tk

img = cv2.imread('recorder/output.png')
img = cv2.resize(img, (640, 480))

isDragging = False
blue, red = (255,0,0),(0,0,255)

position = list(-1 for _ in range(4)) # xs, ys, xe, ye

size = 12
arr = list([] for _ in range(size))
print(arr)

def onMouse(event,x,y,flags,param):
    global isDragging, img
    if event == cv2.EVENT_LBUTTONDOWN:
        isDragging = True
        position[0] = x
        position[1] = y
    elif event == cv2.EVENT_MOUSEMOVE:
        if isDragging:
            img_draw = img.copy()
            cv2.rectangle(img_draw, (position[0], position[1]), (x, y), blue, 2)
            cv2.imshow('img', img_draw)
    elif event == cv2.EVENT_LBUTTONUP:
        if isDragging:
            isDragging = False          
            position[2] = x
            position[3] = y
            w = x - position[0]
            h = y - position[1]
            print("xs:%d, ys:%d, xe:%d, ye:%d" % (position[0], position[1], x, y))
            if w > 0 and h > 0:
                img_draw = img.copy()
                cv2.rectangle(img_draw, (position[0], position[1]), (x, y), red, 2) 
                cv2.imshow('img', img_draw)

                root = tk.Tk()
                root.title("Enter the Position")
                
                label = tk.Label(root, text="Please enter the position: ")
                label.pack()
                
                number_entry = tk.Entry(root)
                number_entry.pack()
                number_entry.focus_set()
                number_entry.focus_force()
                
                confirm_button = tk.Button(root, text="OK", command=lambda: update_position(number_entry))
                confirm_button.pack()
                root.bind('<Return>', lambda event: update_position(number_entry))
                
                root.geometry(f'+{img.shape[1]//2}+{img.shape[0]//2}')
                
                root.mainloop()
                
            else:
                cv2.imshow('img', img)
                print("좌측 상단에서 우측 하단으로 영역을 드래그 하세요.")

def update_position(entry):
    idx = int(entry.get())
    entry.master.destroy()
    
    if 0 <= idx < len(arr):
        arr[idx].append(list(position))
    print(arr)
    
    with open(f'recorder/position.pickle', 'wb') as file:
        pickle.dump(arr, file)

cv2.imshow('img', img)
cv2.setMouseCallback('img', onMouse)
cv2.waitKey()
cv2.destroyAllWindows()