import random
from collections import defaultdict

from sqlalchemy.sql import text

import CustomExceptions

from configs import config

from app import raygun, db, redis_search

reverse_index = defaultdict(list)

reverse_index['sportsman']    = ['wrestler', 'shooter', 'cricketer', 'tennis']
reverse_index['sportsperson'] = ['wrestler', 'shooter', 'cricketer']
reverse_index['experts']      = ['marketing', 'guru', 'yoga', 'doctor', 'astrologer', 'tattoo', 'entrepreneur', 'dancer', 'advocate', 'anchor', 'psychologist']
reverse_index['television']   = ['masterchef', 'actor', 'actress', 'stylist', 'media', 'dancer', 'anchor', 'makeup', 'tattoo', 'models']
reverse_index['tv']           = ['masterchefs', 'actor', 'actress', 'media', 'dancer', 'anchor', 'makeup', 'tattoo', 'models']
reverse_index['stars']        = ['actor', 'actress', 'media', 'dancer', 'anchor', 'makeup', 'tattoo', 'models']
reverse_index['authors']      = ['author']
reverse_index['fashion']      = ['lifestyle']

keyword_map = {
                'aap'           :[
                                    'muffler', 'mufflerman', 'kejriwal', 'aap', 'aam admi', 'aam aadmi', 
                                    'aam admi party', 'aam aadmi party', 'aap party',
                                    'politician','politicians', 'political', 'politics', 'delhi elections', 'elections', 'election', 'delhi', 'dilli', 'party',
                                ],
                
                'congress'      :[
                                    'sonia', 'rahul', 'gandhi', 'congress', 'cong', 'manmohan',
                                    'politician','politicians', 'political', 'politics', 'delhi elections', 'elections', 'election', 'delhi', 'dilli', 'party',
                                ],
                
                'bjp'           :[
                                    'bjp', 'modi', 'bhartiya', 'Janta', 'bedi', 'kiran',
                                    'politician','politicians', 'political', 'politics', 'delhi elections', 'elections', 'election', 'delhi', 'dilli', 'party',
                                ],

                'mufflerman'    :[
                                    'arvind', 'kejriwal', 'aap', 'aam admi', 'aam aadmi', 
                                    'aam admi party', 'aam aadmi party', 'aap party',
                                    'politician','politicians', 'political', 'politics', 'delhi elections', 'elections', 'election', 'delhi', 'dilli', 'party',
                                    'comedy', 'comedian', 'comedians'
                                ],
                
                'kiranbhedi'    :[
                                    'bjp', 'modi', 'bhartiya', 'Janta',
                                    'politician','politicians', 'political', 'politics', 'delhi elections', 'elections', 'election', 'delhi', 'dilli', 'party',
                                    'comedy', 'comedian', 'comedians', 'bedi'
                                ],
                'politician'    :['aap', 'bjp', 'congress' 'politician','politicians', 'political', 'politics', 'delhi elections', 'elections', 'election', 'delhi', 'dilli', 'party'],

                'poet'          :['authors', 'authours', 'music', 'bollywood', 'stars', 'artists', 'writers'],

                'actor'         :['actors', 'bollywood', 'stars', 'movies', 'tv', 'television', 'models'],
                'actress'       :['actors', 'bollywood', 'stars', 'movies', 'tv', 'television', 'models'],
                'stylist'       :['bollywood', 'stars', 'makeup', 'tv', 'television', 'models'],
                'media'         :['television', 'tv', 'anchors'],
                'radio'         :['rj', 'radio', 'jockeys', 'fm'],
                'singer'        :['singers', 'music', 'musicians'],
                'music'         :['singer', 'singers'],
                'chef'          :['chefs', 'master', 'cooks', 'food'],
                'entrepreneur'  :['businessman', 'entrepreneurs', 'startups', 'company', 'founders']
                }


for name, key_list in keyword_map.items():
    for item in key_list:
        reverse_index[item.strip().lower()].append(name.strip().lower())

top_users = ['arvindkejriwal', 'kiranbedi', 'mufflerman', 'kiranbhedi', 'ajaymaken', 'yogendrayadav', 'ashutoshgupta', 'ranveerbrar', 'sunilpal', 'javedakhtar']



