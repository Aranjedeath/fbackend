import datetime

from app import db
from sqlalchemy.sql import text
import make_notification as notification
from mailwrapper import email_helper
from CustomExceptions import ObjectNotFoundException
import controllers
'''
Sends out both Push and email.
Called after the low quality of
video is ready. Since this is a super high priority notification
it is sent to all those users who upvoted or asked the question'''
def post_notifications(post_id):

    result = db.session.execute(text('''Select
                                         p.question, p.question_author, p.answer_author,
                                         q.body,
                                         aa.email, aa.first_name,
                                         n.id, n.link
                                         from posts p
                                         left join questions q on q.id = p.question
                                         left join users aa on aa.id = p.answer_author
                                         left join notifications n on n.object_id = :post_id and n.type = 'post-add-self_user'
                                         where p.id = :post_id limit 1 ;
                                         '''), params={'post_id': post_id})
    try:
        for row in result:
            question_id = row[0]
            question_author_id = row[1]
            answer_author_id = row[2]
            question_body = row[3]
            answer_author_email = row[4]
            answer_author_name = row[5]
            notification_id = row[6]
            link = row[7]

        #Get a set of users who haven't been sent this gcm notification yet
        #This includes the question author
        results = db.session.execute(text('''Select
                                             un.user_id, u.first_name, u.email
                                             from user_notifications un
                                             left join user_push_notifications upn
                                             on upn.notification_id  = :notification_id and upn.user_id = un.user_id
                                             left join users u on u.id = un.user_id
                                             where un.notification_id = :notification_id
                                             and upn.user_id is null'''),
                                             params={'notification_id': notification_id})
        for row in results:
            print row[0]
            if row[0] == question_author_id or count_of_push_notifications_sent(user_id=row[0]) < 5:
                notification.push_notification(notification_id=notification_id, user_id = row[0])
                email_helper.question_answered(receiver_email = row[2], receiver_name = row[1],
                                           celebrity_name = answer_author_name,
                                           question = question_body, web_link=link)
    except ObjectNotFoundException:
        pass

'''
Sends notifications to popular users
'''
def question_asked_notifications():

    users = db.session.execute(text(''' Select u.id, u.email, u.first_name, uni.is_popular, q.id,
                                        q.body
                                        from users u
                                        left join questions q on q.question_to = u.id
                                        and q.timestamp >= date_sub(now(), interval 1 day)
                                        left join user_notification_info uni on uni.user_id = u.id
                                        where q.body is not null
                                        and uni.is_popular = 1
                                        group by q.question_to
                                    '''))

    for user in users:
        print user[2]
        if count_of_notifications_sent_by_type(user_id=user[0], notification_type='question-ask-self_user') == 0:
            print 'No such notification sent during the day'
            results = db.session.execute(text('''Select q.id, n.id from questions q
                                                          left join question_upvotes qu on qu.question = q.id
                                                          left join notifications n on n.object_id = q.id
                                                          where q.question_to = :user_id and q.is_answered = 0
                                                          group by qu.question
                                                          order by count(qu.question) limit 1 ;'''),
                                                  params={'user_id': user[0]})
            for row in results:
                print 'Sending the notification now'
                notification.push_notification(notification_id=row[1], user_id = row[0])



'''Decides popular users on the basis
of number of avg. upvotes on questions that have been
asked to them or on the basis of total questions that have been asked
'''
def decide_popular_users():

    results = db.session.execute(text('''Select u.id from users u
                                         left join questions q on q.question_to = u.id
                                         and q.deleted = false
                                         and q.timestamp >= date_sub(now(), interval 30 day)
                                         where u.monkness = -1 and q.body is not null
                                         group by u.id ; '''))

    for user in results:
        average_upvotes, question_count = average_upvote_count(user_id=user[0])
        if average_upvotes > 3 or question_count > 20:
            db.session.execute(text('''Insert into user_notification_info (user_id, is_popular) values
                                       (:user_id, 1) on Duplicate key update is_popular =1 ; '''),
                               params={'user_id': user[0]})
            db.session.commit()




def average_upvote_count(user_id):
    results = db.session.execute(text("""SELECT COUNT(1) as upvote_count
                                         FROM question_upvotes JOIN questions ON questions.id=question_upvotes.question
                                         WHERE questions.question_to=:user_id
                                         AND questions.deleted=false
                                         AND question_upvotes.downvoted=false
                                         AND question_upvotes.timestamp>=:last_two_months
                                        """),
                                    params={'user_id':user_id,
                                            'last_two_months':datetime.datetime.now() - datetime.timedelta(days=60)
                                            }
                                )
    upvote_count = 0
    for row in results:
        upvote_count = row[0]

    results = db.session.execute(text("""SELECT COUNT(1)
                                            FROM questions
                                            WHERE questions.question_to=:user_id
                                            AND questions.deleted=false
                                            AND questions.timestamp>=:last_two_months
                                        """),
                                    params={'user_id':user_id,
                                            'last_two_months':datetime.datetime.now() - datetime.timedelta(days=60)
                                            }
                                )
    question_count = 0
    for row in results:
        question_count = row[0]
    upvote_count += question_count

    average_upvote_count = (upvote_count/question_count) if question_count else 0
    return average_upvote_count, question_count


