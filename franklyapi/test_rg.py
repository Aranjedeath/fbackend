from video_encoder import make_promo_video

video_data = {
    'video_type':"profile_video",
    'answer_author_username': "Kejriwal_arvind",
    'answer_author_name': "Arvind Kejriwal",
    'question_author_name': 'rishabh',
    'question_body': 'How are you?',
    'answer_author_profile_picture': None#'/home/satyender/Downloads/4c3da9a68f4c11e48b3322000b4c02a7.jpeg'

    }



# answer_author_name= "Amitabh Bacchan"
# answer_author_username= "BacchanAmitabh"
# video_file_path = "'/home/satyender/rg/kiran.mp4'"
# question = "Sir, what are your views about Abhishek Bacchan's acting? "
# question_author_username = "Rishabh Goel"
# answer_author_image_filepath="/home/satyender/downloads/4c3da9a68f4c11e48b3322000b4c02a7.jpeg"
transpose_command = ''

answer_author_name= video_data["answer_author_name"]
answer_author_username= video_data['answer_author_username']
video_file_path = "'/home/satyender/rg/kiran.mp4'"
question = video_data['question_body']
question_author_username = video_data['question_author_name']
answer_author_image_filepath=video_data['answer_author_profile_picture']

a,b = make_promo_video(answer_author_username,video_file_path,transpose_command,answer_author_name,question,question_author_username,answer_author_image_filepath)

# a,b = make_promo_video(answer_author_username,video_file_path,transpose_command,answer_author_name,question,question_author_username,answer_author_image_filepath)
#a,b = make_promo_video(answer_author_username,video_file_path)

print a
print b

