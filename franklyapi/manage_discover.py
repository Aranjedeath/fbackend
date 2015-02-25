import datetime
from sqlalchemy.sql import text

from app import db

from models import User, Post, Question, DiscoverList
from object_dict import questions_to_dict, guest_user_to_dict, posts_to_dict


def get_discover_list(current_user_id, offset, limit=10, day_count=0, add_super=False):
    day_count = 0
    
    if current_user_id:
        result_row = db.session.execute(text("""SELECT users.user_since 
                                                FROM users 
                                                WHERE users.id=:current_user_id
                                            """),
                                        params={'current_user_id':current_user_id}
                                        ).one()
        user_since = result_row[0]
        day_count = int((datetime.datetime.now() - user_since).total_seconds())/(3600*24)
    
    super_items = []
    
    if add_super:
        super_items = db.session.execute(text("""SELECT discover_list.post,
                                                        discover_list.question,
                                                        discover_list.user,
                                                        ROUND(discover_list.show_order, 10)
                                                    FROM discover_list
                                                    WHERE discover_list.is_super=true
                                                        AND discover_list.display_on_day=:day_count 
                                                """),
                                    params={'day_count':day_count})

    items = db.session.execute(text("""SELECT discover_list.post, 
                                                discover_list.question,
                                                discover_list.user,
                                                ROUND(discover_list.show_order, 10)
                                        FROM discover_list
                                        WHERE discover_list.removed=false
                                            AND discover_list.display_on_day<=:day_count
                                        ORDER BY discover_list.show_order DESC
                                        LIMIT :offset, :limit
                                    """),
                                params = {'day_count':day_count, 'offset':offset, 'limit':limit-len(super_items)}
                                )
    resp = {}
    print limit
    print 'what'
    print items
    for item in items:
        print item
        if item[0]:
            resp.update({item[0]: {'type':'post', 'show_order':item[3]}})
        if item[1]:
            resp.update({item[1]: {'type':'question', 'show_order':item[3]}})
        if item[2]:
            resp.update({item[2]: {'type':'user', 'show_order':item[3]}})

    return resp


def get_discover_multitype(current_user_id, offset, limit=10, day_count=0, add_super=False):
    resp = get_discover_list(current_user_id, offset, limit, day_count, add_super)
    
    users = filter(lambda x:resp[x]['type']=='user', resp)
    posts = filter(lambda x:resp[x]['type']=='posts', resp)
    questions = filter(lambda x:resp[x]['type']=='questions', resp)

    user_objects = User.query.filter(User.id.in_(users)).all()
    post_objects = Post.query.filter(Post.id.in_(posts)).all()
    question_objects = Question.query.filter(Question.id.in_(questions)).all()

    user_objects_json = [{'type':'user', 'show_order':resp[u.id]['show_order'], 'user':guest_user_to_dict(u, current_user_id)} for u in user_objects]

    question_objects_json = questions_to_dict(question_objects, current_user_id)
    question_objects_json = [{'type':'question', 'show_order':resp[q['id']]['show_order'], 'question':q} for q in question_objects_json]

    post_objects_json = posts_to_dict(post_objects, current_user_id)
    post_objects_json = [{'type':'post', 'show_order':resp[p['id']]['show_order'], 'post':p} for p in post_objects_json]

    final_list = user_objects_json + question_objects_json + post_objects_json
    final_list.sort(key=lambda item: item['show_order'], reverse=True)

    return final_list



