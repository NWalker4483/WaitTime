import numpy as np 
import cv2

frame = cv2.imread("final-frame.png")
image = frame.copy()
motion_frame = np.load("motion_frame.npy")
# Computes the magnitude and angle of the 2D vectors
magnitude, angle = cv2.cartToPolar(motion_frame[..., 0], motion_frame[..., 1])
            
# Suppress high frequency noise by the edge of the frame
# border = 10
# magnitude[:border] = 0 
# magnitude[magnitude.shape[0] - border:] = 0 
# magnitude[...,:border] = 0 
# magnitude[...,magnitude.shape[1]-border:] = 0

magnitude = cv2.normalize(magnitude, None, 0, 1, cv2.NORM_MINMAX)

dx, dy = cv2.polarToCart(magnitude, angle)

# Init Particle
spacing = 100
trails = []
for x in range(0,dx.shape[1], spacing):
   for y in range(0,dy.shape[0], spacing):
       trails.append([(x,y)])

# Calculate Paths
trail_copy = trails
for i, trail in enumerate(trail_copy):
    x, y = trail[-1]
    for iter in range(2800):
        x, y = x + dx[int(y)][int(x)], y + dy[int(y)][int(x)]
        if (0 > x) or (x >= dx.shape[1]) or (0 > y) or (y >= dy.shape[0]):
            print("Trail Complete")
            break
        trails[i].append((x,y))

# Sort trails by length
def polyline_length(line):
    dist = lambda p1, p2: ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**.5
    traveled = 0 
    for i in range(len(line) - 1):
        traveled += dist(line[i], line[i + 1])
    return traveled

lengths = np.array([polyline_length(trail) for trail in trails])
sizes = lengths * (1/lengths.max())

sorted_trails = sorted(zip(trails, sizes), key= lambda x: x[1], reverse=False)
final = []

# TODO: Make Not terrible
for trail, size in sorted_trails:
    trail = np.array(trail, dtype=np.int32)
    cv2.circle(frame, tuple(trail[0].astype(int)), 3, (0,255,0), -1)
    cv2.circle(frame, tuple(trail[-1].astype(int)), 3, (0,0,255), -1)
    try:
        if size > .5:
            color = (0, int(size*255), 255)
            final.append(trail)
        else:
            color = (255, int(size*255), 0)

        trail = trail.reshape((-1, 1, 2))
        frame = cv2.polylines(frame, [trail], 
                            False, color, int(size * spacing) if int(size * spacing) != 0 else 1 )
    except Exception as e:
        print(e)

good_only = frame.copy()
mask = np.zeros_like(frame)
for trail in final:
    good_only = cv2.polylines(good_only, [trail], 
                            False, color, int(size * 10) if int(size * 10) != 0 else 1 )
    cv2.circle(mask, tuple(trail[0].astype(int)), 1+(spacing//2), (0,255,0), -1)
    cv2.circle(mask, tuple(trail[-1].astype(int)), 1+(spacing//2), (0,0,255), -1)

show_image = image.copy()
b, g, r = cv2.split(mask)

ret, start_thresh = cv2.threshold(g, 40, 255, 0)
ret, stop_thresh = cv2.threshold(r, 40, 255, 0)

contours, hierarchy = cv2.findContours(start_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

if len(contours) != 0:
    # draw in blue the contours that were founded
    # cv2.drawContours(frame, contours, -1, 255, 3)

    # find the biggest countour (c) by the area
    c = max(contours, key = cv2.contourArea)

    x,y,w,h = start = cv2.boundingRect(c)
    # draw the biggest contour (c) in green
    cv2.rectangle(show_image,(x,y),(x+w,y+h),(0,255,0),5)

contours, hierarchy = cv2.findContours(stop_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

if len(contours) != 0:
    # draw in blue the contours that were founded
    # cv2.drawContours(frame, contours, -1, 255, 3)

    # find the biggest countour (c) by the area
    c = max(contours, key = cv2.contourArea)
    
    x,y,w,h = stop = cv2.boundingRect(c)
    # draw the biggest contour (c) in green
    cv2.rectangle(show_image,(x,y),(x+w,y+h),(0,0,255),5)
with open('stop-box.npy', 'wb') as f:
    np.save(f, stop)
with open('start-box.npy', 'wb') as f:
    np.save(f, start)
cv2.imwrite('start-stop-mask.png', mask)
cv2.imwrite('good-only.png', good_only)
cv2.imwrite('start-stop-final.png', np.hstack((good_only, mask, show_image)))
cv2.imwrite('path-traveled.png', frame)
            
