# A modified YOLO combined with Astar PathFinding Algorithm 

## The model weights are uploaded to the Google Drive 
* Put two **.pth** files to _'model_data'_ folder 
* Training sets are not uploaded because you don't need them if you want to train your own set

## Usage: 
* predict file for single image detecting 
* video file for detecting objects in videos 
* train file for YOLO training 

## There are some pictures and video for different scenarios
* You will need to change the related line in video/predict and yolo accordingly.

# A brief description of the training process 
* get **jpg** pictures from environment 
* use _labelimg_ package to generate annotation files for training 
* put the annotations and jpg pictures files into VOCdevkit\VOC2007\Annotations and JPEGImages folders respectively.
* run _voc_annotation_ 
* run _train_


# More details can be found in the Chinese Version README_CN.md 
* Hopefully you can know some Chinese  ( *ˆoˆ* )
* Original version: _Bubbliiiing_
* video version(Chinese): https://www.bilibili.com/video/BV1Hp4y1y788?from=search&seid=17194071580106070679