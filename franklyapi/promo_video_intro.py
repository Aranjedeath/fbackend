from subprocess import check_output
from subprocess import call
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import shutil
import os
from promo_video import make_promo


class Q:
    x, y, w, h = 0, 0, 0, 0
    font = 0
    text = ""
    color = (220, 92, 80)
    ratio = float(1)
    path = ""

def make_celeb_pic(canvas, celeb_pic_q):
    if celeb_pic_q.path:

        img = Image.open(celeb_pic_q.path)

        mask = Image.open('d57og.png').convert('L')
        gola = Image.open('gola.png')

        img = img.resize((celeb_pic_q.w, celeb_pic_q.w))
        mask = mask.resize((celeb_pic_q.w, celeb_pic_q.w))
        gola = gola.resize((celeb_pic_q.w, celeb_pic_q.w))

        canvas.paste(img, (celeb_pic_q.x, celeb_pic_q.y), mask)
        canvas.paste(gola, (celeb_pic_q.x, celeb_pic_q.y), gola)

        # canvas.paste(circle,(celeb_pic_q.x,celeb_pic_q.y))
    return canvas
def make_celeb_name(canvas, celeb_name_q):
    draw = ImageDraw.Draw(canvas)
    draw.text((celeb_name_q.x, celeb_name_q.y),
              celeb_name_q.text, celeb_name_q.color, celeb_name_q.font)
    return canvas

def make_was_asked(canvas, was_asked_q):
    draw = ImageDraw.Draw(canvas)
    draw.text((was_asked_q.x, was_asked_q.y),
              was_asked_q.text, was_asked_q.color, was_asked_q.font)
    return canvas

def make_question(canvas, question_q, user_q, bg_q,
                  question_w_ratio, question_line_gap_ratio,
                  user_y_gap_ratio): # user update
    draw = ImageDraw.Draw(canvas)
    qtext_words = question_q.text.split()
    i = 0
    line = 0
    l = len(qtext_words)
    tlen = 0
    space_w = draw.textsize(" ", font=question_q.font)[0]
    while i < l:
        wlen = draw.textsize(qtext_words[i], font=question_q.font)[0]
        if tlen+wlen < bg_q.w*question_w_ratio:
            draw.text(((question_q.x+tlen+space_w),
                       int(question_q.y+question_q.h*line*question_line_gap_ratio)),
                      qtext_words[i], question_q.color, question_q.font)
            tlen = tlen + wlen+space_w
            i = i + 1
        else:
            tlen = 0
            line = line + 1
    user_q.y = int(question_q.y +
                   question_q.h * (line+1) * question_line_gap_ratio +
                   bg_q.w * user_y_gap_ratio)
    return (canvas, user_q)

def make_user(canvas, user_q):
    draw = ImageDraw.Draw(canvas)
    draw.text((user_q.x, user_q.y), user_q.text, user_q.color, user_q.font)
    return canvas

def make_faded(opacity, canvas, w, h, fadeimage_filename):
    fadeimage = Image.open(fadeimage_filename)
    fadeimage = fadeimage.resize((w, h))
    while opacity > 0:
        canvas.paste(fadeimage, (0, 0), fadeimage)
        opacity = opacity - 1
    return canvas

def save_image(canvas, i, frames_folder):
    if i < 10:
        j = "img00"+str(i)
    elif i < 100:
        j = "img0"+str(i)
    else:
        j = "img"+str(i)
    canvas.save(frames_folder+"/" + j + ".jpeg", "jpeg")

