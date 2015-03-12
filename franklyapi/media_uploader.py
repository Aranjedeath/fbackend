import mimetypes
import requests
import uuid
from boto.s3.connection import S3Connection
import os

import CustomExceptions
from configs import config
import image_processors

BUCKET_NAME = config.CURRENT_BUCKET_NAME
OLD_BUCKET_NAME = config.OLD_BUCKET_NAME
CONN = S3Connection(config.AWS_KEY, config.AWS_SECRET)

ALLOWED_VIDEO_TYPES = ['video/mp4', 'application/octet-stream']
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpeg', 'image/png', 'image/gif', 'application/octet-stream']

BASE_URL = "https://s3.amazonaws.com/{bucket_name}/".format(bucket_name=BUCKET_NAME)

temp_path = '/tmp/downloads'
if not os.path.exists(temp_path):
        os.mkdir(temp_path)


def download_file(url):
    res = requests.get(url)
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    path= '%s/%s'%(temp_path, uuid.uuid4().hex)
    if res.status_code == 200:
        with open(path, 'wb') as f:
            f.write(res.content)
        return path

def save_file_from_request(file_to_save):
    import uuid
    path = '%s/%s'%(temp_path, uuid.uuid4().hex)
    file_to_save.save(path)
    return path

def file_is_valid(file_to_check, file_type):
    return True
    if type(file_to_check) in [type(str()), type(unicode())] :
        mimes = [item.lower() for item in mimetypes.guess_type(file_to_check) if item]
    else:
        mimes = [file_to_check.mimetype.lower()]

    print mimes
    
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
    return BASE_URL+key_name

def upload_user_image(user_id, image_type, image_url=None, image_file_path=None):
    random_string = uuid.uuid1().hex
    key_name = '{user_id}/photos/{random_string}.jpeg'.format(user_id=user_id, random_string=random_string)
    
    final_image_path = None
    
    if image_url and file_is_valid(image_url, 'image'):
        final_image_path = download_file(image_url)

    elif image_file_path and file_is_valid(image_file_path, 'image'):
        final_image_path = image_file_path
        

    if final_image_path:
        if image_type=='profile_picture':
            print image_type
            new_image = image_processors.sanitize_profile_pic(final_image_path)
            new_image_thumb = image_processors.get_profile_pic_thumb(new_image)
            with open(new_image_thumb) as f:
                thumb_key_name = '{user_id}/photos/{random_string}_thumb.jpeg'.format(user_id=user_id, random_string=random_string)
                upload_to_s3(f, thumb_key_name)
            with open(new_image) as f:
                url = upload_to_s3(f, key_name)
            os.remove(new_image)
            os.remove(new_image_thumb)
            os.remove(final_image_path)
            return url

        elif image_type=='cover':
            print image_type
            new_image = image_processors.sanitize_cover_pic(final_image_path)
            with open(new_image) as f:
                url = upload_to_s3(f, key_name)
            os.remove(new_image)
            os.remove(final_image_path)
            return url


    raise CustomExceptions.BadRequestException('Video/Image type is not valid.')


def upload_user_video(user_id, video_type, video_file):
    from video_encoder import make_thumbnail, make_psuedo_streamable

    random_string = uuid.uuid1().hex
    video_file_path = os.path.join(temp_path, random_string+".mp4")
    video_file_new = open(video_file_path, "w")
    video_file_new.write(video_file.read())
    video_file_new.close()
    
    video_thumbnail_path = make_thumbnail(video_file_path)
    video_thumbnail_file = open(video_thumbnail_path, "rb")
    try:
        video_file_path = make_psuedo_streamable(video_file_path)
    except:
        pass

    video_file = open(video_file_path, 'rb')

    video_key_name = '{user_id}/videos/{random_string}.mp4'.format(user_id=user_id, random_string=random_string)
    thumb_key_name = '{user_id}/videos/{random_string}_thumb.jpeg'.format(user_id=user_id, random_string=random_string)
    
    
    if file_is_valid(video_file, 'video') and file_is_valid(video_thumbnail_file, 'image'):
        video_url = upload_to_s3(video_file, video_key_name)
        thumb_url = upload_to_s3(video_thumbnail_file, thumb_key_name)
        os.remove(video_thumbnail_path)
        os.remove(video_file_path)
        return video_url, thumb_url
    raise CustomExceptions.BadRequestException('Video/Image type is not valid.')