def search(cur_user_id, q, offset, limit):
        
    processed_queries_freq = defaultdict(int)
    q = q.lower()
    for i in q.split():
        processed_queries_freq[i] += 1
        if i.strip():
            for match in reverse_index[i.strip()]:
                processed_queries_freq[match] += 1
        
        if len(i) > 3:
            for key, value in reverse_index.items():
                if i in key:
                    for match in value:
                        processed_queries_freq[match] += 1

    #print processed_queries_freq
    processed_queries = processed_queries_freq.keys()

    processed_queries.sort(key=lambda i:processed_queries_freq[i], reverse=True)

    select_query = ''
    where_clause = ''
    order_by_processed_username = ''
    order_by_title = ''
    remove_current_user = ''
    params = {}


    for i in processed_queries:
        idx = processed_queries.index(i)

        select_query += """ user_title LIKE :processed_query_contained_{idx} AS processed_title_match_{idx},
                            username LIKE :processed_query_contained_{idx} AS processed_username_match_{idx}, """.format(idx=idx)

        where_clause += """OR user_title LIKE :processed_query_contained_{idx} OR username LIKE :processed_query_contained_{idx} """.format(idx=idx)

        order_by_processed_username += """processed_username_match_{idx} DESC, """.format(idx=idx)
        order_by_title += """processed_title_match_{idx} DESC, """.format(idx=idx)

        params.update({'processed_query_contained_{idx}'.format(idx=idx): '%{pq}%'.format(pq=i)})

    params.update({ 'query_start':'{q}%'.format(q=q),
                    'query_word_start':' {q}%'.format(q=q),
                    'query_contained':'%{q}%'.format(q=q),
                    'top_users':top_users,
                    'cur_user_id':cur_user_id,
                    'result_offset':offset,
                    'result_limit':limit,
                    })

    print params

    if cur_user_id:
        remove_current_user = "and id!=:cur_user_id"


    query = text("""SELECT id, username, first_name, profile_picture, user_type, user_title, bio,
                                    username LIKE :query_start OR first_name LIKE :query_start AS name_start_match,
                                    first_name LIKE :query_word_start AS name_word_start_match,
                                    user_title LIKE :query_contained AS exact_title_match,
                                    bio LIKE :query_contained AS bio_match,
                                    profile_video IS NOT NULL as profile_video_exists,
                                    (SELECT count(1) FROM questions WHERE questions.question_to=users.id) AS question_count,
                                    (SELECT count(1) FROM user_follows WHERE user_follows.followed=users.id AND user_follows.unfollowed=false) AS followed_count,
                                    (SELECT count(1) FROM user_follows WHERE user_follows.followed=users.id AND user_follows.user=:cur_user_id AND user_follows.unfollowed=false) AS is_following,
                                    (SELECT 4*CAST(search_defaults.show_always AS UNSIGNED)+CAST(search_defaults.score AS UNSIGNED) FROM search_defaults WHERE search_defaults.user=users.id AND search_defaults.category in (SELECT search_categories.id FROM search_categories WHERE search_categories.name LIKE :query_start)) AS search_default,
                                    {select_query}
                                    username IN :top_users AS top_user_score

                                    FROM users WHERE 
                                        (   users.username LIKE :query_start OR users.first_name LIKE :query_start OR users.first_name LIKE :query_word_start
                                            OR users.user_title LIKE :query_contained OR users.bio LIKE :query_contained
                                            OR users.id IN (SELECT search_defaults.user FROM search_defaults WHERE search_defaults.category LIKE :query_start)
                                            {where_clause}
                                        )
                                        and monkness=-1
                                        
                                        {remove_current_user}

                                    ORDER BY search_default DESC, 
                                            user_type DESC,
                                            name_start_match DESC,
                                            name_word_start_match DESC,
                                            profile_video_exists DESC,
                                            is_following DESC,
                                            question_count DESC,
                                            top_user_score DESC,
                                            {order_by_processed_username}
                                            exact_title_match DESC,
                                            {order_by_title}
                                            followed_count DESC
                                            

                                    LIMIT :result_offset, :result_limit""".format( select_query=select_query,
                                                                                   where_clause=where_clause,
                                                                                   order_by_title=order_by_title,
                                                                                   order_by_processed_username=order_by_processed_username,
                                                                                   remove_current_user=remove_current_user,
                                                                                )

                                    )

    sql_results = db.session.execute(query, params = params)
    print query
    results = []
    for item in sql_results:
        print item
        print ''
        results.append(item)


    from controllers import is_following

    results = [{'type':'user',
                'user':{'id':row[0],
                        'username':row[1],
                        'first_name':row[2],
                        'last_name':None,
                        'profile_picture':row[3],
                        'user_type':row[4],
                        'user_title':row[5],
                        'bio':row[6],
                        'is_following':is_following(row[0], cur_user_id) if cur_user_id else False,
                        'channel_id':'user_{user_id}'.format(user_id=row[0])
                        }
                } for row in results]
    #results.sort(key=lambda x: top_users.index(x['user']['username'].lower()) if  x['user']['username'].lower() in top_users else 999)

    count = len(results)
    next_index = -1
    if count:
        next_index = offset+limit

    return {'q':q, 'count':count, 'results':results, 'next_index':next_index}