def decide_question_ask_notification(question_id, user_id):
    if average_upvote_count(user_id)<3 and count_of_notifications_sent_by_type(user_id=user_id, notification_type='question-ask-self_user')< 1:
        return True
    else:
        return False


def list_objects_with_notifications_pushed(user_id, notification_type, day_count=1):
    object_id = []
    result = db.session.execute(text("""SELECT notifications.object_id
                                        FROM user_push_notifications JOIN notifications 
                                            ON user_push_notifications.notification_id=notifications.id
                                        WHERE user_push_notifications.user_id=:user_id
                                            AND notifications.type=:notification_type
                                            AND user_push_notifications.pushed_at>:time_period
                                    """),
                                params={
                                        'user_id':user_id,
                                        'notification_type':notification_type,
                                        'time_period':datetime.datetime.now()-datetime.timedelta(days=day_count)
                                        }
                                )
    for row in result:
        notification_count = row[0]
    return notification_count


def get_popular_questions_in_last_day():

    import controllers

    results = db.session.execute(text('''  Select count(*) as real_upvote_count, i.upvote_count,
                                           q.question_author, q.body,
                                           qu.question
                                           from question_upvotes as qu
                                           left join inflated_stats as i on i.question = qu.question
                                           left join questions q on q.id = qu.question
                                           where
                                           qu.timestamp > date_sub(now(), interval 1 day)
                                           and qu.downvoted = 0
                                           group by qu.question
                                           order by real_upvote_count DESC;'''))
    for row in results:
        upvote_count =row[0] + (row[1] if row[1] is not None else 0)
        if upvote_count > 10:
           upvote_count = controllers.get_question_upvote_count(row[4])
           notification.share_popular_question(user_id=row[2], question_id=row[4],
                                    question_body=row[3], upvote_count=upvote_count)




def get_most_upvoted_questions(user_id):
    questions_with_count = []
    after_date = datetime.datetime.now()
    before_date = after_date - datetime.timedelta(days=1)
    results = db.session.execute(text("""SELECT question_upvotes.question, COUNT(1) as upvote_count
                                                FROM question_upvotes JOIN questions ON
                                                questions.id=question_upvotes.question
                                                WHERE questions.queston_author=:user_id
                                                    AND question_upvotes.downvoted=false
                                                    AND question_upvotes.timestamp>=:after_date
                                                    AND question_upvotes.timestamp<:before_date
                                                ORDER BY upvote_count
                                                LIMIT 0, 10
                                        """),
                                    params={
                                            'user_id':user_id,
                                            'after_date':after_date,
                                            'before_date':before_date
                                            }
                                )
    for row in results:
        questions_with_count.append({'question_id':row[0], 'upvote_count':row[1]})


def count_of_push_notifications_sent(user_id):

    result = db.session.execute(text("Select count(*) from user_push_notifications "
                                     "where user_id = :user_id and pushed_at >= date_sub(NOW(), interval 1 day);"),
                                params={'user_id': user_id})

    for row in result:
        return row[0]


def count_of_notifications_sent_by_type(user_id, notification_type):

    result = db.session.execute(text('''Select count(*) from user_push_notifications upn
                                        left join notifications n on n.id = upn.notification_id
                                        where
                                        user_id = :user_id
                                        and n.type = :type_of_notification
                                        and pushed_at >= date_sub(NOW(), interval 1 day);'''),
                                params={"user_id": user_id,
                                         "type_of_notification": notification_type})
    for row in result:
        return row[0]

# TODO : change method name
def count_of_notifications_sent_by_type_rg(user_id, notification_type):
    '''
    returns count of notifications sent to user with specified notification type.
    '''

    result = db.session.execute(text('''Select count(*) from user_push_notifications upn
                                        left join notifications n on n.id = upn.notification_id
                                        where
                                        user_id = :user_id
                                        and n.type = :type_of_notification;'''),
                                params={"user_id": user_id,
                                         "type_of_notification": notification_type})
    for row in result:
        return row[0]

