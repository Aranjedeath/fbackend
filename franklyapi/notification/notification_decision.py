from app import db
from sqlalchemy.sql import text
from CustomExceptions import ObjectNotFoundException
from models import Question, Notification, UserNotificationInfo, UserPushNotification

import util
import helper
import make_notification as notification
import push_notification as push
import datetime


'''
Sends out both Push and email.
Called after the low quality of
video is ready. Since this is a super high priority notification
it is sent to all those users who upvoted, asked the question or follows the user'''
def post_notifications(post_id):

    result = db.session.execute(text('''Select
                                        aa.first_name, q.body,
                                         n.id, n.link, n.type
                                         from posts p
                                         left join questions q on q.id = p.question
                                         left join users aa on aa.id = p.answer_author
                                         left join notifications n on n.object_id = :post_id
                                         where p.id = :post_id
                                         and n.type in ('post-add-self_user','post-add-following_user')
                                         group by n.type
                                         limit 2 ;
                                         '''), params={'post_id': post_id})
    from mail import make_email
    try:
        for row in result:

            answer_author_name = row[0]
            question_body = row[1]
            notification_id = row[2]
            link = row[3]
            notification_type = row[4]


            #Get a set of users who haven't been sent this gcm notification yet
            #This includes the question author
            results = db.session.execute(text('''Select
                                             un.user_id, u.first_name, u.email
                                             from user_notifications un
                                             left join user_push_notifications upn
                                             on upn.notification_id  = :notification_id and upn.user_id = un.user_id
                                             left join users u on u.id = un.user_id
                                             where
                                             u.monkness = -1 and
                                             un.notification_id = :notification_id
                                             and upn.user_id is null'''),
                                             params={'notification_id': notification_id})

            print 'Notification id: ', notification_id
            print 'Notification type:', notification_type

            for user in results:

                push.send(notification_id=notification_id, user_id=user[0])
                if notification_type == 'post-add-self_user':
                    print user.email
                    make_email.question_answered(receiver_email=user[2], receiver_name=user[1],
                                               celebrity_name=answer_author_name,
                                               user_id=row[0],
                                               question=question_body, web_link=link,
                                               post_id=post_id)
                    break
    except ObjectNotFoundException:
        pass

'''
Decides whether question should be pushed or not
based on

a) Question's upvotes
b) Questions asked that day
c) Such notifications sent to the user
d) Time of day
e) User's overall popularity
'''
def decide_question_push(user_id, question_id):
    ''' Decide pushing notification on the basis
    of user's popularity'''

    notifications_sent_today = count_of_notifications_sent_by_type(user_id=user_id,
                                                                   notification_type='question-ask-self_user')

    good_time = 10 < (datetime.datetime.now() + datetime.timedelta(seconds=18600)).hour < 22


    if notifications_sent_today < 2 and good_time:
        questions_today = Question.query.filter(Question.question_to == user_id, Question.timestamp >=
                                            datetime.datetime.now() - datetime.timedelta(days=1)).count()
        print 'Good time bro'
        if questions_today > 10 or is_popular(user_id):

            upvotes = util.get_question_upvote_count(question_id)
            print 'Upvotes are good'
            if upvotes > 2:
                return True
            else:
                return False

        else:
            return True
    else:
        return False


def push_question_notification(question_id):

    try:
        user_id = Question.query.filter(Question.id == question_id).first().question_to
        n = Notification.query.filter(Notification.object_id == question_id,
                                      Notification.type == 'question-ask-self_user').first()
        if n is not None:
            pushed = UserPushNotification.query.filter(UserPushNotification.notification_id == n.id,
                                                       UserPushNotification.user_id == user_id).count()
            print 'pushed is:', pushed
            if pushed == 0 and decide_question_push(user_id=user_id, question_id=question_id):
                push.send(notification_id=n.id, user_id=user_id)
    except ObjectNotFoundException:
        pass



def is_popular(user_id):

    is_popular = UserNotificationInfo.query.filter(UserNotificationInfo.user_id == user_id).first()
    if is_popular is not None:
        return is_popular.is_popular
    else:
        return 0


