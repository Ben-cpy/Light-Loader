import os
import json
import sys
import time

import astroid
from astroid import parse
import pack_checker
import processUtil
import remove_option
import magic_finder

import shutil
import rewrite_func
import lazy_load

# change, move the `handler.py` to the `python` folder
app_name = "python"

package_path = "/home/app/python"  # need to copy `handler.py` to ./python directory

used_func_path = "/home/app/python/used_func.txt"
new_used_func_result_output = "/home/app/new_used_func.txt"
final_used_func_result_output = "/home/app/final_used_func.txt"
used_fun_result_step4 = "/home/app/used_func_step4.txt"

entry_list = ['handler.handle'] # serverless function entry
input_entry = ['/home/app/python/handler.py']

# magic_path should not be needed afterwards
magic_path ="/home/app/magic_function/magic_function.txt" # save the magic info to this folder
new_magic_path = "/home/app/magic_function/magic_function_new.txt"
final_magic_path = "/home/app/magic_function/magic_function_final.txt"

output_entry_json = "/home/app/output.json"
output_entry_json_re = "/home/app/call_graph.json" 
pycg_output_path = "/home/app/call_graph.json"  # replace above
used_pack_path = '/home/app/used_pack.txt'

gzip_file = "/home/app/gzipinfo.txt"

project_path = "/home/app/LightLoader"


special_key=["requests.utils.set_environ", 
    "requests.sessions.Session.request", 
    "requests.adapters.HTTPAdapter.send", 
    "urllib3.connectionpool.connection_from_url",
    "numpy.linalg.lapack_lite", 
    "numpy.lib._iotools.NameValidator",
    "numpy.lib._iotools._decode_line",
    "numpy.lib._iotools.easy_dtype",
    "numpy.lib.npyio.loadtxt",
    "numpy.lib.npyio.loadtxt.flatten_dtype_internal",
    "numpy.lib.npyio.loadtxt.read_data",
    "numpy.lib.npyio.loadtxt.pack_items",
    "numpy.lib.npyio.loadtxt.split_line",
    "mpl_toolkits.axes_grid1.parasite_axes.host_axes_class_factory",
    "sklearn.ensemble._forest._parallel_build_trees",
    "pandas.io.parsers._read",
    "pandas.io.excel._xlwt._XlwtWriter",
    "pandas.io.excel._xlsxwriter._XlsxWriter",
    "pandas.io.excel._openpyxl._OpenpyxlWriter",
    "pandas.io.excel._odswriter._ODSWriter",
    "pandas.io.excel._base.ExcelWriter",
    "tensorflow.python.platform.resource_loader.get_path_to_datafile",
    "tensorflow.python.training.saving.saveable_object_util.saveable_objects_for_op",
    "tensorflow.python.keras.saving.saved_model.serialized_attributes.CommonEndpoints",
    "tensorflow.python.training.saver.BaseSaverBuilder",
    "tensorflow.python.summary.writer.writer.FileWriter",
    "tensorflow.python.keras.engine.base_layer.Layer",
    "urllib3.request.RequestMethods",
    "keras.saving.saved_model.load_context.load_context",
    "absl.third_party.unittest3_backport.result.TextTestResult",
    "keras.optimizer_v1.Optimizer"
    ]

def reduce_optional_files(path):
    remove_option.remove_option(path)
    remove_option.remove_unused_pack() # now we 

# we don't need function any more, this magic dir is not needed either 
def find_magic_func():
    if not os.path.exists("/home/app/magic_function"):
        os.makedirs("/home/app/magic_function")
    magic_finder.find(app_name,package_path,magic_path)

def find_used_func():

    # global used_func_result_output
    # used_func_result_output = "/home/app/used_func.txt"
    if not os.path.exists(used_func_path):
        with open(used_func_path, 'w') as file:
            pass

    # replace output_entry_json_re  with pycg_output_path
    processUtil.getDynamicContent_new(entry_list,package_path,pycg_output_path,input_entry,used_func_path)
    # there is no error

