import os, os.path, sys , datetime

for x in sys.argv[1:]:
    folderpath = str(x) 
    for root, _, files in os.walk(folderpath, topdown=False):
        for f in files:
            fullpath = os.path.join(root, f) ##Combines the directory & filename, assigns to variable
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
                os.remove(fullpath)