# def decide_question_ask_notification(question_id, user_id):
#     if average_upvote_count(user_id)<3 and count_of_notifications_sent_by_type(user_id=user_id, notification_type='question-ask-self_user')< 1:
#         return True
#     else:
#         return False



''' Gets most popular question that have been asked
and sends out a notification prompting to share the question
'''


def prompt_sharing_popular_question():

    # Select questions that have been upvoted the most
    results = db.session.execute(text('''  Select count(*) as real_upvote_count, i.upvote_count,
                                           q.question_author, q.body,
                                           qu.question
                                           from question_upvotes as qu
                                           left join inflated_stats as i on i.question = qu.question
                                           left join questions q on q.id = qu.question
                                           left join notifications n on n.object_id = q.id
                                           where
                                           qu.timestamp > date_sub(now(), interval 20 day)
                                           and qu.downvoted = 0
                                           and n.type = 'popular-question-self_user'
                                           and n.id is null
                                           and q.is_answered = 0
                                           group by qu.question
                                           order by real_upvote_count DESC;'''))
    for row in results:
        upvote_count =row[0] + (row[1] if row[1] is not None else 0)
        if upvote_count > 10:
           upvote_count = util.get_question_upvote_count(row[4])
           notification.share_popular_question(user_id=row[2], question_id=row[4],
                                    question_body=row[3], upvote_count=upvote_count)


''' Creates milestone notifications
for a user's followers
'''


def user_followers_milestone_notifications():

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
                                        and uf.follower_count > 0
                                        group by uf.user;
                                                        '''))

    for row in result:
        check_and_make_milestone('user_followers_milestone', row[0], row[0], util.get_follower_count(row[0]))


'''
Creates milestone notifications for a
user's likes
'''


def decide_post_milestone(post_id, user_id):

    check_and_make_milestone('post-likes-milestone', user_id, post_id, util.get_post_like_count(post_id))

def decide_follow_milestone(user_id):
    check_and_make_milestone('user-followers-milestone', user_id, user_id, util.get_follower_count(user_id))

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
        check_and_make_milestone('post_likes', row[1], row[0], util.get_post_like_count(row[0]))


def check_and_make_milestone(milestone_name, user_id, associated_item_id, count):
    """
    check the latest crossed milestone and sends a notification about the same.
    
    associated_item_id is the id of post of question in case of likes of upvotes of questions / posts

    """
    # largest milestone count, smaller than count.
    milestone_crossed = get_milestone_crossed(count, helper.milestones[milestone_name])

    # if count is not null.
    if milestone_crossed:

        # make notification type by appending name and count.
        notification_type =  milestone_name + '_' + milestone_crossed

        #check if a notification has been sent to user about this milestone or not
        if count_of_notifications_sent_by_type(user_id=user_id, notification_type=notification_type,
                                               interval=datetime.datetime.now() - datetime.timedelta(days=100000)) == 0:

            #send milestone notification
            notification.send_milestone_notification(milestone_name, milestone_crossed, associated_item_id, user_id)

def get_milestone_crossed(count, milestone_count_list):
    '''
    Returns largest milestone count crossed smaller than count.
        otherwise None
    '''
    try: return str(max(int(t) for t in milestone_count_list if t != '' and int(t) <= int(count)))
    except ValueError: return None


def count_of_push_notifications_sent(user_id):

    result = db.session.execute(text("Select count(*) from user_push_notifications "
                                     "where user_id = :user_id and pushed_at >= date_sub(NOW(), interval 1 day);"),
                                params={'user_id': user_id})

    for row in result:
        return row[0]


def count_of_notifications_sent_by_type(user_id, notification_type, interval=datetime.datetime.now() -
                                                                             datetime.timedelta(days=1)):

    result = db.session.execute(text('''Select count(*) from user_push_notifications upn
                                        left join notifications n on n.id = upn.notification_id
                                        where
                                        user_id = :user_id
                                        and n.type = :type_of_notification
                                        and pushed_at >= :interval ;'''),
                                params={"user_id": user_id,
                                         "type_of_notification": notification_type,
                                         "interval": interval})
    for row in result:
        return row[0]


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



'''
Gives average upvote count of questions that have been asked
to a particular
user'''
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



