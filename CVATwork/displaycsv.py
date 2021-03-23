import matplotlib.pyplot as plt
import cv2
import pandas as pd

def displaycsv(path1,path2):
    ant=pd.read_csv(path1+"track.csv")
    
    for i in range(len(ant)):
        j=int(ant.iloc[i,0])
        img=cv2.imread(path2+str(j)+".jpg")

        img = cv2.rectangle(img, (int(ant.iloc[i,1]),int(ant.iloc[i,2])), (int(ant.iloc[i,3]),int(ant.iloc[i,4])), (0,0,255), 3)                       
        cv2.imwrite(path2+str(ant.iloc[i,0])+".jpg",img)
    
    