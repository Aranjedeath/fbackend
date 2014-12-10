from resources import *
from app import api, app




api.add_resource(RegisterEmail, '/reg/email')
api.add_resource(LoginSocial, '/login/social/<login_type>')
api.add_resource(LoginEmail, '/login/email')

api.add_resource(UserProfile, '/user/profile/<user_id>')
api.add_resource(UserUpdateForm, '/user/update_profile/<user_id>')
api.add_resource(UserProfileUsername, '/user/profile/username/<username>')

api.add_resource(UserFollow, '/user/follow')
api.add_resource(UserUnfollow, '/user/unfollow')
api.add_resource(UserBlock, '/user/block')
api.add_resource(UserUnblock, '/user/unblock')
api.add_resource(UserBlockList, '/user/blocklist')

api.add_resource(ChangeUsername, '/user/change_username')
api.add_resource(ChangePassword, '/user/change_password')
api.add_resource(UserExists, '/user/exists')
api.add_resource(UserSettings, '/user/settings')

api.add_resource(UserLocation, '/user/location')

api.add_resource(UpdateGCMId, '/update/gcm')
api.add_resource(UserUpdateToken, '/user/update_token')


api.add_resource(QuestionAsk, '/question/ask')
api.add_resource(QuestionListMultitype, '/question/list/multitype')
api.add_resource(QuestionListPublic, '/question/list/public/<user_id>')

api.add_resource(QuestionUpvote, '/question/upvote/<question_id>')
api.add_resource(QuestionDownvote, '/question/downvote/<question_id>')
api.add_resource(QuestionIgnore, '/question/ignore')


api.add_resource(PostAdd, '/post/media/add', 'post/add')

api.add_resource(PostLike, '/post/like')
api.add_resource(PostUnLike, '/post/unlike')
api.add_resource(PostDelete, '/post/delete')

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

api.add_resource(InstallRef, '/utils/install_ref')
api.add_resource(BadUsernames, '/utils/badusernames')




#api.add_resource(PostLikeUsers, '/post/like/users')

'''
api.add_resource(RegisterEmail, '/reg/email')
api.add_resource(LoginSocial, '/login/social/<login_type>')
api.add_resource(LoginEmail, '/login/email')
api.add_resource(MergeAccount, '/merge/<int:account_type>')
api.add_resource(Logout, '/logout')



#api.add_resource(UserFollowers, '/user/followers/<user_id>')
#api.add_resource(UserFollowing, '/user/following/<user_id>')






api.add_resource(PostViewLogger, '/post/view/logs')


api.add_resource(GetNotifications, '/getnotifications')
api.add_resource(NotificationsCount, '/notifications/count')
api.add_resource(NotificationsRead, '/notifications/read')
api.add_resource(ReportAbuse, '/reportabuse')

api.add_resource(AddEmail, '/addemail/<token>/<email_type>')
api.add_resource(ContactUs, '/contact_us')
api.add_resource(FeedBack, '/feedback')

api.add_resource(Unsubscribe, '/unsubscribe')
api.add_resource(Subscribe, '/subscribe')


api.add_resource(QuestionImageCreator, '/question/bg_image/<question_id>')

#import admin


@app.route('/mixpanel/trackswitch',methods=['GET'])
def mixpanel_switch():
    return '{"track":"true"}'


@app.route('/elb-test',methods=['GET'])
def elbtest():
    return "{'success':'true','server':'zdexterorroh'}"

'''
if __name__ == '__main__':
    app.run('127.0.0.1', 8000)