# TODO : clean commented code.
def user_followers_milestone_notifications():
    # # old query : gets count from database but cannot pump the count. SEE CONTROLLERS.GET_FOLLOWER_COUNT

    # result = db.session.execute(text('''SELECT distinct uf.followed as user,sum(if(isnull(ufc.id),0,1)) + if(isnull(stc.follower_count),0,stc.follower_count) as follow_count,monkness,username,first_name
    #                                                         from user_follows uf
    #                                                         inner join users u on u.id = uf.followed
    #                                                         left join inflated_stats stc on stc.user = uf.followed
    #                                                         left join user_follows ufc on ufc.followed = uf.followed
    #                                                         where u.monkness = -1
    #                                                         and uf.timestamp >= date_sub(now(), interval 1 day)
    #                                                         and ufc.unfollowed = false
    #                                                         group by uf.id,uf.followed;
    #                                                     '''))
    result = db.session.execute(text('''SELECT distinct uf.followed as user
                                                            from user_follows uf
                                                            inner join users u on u.id = uf.followed
                                                            where u.monkness = -1
                                                            and uf.timestamp >= date_sub(now(), interval 1 day)
                                                            group by uf.followed
                                        union SELECT distinct uf.user as user
                                                            from inflated_stats uf
                                                            inner join users u on u.id = uf.user
                                                            where u.monkness = -1
                                                            and uf.timestamp >= date_sub(now(), interval 1 day)
                                                            group by uf.user;
                                                        '''))

    for row in result:
        check_and_make_milestone('user_followers', row[0], row[0], controllers.get_follower_count(row[0]))

# TODO : clean commented code.
def post_likes_milestone_notifications():
    # result = db.session.execute(text('''SELECT distinct pl.post as post, posts.question_author, sum(if(isnull(plc.id),0,1)) + if(isnull(stc.like_count),0,stc.like_count) as like_count
    #                                                         from post_likes pl
    #                                                         inner join posts on posts.id = pl.post
    #                                                         left join inflated_stats stc on stc.post = pl.post
    #                                                         left join post_likes plc on plc.post = pl.post
    #                                                         where pl.timestamp >= date_sub(now(), interval 1 day)
    #                                                         and plc.unliked = false
    #                                                         group by pl.id,pl.post;
    #                                                     '''))
    result = db.session.execute(text('''SELECT distinct pl.post as post, posts.question_author
                                                            from post_likes pl
                                                            inner join posts on posts.id = pl.post
                                                            where pl.timestamp >= date_sub(now(), interval 1 day)
                                                            group by pl.post
                                        union SELECT distinct pl.post as post, posts.question_author
                                                            from inflated_stats pl
                                                            inner join posts on posts.id = pl.post
                                                            where pl.timestamp >= date_sub(now(), interval 1 day)
                                                            group by pl.post;
                                                        '''))
    for row in result:
        check_and_make_milestone('post_likes', row[1], row[0], controllers.get_post_like_count(row[0]))

def question_upvotes_milestone_notifications():
    result = db.session.execute(text('''SELECT distinct pl.question as question, questions.question_author
                                                            from question_upvotes pl
                                                            inner join questions on questions.id = pl.question
                                                            where pl.timestamp >= date_sub(now(), interval 1 day)
                                                            group by pl.question
                                        union SELECT distinct pl.question as question, questions.question_author
                                                            from inflated_stats pl
                                                            inner join questions on questions.id = pl.question
                                                            where pl.timestamp >= date_sub(now(), interval 1 day)
                                                            group by pl.question;
                                        
                                                        '''))
    
    for row in result:
        check_and_make_milestone('post_likes', row[1], row[0], controllers.get_post_like_count(row[0]))

def check_and_make_milestone(milestone_name,user_id,associated_item_id,count):
    '''
    check the latest crossed milestone and sends a notification about the same.
    
    associated_item_id is the id of post of question in case of likes of upvotes of questions / posts

    '''
    # largest milestone count, smaller than count.
    milestone_crossed = get_milestone_crossed(count,milestones[milestone_name])

    # if count is not null.
    if(milestone_crossed):

        # make notification type by appending name and count.
        notification_type = milestone_name + milestone_crossed

        #check if a notification has been sent to user about this milestone or not
        if count_of_notifications_sent_by_type_rg(user_id=user_id, notification_type=notification_type) == 0:

            #send milestone notification
            notification.send_milestone_notification(notification_type,user_id)

def get_milestone_crossed(count, milestone_count_list):
    '''
    returns largest milestone count crossed smaller than count.
        otherwise null
    '''
    try: return str(max(int(t) for t in milestone_count_list if t != '' and int(t) < int(count)))
    except ValueError: return None



# dictionary that saves counts as milestones
#
# notification type = milestone+count 
# ex - 'user_follwers100'
#
# TODO: move to config or other suitable place.
milestones = {
    'user_followers':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'post_likes':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'upvotes':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'profile_views':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'post_views':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    }

}
