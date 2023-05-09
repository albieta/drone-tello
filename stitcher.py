#import cv2

#stitcher = cv2.Stitcher_create()
#f00 = cv2.imread("./f00.jpeg")
#f01 = cv2.imread("./f01.jpeg")
#f02 = cv2.imread("./f02.jpeg")
#f03 = cv2.imread("./f03.jpeg")
#f10 = cv2.imread("./f10.jpeg")

#result = stitcher.stitch((f00,f01,f02,f03,f10))

#cv2.imwrite("./result.jpg", result[1])

import cv2

# Load images
img1 = cv2.imread('image_0.jpg')
img2 = cv2.imread('image_20.jpg')
img3 = cv2.imread('image_40.jpg')
img4 = cv2.imread('image_60.jpg')
img5 = cv2.imread('image_80.jpg')
img6 = cv2.imread('image_100.jpg')
img7 = cv2.imread('image_120.jpg')
img8 = cv2.imread('image_140.jpg')


# Create stitcher object
stitcher = cv2.Stitcher_create()

# Stitch images
result = stitcher.stitch((img1, img2, img3, img4, img5, img6, img7, img8))

# Save result
cv2.imwrite('./result.jpg', result[1])