import numpy as np
import cv2

# 카메라 장치 열기
cap = cv2.VideoCapture(0)

# 카메라 프레임 사이즈 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 비디오 코덱 설정 및 녹화 객체 생성
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('recorder/output.avi', fourcc, 30.0, (640, 480))

while(cap.isOpened()):
    ret, frame = cap.read()
    
    if ret == True:
        out.write(frame)
        cv2.imshow('frame',frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
out.release()

cv2.destroyAllWindows()