def makeFinalPromo(answer_author_username, video_file_path, transpose_command,
                   temp_path, output_file_name,
                   answer_author_name=None,
                   question=None,
                   question_author_username=None,
                   answer_author_image_filepath=None):

    # HACK : to go to main directory at server
    # TODO : do something with config
    if os.environ['LOGNAME'] == 'ubuntu':
        os.chdir('/home/ubuntu/franklysql/franklyapi')

    path = temp_path

    print 'creating last past fisrt :) . . .'
    end_promo_mpg_name = make_promo(path, video_file_path,
                                    answer_author_username,
                                    transpose_command)

    mpg_with_front_and_end = end_promo_mpg_name # in case only end promo is to be converted


    final_file = output_file_name+'.mp4'
    in_file = video_file_path

    if answer_author_name != None: # if no question then skip front part

        call('rm -rf final', shell=True)
        call('mkdir final', shell=True)
        #---------------------------declare Qs----------------
        celeb_pic_q = Q()
        celeb_name_q = Q()
        was_asked_q = Q()
        question_q = Q()
        user_q = Q()
        bg_q = Q()
    #-------------------------- variables :) --------------------
        fontface = "bariol_bold-webfont_0.ttf"
        font_face_regular = "Bariol_Regular.otf"
        font_face_italics = "Bariol_Regular_Italic.otf"

        fadeimage_filename = "fade1.png"

        celeb_pic_q.path = answer_author_image_filepath

        frames_folder = "final"
        bg_q.file = "snapshot.png"
        reference_pic = "bg1.png"
        overlay_ratio = 1

        font_scale_ratio = 1

        transpose_command2 = ''

        end_file = "end.mp4"

        #------------------------------------------------------------
        call("ffmpeg -loglevel 0 -ss 0.0 "
             "-i "+in_file+" -t 1 "+transpose_command2+
             " -update 1 -f image2 snapshot.png",
             shell=True)
        #----------
        #------------------------------ get font ratio ratio
        farji_im = Image.open(reference_pic)

        bg_q.im = Image.open(bg_q.file)

        overlay_ratio = farji_im.size[0]/float(farji_im.size[1])

        bg_q.w, bg_q.h = bg_q.im.size[0], bg_q.im.size[1]

        reference_height = float(farji_im.size[1])


        bg_q.ratio = bg_q.w/float(bg_q.h)
        if bg_q.ratio > overlay_ratio:
            ov_h = bg_q.h
            ov_w = bg_q.h * overlay_ratio
        else:
            ov_w = bg_q.w
            ov_h = bg_q.w / overlay_ratio
            ov_x, ov_y = int((bg_q.w - ov_w)/2), int((bg_q.h - ov_h)/2)

        font_scale_ratio = ov_h/reference_height

        #--------------------- init
        celeb_name_q.font = ImageFont.truetype(fontface, int(52*font_scale_ratio))
        celeb_name_q.text = answer_author_name
        celeb_name_q.color = (220, 92, 80)

        was_asked_q.font = ImageFont.truetype(font_face_regular, int(52*font_scale_ratio))
        was_asked_q.text = "was asked"
        was_asked_q.color = (255, 255, 255)

        question_q.font = ImageFont.truetype(font_face_regular, int(60*font_scale_ratio))
        question_q.text = "\""+question+"\""
        question_q.color = (200, 200, 200)

        user_q.font = ImageFont.truetype(font_face_italics, int(48*font_scale_ratio))
        user_q.text = "By " + question_author_username
        user_q.color = (80, 80, 80)

        #----------------frame numbers------------
        last_frame_number = 190
        stage1 = 5 # blank
        stage2 = 25 #fade in pic name
        stop2 = 35 # hold
        stage3 = 45 #slide name
        stage4 = 65 # fade in wasasked
        stop4 = 75 # hold ----------------------------------------> > > > done
        stage5 = 85 # slide up pic name asked
        stage6 = 120 # fade in question
        stop6 = 180 # last hold
        stage7 = 190 # fade out
    #------------ratio positioning -----------------
        celeb_pic_y_ratio = 0.30

        if celeb_pic_q.path:
            celeb_pic_width_ratio = 0.40
            celeb_pic_height_ratio = 0.40
        else:
            celeb_pic_width_ratio = 0.1
            celeb_pic_height_ratio = 0.1

        celeb_name_y_gap_ratio = 0.04

        was_asked_x_gap_ratio = 0.02
        was_asked_y_gap_ratio = 0.007

        celeb_slide_ratio = 0.12

        question_y_gap_ratio = 0.08
        question_w_ratio = 0.8
        question_line_gap_ratio = 0.92
        user_y_gap_ratio = 0.02
        user_x_gap_right_ratio = 0.08

        #fade_in_original_video()
        #---------------- positions --------------------------
        celeb_pic_q.x = int(bg_q.w*(1-celeb_pic_width_ratio)/2)
        celeb_pic_q.y = int(bg_q.h*celeb_pic_y_ratio)
        celeb_pic_q.w = int(bg_q.w*celeb_pic_width_ratio)
        celeb_pic_q.h = int(bg_q.h*celeb_pic_height_ratio)

        celeb_name_q.y = int((bg_q.h * (celeb_name_y_gap_ratio+celeb_pic_y_ratio))+
                             (bg_q.w * celeb_pic_height_ratio))

        question_q.x = int(bg_q.w*0.1)
        question_q.y = int(bg_q.h*0.7)
        #--------------------------------loop ---------------
        i = 0
        while i < last_frame_number:
            canvas = Image.new("RGBA", (bg_q.w, bg_q.h), (0, 0, 0))
            if i < stage1: # blank black
                draw = ImageDraw.Draw(canvas)
                celeb_name_q.w = draw.textsize(celeb_name_q.text, font=celeb_name_q.font)[0]
                celeb_name_q.h = draw.textsize(celeb_name_q.text, font=celeb_name_q.font)[1]

                celeb_name_q.x = (bg_q.w - celeb_name_q.w)/2
                was_asked_q.w = draw.textsize(was_asked_q.text, font=was_asked_q.font)[0]
                was_asked_q.h = draw.textsize(was_asked_q.text, font=was_asked_q.font)[1]
                was_asked_q.x = (bg_q.w - was_asked_q.w)/2
                #was_asked_y_gap_ratio = ((celeb_name_q.h - was_asked_q.h)/bg_q.h)/float(2)
                question_q.h = draw.textsize(question_q.text, font=question_q.font)[1]
                user_q.w = draw.textsize(user_q.text, font=user_q.font)[0]
                user_q.x = bg_q.w - user_q.w- bg_q.w*user_x_gap_right_ratio

            elif i < stage2: # fade in pic and name
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)
                canvas = make_faded(stage2-i-1, canvas, bg_q.w, bg_q.h, fadeimage_filename)
            elif i < stop2: # fade in pic and name
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)

            elif i < stage3: # slide left
                slideint = int((i-stop2) *
                               (((bg_q.w - celeb_name_q.w)/2) -
                                (bg_q.w - (celeb_name_q.w +
                                           was_asked_q.w +
                                           bg_q.w * was_asked_x_gap_ratio)
                                )/2)/(stage3-stop2))

                celeb_name_q.x = ((bg_q.w - celeb_name_q.w)/2) - slideint

                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)

            elif i < stage4:
                was_asked_q.x = int(((bg_q.w - (celeb_name_q.w+was_asked_q.w))/2) +
                                    celeb_name_q.w + bg_q.w*was_asked_x_gap_ratio)
                was_asked_q.y = int((bg_q.h * (celeb_name_y_gap_ratio +
                                               celeb_pic_y_ratio +
                                               was_asked_y_gap_ratio)) +
                                    (bg_q.w * celeb_pic_height_ratio))
                canvas = make_was_asked(canvas, was_asked_q)
                canvas = make_faded(stage4-i-1, canvas, bg_q.w, bg_q.h, fadeimage_filename)
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)
            elif i < stop4:
                canvas = make_was_asked(canvas, was_asked_q)
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)

            elif i < stage5: # ------------slide up
                slideint = int((i-stop4)*(bg_q.h*(celeb_pic_y_ratio -
                                                  celeb_slide_ratio))/
                               (stage5-stop4))
                celeb_pic_q.y = int(bg_q.h*celeb_pic_y_ratio) - slideint
                celeb_name_q.y = int((bg_q.h*(celeb_name_y_gap_ratio+
                                              celeb_pic_y_ratio))+
                                     (bg_q.w*celeb_pic_height_ratio)) - slideint
                was_asked_q.y = int((bg_q.h*(celeb_name_y_gap_ratio+
                                             celeb_pic_y_ratio+
                                             was_asked_y_gap_ratio))+
                                    (bg_q.w*celeb_pic_height_ratio)) - slideint
                question_q.y = (was_asked_q.y +
                                was_asked_q.h +
                                bg_q.h * question_y_gap_ratio)
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)
                canvas = make_was_asked(canvas, was_asked_q)

            elif i < stage6: #----------------------------------- question fade in

                canvas, user_q = make_question(canvas, question_q,
                                               user_q, bg_q,
                                               question_w_ratio,
                                               question_line_gap_ratio,
                                               user_y_gap_ratio)
                canvas = make_user(canvas, user_q)
                make_faded(stage6-i, canvas, bg_q.w, bg_q.h, fadeimage_filename)
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)
                canvas = make_was_asked(canvas, was_asked_q)

            elif i < stop6: #----------------------------------- hold question

                canvas, user_q = make_question(canvas, question_q,
                                               user_q, bg_q,
                                               question_w_ratio,
                                               question_line_gap_ratio,
                                               user_y_gap_ratio)
                canvas = make_user(canvas, user_q)
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)
                canvas = make_was_asked(canvas, was_asked_q)

            else:# question fadeout
                canvas = make_celeb_pic(canvas, celeb_pic_q)
                canvas = make_celeb_name(canvas, celeb_name_q)
                canvas = make_was_asked(canvas, was_asked_q)
                canvas, user_q = make_question(canvas, question_q,
                                               user_q, bg_q,
                                               question_w_ratio,
                                               question_line_gap_ratio,
                                               user_y_gap_ratio)
                canvas = make_user(canvas, user_q)
                make_faded(i-stop6, canvas,
                           bg_q.w, bg_q.h,
                           fadeimage_filename)

            save_image(canvas, i, frames_folder)
            i = i + 1
        #-------------------------- make video----
        print "making question video ..."
        call("ffmpeg -loglevel 0 -i "+frames_folder+
             "/img%03d.jpeg -c:v libx264 "+end_file,
             shell=True)
        call("ffmpeg -loglevel 0 -i "+end_file+
             " -qscale:v 1 intermediate2.mpg",
             shell=True) #intro
        call("ffmpeg -loglevel 0 -i intermediate2.mpg -i "+end_promo_mpg_name+
             " -vol 0 -map 0:0 -map 1:1 -shortest endfile.mpg",
             shell=True) #intro

        call("ffmpeg -loglevel 0 "+
             "-i concat:\"endfile.mpg|"+end_promo_mpg_name+
             "\" -c copy final2.mpg",
             shell=True)

        mpg_with_front_and_end = 'final2.mpg'
        print "question video successful"

    print "making final video..."
    fcall = ('avconv -loglevel 0 -y -i "'+mpg_with_front_and_end+
             '" -r 25 -vf scale="320:trunc(ow/a/2)*2" -strict experimental'
             ' -preset veryslow -b:v 256k -pass 1 -c:v libx264  -ar 22050 '
             '-ac 1 -ab 44k -f mp4 /dev/null && avconv -y -i "'+
             mpg_with_front_and_end+
             '" -r 25 -vf scale="320:trunc(ow/a/2)*2" -strict experimental'
             ' -preset veryslow -b:v 256k -pass 2 -c:v libx264  -ar 22050 '
             '-ac 1 -ab 25k '+final_file)
    call(fcall, shell=True)
    print "final video created."

#----------------------------clean up -------------------------------------
    shutil.copy(final_file, "../"+final_file)
    os.chdir('../../')
