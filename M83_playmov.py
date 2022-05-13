import nuke
import nukescripts
import os
import subprocess
import re

def playMOV():
    path = nuke.root().name()
    if os.environ.get('PARTNAME') in ["comp", "remove", "roto"] or os.environ.get('PARTNAME').lower().startswith('comp'):
        path_mov = path.replace("wip/nk/","pub/mov/").replace(".nk",".mov")
    else:
        path_mov = path.replace("wip/nk/","wip/preview/MOV/").replace(".nk",".mov")

    final_mov_path = "" 
    if os.path.exists(path_mov):
        final_mov_path = path_mov

    elif os.environ.get('DELIVERY_CODE1'):
        dir_mov = os.path.dirname(path_mov)
        if dir_mov.split('/')[6] in ['comp', 'lit', 'fx']:
            ext_path = '_'.join(path_mov.split('/')[-1].split('_')[2:])
            file_name = '_'.join([os.environ['DELIVERY_CODE1'], ext_path])
            final_mov_path = os.path.join(dir_mov, file_name)

    else:
        # find version
        dir_mov = os.path.dirname(path_mov)

        if os.path.exists(dir_mov):
            for file in reversed(sorted(os.listdir(dir_mov))):
                find_ver = re.search("v[0-9]{3}", path_mov.split('/')[-1])
                if file.endswith('.mov') and find_ver:
                    final_mov_path = os.path.join(dir_mov, file)
                    break

    """Run RV"""
    if final_mov_path == "":
        nuke.message("The current/latest mov does not exist in the following path:\n" + os.path.dirname(path_mov))
        return
    subprocess.Popen( ['rv', final_mov_path] )
    print 'Play MOV: ', final_mov_path

