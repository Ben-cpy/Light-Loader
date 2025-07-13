import json
import os

def read_context(fileinput):
    with open(fileinput,'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict
def find_used_func(entry_list, path, input_json, input_entry,used_func_entry):
    dir_name = "{}/".format(path)
    load_dict = read_context(input_json)

    main_func = []
    use_func = []
    main_func.extend(entry_list)
    use_func.extend(main_func)


    for i in input_entry:
        use_func = get_handler(i, use_func,load_dict)

def get_handler(handler_path, used_func_entry,load_dict):
    # unix change path
    abs_path = os.path.realpath(handler_path)
    reletive_path = os.path.splitext(abs_path)[0].split("\\")[:-1]
    reletive_path = ".".join([path for path in reletive_path]) # use `.` form to present import 

    used_func_entry = seed_func_relation(used_func_entry, load_dict, reletive_path)

    # repeat use seed_func_relation() for what ? 
    add_dir = []
    for fn in used_func_entry:
        fn_list = fn.split(".")
        dirs = reletive_path 
        for i in range(0, len(fn_list)):   
            dirs = "{}.{}".format(dirs,fn_list[i])
            if os.path.exists(dirs.replace(".","\\")):# for win
                add_dir.append(dirs.replace(reletive_path+".",""))
    
    add_dir = list(set(add_dir))
    used_func_entry.extend(add_dir)

    use_func_size = 0
    num = 0
    while len(used_func_entry) > 0:
        num = num + 1
        use_func_size = len(used_func_entry)
        used_func_entry = seed_func_relation(used_func_entry,load_dict,reletive_path)

    return used_func_entry

    

def seed_func_relation(used_func_entry, load_dict, rel_dir):
    used_func = used_func_entry[:]
    
    main_func = list(set(used_func_entry))
    use_func = list(set(use_func))
    result = extend_func(main_func, load_dict)
    use_func.extend(result)
    use_functions = []

# add the dict info into the list
def extend_func(main_func, load_dict):
    list_size = 0
    use_func = []
    main_func = list(set(main_func))
    for i in main_func:
        use_func.append(i)
    num = 0
    while len(use_func) > list_size:
        list_size = len(use_func)
        num = num + 1
        use_func_tmp = []
        for i in use_func:
            use_func_tmp.append(i)
            if i in load_dict.keys():
                use_func_tmp.extend(load_dict[i])
        use_func = list(set(use_func_tmp))
    return use_func
if __name__ == '__main__':
    pass