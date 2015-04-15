from PIL import Image
import uuid

def toDimensions(image_file, out_file, dim_x, dim_y, allowLow=True, return_file_object=False):
    im = Image.open(image_file)
    im_x = im.size[0]
    im_y = im.size[1]
    print 'im_x: %s' %im_x
    print 'im_y: %s' %im_y 
    flag = True
    if not allowLow:
        flag = (im_x >= dim_x) and (im_y >= dim_y)
    print 'flag: %s' %flag
    if flag:
        box = get_box(im_x=im_x, im_y=im_y, dim_x=dim_x, dim_y=dim_y)
        print 'box: ' + str(box)
        im = im.crop(box)
        im_x = im.size[0]
        im_y = im.size[1]
        print 'im_x: %s' %im_x
        print 'im_y: %s' %im_y 
        im = im.resize((dim_x,dim_y))
        im_x = im.size[0]
        im_y = im.size[1]
        print 'im_x: ' + im_x
        print 'im_y: ' + im_y 
        
        if return_file_object:
            from StringIO import StringIO
            out_file = StringIO()
            im.convert('RGB').save(out_file, "jpeg")
            out_file.seek(0)
        else:
            im.convert('RGB').save(out_file, "jpeg")
        return out_file
    else:
        raise Exception("Small Size")

def get_box(im_x, im_y, dim_x, dim_y):
    aspectRatioIn = im_x / float(im_y)
    aspectRatioOut = dim_x / float(dim_y)
    print 'ari: %s' %aspectRatioIn
    print 'aro: %s' %aspectRatioOut
    if(aspectRatioIn > aspectRatioOut):
        if(aspectRatioOut < 1):
            if(aspectRatioIn > 1):
                fin_x = im_x
                fin_y = im_x * aspectRatioOut
            else:
                fin_y = im_x/aspectRatioOut
                fin_x = im_x
        else:
            fin_y = im_y
            fin_x = im_y * aspectRatioOut
    else:
        if(aspectRatioOut < 1):
            if(aspectRatioIn > 1):
                fin_x = im_x
                fin_y = im_x * aspectRatioOut
            else:
                fin_y = im_x/aspectRatioOut
                fin_x = im_x
        else:
            fin_x = im_x
            fin_y = im_x * aspectRatioOut
    print 'fin_x: %s\nfin_y: %s' %(fin_x, fin_y)
    box = (int((im_x - fin_x)/2), int((im_y - fin_y)/2), int((im_x + fin_x)/2), int((im_y + fin_y)/2) )
    return box


def sanitize_profile_pic(image_file):
    path = '/tmp/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
    toDimensions(image_file, path, 240, 240)
    return path

def get_profile_pic_thumb(image_file):
    path = '/tmp/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
    toDimensions(image_file, path, 50, 50)
    return path

def sanitize_cover_pic(image_file):
    path = '/tmp/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
    toDimensions(image_file, path, 320, 560)
    return path

def resize_video_thumb(image_file, height=262, width=262):
    path = ''
    return toDimensions(image_file, path, height, width, return_file_object=True)


