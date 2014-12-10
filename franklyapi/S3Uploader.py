import boto.s3 as s3
import time
import hashlib
import os
from PIL import Image
import traceback
import requests
import math
thumb_size = (100,100)

class FileIntegrityError(Exception):
    pass


class BadRequestError(Exception):
    pass

class AmazonS3():

    def __init__(self):
        self.ConnectObjects = dict(
            [(region.name, region.connect()) for region in s3.regions()])
        self.Region = 'us-east-1'
        self.Bucket = 'franklyapp'
        self.conn = self.ConnectObjects[self.Region]

        self.FolderNames = {'picture': 'photos',
                            'video': 'videos',
                            'answer_video':'videos',
                            'rawvideo': 'rawvideo',
                            'appmedia': 'appmedia',
                            'audio': 'audio',
                            'meme': 'meme'}

        self.BaseURL = "https://s3.amazonaws.com/"


    def check_if_key_exists(self, url):
        key_name = url.strip(self.BaseURL+self.Bucket).strip('/')
        bucket = self.conn.get_bucket(self.Bucket)
        key = bucket.get_key(key_name)
        if not key:
            return False
        return True


    def get_file(self, url):
        # saves video and image to local to upload to s3
        print 'getting cover from facebook.'
        res = requests.get(url)
        name = url.split('/')[-1]
        if res.status_code == 200:
            with open(''.join(['/tmp/',name]), 'wb') as f:
                f.write(res.content)
            return ''.join(['/tmp/',name])

    def crop_cover(self, file_path, offset_y):
        print 'cropping cover'
        with open(file_path) as f:
            img = Image.open(f)
            ratio=1.62
            width,height = img.size
            crop_index = int(math.ceil(height*offset_y*0.01))
            if offset_y == 0:
                crop_index = height/2 
            top_height = crop_index
            bottom_height = height-crop_index
         
            new_height = int(min(top_height, bottom_height) * 2)
            new_width = int(width)
         
            if new_width/ratio <= new_height:
                print 'height is larger; trim height'
                aspect_height = int(math.ceil(new_width/1.62))
                height_diff = new_height - aspect_height
                print (0,int(crop_index-(new_height/2-math.ceil(height_diff/2))), new_width,int(crop_index+(new_height/2-math.ceil(height_diff/2))))
                cover = img.crop((0,int(crop_index-(new_height/2-math.ceil(height_diff/2))), new_width,int(crop_index+(new_height/2-math.ceil(height_diff/2)))))
            else:
                print 'width is larger; trim width;'
                aspect_width = math.ceil(new_height*1.62)
                width_diff = new_width - aspect_width
                # left top right bottom
                print (int(0+math.ceil(width_diff/2)), crop_index - new_height/2, int(aspect_width + math.ceil(width_diff/2)), crop_index+new_height/2)
                cover = img.crop((int(0+math.ceil(width_diff/2)), int(crop_index - new_height/2), int(aspect_width + math.ceil(width_diff/2)), int(crop_index+new_height/2)))

            name = str(int(time.time()))
            cover.save(''.join(['/tmp/',name]),'jpeg')
            return ''.join(['/tmp/',name])


    def make_thumbnail(self, file_path, md5):
        print 'making thumbnail'
        try:
            global thumb_size
            with open(file_path) as f:
                img = Image.open(f)
            width, height = img.size
            temp = min([width,height])
            if temp < 100:
                thumb_size = (temp,temp)
            if width > height:
               delta = width - height
               left = int(delta/2)
               upper = 0
               right = height + left
               lower = height
            else:
               delta = height - width
               left = 0
               upper = int(delta/2)
               right = width
               lower = width + upper
            img = img.crop((left, upper, right, lower))
            img.thumbnail(thumb_size)
            img.save("/tmp/thumbnail_%s"%(md5),'jpeg')
            return "/tmp/thumbnail_%s"%(md5)
        except Exception as e:
            print traceback.format_exc(e)

    def get_key_name(self, user_id):
        key_name = hashlib.md5('%s%s' % (user_id, time.time())).hexdigest()
        return key_name

    def get_s3_path(self, user_id, folder, key_name):
        s3_path = os.path.join(user_id, folder, key_name)
        return s3_path

    def upload_file(self, s3_path, u_file_path, checksum):
        conn = self.conn
        bucket = conn.get_bucket(self.Bucket)
        key = bucket.new_key(s3_path)
        with open(u_file_path) as u_file:
            key.set_contents_from_file(u_file)
        print s3_path
        print checksum,key.md5
        '''
        if key.md5 != checksum:
            bucket.delete_key(key)
            raise FileIntegrityError
        '''
        key.make_public()
        url = "http://s3.amazonaws.com/%s/%s" % (self.Bucket, s3_path)
        return url

    def upload(self, FilePath, FileType, Md5CheckSum, file_ext, UserId=None, video_thumb_path=None, thumbnail_ext=None):
        print 'making conn'
        conn = self.conn
        print 'conn eshtablished'

        if FileType in ['appmedia', 'meme']:
            KeyName = hashlib.md5('%s%s' % (FileType, time.time())).hexdigest()
            thumbKeyName = KeyName + '%s.%s' %('_thumb',file_ext) 
            KeyName = KeyName + '.%s' % file_ext
            full_key_name = os.path.join(self.FolderNames[FileType], KeyName)
            thumb_key_name = os.path.join(self.FolderNames[FileType], thumbKeyName)

        else:
            if not UserId:
                raise BadRequestError
            if FileType == 'answer_video' and not video_thumb_path:
                raise BadRequestError
                    
            KeyName = hashlib.md5('%s%s' % (UserId, time.time())).hexdigest()
            thumbKeyName = KeyName + '%s.%s' %('_thumb',file_ext)
            KeyName = KeyName + '.%s' % file_ext 
            full_key_name = os.path.join(
                UserId, self.FolderNames[FileType], KeyName)
            thumb_key_name = os.path.join(
                UserId, self.FolderNames['picture'], thumbKeyName)

        print 'making keyname'
        print full_key_name
        print 'getting bucket'
        bucket = conn.get_bucket(self.Bucket)
        print 'making new key in bucket...'
        key = bucket.new_key(full_key_name)
        thumb_key = bucket.new_key(thumb_key_name)

        try:
            print 'setting content...'
            with open(FilePath) as f:
                key.set_contents_from_file(f)
            if FileType == 'answer_video':
                thumb_key = bucket.new_key(full_key_name.strip('.'+file_ext) + '_thumb.'+thumbnail_ext)
                with open(video_thumb_path) as f:
                    with open('admin_error', 'a') as af:
                        af.write('\nurl: '+ full_key_name.strip('.'+file_ext) + '_thumb.'+thumbnail_ext +'\n')
                    thumb_key.set_contents_from_file(f)


            print key.md5, Md5CheckSum
            '''
            if key.md5 != Md5CheckSum:
                bucket.delete_key(key)
                raise FileIntegrityError
            '''

            url = "https://s3.amazonaws.com/%s/%s" % (self.Bucket, full_key_name)
            print url
            key.make_public()
            if FileType == 'picture':
                print 'here'
                path = self.make_thumbnail(FilePath, Md5CheckSum)
                if path:
                    with open(path) as f:
                        thumb_key.set_contents_from_file(f)
                    thumb_key.make_public()
                    os.remove(path)                
            return url

        except FileIntegrityError(), e:
            print e
            return None

    def delete(self, key_name):
        conn = self.conn
        bucket = conn.get_bucket(self.Bucket)
        bucket.delete_key(key_name)
        print 'done'


if __name__ == '__main__':
    # test
    uploader = AmazonS3()
    file_path = '/Users/tushar/Desktop/batman_symbol_863.jpeg'
    with open(file_path) as f:
        checksum = hashlib.md5(f.read()).hexdigest()
    media = uploader.upload(FilePath=file_path, FileType='appmedia',
                            Md5CheckSum=checksum, file_ext='jpg', UserId='12334342314')
    raw_input('Press enter to delete uploaded media.')
    key = media.split('qmemedia/')[1]
    uploader.delete(key)
