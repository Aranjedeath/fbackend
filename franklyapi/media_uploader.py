import mimetypes
import requests
import uuid
from boto.s3.connection import S3Connection
import os

import CustomExceptions
from configs import config
import image_processors

REGION_NAME = 'us-east-1'
BUCKET_NAME = 'franklyapp'
CONN = S3Connection(config.AWS_KEY, config.AWS_SECRET)

ALLOWED_VIDEO_TYPES = ['video/mp4']
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpeg', 'image/png', 'image/gif']

BASE_URL = "https://s3.amazonaws.com/{bucket_name}/".format(bucket_name=BUCKET_NAME)


def download_file(url):
    res = requests.get(url)
    path= '/tmp/downloads/%s'%(uuid.uuid4().hex)
    if res.status_code == 200:
        with open(path, 'wb') as f:
            f.write(res.content)
        return path

def save_file_from_request(file_to_save):
    import uuid
    path = '/tmp/%s'%(uuid.uuid4().hex)
    file_to_save.save(path)
    return path

def file_is_valid(file_to_check, file_type):
    if type(file_to_check) == type(''):
        mimes = mimetypes.guess_type(file_to_check)
    else:
        mimes = [file_to_check.mimetype]
    
    if file_type=='image':
        if set(ALLOWED_IMAGE_TYPES).intersection(set(mimes)):
            return True
    if file_type=='video':
        if set(ALLOWED_VIDEO_TYPES).intersection(set(mimes)):
            return True
    return False


def upload_to_s3(file_to_upload, key_name, public=True):
    bucket = CONN.get_bucket(BUCKET_NAME)
    key = bucket.new_key(key_name)
    file_to_upload.seek(0, 0)
    key.set_contents_from_file(file_to_upload)
    if public:
        key.make_public()
    return BASE_URL+key

def upload_user_image(user_id, image_type, image_url=None, image_file_path=None):
    random_string = uuid.uuid1().hex
    key_name = '{user_id}/photos/{random_string}.jpeg'.format(user_id=user_id, random_string=random_string)
    
    if image_url and file_is_valid(image_url, 'image'):
        image_file_path = download_file(image_url)
        

    if image_file_path and file_is_valid(image_file_path, 'image'):
        if image_type=='profile_picture':
            new_image = image_processors.sanitize_profile_pic(image_file_path)
            new_image_thumb = image_processors.get_profile_pic_thumb(new_image)
            with open(new_image_thumb) as f:
                thumb_key_name = '{user_id}/photos/{random_string}_thumb.jpeg'.format(user_id=user_id, random_string=random_string)
                upload_to_s3(f, thumb_key_name)
            with open(new_image) as f:
                url = upload_to_s3(f, key_name)
            os.remove(new_image)
            os.remove(new_image_thumb)
            os.remove(image_file_path)
            return url

        elif image_type=='cover':
            new_image = image_processors.sanitize_cover_pic(image_file_path)
            with open(new_image) as f:
                url = upload_to_s3(f, key_name)
            os.remove(new_image)
            os.remove(image_file_path)
            return url


    raise CustomExceptions.BadRequestException('Video/Image type is not valid.')


def upload_user_video(user_id, video_type, video_file, video_thumbnail_file):
    random_string = uuid.uuid1().hex
    video_key_name = '{user_id}/videos/{random_string}.mp4'.format(user_id=user_id, random_string=random_string)
    thumb_key_name = '{user_id}/videos/{random_string}_thump.jpeg'.format(user_id=user_id, random_string=random_string)
    
    if file_is_valid(video_file, 'video') and file_is_valid(video_thumbnail_file, 'image'):
        video_url = upload_to_s3(video_file, video_key_name)
        thumb_url = upload_to_s3(video_thumbnail_file, thumb_key_name)
        return video_url, thumb_url
    raise CustomExceptions.BadRequestException('Video/Image type is not valid.')


