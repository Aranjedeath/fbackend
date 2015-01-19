from resources import *
from app import api, app


api.add_resource(RegisterEmail, '/reg/email')
api.add_resource(LoginSocial, '/login/social/<login_type>')
api.add_resource(LoginEmail, '/login/email')

api.add_resource(UserProfile, '/user/profile/<user_id>')
api.add_resource(UserUpdateForm, '/user/update_profile/<user_id>')
api.add_resource(UserProfileUsername, '/user/profile/username/<username>')

api.add_resource(UserFollow, '/user/follow')
api.add_resource(UserFollowers, '/user/followers/<user_id>')

api.add_resource(UserUnfollow, '/user/unfollow')
api.add_resource(UserBlock, '/user/block')
api.add_resource(UserUnblock, '/user/unblock')
api.add_resource(UserBlockList, '/user/blocklist')

api.add_resource(ChangeUsername, '/user/change_username')
api.add_resource(ChangePassword, '/user/change_password')
api.add_resource(UserExists, '/user/exists')
api.add_resource(UserSettings, '/user/settings')

api.add_resource(UserLocation, '/user/location')

api.add_resource(UpdatePushId, '/update/push_id')
api.add_resource(UserUpdateToken, '/user/update_token')


api.add_resource(QuestionAsk, '/question/ask')
api.add_resource(QuestionList, '/question/list/multitype')
api.add_resource(QuestionListPublic, '/question/list/public/<user_id>')

api.add_resource(QuestionUpvote, '/question/upvote/<question_id>')
api.add_resource(QuestionDownvote, '/question/downvote/<question_id>')
api.add_resource(QuestionIgnore, '/question/ignore')


api.add_resource(PostAdd, '/post/media/add', '/post/add')

api.add_resource(PostLike, '/post/like')
api.add_resource(PostUnLike, '/post/unlike')
api.add_resource(PostDelete, '/post/delete')
api.add_resource(PostReshare, '/post/reshare')


api.add_resource(PostView, '/post/view/<post_id>', '/post/view/p/<post_id>')

api.add_resource(CommentAdd, '/comment/add')
api.add_resource(CommentDelete, '/comment/delete')
api.add_resource(CommentList, '/comment/list')

api.add_resource(TimelineUser, '/timeline/user/<user_id>/multitype')
api.add_resource(TimelineHome, '/timeline/home/multitype', '/timeline/homenew',)
api.add_resource(DiscoverPost, '/discover/post/multitype')

api.add_resource(ForgotPassword, '/forgotpassword')
api.add_resource(CheckForgotPasswordToken, '/forgotpassword/check_token')
api.add_resource(ResetPassword, '/forgotpassword/reset/<token>')


api.add_resource(Notifications, '/getnotifications')
api.add_resource(NotificationCount, '/notifications/count')

api.add_resource(InstallRef, '/utils/install_ref')
api.add_resource(BadUsernames, '/utils/badusernames')

api.add_resource(Logout, '/logout')
api.add_resource(VideoView, '/videoview')

api.add_resource(QuestionImageCreator, '/question/bg_image/<question_id>')

api.add_resource(InterviewVideoResource, '/interview/medialist')
api.add_resource(WebHiringForm, '/web/hiring_form')
api.add_resource(Search, '/search')
api.add_resource(ContactUs, '/contactus')




#api.add_resource(PostLikeUsers, '/post/like/users')

'''


api.add_resource(ReportAbuse, '/reportabuse')

api.add_resource(AddEmail, '/addemail/<token>/<email_type>')
api.add_resource(ContactUs, '/contact_us')
api.add_resource(FeedBack, '/feedback')

api.add_resource(Unsubscribe, '/unsubscribe')
api.add_resource(Subscribe, '/subscribe')


api.add_resource(QuestionImageCreator, '/question/bg_image/<question_id>')

#import admin
'''

@app.route('/mixpanel/trackswitch',methods=['GET'])
def mixpanel_switch():
    return '{"track":"true"}'

@app.route('/elb-test',methods=['GET'])
def elbtest():
    return "{'success':'true','server':'zdexterorroh'}"

