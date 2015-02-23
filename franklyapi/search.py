import random
from collections import defaultdict

from sqlalchemy.sql import text

import CustomExceptions

from configs import config

from app import raygun, db, redis_search

reverse_index = defaultdict(list)

reverse_index['sportsman'] = ['wrestler', 'shooter', 'cricketer', 'tennis']
reverse_index['sportsperson'] = ['wrestler', 'shooter', 'cricketer']
reverse_index['experts'] = ['marketing', 'guru', 'yoga', 'doctor', 'astrologer', 'tattoo', 'entrepreneur', 'dancer', 'advocate', 'anchor', 'psychologist']
reverse_index['television'] = ['masterchef', 'actor', 'actress', 'stylist', 'media', 'dancer', 'anchor', 'makeup', 'tattoo', 'models']
reverse_index['tv'] = ['masterchefs', 'actor', 'actress', 'media', 'dancer', 'anchor', 'makeup', 'tattoo', 'models']
reverse_index['stars'] = ['actor', 'actress', 'media', 'dancer', 'anchor', 'makeup', 'tattoo', 'models']
reverse_index['authors'] = ['author']

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
        if i.strip():
            for match in reverse_index[i.strip()]:
                processed_queries_freq[match] = processed_queries_freq[match]+1
        
        if len(i) > 3:
            for key, value in reverse_index.items():
                if i in key:
                    for match in value:
                        processed_queries_freq[match] = processed_queries_freq[match]+1

    print processed_queries_freq
    processed_queries = processed_queries_freq.keys()

    processed_queries.sort(key=lambda i:processed_queries_freq[i], reverse=True)

    select_query = ''
    where_clause = ''
    order_by_processed_username = ''
    order_by_title = ''
    order_by_bio = ''
    remove_current_user = ''
    bio_query = ''
    bio_where = ''
    bio_order = ''
    params = {}


    for i in processed_queries:
        idx = processed_queries.index(i)

        select_query += """ user_title like :processed_query_contained_{idx} as processed_title_match_{idx},
                            username like :processed_query_contained_{idx} as processed_username_match_{idx}, """.format(idx=idx)

        where_clause += """or user_title like :processed_query_contained_{idx} or username like :processed_query_contained_{idx} """.format(idx=idx)

        order_by_processed_username += """processed_username_match_{idx} desc, """.format(idx=idx)
        order_by_title += """processed_title_match_{idx} desc, """.format(idx=idx)
        order_by_bio += """processed_bio_match_{idx} desc, """.format(idx=idx)

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

    if len(q.strip()) > 4:
        bio_where = " or bio like :query_contained "
        bio_query = " bio like :query_contained as bio_match, "



    query = text("""SELECT id, username, first_name, profile_picture, user_type, user_title, bio,
                                    username like :query_start or first_name like :query_start as name_start_match,
                                    first_name like :query_word_start as name_word_start_match,
                                    user_title like :query_contained as exact_title_match,
                                    {select_query}
                                    username in :top_users as top_user_score

                                    from users WHERE 
                                        (   username like :query_start or first_name like :query_start or first_name like :query_word_start
                                            or user_title like :query_contained
                                            {where_clause}
                                        )
                                        and monkness=-1
                                        
                                        {remove_current_user}

                                    order by user_type desc,
                                            name_start_match desc,
                                            top_user_score desc,
                                            {order_by_processed_username}
                                            exact_title_match desc,
                                            {order_by_title}
                                            name_word_start_match desc

                                    limit :result_offset, :result_limit""".format( select_query=select_query,
                                                                                   where_clause=where_clause,
                                                                                   order_by_title=order_by_title,
                                                                                   order_by_processed_username=order_by_processed_username,
                                                                                   remove_current_user=remove_current_user,
                                                                                )

                                    )

    results = db.session.execute(query, params = params)

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
    results.sort(key=lambda x: top_users.index(x['user']['username'].lower()) if  x['user']['username'].lower() in top_users else 999)

    count = len(results)
    next_index = -1
    if count >= offset+limit:
        next_index = offset+limit

    return {'q':q, 'count':count, 'results':results, 'next_index':next_index}





