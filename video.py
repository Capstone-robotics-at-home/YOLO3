#-------------------------------------#
#       Video detection 
#-------------------------------------#
from yolo import YOLO
from PIL import Image
import numpy as np
import cv2
import time
from Astar import Astar
from Path_Utils import plotting, env
yolo = YOLO()
# get the camera 
# capture=cv2.VideoCapture("1.mp4" Or 0)
capture=cv2.VideoCapture("img/a.mp4") 
# capture=cv2.VideoCapture(0) 

fps = 0.0
while(True): 
    t1 = time.time()
    # get one frame
    ref,frame=capture.read()
    # change format，BGRtoRGB
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    # change to Image
    frame = Image.fromarray(np.uint8(frame))

    # start detecting 
    frame, objects = yolo.detect_image(frame)
    if not len(objects) == 4:  # if all the objects are not detected -> recheck 
        continue

    # Use Astar
    s_start = objects['Jetbot'][0]
    s_goal = objects['Target'][0]
    obstacle_ls = objects['Obstacle']
    if type(obstacle_ls[0]) == type(()):  # if there is only one obstacle:
        obstacle_ls = [obstacle_ls]
    astar = Astar(s_start, s_goal, obstacle_ls)
    path, visited = astar.searching()

    plot = plotting.Plotting(s_start, s_goal, obstacle_ls)
    # plot.animation(path,visited,'AStar')
    frame = plot.plot_image_path(frame,path)


    frame = np.array(frame)

    # RGBtoBGR to satisfy opencv display format 
    frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)

    fps  = ( fps + (1./(time.time()-t1)) ) / 2
    print("fps= %.2f"%(fps))
    frame = cv2.putText(frame, "fps= %.2f"%(fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("video",frame)


    c= cv2.waitKey(30) & 0xff 
    if c==27:
        capture.release()
        break
