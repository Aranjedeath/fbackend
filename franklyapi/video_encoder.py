import subprocess
import uuid
import traceback
import os

from configs import config
import media_uploader

from raygun4py import raygunprovider

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)
#key is network speed
# 45 kbps - 150kbps   => ultralow
# 150 kbps - 300kbps  => low
# 300 kbps - 700kbps  => med
# 700 kbps - 1500kbps => opt

VIDEO_ENCODING_PROFILES = {
                                'opt':{
                                        'command' : 'avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-1 -preset veryslow -b:v 636k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 64k -f mp4 /dev/null && avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-2 -preset veryslow -b:v 636k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 64k {output_file}',
                                        'file_prefix': '_opt',
                                        'file_extension': 'mp4'
                                    },
                                'med':{
                                        'command' : 'avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-1 -preset veryslow -b:v 256k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 44k -f mp4 /dev/null && avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-2 -preset veryslow -b:v 256k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 44k {output_file}',
                                        'file_prefix': '_med',
                                        'file_extension': 'mp4'
                                },
                                'low':{
                                        'command' : 'avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-1 -preset veryslow -b:v 125k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 24k -f mp4 /dev/null && avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-2 -preset veryslow -b:v 125k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 25k {output_file}',
                                        'file_prefix': '_low',
                                        'file_extension': 'mp4'
                                },
                                'ultralow':{
                                        'command' : 'avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-1 -preset veryslow -b:v 25k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 20k -f mp4 /dev/null && avconv -y -i {input_file} -r 25 {transpose_command} -vf scale=480:-2 -preset veryslow -b:v 25k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 20k {output_file}',
                                        'file_prefix': '_ultralow',
                                        'file_extension': 'mp4'
                                }
                        }

def get_key_name_from_url(url):
    domain = 's3.amazonaws.com/{bucket_name}/'.format(bucket_name=media_uploader.BUCKET_NAME)
    if domain not in url:
        raise Exception("Invalid Url")
    return url.split(domain)[1]

def get_key_name_for_profile(url, profile):
    original_key = get_key_name_from_url(url)
    non_extension_key = original_key.split('.')[0]
    new_key = '{base_key}_{prefix}.{extention}'.format(base_key=non_extension_key,
                                                        prefix=profile['file_prefix'],
                                                        extention=profile['file_extension']
                                                        )
    return new_key


def make_psuedo_streamable(path):
    command = 'qtfaststart {path}'.format(path=path)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    print process.stdout.read()

def get_rotation(file_path):
    command = "mediainfo '--Inform=Video;%Rotation%' {path}".format(path=file_path)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    rotation = process.stdout.read().strip()
    if rotation:
        return int(float(rotation))
    return 0

def get_transpose_command(file_path):
    transpose_command = ''
    if get_rotation(file_path) == 270:
        transpose_command = '-vf "transpose=2"'
    if get_rotation(file_path) == 90:
        transpose_command = '-vf "transpose=1"'
    return transpose_command


def encode_video_to_profile(file_path, video_url, profile_name):
    transpose_command = get_transpose_command(file_path)
    result = {}
    profile = VIDEO_ENCODING_PROFILES[profile_name]
    try:
        output_file_path = '/tmp/{random_string}.mp4'.format(random_string=uuid.uuid1().hex)
        command = profile['command'].format(input_file=file_path, output_file=output_file_path, transpose_command = transpose_command)
        subprocess.call(command, shell=True)
        print 'converting video to with command:', profile['command']
        make_psuedo_streamable(output_file_path)
        new_s3_key = get_key_name_for_profile(video_url, profile)
        with open(output_file_path, 'rb') as f:
                result[profile_name] = media_uploader.upload_to_s3(f, new_s3_key)
        os.remove(output_file_path)
    except Exception as e:
            print traceback.format_exc(e)
    return result



