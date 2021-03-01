#-------------------------------------#
#       single image detection
#-------------------------------------#
from yolo import YOLO
from PIL import Image
from Astar import Astar
from Path_Utils import plotting, env

yolo = YOLO()

img = 'img/026.jpg'
try:
    image = Image.open(img)
except:
    print('Open Error! Try again!')
else:
    r_image, objects = yolo.detect_image(image)
    # r_image.show()

s_start = objects['Jetbot'][0]
s_goal = objects['Target'][0]
obstacle_ls = objects['Obstacle']
if type(obstacle_ls[0]) == type(()):  # if there is only one obstacle:
    obstacle_ls = [obstacle_ls]
astar = Astar(s_start, s_goal, obstacle_ls)
path, visited = astar.searching()

plot = plotting.Plotting(s_start, s_goal, obstacle_ls)
img = plot.plot_image_path(r_image,path)
img.show() 


