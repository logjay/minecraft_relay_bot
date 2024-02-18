import json    

def write_dict(this_dict, file_path):
    with open(file_path,'w+') as tempjson:
        tempjson.write(json.dumps(this_dict, sort_keys=True, indent=2))

def get_dict(file_path):
    with open(file_path,'r') as tempjson:
        return json.loads(tempjson.read())
    