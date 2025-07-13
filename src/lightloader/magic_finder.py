import os
import argparse
import astroid
from astroid import parse

window = False
handle_file = ""
file_name = ""
magic_save = []
magic_save_used = []
handler_entry = []
magic_save_path = "/home/app/magic_function/magic_function.txt"
handler_entry_path = "/home/app/handler_entry.txt" # to be create,

"""
node reference:
node.name                  # function name
node.args                  # function arguments (arguments node)
node.body                  # statement list in function body
node.decorator_list        # function decorator list
node.returns               # function return type annotation (if any)
node.lineno                # starting line number of function definition
node.col_offset            # starting column offset of function definition
node.parent                # parent node containing this function definition
node.doc                   # function docstring
node.async                 # boolean indicating if it's an async function
node.type_comment          # function type annotation (if any)
"""
def function_transform(node: astroid.FunctionDef ):
    newnode = node
    parent_func = [ node.name ] # all parent function that call this function
    
    while newnode.parent:
        if newnode.parent.__class__ == astroid.FunctionDef or newnode.parent.__class__ == astroid.ClassDef: 
            parent_func.append(newnode.parent.name)
            newnode = newnode.parent
        else: # common node
            newnode = newnode.parent

    road=handle_file.split("/")  # array type
    str_name=road.pop().split(".")
    parent_func.append(str_name[0]) # get app name without suffix

    """get the path of the file"""
    while len(road)>0: # add complete path to XX.xx.xx format
        x=road.pop()
        if x==file_name:
            break
        parent_func.append(x)

    parent_func= [i for i in parent_func if(len(str(i))!=0)] # remove len=0 
    parent_func.reverse()
    magic_func = ["__getitem__", "__setitem__", "__delitem__","__len__", "__iter__"]

    # magic func, add it
    if node.name in magic_func:
        if not ".".join(parent_func) in magic_save:
            magic_save.append(".".join(parent_func))
    

    if (node.args.args) and (len(node.args.args) == 1):
        if node.args.args[0].__class__ == astroid.AssignName:
            if node.args.args[0].name == 'req' and node.name == 'handle':
                handler_entry.append(".".join(parent_func))
    
    return node


def function_transform_by_used(node: astroid.FunctionDef ):
    body = []
    newnode = node
    parent_func = [ node.name ]

    while newnode.parent:
        if newnode.parent.__class__ == astroid.FunctionDef or newnode.parent.__class__ == astroid.ClassDef:
            parent_func.append(newnode.parent.name)
            newnode = newnode.parent
        else:
            newnode = newnode.parent
            continue

    road=handle_file.split("/")
    str_name=road.pop().split(".")
    parent_func.append(str_name[0])

    """get the path of the file"""
    while len(road)>0:
        x=road.pop()
        if x==file_name:
            break
        parent_func.append(x)

    parent_func= [i for i in parent_func if(len(str(i))!=0)]
    parent_func.reverse()
    moshu_func = ["__getitem__", "__setitem__", "__delitem__","__len__", "__iter__"]

    if node.name in moshu_func:
        if not ".".join(parent_func) in magic_save_used:
            magic_save_used.append(".".join(parent_func))
    
    return node


def get_content(file_path):
    global handle_file
    # file_path (./function/handler.py /index.py /python/{package})
    for root, dirs, files in os.walk(file_path): # just for user write function
        for file in files:
            if file.endswith(".py"):
                handle_file = os.path.join(root, file) # open each .py file
                with open(handle_file,'r',encoding='utf-8') as f:
                    content = f.read() 
                tree = parse(content)


def save_magic_function():
    if not os.path.exists(magic_save_path):
        with open(magic_save_path,'w') as f:
            f.write('')
    with open(magic_save_path,'w', encoding='utf-8') as f:
        for i in magic_save:
            f.write(i+"\n")


def save_handler_function():
    if not os.path.exists(handler_entry_path):
        with open(handler_entry_path,'w') as f :
            f.write('')
    with open(handler_entry_path,'w', encoding='utf-8') as f:
        for i in handler_entry:
            f.write(i+"\n")

def save_file(file_path,file):
    if os.path.exists(file_path):
        with open(file_path):
            pass    
    with open(file_path,'w', encoding='utf-8') as f:
        for i in file:
            f.write(i+"\n")


def find(dir_name, file_path,magic_path):
    global file_name, magic_save_path
    astroid.MANAGER.register_transform(astroid.nodes.FunctionDef, function_transform)
    file_name = dir_name
    magic_save_path = magic_path
    get_content(file_path)

    save_magic_function()

    save_handler_function() 

def find_by_used(dir_name, package_path, used_func_path, magic_output_path):
    dirset=[]
    for line in open(used_func_path):
        line = line.strip('\n')
        if len(line)>0:
            dirset.append(line)

    global file_name,handle_file # handle_file is change, and it is a global var
    file_name = dir_name
    astroid.MANAGER.register_transform( astroid.nodes.FunctionDef, function_transform_by_used )
    # check if these .py files are in our used_func
    for root, dirs, files in os.walk(package_path):
        for name in files:
            if name.endswith('.py'):
                handle_file = ""+os.path.join(root, name)
                for dir_i in dirset:
                    dir_i = dir_i.replace(".","/")
                    if dir_i in handle_file:
                        with open(handle_file,'r',encoding='utf-8') as f:
                            content = f.read()
                        tree = parse(content)
    save_file(magic_output_path,magic_save_used)

if __name__ == "__main__": 
    pass
