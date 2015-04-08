import datetime
from sqlalchemy.sql import text

from app import db

from models import User, Post, Question, DiscoverList, UserScroll
from object_dict import questions_to_dict, guest_user_to_dict, posts_to_dict
from configs import config


def get_discover_list(current_user_id, offset, limit=10, day_count=0,
                      add_super=False, exclude_users=[]):
    # include dirty items
    if not day_count:
        day_count = 0
    day_count = get_day_count(current_user_id)
    super_inclusion = [False, True, None]
    count_of_dirty_sent = 0
    dirty_items = []
    max_id = 0
    user_scroll = None
    if day_count < 10:
        super_inclusion.remove(True)
        dirty_items = get_dirty_items(offset, limit, day_count)
        dirty_items = make_resp_multitype(current_user_id, dirty_items,
                                          order_key='dirty_index',
                                          reverse_sort=False)
        count_of_dirty_sent = get_count_of_dirty_items_sent(offset, day_count)

    # recycle discover feeds
    recycled_items = []
    recycled_upto = 0
    if offset == 0 and current_user_id:
        print 'offset 0'
        user_scroll = UserScroll.query.filter(
            UserScroll.user == current_user_id).first()
        if user_scroll:
            print 'scroll data found'
            max_id = user_scroll.scrolled_upto
            recycled_upto = user_scroll.recycled_upto
            if check_not_added_discover_item(user_scroll.last_visit, max_id):
                print 'last item added was way too puraana'
                if check_user_last_visit_threshold_cross(user_scroll.last_visit):
                    print 'threshold crossed'
                    user_scroll.last_visit = datetime.datetime.now()
                    if user_scroll:
                        if check_recycle_upper_limit_reached(user_scroll.last_recycled_upto, limit-len(dirty_items)):
                            user_scroll.last_recycled_upto = 0
                            user_scroll.recycled_upto = 0
                        else:
                            user_scroll.last_recycled_upto = \
                                user_scroll.recycled_upto
                else:
                    print 'time nhi hua jyada beta.'

                recycled_items, recycled_upto = \
                    get_recycled_items(user_scroll.last_recycled_upto, super_inclusion)
                if len(recycled_items)>0:
                    recycled_items = make_resp_multitype(current_user_id,
                                                         recycled_items,
                                                         order_key='recycled_index',
                                                         reverse_sort=True)
                    user_scroll.recycled_upto = recycled_upto
            else:
                print 'abhi abhi to post add hua h boss'
            
            db.session.commit()
        else:
            print 'scroll data not found.. creating data'
            user_scroll = UserScroll(current_user_id)
            db.session.add(user_scroll)
            db.session.commit()

    # fetch normal discover feeds
    items = db.session.execute(
        text("""SELECT discover_list.post,
                       discover_list.question,
                       discover_list.user,
                       discover_list.id
                FROM discover_list
                WHERE discover_list.removed=false
                  AND discover_list.display_on_day<=:day_count
                  AND discover_list.is_super IN :super_inclusion
                  AND discover_list.display_date <= now()
                ORDER BY discover_list.display_date DESC, discover_list.id DESC
                LIMIT :offset, :limit
            """),
        params={'super_inclusion':super_inclusion,
                'day_count':day_count,
                'offset':offset-count_of_dirty_sent,
                'limit':limit-len(dirty_items)-len(recycled_items)}
        )
    resp = {}

    for item in items:
        max_id = max(item[3], max_id)
        if item[0]:
            resp.update({item[0]: {'type':'post', 'show_order':item[3]}})
        if item[1]:
            resp.update({item[1]: {'type':'question', 'show_order':item[3]}})
        if item[2]:
            resp.update({item[2]: {'type':'user', 'show_order':item[3]}})

    if user_scroll:
        user_scroll.scrolled_upto = max_id
        db.session.commit()

    all_other_items = make_resp_multitype(current_user_id, resp,
                                          order_key='show_order',
                                          reverse_sort=True)
    # merge dirty items
    [all_other_items.insert(dirty_item['dirty_index'],
                                              dirty_item
                                             ) for dirty_item in dirty_items]
    print 'dirty added :',len(dirty_items)
    
    print 'count : ', len(all_other_items)
    # prepend recycled items
    [all_other_items.insert(0, recycled_item)
        for recycled_item in recycled_items]
    print 'recycled :', len(recycled_items)
    
    print 'count : ', len(all_other_items)
    
    print day_count

    return all_other_items

