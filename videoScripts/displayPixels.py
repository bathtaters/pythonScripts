# Draws an image based on raw pixel data
# Uses tkinter

# Raw pixel data file
filename = '/path/to/pixels.rgb'

# Image options
width = 1920 # Frame width
height = 1080 # Frame height
bit_depth = 10 # Pixel bit depth
crop = False # False will shrink to fit

# Change pixel data before output
def alter(pix):
    # pix = [ G, B, R ] as ints
    return pix

# Advanced options
ENDI = 'little' # Endianess
CHANCOUNT = 3 # Number of Color Channels (RGB=3)
MAXRES = 150000 # Max resolution (WxH) to render
BARLEN = 50 # Update rate of loading bar
bytelen = -1 # Byte size of pixel (-1 sets from bitDepth)









# Imports
from os.path import getsize
from tkinter import *

# Initialize globals
wd = 1
ht = 1
pix_map = []
if bytelen < 0:
    # Ceil of bit_depth/8
    bytelen = int(bit_depth/8 + 1) if bit_depth/8 - int(bit_depth/8) else int(bit_depth/8)


# Tkinter Object
class Popper:

    def __init__(self, master):

        # create window               
        frame = Frame(master)
        frame.pack()

        # create canvas the size of incoming image
        self.pic = Canvas(frame, width=wd, height=ht)
        self.pic.pack()
        
        for y in range(ht):           
            for x in range(wd):
                # Convert integer pixel map to hex
                r = hex(min(2**16-1,max(0,pix_map[y][x][0])*2**(-bit_depth+16)))[2:6].zfill(4)
                g = hex(min(2**16-1,max(0,pix_map[y][x][1])*2**(-bit_depth+16)))[2:6].zfill(4)
                b = hex(min(2**16-1,max(0,pix_map[y][x][2])*2**(-bit_depth+16)))[2:6].zfill(4)
                #x1cf77dcxebe
                color_a = ['#' + r + g + b]
                color_a.append('#' + r + b + g)
                color_a.append('#' + g + b + r)
                color_a.append('#' + g + r + b)
                color_a.append('#' + b + g + r)
                color_a.append('#' + b + r + g)

                color = color_a[pix_ar]
                

                # Draw 1 pixel using RGB value from above
                self.pic.create_line(x,y,x+1,y,fill=color)
                    

# Methods
def setp(inp):
    # Set integer RGB pixel map to draw
    global pix_map,wd,ht
    pix_map = inp
    wd=len(pix_map[0])
    ht=len(pix_map)           
    

def showp(inp=None,pixarrange=0,crop=crop,max_res=MAXRES,bitsperchannel=bit_depth):
    # Draw RGB pixel map
    global pix_ar, bit_depth
    bit_depth = bitsperchannel

    pix_ar = min(max(0,pixarrange),5)
    # Set pixel map (Optional)
    if inp == None or len(inp) < 2: return -1
    setp(inp)

    # Resize pixel map to a reasonable size
    while (wd*ht) > max_res:
        print(str(wd)+'x'+str(ht)+' is too large. Downsizing...')
        setp(halfit(pix_map))
    print('Drawing '+str(wd)+'x'+str(ht)+' image...', end=' ')

    # Create new object and draw image
    root = Tk()
    test = Popper(root)
    root.mainloop()

    print('DONE\n')

    return 0

def crophalf(orig):
    # Crop and center (Full res, partial image)
    lin_l = len(orig)//4
    lin_r = lin_l*3
    pix_l = len(orig[0])//4
    pix_r = pix_l*3
    
    small = []
    for y in range(lin_l,lin_r):
        small = small + [orig[y][pix_l:pix_r]]
    return small
    
def halfit(orig):
    if crop: return crophalf(orig)
    
    # Shrink by half (Uses NO pixel averaging/sampling)
    small = []

    # Iterate through rows/pixels skipping every other one
    for y in range(len(orig)):
        line = []
        if y%2==0:
            for x in range(len(orig[y])):
                if x%2==0: line = line + [orig[y][x]]
            small = small + [line]
    return small


def import_file(filepath):
    frame = []
    with open(filepath, mode='rb') as f:
        for y in range(height):
            line = []
            if len(frame)%int(height/BARLEN + 0.5) == 0: print('.',end='')
            for x in range(width):
                pixel = []
                for c in range(CHANCOUNT):
                    pixel.append(int.from_bytes(f.read(bytelen), byteorder=ENDI))
                pixel = alter(pixel)
                line.append(pixel)
            frame.append(line)

    return frame


def main():
    print('Parsing input file:')
    print('0%'+' '*int(BARLEN/2 - 1.5)+'50%'+' '*int(BARLEN/2 - 1.5)+'100%')
    print(' .',end='')
    frame = import_file(filename)
    print()
    showp(inp=frame, bitsperchannel=bit_depth)


main()
