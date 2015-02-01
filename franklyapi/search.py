import random
from collections import defaultdict

from sqlalchemy.sql import text

import CustomExceptions

from configs import config

from app import raygun, db, redis_search






keyword_map = {
                'aap'           :['muffler','kejriwal', 'aap', 'aam admi', 'aam aadmi', 
                                'aam admi party', 'aam aadmi party', 'aap party',
                                'politician', 'delhi elections', 'elections',
                                'delhi', 'party'],
                
                'congress'      :['sonia', 'rahul gandhi', 'gandhi', 'congress',
                                    'cong', 'delhi elections', 'elections', 'delhi',
                                    'party', 'politician'],
                
                'bjp'           :['BJP', 'modi', 'bhartiya', 'Janta', 'delhi elections',
                                    'elections', 'delhi', 'party', 'politician']
                }

reverse_index = defaultdict(list)

for name, key_list in keyword_map.items():
    for item in key_list:
        reverse_index[item.strip()].append(name.strip())

top_users = ['arvindkejriwal', 'kiranbedi', 'mufflerman', 'ajaymaken', 'yogendrayadav', 'ashutoshgupta', 'ranveerbrar', 'sunilpal', 'javedakhtar']


def search(cur_user_id, q, offset, limit):
    processed_queries = set()
    
    for i in q.split():
        if q.strip():
            for match in reverse_index[i.strip()]:
                processed_queries.add(match)

    processed_queries = list(processed_queries)
    
    random.shuffle(processed_queries)
    
    select_query = ''
    where_clause = ''
    order_by_title = ''
    order_by_bio = ''
    params = {}

    for i in processed_queries:
        idx = processed_queries.index(i)

        select_query += """ bio like :processed_query_contained_{idx} as process_bio_match_{idx},
                            user_title like :processed_query_contained_{idx} as processed_title_match_{idx}, """.format(idx=idx)

        where_clause += """ or bio like :processed_query_contained_{idx} or user_title like :processed_query_contained_{idx} """.format(idx=idx)

        order_by_title += """process_title_match_{idx} desc, """.format(idx=idx)
        order_by_bio += """process_bio_match_{idx} desc, """.format(idx=idx)

        params.update({'processed_query_contained_{idx}'.format(idx=idx): '%s{pq}%s'.format(pq=i)})

    params.update({ 'query_start':'{q}%'.format(q=q),
                    'query_word_start':' {q}%'.format(q=q),
                    'query_contained':'%{q}%'.format(q=q),
                    'top_users':top_users,
                    'cur_user_id':cur_user_id,
                    'result_offset':offset,
                    'result_limit':limit,
                    })

    results = db.session.execute(text("""SELECT id, username, first_name, profile_picture, user_type, user_title,
                                    username like :query_start or first_name like :query_start as name_start_match,
                                    first_name like :query_word_start as name_match as name_word_start_match,
                                    user_title like :query_contained as exact_title_match,
                                    bio like :query_contained as bio_match,
                                    {select_query}
                                    username in :top_users as top_user_score

                                    from users WHERE 
                                        (   username like :query_start or first_name like :query_start or first_name like :query_word_start
                                            or user_title like :query_contained or bio like :query_contained 
                                            {where_clause}
                                        )
                                        and monkness=-1 
                                        and profile_video is not null
                                        and id != :cur_user_id
                                    
                                    order by name_start_match desc,
                                            exact_title_match desc,
                                            name_word_start_match desc,
                                            {order_by_title}
                                            bio_match desc,
                                            {order_by_bio}
                                            top_user_score desc, 

                                    limit :result_offset, :result_limit""".format( select_query=select_query,
                                                                                   where_clause=where_clause,
                                                                                   order_by_title=order_by_title,
                                                                                   order_by_bio=order_by_bio
                                                                                )

                                    ),
                        
                                params = params
                                )
    
    results = [{'type':'user',
                'user':{'id':row[0],
                        'username':row[1],
                        'first_name':row[2],
                        'last_name':None,
                        'profile_picture':row[3],
                        'user_type':row[4],
                        'user_title':row[5]
                        }
                } for row in results]

    count = len(results)
    next_index = -1
    if count < offset+limit:
        next_index = offset+limit
    
    return {'q':q, 'count':count, 'results':results, 'next_index':next_index}