def get_dirty_items(offset, limit, day_count):
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
                                            'offset':offset
                                            }
                                    )
    dirty_item_sent_count = 0
    for row in result:
        dirty_item_sent_count = row[0]

    return dirty_item_sent_count

def get_day_count(current_user_id):
    day_count = 0
    if current_user_id:
        result = db.session.execute(text("""SELECT users.user_since
                                                FROM users 
                                                WHERE users.id=:current_user_id
                                            """),
                                    params={'current_user_id':current_user_id})
        for row in result:
            user_since = row[0]
            day_count = int((
                             datetime.datetime.now()-user_since
                            ).total_seconds())/(3600*24)
    return day_count


def get_recycled_items(last_recycled_upto, super_inclusion):
    try:
        recycled_upto = last_recycled_upto
        print 'recycled_upto ', recycled_upto

        items = db.session.execute(
            text("""SELECT
                        discover_list.post,
                        discover_list.question,
                        discover_list.user,
                        discover_list.id
                    FROM discover_list
                    WHERE 
                        discover_list.id > :start_pointer
                        AND discover_list.is_super in :super_inclusion
                        AND discover_list.display_date <= now()
                    ORDER BY id
                    LIMIT :count
            """),
            params={'start_pointer':last_recycled_upto,
                    'super_inclusion':super_inclusion,            
                    'count':config.DISCOVER_RECYCLE_COUNT
                   }
            )
        resp = {}

        for index, item in enumerate(items, start=0):
            recycled_upto = max(last_recycled_upto, item[3])
            if item[0]:
                resp.update({item[0]: {'type':'post', 'recycled_index':index}})
            if item[1]:
                resp.update({item[1]: {'type':'question', 'recycled_index':index}})
            if item[2]:
                resp.update({item[2]: {'type':'user', 'recycled_index':index}})
        print 'recycled_upto ', recycled_upto

        return resp, recycled_upto
    except Exception as e:
        # print traceback.format_exc(e)
        print e.message
        print 'exception'
        return [], None

def make_resp_multitype(current_user_id, resp, order_key, reverse_sort=True):
    users = filter(lambda x: resp[x]['type'] == 'user', resp)
    posts = filter(lambda x: resp[x]['type'] == 'post', resp)
    questions = filter(lambda x: resp[x]['type'] == 'question', resp)

    users = User.query.filter(User.id.in_(users)).all()
    posts = Post.query.filter(Post.id.in_(posts)).all()
    questions = Question.query.filter(Question.id.in_(questions)).all()

    users = [{'type':'user',
              order_key:resp[u.id][order_key],
              'user':guest_user_to_dict(u, current_user_id)
             } for u in users]

    questions = questions_to_dict(questions, current_user_id)
    questions = [{'type':'question',
                  order_key:resp[q['id']][order_key],
                  'question':q
                 } for q in questions]

    posts = posts_to_dict(posts, current_user_id)
    posts = [{'type':'post',
              order_key:resp[p['id']][order_key],
              'post':p
             } for p in posts]

    final_list = users + questions + posts
    final_list.sort(key=lambda item: item[order_key], reverse=reverse_sort)

    return final_list


def check_user_last_visit_threshold_cross(last_visit):

    print (datetime.datetime.now() - last_visit).total_seconds()
    print config.DISCOVER_RECYCLE_HOURS * 3600
    print ((datetime.datetime.now() - last_visit).total_seconds() >
           config.DISCOVER_RECYCLE_HOURS * 3600)
    return ((datetime.datetime.now() - last_visit).total_seconds() >
            config.DISCOVER_RECYCLE_HOURS * 3600)

def check_not_added_discover_item(last_visit,max_id):
    count = DiscoverList.query.filter(DiscoverList.display_date > last_visit, DiscoverList.id > max_id).\
            count()
    print count, last_visit
    return count == 0
def check_recycle_upper_limit_reached(last_recycled_upto, margin):
    count = DiscoverList.query.filter(DiscoverList.id >= last_recycled_upto,
                                      DiscoverList.display_date <= datetime.datetime.now(),
                                      DiscoverList.is_super == False).count()
    return count < margin
