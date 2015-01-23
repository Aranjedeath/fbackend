import flask

def doc_gen(app, resources=None):
    endpoint_rule_mapping = {}

    for i in app.url_map.iter_rules():
        endpoint_rule_mapping[i.endpoint] = i.rule

    list_of_attributes = dir(resources) if resources else dir()

    views = [getattr(list_of_attributes, item) for item in list_of_attributes if type(getattr(list_of_attributes, item)) == flask.views.MethodViewType]

    doc_items = []

    for item in views:
        doc_item = {}
        try:
            url = endpoint_rule_mapping[item.endpoint]
        except AttributeError:
            continue
        
        doc_item['url'] = url
        doc_item['methods'] = item.methods

        for method in item.methods:
            doc_item[method] = {}

            method_func = getattr(item, method.lower())
            method_func_doc = method_func.im_func.func_doc
            doc_item[method]['docstring'] = method_func_doc
            
            arg_objects = []
            try:
                arg_parser = getattr(item, '%s_parser'%(method.lower()))
                arg_objects = arg_parser.args
            except AttributeError:
                pass

            arg_items = []
            for arg in arg_objects:
                arg_items.append({      
                                                        'name'    : arg.name,
                                                        'choices' : arg.choices,
                                                        'default' : arg.default,
                                                        'required': arg.required,
                                                        'location': arg.location,
                                                        'type'    : arg.type.__name__,
                                                        'help'    : arg.help
                                                    })
            arg_items.sort(key=lambda x:x['name'])
            arg_items.sort(key=lambda x:x['required'])
            [i.pop('default') for i in arg_items if i['required']]
            [i.pop('choices') for i in arg_items if not i['choices']]
            [i.pop('help') for i in arg_items if not i['help']]

        doc_items.append(doc_item)

    return doc_items





        