def find_used_pack():
    if not os.path.exists(used_pack_path):
        with open(used_pack_path, 'w') as file:
            pass
    pack_checker.getPackageName(used_func_path, package_path, used_pack_path)

    if not os.path.exists(new_magic_path):
        with open(new_magic_path, 'w') as f:
            pass
    # new magic file is less than the first magic 
    magic_finder.find_by_used(app_name,package_path,used_pack_path, new_magic_path)
    
    if not os.path.exists(final_magic_path):
        with open(final_magic_path, 'w') as file:
            pass  
    
    processUtil.moshu_update(new_magic_path, special_key, final_magic_path) # may contains bugs

    global entry_list,output_entry_json_re,input_entry

    
    if not os.path.exists(new_used_func_result_output):
        with open(new_used_func_result_output, 'w') as file:
            pass  

    processUtil.getDynamicContent(entry_list,package_path,output_entry_json_re,input_entry,final_magic_path,new_used_func_result_output)
    # used func will increase
    if not os.path.exists(final_used_func_result_output):
        with open(final_used_func_result_output, 'w') as file:
            pass
    
    special_key_append = ["unittest.TestCase"]
    processUtil.result_process(package_path, new_used_func_result_output,final_used_func_result_output, special_key_append)

def lazy_load_package():
    lazy_load.lazy_load_the_folder(package_path) # containing package-absent error
    lazy_load.repair_folder("/home/app/copy", "/home/app/python") # /home/app/copy would be created automatically

    # Restore the original content of /home/app/python from /home/app/copy
    # This reverts any changes made during lazy loading and ensures the original file structure is maintained.
    shutil.rmtree(package_path)  # Remove the existing python directory
    shutil.copytree("/home/app/copy", package_path) # Copy the backed-up copy
    shutil.rmtree("/home/app/copy")
    # Move the modified handler.py to the function directory.
    os.chdir("/home/app/python")
    shutil.move("/home/app/function/handler.py", "handler.py")
def rewrite():

    if not os.path.exists(used_fun_result_step4):
        with open(used_fun_result_step4, 'w') as f:
            pass

    os.chdir(project_path)
    prefunc_dir = "import-prefunc"

    import processUtil
    processUtil.result_addlibray(final_used_func_result_output, used_pack_path, prefunc_dir, used_fun_result_step4)
    # used_fun_result_step4 is the final obtained used files

    buits_list_file = "built_list.txt"
    
    remove_option.remove_option(package_path)
    
    if not os.path.exists(gzip_file):
        with open(gzip_file, 'w') as file:
            pass
    
    
    rewrite_func.rewrite(app_name, package_path, used_fun_result_step4, gzip_file, buits_list_file)

    os.chdir("/home/app/LightLoader")
    shutil.copy("custom_funtemplate_final_clear.py", "{}/custom_funtemplate.py".format("/home/app"))
    # modified handler.py overwrites the previous one
    os.chdir("/home/app/python")
    shutil.copy("handler.py","/home/app/function/handler.py")
    # this is not sure 
    os.chdir("/home/app")
    shutil.copy("gzipinfo.txt","/home/app/function")


if __name__ == '__main__':
    # Step 1 reduce optional files
    print('step 1')
    reduce_optional_files(package_path)
    
    # Step 2 get handler function location. create entry_point.txt
    # print('step 2')
    # input_entry = serverless_func()

    # Step 3 find magic function
    print('step 3')
    find_magic_func()

    # Step 4 
    print('step 4')
    # entry_point.txt & magic_func.txt
    # construct_graph()

    # Step 5 find the used function 
    print('step 5')
    find_used_func()

    # Step 6 find the used package
    print('step 6')
    find_used_pack()

    # Step 7 lazy load code
    print("step 7")
    lazy_load_package()

    # Step 8 rewrite the code
    print("step 8")
    rewrite()

