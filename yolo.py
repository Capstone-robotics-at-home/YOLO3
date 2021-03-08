#-------------------------------------#
#       YOLO Class 
#-------------------------------------#
import cv2
import numpy as np
import colorsys
import os
import torch
import torch.nn as nn
from nets.yolo3 import YoloBody
import torch.backends.cudnn as cudnn
from PIL import Image, ImageFont, ImageDraw
from torch.autograd import Variable
from utils.config import Config
from utils.utils import non_max_suppression, bbox_iou, DecodeBox, letterbox_image, yolo_correct_boxes


class YOLO(object):
    _defaults = {
        # "model_path": 'model_data/yolo_weights.pth',
        # "classes_path": 'model_data/coco_classes.txt',
        "model_path": 'model_data/jetbot_weights.pth',
        "classes_path": 'model_data/jetbot_class.txt',
        "model_image_size": (416, 416, 3),
        "confidence": 0.5,
        "cuda": True
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    #---------------------------------------------------#
    #   initialize YOLO
    #---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.class_names = self._get_class()
        self.config = Config
        self.generate()
    #---------------------------------------------------#
    #   get all the classes 
    #---------------------------------------------------#

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names
    #---------------------------------------------------#
    #   get all the classes 
    #---------------------------------------------------#

    def generate(self):
        self.config["yolo"]["classes"] = len(self.class_names)
        self.net = YoloBody(self.config)

        state_dict = torch.load(self.model_path)
        self.net.load_state_dict(state_dict)
        self.net = self.net.eval()

        if self.cuda:
            os.environ["CUDA_VISIBLE_DEVICES"] = '0'
            self.net = nn.DataParallel(self.net)
            self.net = self.net.cuda()

        self.yolo_decodes = []
        for i in range(3):
            self.yolo_decodes.append(DecodeBox(
                self.config["yolo"]["anchors"][i], self.config["yolo"]["classes"],  (self.model_image_size[1], self.model_image_size[0])))

        print('{} model, anchors, and classes loaded.'.format(self.model_path))
        # set different colors for the rectangle 
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))

    #---------------------------------------------------#
    #   detect pictures 
    #---------------------------------------------------#
    def detect_image(self, image):
        image_shape = np.array(np.shape(image)[0:2])

        crop_img = np.array(letterbox_image(
            image, (self.model_image_size[0], self.model_image_size[1])))
        photo = np.array(crop_img, dtype=np.float32)
        # normalize
        photo /= 255.0
        photo = np.transpose(photo, (2, 0, 1))
        photo = photo.astype(np.float32)
        # extend the dimension 
        images = []
        images.append(photo)
        # turn to tensor
        images = np.asarray(images)
        images = torch.from_numpy(images)
        if self.cuda:
            images = images.cuda()

        with torch.no_grad():
            outputs = self.net(images)
            output_list = []
            for i in range(3):
                output_list.append(self.yolo_decodes[i](outputs[i]))
            output = torch.cat(output_list, 1)
            # non-max suppression 
            batch_detections = non_max_suppression(output, self.config["yolo"]["classes"],
                                                   conf_thres=self.confidence,
                                                   nms_thres=0.3)
        try:
            batch_detections = batch_detections[0].cpu().numpy()
        except:
            return image, {}
        top_index = batch_detections[:, 4] * \
            batch_detections[:, 5] > self.confidence
        top_conf = batch_detections[top_index, 4] * \
            batch_detections[top_index, 5]
        top_label = np.array(batch_detections[top_index, -1], np.int32)
        top_bboxes = np.array(batch_detections[top_index, :4])
        top_xmin, top_ymin, top_xmax, top_ymax = np.expand_dims(top_bboxes[:, 0], -1), np.expand_dims(
            top_bboxes[:, 1], -1), np.expand_dims(top_bboxes[:, 2], -1), np.expand_dims(top_bboxes[:, 3], -1)

        # drop the grey area 
        boxes = yolo_correct_boxes(top_ymin, top_xmin, top_ymax, top_xmax, np.array(
            [self.model_image_size[0], self.model_image_size[1]]), image_shape)

        font = ImageFont.truetype(font='model_data/simhei.ttf',
                                  size=np.floor(3e-2 * np.shape(image)[1] + 0.5).astype('int32'))

        thickness = (np.shape(image)[0] + np.shape(image)
                     [1]) // self.model_image_size[0]

        objs = dict()  # the diction of all the objects {'name':[center,left,right,bottom,top]}

        for i, c in enumerate(top_label):
            predicted_class = self.class_names[c]
            score = top_conf[i]

            top, left, bottom, right = boxes[i]
            top = top - 5
            left = left - 5
            bottom = bottom + 5
            right = right + 5

            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(np.shape(image)[0], np.floor(
                bottom + 0.5).astype('int32'))
            right = min(np.shape(image)[1], np.floor(
                right + 0.5).astype('int32'))

            # paint the rectangles 
            # label = '{} {:.2f}'.format(predicted_class, score)
            label = predicted_class
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)
            label = label.encode('utf-8')
            # print(label)

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[self.class_names.index(predicted_class)])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[self.class_names.index(predicted_class)])
            draw.text(text_origin, str(label, 'UTF-8'),
                      fill=(0, 0, 0), font=font)
            center = ((left + right) //2, (top + bottom) // 2)
            draw.text(center,'X',fill =self.colors[self.class_names.index(predicted_class)])   # point out the center as X 
            dict_output = [center,left, right, bottom, top]
            if not predicted_class in objs:
                objs[predicted_class] = dict_output
            else:
                if not len(objs[predicted_class]) == 1: 
                    objs[predicted_class] = [objs[predicted_class]] 
                objs[predicted_class].append(dict_output)
            del draw
        print('Detection results: ', objs)
        return image, objs 
