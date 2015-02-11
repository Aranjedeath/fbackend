from subprocess import check_output
from subprocess import call
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import shutil
import os
from promo_video import make_promo

class Q:
		x,y,w,h = 0,0,0,0
		font = 0
		text=""
		color = (220,92,80)
		ratio = float(1)
		path=""
		pass
def makeCelebPic(canvas,celebPicQ):
	img = Image.open(celebPicQ.path)
	bigsize = (img.size[0] * 3, img.size[1] * 3)
	# inbigsize = (int(img.size[0] * 2.8), int(img.size[1] * 2.8))
	mask = Image.open('d57og.png').convert('L')
	
	# circle = Image.new('L', bigsize, 0)
	# draw = ImageDraw.Draw(circle) 
	# draw.ellipse((0, 0) + bigsize, fill=255)
	# circle = circle.resize(img.size, Image.ANTIALIAS)
	
	# incircle = Image.new('L', bigsize, 255)
	# indraw = ImageDraw.Draw(incircle) 
	# indraw.ellipse((bigsize-inbigsize)/2 + inbigsize , fill=0)
	# incircle = incircle.resize(img.size, Image.ANTIALIAS)
	# circle.putalpha(incircle)
	
	img = img.resize((celebPicQ.w,celebPicQ.w))
	mask = mask.resize((celebPicQ.w,celebPicQ.w))

	canvas.paste(img,(celebPicQ.x,celebPicQ.y),mask)
	# canvas.paste(circle,(celebPicQ.x,celebPicQ.y))
	return canvas
def makeCelebName(canvas,celebNameQ):
	draw = ImageDraw.Draw(canvas)
	draw.text((celebNameQ.x,celebNameQ.y),celebNameQ.text,celebNameQ.color,celebNameQ.font)        
	return canvas
def makeWasAsked(canvas,wasAskedQ):
	draw = ImageDraw.Draw(canvas)
	draw.text((wasAskedQ.x,wasAskedQ.y),wasAskedQ.text,wasAskedQ.color,wasAskedQ.font)
	return canvas
def makeQuestion(canvas,questionQ,userQ,bgQ,questionWRatio,questionLineGapRatio,userYGapratio): # user update
	draw = ImageDraw.Draw(canvas)
	qtext_words = questionQ.text.split()
	i= 0
	line=0
	l= len(qtext_words)
	tlen=0;
	space_w = draw.textsize(" ",font=questionQ.font)[0]
	while(i<l):
		wlen = draw.textsize(qtext_words[i],font=questionQ.font)[0]
		if(tlen+wlen < bgQ.w*questionWRatio):
			draw.text(((questionQ.x+tlen+space_w),int(questionQ.y+questionQ.h*line*questionLineGapRatio)),qtext_words[i],questionQ.color,questionQ.font)
			tlen=tlen + wlen+space_w
			i=i+1
		else:
			tlen=0
			line= line+1
	userQ.y= int(questionQ.y+questionQ.h*(line+1)*questionLineGapRatio + bgQ.w*userYGapratio)
	return (canvas,userQ)
def makeUser(canvas,userQ):
	draw = ImageDraw.Draw(canvas)
	draw.text((userQ.x,userQ.y),userQ.text,userQ.color,userQ.font)        
	return canvas
def makeFaded(opacity,canvas,w,h,fadeimage_filename):
	fadeimage = Image.open(fadeimage_filename)
	fadeimage = fadeimage.resize((w,h))
	while(opacity>0):
		canvas.paste(fadeimage,(0,0),fadeimage)
		opacity=opacity-1
	return canvas
def saveImage(canvas,i,framesFolder):
	if(i<10):
		j = "img00"+str(i)
	elif(i<100):
		j = "img0"+str(i)
	else:
		j = "img"+str(i)
	#canvas.resize(bgQ.w/5,bgQ.h/5)
	canvas.save(framesFolder+"/"+j+".jpeg","jpeg")
