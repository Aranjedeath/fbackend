from PIL import Image
import os
from utils import download_file

def resolutions_locations_for_collage(x,y):
    return [ [((x,y),(0,0))] ,
        [((x/2,y),(0,0)),((x - x/2,y),(x/2,0))] ,
        [((x - x/3,y),(0,0)),((x/3,y/2),(x-x/3,0)),((x/3,y-(y/2)),(x-x/3,y/2))],
        [((x - x/4,y),(0,0)),((x/4,y-(2*y/3)),(x-x/4,0)),((x/4,y/3),(x-x/4,y-(2*y/3))),((x/4,y/3),(x-x/4,y-y/3))],
        [((x/2,y),(0,0)),((x - (x/2 + x/4),y),(x/2+x/4,0)),((x/4,y-(2*y/3)),(x/2,0)),((x/4,y/3),(x/2,y-(2*y/3))),((x/4,y/3),(x/2,y-y/3))],
        [((x - x/3,y-y/3),(0,0)),((x-x/2,y/3),(x/2,y-y/3)),((x/3,y-(2*y/3)),(x-x/3,0)),((x/3,y/3),(x-x/3,y-(2*y/3))),((x/2-x/4,y/3),(x/4,y-y/3)),((x/4,y/3),(0,y-y/3))],
        [((x-x/2,y-y/3),(0,0)),((x/4,y),(x-x/4,0)),((x/2-x/4,y-(2*y/3)),(x-x/2,0)),((x/2-x/4,y/3),(x-x/2,y-(2*y/3))),((x/2-x/4,y/3),(x-x/2,y-y/3)),((x-(x/2+x/4),y/3),(x/4,y-y/3)),((x/4,y/3),(0,y-y/3))],
        [((x-x/2,y-y/3),(0,0)),((x/4,y-y/2),(x-x/4,0)),((x/4,y/2),(x-x/4,y-y/2)),((x/2-x/4,y-(2*y/3)),(x-x/2,0)),((x/2-x/4,y/3),(x-x/2,y-(2*y/3))),((x/2-x/4,y/3),(x-x/2,y-y/3)),((x-(x/2+x/4),y/3),(x/4,y-y/3)),((x/4,y/3),(0,y-y/3))],
    ]

def resolve_image(canvas,image,size_loc):
    size_x,size_y,loc_x,loc_y = size_loc[0][0],size_loc[0][1],size_loc[1][0],size_loc[1][1]
    if (size_x / float(size_y) < 0.5):
        image = image.resize((size_y,size_y))
        image = image.crop((size_y-size_x/2,0,size_y+size_x/2, size_y))
    image = image.resize((size_x,size_y))
    canvas.paste(image,(loc_x,loc_y,loc_x+size_x,loc_y+size_y))
    return canvas

def toCollage(images, out_file = True, collage_x = 640, collage_y = 490):
    im = []
    for imin in images:
        im.append(Image.open(imin))
    size_locs = resolutions_locations_for_collage(collage_x,collage_y)[len(im)-1]
    canvas = Image.new("RGB",(collage_x,collage_y))
    i = 0
    while(i<len(im)):
        canvas = resolve_image(canvas,im[i],size_locs[i])
        i += 1
    overlay = Image.new('RGB',(collage_x,collage_y),(30, 30, 30))
    mask = Image.new('RGBA',(collage_x,collage_y),(0,0,0,60))
    canvas = Image.composite(canvas,overlay,mask).convert('RGB')
    canvas.show()
    canvas.save(out_file,"jpeg")


def make_collage(image_urls):
    import uuid
    images = []
    for url in image_urls:
        image_path = download_file(url)
        if image_path:
            images.append(image_path)
    path = '/tmp/collage/{random.string}.jpeg'.format(random_string=uuid.uuid1().hex)
    toCollage(images, out_file = path, collage_x = 640, collage_y = 490)
    [os.remove(image_path) for image_path in images]
    return path

