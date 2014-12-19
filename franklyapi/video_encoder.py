import subprocess
import uuid
import traceback
import os
import shutil
import promo_video

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
                                'promo':{
                                        'file_prefix' : '_promo',
                                        'file_extension' : 'mp4'
                                },
                                'thumbnail':{
                                        'command' : 'ffmpeg -loglevel 0 -ss 0 -i "{input_file}" {transpose_command2} -t 1 -update 1 -f image2 {output_file}',
                                        'file_prefix' : '_thumb',
                                        'file_extension' : 'jpg'
                                },
                                'opt':{
                                        'command' : 'avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="480:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 636k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 64k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="480:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 636k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 25k {output_file}',
                                        'file_prefix': '_opt',
                                        'file_extension': 'mp4'
                                    },
                                'medium':{
                                        'command' : 'avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 256k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 44k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 256k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 25k {output_file}',
                                        'file_prefix': '_medium',
                                        'file_extension': 'mp4'
                                },
                                'low':{
                                        'command' : 'avconv -y -i "{input_file}" -r 16 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 125k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 24k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 16 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 125k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 25k {output_file}',
                                        'file_prefix': '_low',
                                        'file_extension': 'mp4'
                                },
                                'ultralow':{
                                        'command' : 'avconv -y -i "{input_file}" -r 10 -vf {transpose_command}scale="240:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 25k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 20k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 10 -vf {transpose_command}scale="240:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 25k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 20k {output_file}',
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
    new_key = '{base_key}{prefix}.{extention}'.format(base_key=non_extension_key,
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
        transpose_command = 'transpose="2",'
    if get_rotation(file_path) == 90:
        transpose_command = 'transpose="1",'
    return transpose_command

def encode_video_to_profile(file_path, video_url, profile_name, username):
    cdir = os.getcwd()
    print_output('BEGINNING: '+file_path+' '+video_url )
    transpose_command = get_transpose_command(file_path)
    result = {}
    profile = VIDEO_ENCODING_PROFILES[profile_name]
    try:
        if(profile_name == 'thumb'):
            temp_path = '/tmp/{random_string}'.format(random_string=uuid.uuid1().hex)
            print_output("Making thumbnail")
            transpose_command2 = ''
            if(transpose_command != ''):
                transpose_command2 = '-vf '+transpose_command[:-1]
            command = profile['command'].format(input_file=file_path,transpose_command2=transpose_command2,output_file=temp_path+".jpg")
            print_output('COMMAND: '+command)
            subprocess.call(command,shell=True)
            output_file_path = temp_path + ".jpg"
        else:
            if profile_name=='promo':
                temp_path, output_file_name = make_promo_video(file_path,username,transpose_command)
                output_file_path = temp_path + '/' + output_file_name + ".mp4"
            else:
                temp_path = '/tmp/{random_string}'.format(random_string=uuid.uuid1().hex)
                output_file_path = temp_path + '/{random_string}.mp4'.format(random_string=uuid.uuid1().hex)
                os.mkdir(temp_path)
                os.chdir(temp_path)
                command = profile['command'].format(input_file=file_path, output_file=output_file_path, transpose_command = transpose_command)
                print_output('COMMAND: '+command)
                subprocess.call(command, shell=True)
            
            print_output('MAKING STREAMABLE')
            make_psuedo_streamable(output_file_path)
        
        new_s3_key = get_key_name_for_profile(video_url, profile)
        print_output('NEW_KEY: '+new_s3_key)
            
        with open(output_file_path, 'rb') as f:
            result[profile_name] = media_uploader.upload_to_s3(f, new_s3_key)
        os.remove(output_file_path)
        if(profile_name != 'thumbnail'):
            shutil.rmtree(temp_path)
        print_output('RESULT: '+ str(result))
        os.chdir(cdir)
    except Exception as e:
            print traceback.format_exc(e)
    return result

def make_promo_video(file_path,username,transpose_command):
    temp_path = '/tmp/{random_string}'.format(random_string=uuid.uuid1().hex)
    output_file_name = '{random_string}'.format(random_string=uuid.uuid1().hex)
    os.mkdir(temp_path)
    promo_video.make_promo(temp_path,file_path,output_file_name,'promo_content/','overlay_png1','overlay_png2','overlay_png3','bariol_bold-webfont_0.ttf',username,transpose_command)
    return (temp_path , output_file_name)

def print_output(statement):
    print ''
    print statement
    print '-----------------------'
