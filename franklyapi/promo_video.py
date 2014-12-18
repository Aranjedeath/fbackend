## for z in * ; do q=$(echo $z | sed 's/end_vid_0\+//'); mv $z $q; done; mv .png 0.png
from subprocess import check_output
from subprocess import call
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import shutil
import os

def overlay(bg_file,ov_bg_file,ov_static_file,ov_black_line_file,ov_black_line_ratio,out_dir,out_file,overlay_ratio=9/float(16),stext=None,stext_y_ratio=None,stext_color=None,text=None,text_y_ratio=None,text_color=None,stext_font="bariol_bold-webfont_0.ttf",text_font="bariol_bold-webfont_0.ttf",sfont_size=34,font_size=56):
    bg_im = Image.open(bg_file)
    bg_w,bg_h = bg_im.size[0],bg_im.size[1]
    background_ratio = bg_w/float(bg_h)
    if(background_ratio > overlay_ratio):
        ov_h = bg_h
        ov_w = bg_h * overlay_ratio
    else:
        ov_w = bg_w
        ov_h = bg_w * overlay_ratio
    ov_x,ov_y = int((bg_w - ov_w)/2) , int((bg_h - ov_h)/2)
    canvas = Image.new("RGBA",(bg_w,bg_h))
    #bg_im = bg_im.resize((bg_x,bg_y))
    canvas.paste(bg_im,(0,0))
    ov1_im = Image.open(ov_bg_file)
    ov1_im = ov1_im.resize((bg_w,bg_h))
    canvas.paste(ov1_im,(0,0),ov1_im)
    ov2_im = Image.open(ov_black_line_file)
    ov2_im = ov2_im.resize((bg_w,int(ov_h*ov2_im.size[1]/float(1280))))
    canvas.paste(ov2_im,(0,int(ov_y+ov_h*ov_black_line_ratio)),ov2_im)
    ov3_im = Image.open(ov_static_file)
    ov3_im = ov3_im.resize((int(ov_w),int(ov_h)))
    canvas.paste(ov3_im,(ov_x,ov_y),ov3_im)
    if(text and text_font and text_color):
        sfont = ImageFont.truetype(stext_font,int(sfont_size*ov_h/float(1280)))
        font = ImageFont.truetype(text_font,int(font_size*ov_h/float(1280)))
        draw = ImageDraw.Draw(canvas)
        stext_w = draw.textsize(stext,font=sfont)[0]
        text_w = draw.textsize(text,font=font)[0]
        stext_x = (bg_w - (stext_w + text_w))/2
        text_x = stext_x + stext_w
        draw.text((stext_x,int(ov_h*stext_y_ratio)),stext,stext_color,sfont)
        draw.text((text_x,int(ov_h*text_y_ratio)),text,text_color,font)
    #canvas.save(out_dir+"/"+out_file+".png","PNG")
    canvas.save(out_dir+"/"+out_file+".jpeg","jpeg")

def promo_video(in_file = "kiran.mp4",out_file = "kiran.jpg",end_file = "kiran_end.mp4",final_file = "kiran_final.mp4",stext = "www.frankly.me",stext_y_ratio = 1118/float(1280),text = "/kiranbedi",text_y_ratio = 1100/float(1280),color = (220,92,80),scolor = (255,255,255),n = 85,n2 = 54,infold1 = 'overlay_png1',infold2 = 'overlay_png2',infold3 = 'overlay_png3',final_fold = 'final',overlay_ratio=9/float(16)):
    in_width = int(check_output("ffprobe -v error -show_format -show_streams "+in_file+" | grep \"width\" | awk -F= '/width/{print $NF}'",shell=True))
    in_height = int(check_output("ffprobe -v error -show_format -show_streams "+in_file+" | grep \"height\" | awk -F= '/height/{print $NF}'",shell=True))
    in_duration = float(check_output("ffprobe -v error -show_format "+in_file+" | grep \"duration\" | awk -F= '/duration/{print $NF}'",shell=True))
    conv = call("ffmpeg -loglevel 0 -ss "+str(int(in_duration))+" -i "+in_file+" -t 1 -s "+str(in_width)+"x"+str(in_height)+" "+out_file,shell=True)
    rdir = call('rm -rf '+final_fold,shell=True)
    mdir = call('mkdir '+final_fold,shell=True)
    i = 0
    while i < n:
        if not (i > n2):
            if(i<10):
                j = "img00"+str(i)
            else:
                j = "img0"+str(i)
            overlay(out_file,infold1+"/"+str(i)+".png",infold2+"/"+str(i)+".png",infold3+"/"+str(i)+".png",1100/float(1280),final_fold,j,overlay_ratio)
        else:
            if(i<100):
                j = "img0"+str(i)
            else:
                j = "img"+str(i)
            overlay(out_file,infold1+"/"+str(i)+".png",infold2+"/"+str(i)+".png",infold3+"/"+str(i)+".png",1100/float(1280),final_fold,j,overlay_ratio,stext,stext_y_ratio,scolor,text,text_y_ratio,color)
        i = i + 1
    newvid = call("ffmpeg -loglevel 0 -i "+final_fold+"/img%03d.jpeg -c:v libx264 "+end_file,shell=True)
    i1_vid = call("ffmpeg -loglevel 0 -i "+in_file+" -qscale:v 1 intermediate1.mpg",shell=True)
    i2_vid = call("ffmpeg -loglevel 0 -i "+end_file+" -qscale:v 1 intermediate2.mpg",shell=True)
    fvid = call("ffmpeg -loglevel 0 -i concat:\"intermediate1.mpg|intermediate2.mpg\" -c copy final.mpg",shell=True)
    print final_file
    finalvid = call("ffmpeg -loglevel 0 -i final.mpg -qscale:v 2 "+final_file,shell=True)
    rimage = call('rm '+out_file,shell=True)
    rinter = call('rm intermediate1.mpg intermediate2.mpg final.mpg',shell=True)
    rdir = call('rm -rf '+final_fold,shell=True)
    rend = call('rm '+end_file,shell=True)
    pass

def make_promo(path,in_file,out_file_name,container,infold1,infold2,infold3,font_file,username):
    shutil.copytree(container+infold1,path+"/"+infold1)
    shutil.copytree(container+infold2,path+"/"+infold2)
    shutil.copytree(container+infold3,path+"/"+infold3)
    shutil.copy(container+font_file,path+"/"+font_file)
    os.chdir(path)
    promo_video(in_file,text=('/'+username),out_file='temp.jpg',end_file='end.mp4',final_file=(out_file_name+'.mp4'),infold1=infold1,infold3=infold3,infold2=infold2)