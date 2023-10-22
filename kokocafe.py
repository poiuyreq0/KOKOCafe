import cv2
from ultralytics import YOLO
import pickle
import datetime
from collections import deque
import numpy as np
import requests
import json
from collections import Counter
import csv
import os

# Load the YOLOv8 model
model = YOLO('yolov8s.pt')

with open('recorder/position.pickle', 'rb') as file:
    arr = pickle.load(file)
length = len(arr)
print('arr', arr)

time_pre = -1
dq = deque()

def combine_positions(results):
    outputs = []
    
    for result in results:
        for xyxy in result.boxes.xyxy:
            x1, y1, x2, y2 = xyxy.tolist()
            mid_x = (x1+x2)//2
            mid_y = (y1+y2)//2
            
            position = -1
            for i in range(length):
                for j in range(len(arr[i])):
                    if arr[i][j][0]<=mid_x<=arr[i][j][2] and arr[i][j][1]<=mid_y<=arr[i][j][3]:
                        position = i
                        break
                    
            outputs.append(position)
    
    print('outputs', outputs)
            
    return outputs



def combine_avgs(outputs, size=30, w=0.5):
    global time_pre
    global dq
    
    current_time = datetime.datetime.now()
    time_cur = int(current_time.strftime('%S'))
    
    positionCounts = np.zeros(length)
    positionSums = np.zeros(length)
    positionAvgs = np.zeros(length)
    
    # 1초 단위로 저장
    if time_cur != time_pre:
        time_pre = time_cur
    else:
        for output in outputs:
            if output!=-1:
                positionCounts[output] += 1
                
        dq.append(positionCounts)
        if len(dq) > size:
            dq.popleft()
            
        for positionCounts in dq:
            # 예외 처리
            if len(positionCounts) == 0:
                break
            
            positionSums += positionCounts
        
        positionAvgs = np.floor((positionSums / size) + w).astype(int)
                
        print("Cnt:", positionCounts.tolist())
        print("Avg:", positionAvgs.tolist())
        
    return positionAvgs.tolist()



# def write_csv(outputs):
#     current_time = datetime.datetime.now()
#     date_str = current_time.strftime('%Y-%m-%d')
#     time_str = current_time.strftime('%H:%M:%S')
    
#     counts = Counter(outputs)
#     cnt0 = counts[0]
#     cnt1 = counts[1]
#     cnt2 = counts[2]

#     fields = ['date', 'time', 'entire_num', 'center_num', 'bottom_num', 'right_num']
    
#     file_exists = os.path.exists('data.csv')

#     with open('data.csv', 'a', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=fields)
        
#         if not file_exists:
#             writer.writeheader()
        
#         data = {
#             'date': date_str, 'time': time_str, 'entire_num': len(outputs),
#             'center_num': cnt0, 'bottom_num': cnt1, 'right_num': cnt2
#             }
        
#         writer.writerow(data)



def main():
    # video_path = 0
    video_path = 'recorder/output.mp4'
    cap = cv2.VideoCapture(video_path)
    
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLOv8 inference on the frame
            results = model.predict(frame, conf=0.2, iou=0.45, classes=0, hide_conf=False)
            
            outputs = combine_positions(results)
            
            avgs = combine_avgs(outputs, size=30, w=0.5)
            
            params = {"name": "koko1"}
            data = json.dumps(avgs)
            headers = {"Content-Type": "application/json"}
            # response = requests.put("http://192.168.55.59:8080/positions/update", params=params, data=data, headers=headers)
            response = requests.put("http://ec2-43-202-59-190.ap-northeast-2.compute.amazonaws.com:8080/positions/update", params=params, data=data, headers=headers)
            
            # write_csv(outputs)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()