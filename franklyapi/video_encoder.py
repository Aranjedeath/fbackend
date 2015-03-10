import subprocess
import uuid
import traceback
import os
import shutil
import promo_video_intro
import video_db
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
                                        'command' : 'ffmpeg -ss 0 -i "{input_file}" -vframes 1 {transpose_command2} -t 1 -f image2 {output_file}',
                                        'file_prefix' : '_thumb',
                                        'file_extension' : 'jpeg'
                                },
                                'opt':{
                                        'command' : 'avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="480:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 636k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 24k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="480:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 636k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 24k {output_file}',
                                        'file_prefix': '_opt',
                                        'file_extension': 'mp4'
                                    },
                                'medium':{
                                        'command' : 'avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 256k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 24k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 25 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 256k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 24k {output_file}',
                                        'file_prefix': '_medium',
                                        'file_extension': 'mp4'
                                },
                                'low':{
                                        'command' : 'avconv -y -i "{input_file}" -r 16 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 125k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 24k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 16 -vf {transpose_command}scale="320:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 125k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 24k {output_file}',
                                        'file_prefix': '_low',
                                        'file_extension': 'mp4'
                                },
                                'ultralow':{
                                        'command' : 'avconv -y -i "{input_file}" -r 10 -vf {transpose_command}scale="240:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 25k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 24k -f mp4 /dev/null && avconv -y -i "{input_file}" -r 10 -vf {transpose_command}scale="240:trunc(ow/a/2)*2" -strict experimental -preset slow -b:v 25k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 24k {output_file}',
                                        'file_prefix': '_ultralow',
                                        'file_extension': 'mp4'
                                }
                        }



def check_make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


TEMP_DIR = '/tmp/downloads'
check_make_dir(TEMP_DIR)



def get_key_name_from_url(url):
    domain = 's3.amazonaws.com/{bucket_name}/'.format(bucket_name=media_uploader.BUCKET_NAME)
    old_domain = 's3.amazonaws.com/{bucket_name}/'.format(bucket_name=media_uploader.OLD_BUCKET_NAME)
    if domain in url:
        return url.split(domain)[1]
    elif old_domain in url:
        return url.split(old_domain)[1]
    
    raise Exception("Invalid Url")
    

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
    return path

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

def make_thumbnail(file_path):
    profile = VIDEO_ENCODING_PROFILES['thumbnail']

    temp_file_path = os.path.join(TEMP_DIR, uuid.uuid1().hex+'.'+profile['file_extension'])

    print_output("Making thumbnail")
    transpose_command = get_transpose_command(file_path)
    transpose_command2 = '-vf '+transpose_command[:-1] if transpose_command != '' else ''

    command = profile['command'].format(input_file=file_path,
                                        transpose_command2=transpose_command2,
                                        output_file=temp_file_path)
    print_output('COMMAND: '+command)
    subprocess.call(command,shell=True)
    return temp_file_path

def encode_video_to_profile(file_path, video_url, profile_name, username=None):
    current_dir = os.getcwd()
    
    print_output('BEGINNING: '+file_path+' '+video_url )
    
    transpose_command = get_transpose_command(file_path)
    
    profile = VIDEO_ENCODING_PROFILES[profile_name]
    temp_path = os.path.join(TEMP_DIR, uuid.uuid1().hex)
    check_make_dir(temp_path)

    result = {}
    try:
        if profile_name == 'thumbnail': 
            output_file_path = make_thumbnail(file_path)

        elif profile_name=='promo':
            video_data = video_db.get_video_data(video_url)
            
            answer_author_image_filepath = None if not video_data['answer_author_profile_picture'] else media_uploader.download_file(video_data['answer_author_profile_picture'])

            output_file_dir, output_file_name = make_promo_video(answer_author_username=video_data['answer_author_username'],
                                                            video_file_path=file_path,
                                                            transpose_command=transpose_command,
                                                            answer_author_name=video_data["answer_author_name"],
                                                            question=video_data['question_body'], 
                                                            question_author_username=video_data['question_author_name'],
                                                            answer_author_image_filepath=answer_author_image_filepath)
            output_file_path = os.path.join(output_file_dir, output_file_name)
            print 'PROMO VIDEO AT:', output_file_path
            make_psuedo_streamable(output_file_path)
        
        else:
            check_make_dir(temp_path)
            output_file_path = os.path.join(temp_path, uuid.uuid1().hex+'.'+profile['file_extension'])
            os.chdir(temp_path)
            command = profile['command'].format(input_file=file_path, output_file=output_file_path, transpose_command = transpose_command)
            print_output('COMMAND: '+command)
            subprocess.call(command, shell=True)
            
            print_output('MAKING STREAMABLE')
            make_psuedo_streamable(output_file_path)
        
        new_s3_key = get_key_name_for_profile(video_url, profile)
        print_output('NEW_KEY: '+new_s3_key)
            
        if os.path.exists(output_file_path):
            with open(output_file_path, 'rb') as f:
                result[profile_name] = media_uploader.upload_to_s3(f, new_s3_key)
            os.remove(output_file_path)

        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        
        print_output('RESULT: '+ str(result))
        os.chdir(current_dir)
    except Exception as e:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        os.chdir(current_dir)
        print traceback.format_exc(e)
    return result

def make_promo_video(answer_author_username, video_file_path, transpose_command='',
                    answer_author_name=None, question=None, question_author_username=None,
                    answer_author_image_filepath=None):
    
    
    
    profile = VIDEO_ENCODING_PROFILES['promo']
    temp_path = os.path.join(TEMP_DIR, uuid.uuid1().hex)
    output_file_name = uuid.uuid1().hex+'.'+profile['file_extension']
    
    promo_video_intro.makeFinalPromo(answer_author_username, video_file_path,
                                        transpose_command, temp_path, output_file_name,
                                        answer_author_name, question, question_author_username,
                                        answer_author_image_filepath
                                    )
    

    #promo_video_intro.makeFinalPromo(answer_author_name,video_file_path,question,question_author_username,answer_author_image_filepath,transpose_command,temp_path,output_file_name)
    #promo_video.make_promo(temp_path,file_path,output_file_name,'promo_content/','overlay_png1','overlay_png2','overlay_png3','bariol_bold-webfont_0.ttf',username,transpose_command)
    return (temp_path , output_file_name)

def print_output(statement):
    print ''
    print statement
    print '-----------------------'

