import datetime
from sqlalchemy.sql import text

from app import db

from models import User, Post, Question, DiscoverList
from object_dict import questions_to_dict, guest_user_to_dict, posts_to_dict


def get_discover_list(current_user_id, offset, limit=10, day_count=0, add_super=False, exclude_users=[]):
    if not day_count:
        day_count = 0

    if current_user_id:
        result = db.session.execute(text("""SELECT users.user_since
                                                FROM users 
                                                WHERE users.id=:current_user_id
                                            """),
                                    params={'current_user_id':current_user_id})
        for row in result:
            user_since = row[0]
            day_count = int((datetime.datetime.now() - user_since).total_seconds())/(3600*24)

    super_inclusion = [False, True, None]
    count_of_dirty_sent = 0
    dirty_items = []
    
    recycled_items = []

    if datetime.datetime.now() - user_last_visit > config.DISCOVER_RECYCLE_TIME:
        if offset = 0:
            recycled_items = get_recycled_items(current_user_id)
            recycled_items = make_resp_multitype(current_user_id, recycled_items, order_key='recycled_index', reverse_sort=False)

    if day_count < 10:
        super_inclusion.remove(True)
        dirty_items = get_dirty_items(current_user_id, offset, limit, day_count)
        dirty_items = make_resp_multitype(current_user_id, dirty_items, order_key='dirty_index', reverse_sort=False)
        count_of_dirty_sent = get_count_of_dirty_items_sent(offset, day_count)

    items = db.session.execute(text("""SELECT discover_list.post, 
                                                discover_list.question,
                                                discover_list.user,
                                                discover_list.id
                                        FROM discover_list
                                        WHERE discover_list.removed=false
                                            AND discover_list.display_on_day<=:day_count
                                            AND discover_list.is_super in :super_inclusion
                                        ORDER BY discover_list.id DESC
                                        LIMIT :offset, :limit
                                    """),
                                params = {'super_inclusion':super_inclusion, 
                                            'day_count':day_count, 
                                            'offset':offset-count_of_dirty_sent, 
                                            'limit':limit - len(dirty_items) - len(recycled_items)}
                                )
    resp = {}
    for item in items:
        if item[0]:
            resp.update({item[0]: {'type':'post', 'show_order':item[3]}})
        if item[1]:
            resp.update({item[1]: {'type':'question', 'show_order':item[3]}})
        if item[2]:
            resp.update({item[2]: {'type':'user', 'show_order':item[3]}})

    all_other_items = make_resp_multitype(current_user_id, resp, order_key='show_order', reverse_sort=True)
    [all_other_items.insert(dirty_item['dirty_index'], dirty_item) for dirty_item in dirty_items]
    [all_other_items.insert(recycled_item['recycled_index'],recycled_item) for recycled_item in recycled_items]

    return all_other_items

def get_dirty_items(current_user_id, offset, limit, day_count):
    dirty_items = db.session.execute(text("""SELECT discover_list.post,
                                                        discover_list.question,
                                                        discover_list.user,
                                                        discover_list.dirty_index
                                                    FROM discover_list
                                                    WHERE discover_list.is_super=true
                                                        AND discover_list.display_on_day<=:day_count
                                                        AND discover_list.dirty_index>=:lower_limit
                                                        AND discover_list.dirty_index<:upper_limit
                                                """),
                                    params={'day_count':day_count, 
                                            'lower_limit':offset, 
                                            'upper_limit':offset+limit
                                            }
                                    )
    resp = {}
    for item in dirty_items:
        if item[0]:
            resp.update({item[0]: {'type':'post', 'dirty_index':item[3]}})
        if item[1]:
            resp.update({item[1]: {'type':'question', 'dirty_index':item[3]}})
        if item[2]:
            resp.update({item[2]: {'type':'user', 'dirty_index':item[3]}})
    return resp


def get_count_of_dirty_items_sent(offset, day_count):
    result = db.session.execute(text("""SELECT count(1)
                                                    FROM discover_list
                                                    WHERE discover_list.is_super=true
                                                        AND discover_list.display_on_day<=:day_count
                                                        AND discover_list.dirty_index<:offset
                                                """),
                                    params={'day_count':day_count, 
                                            'offset':offset, 
                                            }
                                    )
    dirty_item_sent_count = 0
    for row in result:
        dirty_item_sent_count = row[0]

    return dirty_item_sent_count

def get_recycled_items(current_user_id, offset, limit, day_count):
    # TODO: write query to get N iitems after users B pointer
    items = db.session.execute(
        text("""SELECT 
                    discover_list.post,
                    discover_list.question,
                    discover_list.user,
                    discover_list.id
                FROM discover_list
                WHERE 
                    discover_list.is_super=true
                    AND discover_list.display_on_day<=:day_count
                    AND discover_list.dirty_index>=:lower_limit
                    AND discover_list.dirty_index<:upper_limit
                ORDER BY id DESC
        """),
        params={'day_count':day_count, 
                'lower_limit':offset, 
                'upper_limit':offset+limit
                }
        )
    resp = {}

    for index,item in enumerate(items, start=1):
        if item[0]:
            resp.update({item[0]: {'type':'post', 'recycled_index':-index}})
        if item[1]:
            resp.update({item[1]: {'type':'question', 'recycled_index':-index}})
        if item[2]:
            resp.update({item[2]: {'type':'user', 'recycled_index':-index}})
    return resp



def make_resp_multitype(current_user_id, resp, order_key, reverse_sort=True):    
    users = filter(lambda x:resp[x]['type']=='user', resp)
    posts = filter(lambda x:resp[x]['type']=='post', resp)
    questions = filter(lambda x:resp[x]['type']=='question', resp)

    user_objects = User.query.filter(User.id.in_(users)).all()
    post_objects = Post.query.filter(Post.id.in_(posts)).all()
    question_objects = Question.query.filter(Question.id.in_(questions)).all()

    user_objects_json = [{'type':'user', order_key:resp[u.id][order_key], 'user':guest_user_to_dict(u, current_user_id)} for u in user_objects]

    question_objects_json = questions_to_dict(question_objects, current_user_id)
    question_objects_json = [{'type':'question', order_key:resp[q['id']][order_key], 'question':q} for q in question_objects_json]

    post_objects_json = posts_to_dict(post_objects, current_user_id)
    post_objects_json = [{'type':'post', order_key:resp[p['id']][order_key], 'post':p} for p in post_objects_json]

    final_list = user_objects_json + question_objects_json + post_objects_json
    final_list.sort(key=lambda item: item[order_key], reverse=reverse_sort)

    return final_list



