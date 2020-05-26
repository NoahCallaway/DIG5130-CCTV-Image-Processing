#Noah Callaway 2020
#BCU DIG5130
import cv2
import numpy as np


class CCTV:
    def __init__(self):
        #Define default parameters for processing
        self.kernel = 25
        self.max_kernel_size = 100
        self.blur = 15
        self.max_blur_size = 100
        self.motion_sensitivity = 12
        self.max_motion_sensitivity = 30
        self.colour_enable = 0
        
        #initialise web cam input
        self.cam = cv2.VideoCapture(0)

        #Define Gui
        self.window_name = 'Main Window'
        self.window_kernel_size = 'Kernel Size:'
        self.window_blur_size = 'Blur Size: '
        self.window_motion_sensitivity = 'Motion Sensitivity: '
        self.window_colour_enable = 'Colour Enable: '
        #Create Gui
        cv2.namedWindow(self.window_name)
        cv2.createTrackbar(self.window_kernel_size, self.window_name, self.kernel, self.max_kernel_size, self.update_params)
        cv2.createTrackbar(self.window_blur_size, self.window_name, self.blur, self.max_blur_size, self.update_params)
        cv2.createTrackbar(self.window_motion_sensitivity, self.window_name, self.motion_sensitivity, self.max_motion_sensitivity, self.update_params)
        cv2.createTrackbar(self.window_colour_enable, self.window_name, 0, 1, self.update_params)
    
    #Function to collect two frames returns one in colour and one GRAY
    def get_frame(self):
        ret, frame = self.cam.read()
        #Handle error
        if ret == 'False':
            print('ERROR Grabbing Frame')
            pass
        else:
            return [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),frame]

    #Function to process motion and display box
    def process_motion(self, orig, diff):
        #Make a copy of image passed in color or gray
        orig = orig[self.colour_enable].copy()

        #Process the image and chonkify
        kernel = np.ones((self.kernel,self.kernel))
        diff = cv2.GaussianBlur(diff.copy(), (self.blur,self.blur), 0)
        #thresh every value become 1 or 0 
        ret, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, kernel, iterations=1)

        #Find contours and draw them
        contours, heirarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            cnt = contours[0]
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(orig, (x,y), (x+w,y+h), (255,255,0), 2)
        
        #Add text and return image
        cv2.putText(orig, 'MOTION DETECTED', (10,450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)        
        cv2.imshow('thresh', thresh)
        return orig

    #Main procedure
    def main_loop(self):
        #Get first frame
        last_frame = self.get_frame() [0]
    
        while (True):
            #capture each frame and calculate difference
            frame = self.get_frame()
            diff = cv2.absdiff(frame[0].copy(),last_frame.copy())
            #add new frame to buffer
            last_frame = frame[0]
            
            #see if motion in difference frame
            if np.mean(diff) > (self.motion_sensitivity/10):
                im = self.process_motion(frame.copy(),diff.copy())
                #self.process_motion(frame,diff)
            else:
                im = frame[self.colour_enable]
                #cv2.imshow(self.window_name,frame[self.colour_enable])
            cv2.imshow(self.window_name, im)

            #end if quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("BREAK")
                break
        self.cam.release()
        cv2.destroyAllWindows()
    
    #Update paramaters on slider change
    def update_params(self,val):
        self.kernel = cv2.getTrackbarPos(self.window_kernel_size, self.window_name)
        self.blur = cv2.getTrackbarPos(self.window_blur_size, self.window_name)
        self.blur = self.blur + 1 if self.blur % 2 == 0 else self.blur
        self.motion_sensitivity = cv2.getTrackbarPos(self.window_motion_sensitivity, self.window_name)
        self.colour_enable = cv2.getTrackbarPos(self.window_colour_enable, self.window_name)

    

cam = CCTV()
cam.main_loop()