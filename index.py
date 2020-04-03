import cv2
import numpy as np
from matplotlib import pyplot as plt

def resizeAndPad(img, size, padColor=0):

    h, w = img.shape[:2]
    sh, sw = size

    # interpolation method
    if h > sh or w > sw: # shrinking image
        interp = cv2.INTER_AREA
    else: # stretching image
        interp = cv2.INTER_CUBIC

    # aspect ratio of image
    aspect = w/h  # if on Python 2, you might need to cast as a float: float(w)/h

    # compute scaling and pad sizing
    if aspect > 1: # horizontal image
        new_w = sw
        new_h = np.round(new_w/aspect).astype(int)
        pad_vert = (sh-new_h)/2
        pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
        pad_left, pad_right = 0, 0
    elif aspect < 1: # vertical image
        new_h = sh
        new_w = np.round(new_h*aspect).astype(int)
        pad_horz = (sw-new_w)/2
        pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
        pad_top, pad_bot = 0, 0
    else: # square image
        new_h, new_w = sh, sw
        pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

    # set pad color
    if len(img.shape) is 3 and not isinstance(padColor, (list, tuple, np.ndarray)): # color image but only one color provided
        padColor = [padColor]*3

    # scale and pad
    scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
    scaled_img = cv2.copyMakeBorder(scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=padColor)

    return scaled_img

img = cv2.imread('img2.jpg')

edges = cv2.Canny(img,100,200)
h, w = edges.shape[:2]
scaled_mask = resizeAndPad(edges, (h+2,w+2), 255)
#original_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

hsv_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
h, s, v = cv2.split(hsv_image)
h.fill(165)
hsv_image = cv2.merge([h, s, v])
rgb_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)

#intensity = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
old_edges = edges.copy()
cv2.floodFill(edges, scaled_mask, (100, 100), 255)
cv2.subtract(edges, old_edges, edges)
wall = edges

a = cv2.bitwise_and(rgb_image, rgb_image, mask=wall)
# pattern = np.zeros(img.shape[:],np.uint8)
# pattern[:]=(58,205,142) 
# lab_pattern = cv2.cvtColor(pattern, cv2.COLOR_RGB2LAB)
# lp, ap, bp = cv2.split(lab_pattern)

# clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
# cl = clahe.apply(l)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(a, cmap = 'gray')
plt.title('New Image'), plt.xticks([]), plt.yticks([])
plt.show()



# cap = cv2.VideoCapture(0)

# while(1):

#     # Take each frame
#     _, frame = cap.read()

#     # Convert BGR to HSV
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#     # define range of blue color in HSV
#     lower_blue = np.array([110,50,50])
#     upper_blue = np.array([130,255,255])

#     # Threshold the HSV image to get only blue colors
#     mask = cv2.inRange(hsv, lower_blue, upper_blue)

#     # Bitwise-AND mask and original image
#     res = cv2.bitwise_and(frame,frame, mask= mask)

#     cv2.imshow('frame',frame)
#     cv2.imshow('mask',mask)
#     cv2.imshow('res',res)
#     k = cv2.waitKey(5) & 0xFF
#     if k == 27:
#         break

# cv2.destroyAllWindows()

# IplImage image = cvLoadImage("img2.jpg");
# CvSize cvSize = cvGetSize(image);


# IplImage hsvImage = cvCreateImage(cvSize, image.depth(),image.nChannels());

# IplImage hChannel = cvCreateImage(cvSize, image.depth(), 1); 
#         IplImage  sChannel = cvCreateImage(cvSize, image.depth(), 1); 
#         IplImage  vChannel = cvCreateImage(cvSize, image.depth(), 1);
# cvSplit(hsvImage, hChannel, sChannel, vChannel, null);


# IplImage cvInRange = cvCreateImage(cvSize, image.depth(), 1);
# CvScalar source=new CvScalar(72/2,0.07*255,66,0); //source color to replace
# CvScalar from=getScaler(source,false);
# CvScalar to=getScaler(source, true);

# cvInRangeS(hsvImage, from , to, cvInRange);

# IplImage dest = cvCreateImage(cvSize, image.depth(), image.nChannels());

# IplImage temp = cvCreateImage(cvSize, IPL_DEPTH_8U, 2);
# cvMerge(hChannel, sChannel, null, null, temp);

# cvSet(temp, new CvScalar(45,255,0,0), cvInRange);// destination hue and sat
# cvSplit(temp, hChannel, sChannel, null, null);
# cvMerge(hChannel, sChannel, vChannel, null, dest);
# cvCvtColor(dest, dest, CV_HSV2BGR);
# cvSaveImage("output.png", dest);