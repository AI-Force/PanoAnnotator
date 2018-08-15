import os

import data
import utils
import configs.Params as pm
import estimator

class Scene(object):

    def __init__(self, mainWindows):
        
        self.__mainWindows = mainWindows
        self.__isAvailable = False
        self.__mainDirPath = ""

        ### Pano color
        self.__panoColor = data.Resource('Color')

        ### Pano depth
        self.depthPred = None
        self.__panoDepth = data.Resource('Depth')
        self.__panoPointCloud = None

        ### Pano Lines and Omap
        self.__panoLines = data.Resource('Lines')
        self.__panoOmap = data.Resource('Omap')

        ### Layout Map
        self.__layoutEdgeMap = data.Resource('Edge Map')
        self.__layoutNormalMap = data.Resource('Normal Map')

        ### Annotation
        self.label = data.Annotation(self)
        self.selectObjs = []

    def initScene(self, filePath, depthPred=None):

        self.__mainDirPath = os.path.dirname(os.path.realpath(filePath))
        self.__panoColor.path = filePath

        self.__initColor()

        self.depthPred = depthPred
        self.__initDepth()

        self.__checkIsAvailable()

        return self.isAvailable()

    def initScene2(self):

        self.__initLines()
        self.__initOmap()
        
        self.label.calcInitLayout()

    def __initColor(self):
        self.__panoColor.initByImageFile(self.__panoColor.path)
    
    
    def __initDepth(self):
        
        panoDepthPath = os.path.join(self.__mainDirPath, pm.depthFileDefaultName)
        isExist = self.__panoDepth.initByImageFile(panoDepthPath)
        if isExist:
            depthData = self.__panoDepth.data.astype(float) / 4000 #For Matterport3d GT
            self.__panoDepth.data = depthData
        else:
            pred = self.depthPred.predict(self.__panoColor.image)
            self.__panoDepth.data = pred

    def __initLines(self):

        panoLinesPath = os.path.join(self.__mainDirPath, pm.linesFileDefaultName)
        isExist = self.__panoLines.initByImageFile(panoLinesPath)

        #dilation & BLur data
        if isExist:
            self.__panoLines.data /= 255
            dataDilate = utils.imageDilation(self.__panoLines.data, 8)
            dataBlur = utils.imageGaussianBlur(dataDilate, 10)
            self.__panoLines.pixmap = utils.data2Pixmap(dataBlur)
    
    def __initOmap(self):

        panoOmapPath = os.path.join(self.__mainDirPath, pm.omapFileDefaultName)
        isExist = self.__panoOmap.initByImageFile(panoOmapPath)
        if isExist:
            self.__panoOmap.data /= 255
            #self.__panoOmap.data[(self.__panoOmap.data[:,:,0]>0)] = [1,0,0]
            #self.__panoOmap.data[(self.__panoOmap.data[:,:,1]>0)] = [0,1,0]
            #self.__panoOmap.data[(self.__panoOmap.data[:,:,2]>0)] = [0,0,1]
            self.__panoOmap.pixmap = utils.data2Pixmap(self.__panoOmap.data)

    #####
    #Getter & Setter
    #####

    #Available
    def __checkIsAvailable(self):

        if self.__panoColor.image and (self.__panoDepth.data is not None):
            self.__isAvailable = True
        else :
            self.__isAvailable = False
    
    def isAvailable(self):
        return self.__isAvailable

    #Mainwindows
    def getMainWindows(self):
        return self.__mainWindows

    #Pano Color
    def getPanoColorImage(self):
        return self.__panoColor.image
    def getPanoColorPixmap(self):
        return self.__panoColor.pixmap
    def getPanoColorData(self):
        return self.__panoColor.data

    #Pano Depth
    def getPanoDepthData(self):
        return self.__panoDepth.data

    #Pano lines and Omap
    def getPanoLinesData(self):
        return self.__panoLines.data
    def getPanoLinesPixmap(self):
        return self.__panoLines.pixmap
    def getPanoOmapData(self):
        return self.__panoOmap.data
    def getPanoOmapPixmap(self):
        return self.__panoOmap.pixmap

    #Pano Point Cloud
    def setPanoPointCloud(self, pc):
        self.__panoPointCloud = pc
        return self.__panoPointCloud
    def getPanoPointCloud(self):
        return self.__panoPointCloud

    def setLayoutEdgeMapPixmap(self, pixmap):
        self.__layoutEdgeMap.pixmap = pixmap
    def getLayoutEdgeMapPixmap(self):
        return self.__layoutEdgeMap.pixmap
    
    def setLayoutNormalMapPixmap(self, pixmap):
        self.__layoutNormalMap.pixmap = pixmap
    def getLayoutNormalMapPixmap(self):
        return self.__layoutNormalMap.pixmap

    def getSelectObjs(self, objType=None):
        objs = []
        typeDict = {'GeoPoint':data.GeoPoint, 'WallPlane':data.WallPlane, 
                    'FloorPlane':data.FloorPlane}
        if objType:
            for obj in self.selectObjs:
                if type(obj) == typeDict[objType]:
                    objs.append(obj)
            return objs
        elif objType == None:
            return self.selectObjs
        
    

