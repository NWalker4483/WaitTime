from os import times, wait
import cv2 
import numpy as np
from datetime import datetime
import os
from tqdm import tqdm
from utils import BOXLoader

frame_shape = (360, 640)
motion_frame = np.zeros((*frame_shape, 2))
time_template = '%Y_%m_%d-%I:%M:%S_%p'

try:
    for i, name in enumerate(os.listdir("stream")):
        if not os.path.exists(os.path.join("detections", f"{name[:-4]}.csv")):
            continue

        vid = cv2.VideoCapture(os.path.join("stream", name))
        det = BOXLoader(os.path.join("detections", f"{name[:-3]}csv"))

        start, stop = name[:-4].split("_to_")
        start, stop = datetime.strptime(start, time_template), datetime.strptime(stop, time_template)
        
        ret, frame = vid.read()
        det.update(frame)

        FPS = vid.get(cv2.CAP_PROP_FPS)
        DT = (stop - start).total_seconds()
        FRAME_COUNT = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"VIDEO: {name}\n\t FPS: {FRAME_COUNT/DT}")

        ret = True
        last_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        frame_num = 0 
        for j in tqdm(range(FRAME_COUNT)): 
            ret, frame = vid.read()
            frame_num += 1
            if not ret:
                break

            detections = det.update(frame)
            for (bbox,class_name, ID) in detections:
                if class_name == "person":
                    cv2.rectangle(frame, tuple(bbox[2:]), tuple(bbox[:2]), (255,0,0), 5)
            cv2.imshow("dfd",frame)
            cv2.waitKey(1)
            # # Converts each frame to grayscale - we previously 
            # # only converted the first frame to grayscale
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # # Calculates dense optical flow by Farneback method
            # flow = cv2.calcOpticalFlowFarneback(last_gray, gray, 
            #                                 None,
            #                                 0.5, 3, 15, 3, 5, 1.2, 0)
            # last_gray = gray
            # motion_frame += flow
        
            # # Creates an image filled with zero
            # # intensities with the same dimensions 
            # # as the frame
            # mask = np.zeros_like(frame)

            # # Sets image saturation to maximum
            # mask[..., 1] = 255

            # # Computes the magnitude and angle of the 2D vectors
            # magnitude, angle = cv2.cartToPolar(motion_frame[..., 0], motion_frame[..., 1])
            
            # # Suppress high frequency noise by the edge of the frame
            # border = 10
            # magnitude[:border] = 0 
            # magnitude[magnitude.shape[0] - border:] = 0 
            # magnitude[...,:border] = 0 
            # magnitude[...,magnitude.shape[1]-border:] = 0
            
            # magnitude[magnitude > 0] = 1/magnitude[magnitude > 0]

            # # Sets image hue according to the optical flow 
            # # direction
            # mask[..., 0] = angle * 180 / np.pi / 2
            
            # norm_mag = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
            # # (T, mag) = cv2.threshold(mag, 50, 255, cv2.THRESH_BINARY)
            # mask[..., 2] = norm_mag
            # # print(mask.shape)
            # # Converts HSV to RGB (BGR) color representation
            # rgb = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
            # added_image = cv2.addWeighted(frame,0.5,rgb,0.5,0)
            # #cv2.imshow("Long-Term Flow Frame + Current Image",added_image)#np.hstack((rgb, frame)))
            # #cv2.waitKey(1)
            # cv2.imwrite(f'current-combined.png', added_image)
except Exception as e:
    raise(e)
finally:
    pass
    # cv2.imwrite('total-frame.png', frame)
    # cv2.imwrite('total-flow.png', rgb)
    # cv2.imwrite('total-combined.png', added_image)
    # np.savetxt("motion_frame.txt", motion_frame)
#2021_09_18-03/50/21_PM_to_2021_09_18-04/05/21_PM.mp4