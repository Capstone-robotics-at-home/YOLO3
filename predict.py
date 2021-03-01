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
obstacle = objects['Obstacle']
obstacle = [obstacle[0]] if len(obstacle[0]) == 2 else [i[0] for i in obstacle]
astar = Astar(s_start, s_goal, obstacle)
path, visited = astar.searching()

plot = plotting.Plotting(s_start, s_goal, obstacle)
img = plot.plot_image_path(r_image,path)
img.show() 