def fadeInOriginalVideo():
	n=25
	i=0
	while(i<n):
		if(i<10):
			k = "img00"+str(i)
		elif(i<100):
			k= "img0"+str(i)
		else:
			k = "img"+str(i)
		call("ffmpeg -loglevel 0 -ss 2 -i "+in_file+" -t 1 "+transpose_command2+" -update 1 -f image2 tempfade/"+str(k)+".jpeg",shell=True)
		tempimg = Image.open("tempfade/"+str(k)+".jpeg")
		tempimg=makeFaded(n-i,tempimg,bgQ.w,bgQ.h,fadeimage_filename)
		tempimg.save("tempfade/"+str(k)+".jpeg")
		i=i+1
def makeFinalPromo(answer_author_username,video_file_path,transpose_command='',temp_path="temprg/vid3",output_file_name="a.mp4",answer_author_name=None,question=None,question_author_username=None,answer_author_image_filepath=None):
	
	path = temp_path

	end_promo_mpg_name = make_promo(path,video_file_path,'kiran.jpg','promo_content/','overlay_png1','overlay_png2','overlay_png3','bariol_bold-webfont_0.ttf',answer_author_username,transpose_command)
	
	mpg_with_front_and_end = end_promo_mpg_name # in case only end promo is to be converted


	final_file = output_file_name+'.mp4'
	in_file = video_file_path

	if (answer_author_name != None): # if no question then skip front part

		rdir = call('rm -rf final',shell=True)
		rdir = call('mkdir final',shell=True)
	#---------------------------declare Qs----------------
		celebPicQ = Q()
		celebNameQ = Q()
		wasAskedQ = Q()
		questionQ = Q()
		userQ = Q()
		bgQ = Q()
	#-------------------------- variables :) --------------------
		fontface = "bariol_bold-webfont_0.ttf"
		fontfaceRegular = "Bariol_Regular.otf"
		fontfaceItalics = "Bariol_Regular_Italic.otf"

		fadeimage_filename = "fade1.png"
		celebPicQ.path = answer_author_image_filepath
		framesFolder = "final"
		bgQ.file="snapshot.png"
		referencepic = "bg1.png"
		overlay_ratio=1

		fontScaleRatio = 1

		transpose_command2=''

		end_file = "end.mp4"

		
	#-------------------------------------------------------------
		snapshot = call("ffmpeg -loglevel 0 -ss 0.0 -i "+in_file+" -t 1 "+transpose_command2+" -update 1 -f image2 snapshot.png",shell=True)
		#----------
	#------------------------------ get font ratio ratio
		farjiIm = Image.open(referencepic)

		bgQ.im = Image.open(bgQ.file)

		overlay_ratio = farjiIm.size[0]/float(farjiIm.size[1])

		bgQ.w,bgQ.h = bgQ.im.size[0],bgQ.im.size[1]

		referenceHeight = float(farjiIm.size[1])


		bgQ.ratio = bgQ.w/float(bgQ.h)
		if(bgQ.ratio > overlay_ratio):
			ov_h = bgQ.h
			ov_w = bgQ.h * overlay_ratio
		else:
			ov_w = bgQ.w
			ov_h = bgQ.w / overlay_ratio
			ov_x,ov_y = int((bgQ.w - ov_w)/2) , int((bgQ.h - ov_h)/2)

		fontScaleRatio = ov_h/referenceHeight
	#--------------------- init

		celebNameQ.font = ImageFont.truetype(fontface,int(52*fontScaleRatio))
		celebNameQ.text=answer_author_name
		celebNameQ.color=(220,92,80)

		wasAskedQ.font = ImageFont.truetype(fontfaceRegular,int(52*fontScaleRatio))
		wasAskedQ.text = "was asked"
		wasAskedQ.color=(255,255,255)

		questionQ.font = ImageFont.truetype(fontfaceRegular,int(60*fontScaleRatio))
		questionQ.text = "\""+question+"\""
		questionQ.color=(200,200,200)

		userQ.font = ImageFont.truetype(fontfaceItalics,int(48*fontScaleRatio))
		userQ.text = "By " + question_author_username
		userQ.color=(80,80,80)
	#----------------frame numbers------------
		lastFrameNumber = 190
		stage1=5 # blank
		stage2=25 #fade in pic name
		stop2 =35 # hold
		stage3=45 #slide name
		stage4=65 # fade in wasasked
		stop4 =75 # hold ------------------------------------------------- > > > > done
		stage5=85 # slide up pic name asked
		stage6=120 # fade in question
		stop6 =180 # last hold
		stage7=190 # fade out
	#------------ratio positioning -----------------
		celebPicYRatio=0.30
		celebPicWidthRatio=0.40
		celebPicHeightRatio=0.40

		celebNameYGapRatio = 0.04

		wasAskedXGapRatio = 0.02
		wasAskedYGapRatio = 0.007 

		celebSlideRatio = 0.12

		questionYGapRatio = 0.08
		questionWRatio = 0.8
		questionLineGapRatio = 0.92
		userYGapratio= 0.02
		userXGapRightRatio = 0.08

	#fadeInOriginalVideo()
	#---------------- positions ------------------------------------
		celebPicQ.x = int(bgQ.w*(1-celebPicWidthRatio)/2)
		celebPicQ.y = int(bgQ.h*celebPicYRatio)
		celebPicQ.w = int(bgQ.w*celebPicWidthRatio)
		celebPicQ.h = int(bgQ.h*celebPicHeightRatio)

		celebNameQ.y = int((bgQ.h*(celebNameYGapRatio+celebPicYRatio))+(bgQ.w*celebPicHeightRatio))
		
		questionQ.x = int(bgQ.w*0.1)
		questionQ.y = int(bgQ.h*0.7)
	#--------------------------------loop ---------------
		i=0
		while(i < lastFrameNumber):
			canvas = Image.new("RGBA",(bgQ.w,bgQ.h),(0,0,0))
			if(i < stage1): # blank black
				draw = ImageDraw.Draw(canvas)
				celebNameQ.w = draw.textsize(celebNameQ.text,font=celebNameQ.font)[0]
				celebNameQ.h = draw.textsize(celebNameQ.text,font=celebNameQ.font)[1]

				celebNameQ.x = (bgQ.w - celebNameQ.w)/2
				wasAskedQ.w = draw.textsize(wasAskedQ.text,font=wasAskedQ.font)[0]
				wasAskedQ.h = draw.textsize(wasAskedQ.text,font=wasAskedQ.font)[1]
				wasAskedQ.x = (bgQ.w - wasAskedQ.w)/2
				#wasAskedYGapRatio = ((celebNameQ.h - wasAskedQ.h)/bgQ.h)/float(2)
				questionQ.h = draw.textsize(questionQ.text,font=questionQ.font)[1]
				userQ.w = draw.textsize(userQ.text,font=userQ.font)[0]
				userQ.x = bgQ.w - userQ.w- bgQ.w*userXGapRightRatio
				
			elif(i < stage2): # fade in pic and name
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				canvas = makeFaded(stage2-i-1,canvas,bgQ.w,bgQ.h,fadeimage_filename)
			elif(i < stop2): # fade in pic and name
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
			

			elif(i < stage3): # slide left
				slideint = int((i-stop2)*(((bgQ.w - celebNameQ.w)/2) - (bgQ.w - (celebNameQ.w+wasAskedQ.w+bgQ.w*wasAskedXGapRatio))/2)/(stage3-stop2))
				
				celebNameQ.x = ((bgQ.w - celebNameQ.w)/2) - slideint
				
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				

			elif(i < stage4):
				#slideint = int((i-stop2)*(((bgQ.w - celebNameQ.w)/2) - (bgQ.w - (celebNameQ.w+wasAskedQ.w+bgQ.w*wasAskedXGapRatio))/2)/(stage4-stop2))
				
				#celebNameQ.x = ((bgQ.w - celebNameQ.w)/2) - slideint
				wasAskedQ.x = int(((bgQ.w - (celebNameQ.w+wasAskedQ.w))/2) + celebNameQ.w + bgQ.w*wasAskedXGapRatio)
				wasAskedQ.y = int((bgQ.h*(celebNameYGapRatio+celebPicYRatio+wasAskedYGapRatio))+(bgQ.w*celebPicHeightRatio))
				canvas = makeWasAsked(canvas,wasAskedQ)
				canvas = makeFaded(stage4-i-1,canvas,bgQ.w,bgQ.h,fadeimage_filename)
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
			elif(i < stop4):
				canvas = makeWasAsked(canvas,wasAskedQ)
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				
			elif(i < stage5): # ----------------------------------------------------------------------------------slide up
				slideint = int((i-stop4)*(bgQ.h*(celebPicYRatio - celebSlideRatio))/(stage5-stop4))
				celebPicQ.y = int(bgQ.h*celebPicYRatio) - slideint
				celebNameQ.y = int((bgQ.h*(celebNameYGapRatio+celebPicYRatio))+(bgQ.w*celebPicHeightRatio)) - slideint
				wasAskedQ.y = int((bgQ.h*(celebNameYGapRatio+celebPicYRatio+wasAskedYGapRatio))+(bgQ.w*celebPicHeightRatio)) - slideint
				questionQ.y = wasAskedQ.y + wasAskedQ.h + bgQ.h* questionYGapRatio
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				canvas = makeWasAsked(canvas,wasAskedQ)
				
			elif(i < stage6): #----------------------------------- question fade in
				
				canvas,userQ = makeQuestion(canvas,questionQ,userQ,bgQ,questionWRatio,questionLineGapRatio,userYGapratio)
				canvas = makeUser(canvas,userQ)
				makeFaded(stage6-i,canvas,bgQ.w,bgQ.h,fadeimage_filename)
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				canvas = makeWasAsked(canvas,wasAskedQ)
				
			elif(i < stop6): #----------------------------------- hold question
				
				canvas,userQ = makeQuestion(canvas,questionQ,userQ,bgQ,questionWRatio,questionLineGapRatio,userYGapratio)
				canvas = makeUser(canvas,userQ)
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				canvas = makeWasAsked(canvas,wasAskedQ)
				
				
		   	else:# question fadeout
			
				canvas = makeCelebPic(canvas,celebPicQ)
				canvas = makeCelebName(canvas,celebNameQ)
				canvas = makeWasAsked(canvas,wasAskedQ)
				canvas,userQ = makeQuestion(canvas,questionQ,userQ,bgQ,questionWRatio,questionLineGapRatio,userYGapratio)
				canvas = makeUser(canvas,userQ)
				makeFaded(i-stop6,canvas,bgQ.w,bgQ.h,fadeimage_filename)
			
			saveImage(canvas,i,framesFolder)
			i=i+1
	#-------------------------- make video----
		frontvid = call("ffmpeg -loglevel 0 -i "+framesFolder+"/img%03d.jpeg -c:v libx264 "+end_file,shell=True)
		front_mpg = call("ffmpeg -loglevel 0 -i "+end_file+" -qscale:v 1 intermediate2.mpg",shell=True) #intro
		fvid = call("ffmpeg -loglevel 0 -i concat:\"intermediate2.mpg|"+end_promo_mpg_name+"\" -c copy final2.mpg",shell=True)
		mpg_with_front_and_end = 'final2.mpg'
	
	fcall = 'avconv -loglevel 0 -y -i "'+mpg_with_front_and_end+'" -r 25 -vf scale="320:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 256k -pass 1 -c:v libx264  -ar 22050 -ac 1 -ab 44k -f mp4 /dev/null && avconv -y -i "'+mpg_with_front_and_end+'" -r 25 -vf scale="320:trunc(ow/a/2)*2" -strict experimental -preset veryslow -b:v 256k -pass 2 -c:v libx264  -ar 22050 -ac 1 -ab 25k '+final_file
	finalvid = call(fcall,shell=True)
#----------------------------clean up -------------------------------------------		
	# rdir = call('rm -rf final',shell=True)
	# rinter = call('rm intermediate2.mpg final.mpg final2.mpg',shell=True)
	# rinter = call('rm snapshot.png end.mp4',shell=True)	
	shutil.copy(final_file,"../"+final_file)
	os.chdir('../../')
	rdir = call('rm -rf '+path,shell=True)

#makeFinalPromo(answer_author_username = 'kejriwal_Arvind',video_file_path = '',transpose_command='',temp_path="temprg/vid3",output_file_name="a.mp4",answer_author_name=None,question=None,question_author_username=None,answer_author_image_filepath=None)
#makeFinalPromo("Kejriwal Arvind","rawvid2.mp4","Hello bhaiya ji... sab badhiya chal rha h? hello bhaiya ji... sab badhiya chal rha h?","Rishabh Goel","photo.png",'','tempppp/dd','rg2')