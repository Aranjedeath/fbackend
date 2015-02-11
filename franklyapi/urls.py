from resources import *
from app import api, app


api.add_resource(RegisterEmail, '/reg/email')
api.add_resource(LoginSocial, '/login/social/<login_type>')
api.add_resource(LoginEmail, '/login/email')

api.add_resource(UserProfile, '/user/profile/<user_id>')
api.add_resource(UserUpdateForm, '/user/update_profile/<user_id>')

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

api.add_resource(TopLikedUsers, '/user/top_liked_users')



api.add_resource(QuestionAsk, '/question/ask')
api.add_resource(QuestionCount, '/question/count')
api.add_resource(QuestionView, '/question/view/<question_id>')
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
api.add_resource(ContactUs, '/contactus')

api.add_resource(Search, '/search')
api.add_resource(SearchDefault, '/search/default', '/accountsetup/follow/celebs')

api.add_resource(InviteCeleb, '/invite/celeb')

api.add_resource(FeedBackResponse, '/feedback')

api.add_resource(ChannelFeed, '/channel/<channel_id>')





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

@app.route('/test/<int:bytesize>',methods=['GET'])
def test_size(bytesize):
    return 'a'*bytesize

@app.route('/elb-test',methods=['GET'])
def elbtest():
    return "{'success':'true','server':'zdexterorroh'}"



@app.route('/admin/apidoc',methods=['GET'])
def apidoc():
    try:
        from doc_generator import doc_gen
        import resources
        from flask import render_template

        #return Response(json.dumps(doc_gen(app, resources)), content_type='application/json')
        return render_template('api_doc.html', endpoints=doc_gen(app, resources))
    except Exception as e:
        import traceback
        print traceback.format_exc(e)

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
api.add_resource(admin.AdminCelebSearch, '/admin/celeb/search/<query>')
api.add_resource(admin.AdminQueueDelete, '/admin/queue/delete')
api.add_resource(admin.AdminCelebsAskedToday, '/admin/most/asked/today')
api.add_resource(admin.AdminQuestionTodayList, '/admin/question/today/list')
api.add_resource(admin.AdminPostEdit, '/admin/post/edit')
api.add_resource(admin.AdminDeleteSearchDefaultUser, '/admin/search/default/delete')
api.add_resource(admin.AdminUpdateSearchDefaultCategoryOrder, '/admin/search/default/update')
api.add_resource(admin.AdminGetUnansweredQuestionListWithSameCount, '/admin/question/list/same')
api.add_resource(admin.AdminGetSimilarQuestions, '/admin/question/similar')
api.add_resource(admin.AdminSearchDefault, '/admin/search/default')

if __name__ == '__main__':
    app.run('127.0.0.1', 8000)