@app.route('/search/default',methods=['GET'])
def search_default():
    return '{"results": [{"users": [{"username": "Arvindkejriwal", "first_name": "Arvind Kejriwal", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/cab4132c5447879cdf31033c4c029efd/photos/e735b1048c1511e4af7622000b4c02a7.jpeg", "user_title": "Politician", "id": "cab4132c5447879cdf31033c4c029efd"}, {"username": "KiranBedi", "first_name": "Kiran Bedi", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/cab4132c5475cab4df31032d5dd12351/photos/eb779a4a8c1d11e48e7c22000b4c02a7.jpeg", "user_title": "Social Activist", "id": "cab4132c5475cab4df31032d5dd12351"}, {"username": "YogendraYadav", "first_name": "Yogendra Yadav", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/efa597cddfee48f488d4ac953aca21bc/photos/418f9614875311e4aaaf22000b4c02a7.jpeg", "user_title": "Politician", "id": "efa597cddfee48f488d4ac953aca21bc"}], "category_name": "Politicians"}, {"users": [{"username": "GurdasMaan", "first_name": "Gurdas Maan", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/04e666ee64b3434a8b38daabe76ddd2c/photos/3a712a5897fe11e48e1422000b5119ba.jpeg", "user_title": "Singer", "id": "04e666ee64b3434a8b38daabe76ddd2c"}, {"username": "SnehaPant", "first_name": "Sneha Pant", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/29e6d8c53aa04e5eaa14c3835e7f6ac0/photos/bae49cfa9c9111e4b48e22000b5119ba.jpeg", "user_title": "Singer", "id": "29e6d8c53aa04e5eaa14c3835e7f6ac0"}, {"username": "ShafqatAmanatAli", "first_name": "Shafqat Amanat Ali", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/551c4d8fb5e14bf0ab9b1ae8da5af3b4/photos/733f3c24963e11e49fa122000b5119ba.jpeg", "user_title": "Singer", "id": "551c4d8fb5e14bf0ab9b1ae8da5af3b4"}], "category_name": "Singers"}, {"users": [{"username": "RJSayema", "first_name": "RJ Sayema", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/3d75b05d82694b1cbefae6c5ae14012d/photos/241a22ce874a11e4b6cd22000b4c02a7.jpeg", "user_title": "Radio Jockey", "id": "3d75b05d82694b1cbefae6c5ae14012d"}, {"username": "RJNaved", "first_name": "RJ Naved", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/8285cc36fe174664b283bc9a57c829d2/photos/bd233154874f11e4bc0022000b4c02a7.jpeg", "user_title": "Radio Jockey", "id": "8285cc36fe174664b283bc9a57c829d2"}, {"username": "RJRhicha", "first_name": "Richa Vyas", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/cab4132c546c6770df31033ce3dcc96f/photos/e9d22eae8c1c11e4a7bd22000b4c02a7.jpeg", "user_title": "Radio Jockey", "id": "cab4132c546c6770df31033ce3dcc96f"}], "category_name": "RadioJockeys"}, {"users": [{"username": "VikasKhanna", "first_name": "Vikas Khanna", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/2882c51a950642e9b684cb25176a690c/photos/367edfc2875411e4aaaf22000b4c02a7.jpeg", "user_title": "Masterchef", "id": "2882c51a950642e9b684cb25176a690c"}, {"username": "SarahTodd", "first_name": "Sarah Todd", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/3912895ebcdc48a3b90f1361cd0d5af1/photos/df2431ac874c11e4bc0022000b4c02a7.jpeg", "user_title": "Masterchef", "id": "3912895ebcdc48a3b90f1361cd0d5af1"}, {"username": "SaranshGoila", "first_name": "Saransh Goila", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/85cf5cccbb4c434ab40e6272ca6c9ddc/photos/9a2a16ee8f4d11e48b3322000b4c02a7.jpeg", "user_title": "MasterChef", "id": "85cf5cccbb4c434ab40e6272ca6c9ddc"}], "category_name": "Chefs"}, {"users": [{"username": "AvnishBajaj", "first_name": "Avnish Bajaj", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/daf6e8dd67bd4dd2b971c6b876c12feb/photos/175e19e4875b11e4aaaf22000b4c02a7.jpeg", "user_title": "Entrepreneur", "id": "daf6e8dd67bd4dd2b971c6b876c12feb"}, {"username": "NaveenTiwari", "first_name": "Naveen Tiwari", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/0588e80bfe87452a9042818dfd97bdb2/photos/d9c402a28f4c11e4990622000b4c02a7.jpeg", "user_title": "Entrepreneur", "id": "0588e80bfe87452a9042818dfd97bdb2"}, {"username": "KunalBahl", "first_name": "Kunal Bahl", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/980b87b03a154e949bae2f0271bb738f/photos/da5fa1b4964311e4a8e822000b5119ba.jpeg", "user_title": "entrepreneur", "id": "980b87b03a154e949bae2f0271bb738f"}], "category_name": "Entrepenuers"}, {"users": [{"username": "PavanDuggal", "first_name": "Pavan Duggal", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/64261177e93c4f05bc20acbfff2dd686/photos/8166b36e875b11e4aaaf22000b4c02a7.jpeg", "user_title": "Advocate", "id": "64261177e93c4f05bc20acbfff2dd686"}, {"username": "JayantiDutta", "first_name": "Jayanti Dutta", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/e468090c43574616845533d58f619911/photos/5c8f0fc48f4d11e480ef22000b4c02a7.jpeg", "user_title": "Psychologist", "id": "e468090c43574616845533d58f619911"}, {"username": "SuneelSingh", "first_name": "Suneel Singh", "last_name": null, "user_type": 2, "profile_picture": "https://s3.amazonaws.com/franklyapp/ef64ed594e334ed7ae44a7c6678feb7d/photos/ea33e0028f4d11e4990622000b4c02a7.jpeg", "user_title": "Yoga Guru", "id": "ef64ed594e334ed7ae44a7c6678feb7d"}], "category_name": "Subject Experts"}]}'








#=================ADMIN URLS========================#

import admin

api.add_resource(admin.AdminQuestionList, '/admin/question/list')
api.add_resource(admin.AdminQuestionDelete, '/admin/question/delete')
api.add_resource(admin.AdminQuestionUndelete, '/admin/question/undelete')
api.add_resource(admin.AdminQuestionEdit, '/admin/question/edit')
api.add_resource(admin.AdminUserEdit, '/admin/user/edit')
api.add_resource(admin.AdminUserAdd, '/admin/user/add')
api.add_resource(admin.AdminQuestionAdd, '/admin/question/add')
api.add_resource(admin.AdminQueOrderEdit, '/admin/queue/order')
api.add_resource(admin.AdminCelebList, '/admin/celeb/list/<int:offset>/<int:limit>')
api.add_resource(admin.AdminAddCelebQue, '/admin/queue/add')




if __name__ == '__main__':
    app.run('127.0.0.1', 8000)
