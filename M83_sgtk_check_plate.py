import shotgun_api3
import nuke
import os
import re

def get_shotgun_module():
    # connect
    sgl = sg_connect()
    sg = sgl.script_auth(script_name="Toolkit", api_key="")
    return sg

sg = get_shotgun_module()

def check_plate():
    try:
        # get plate version data from shotgun
        filters = [
                      ['project.Project.name', 'is', os.environ.get('SHOW')],
                      ['code', 'is', '{0}_{1}'.format(
                        os.environ.get('SEQ'), os.environ.get('SHOT'))
                      ]
        ]
        plate_data = sg.find_one('Shot', 
                                 filters=filters,
                                 fields=['code', 'sg_shot_type', 'sg_plate_ver'])
    except:
        return


    # return if couldn't find any field values
    if not plate_data:
        return


    # convert version integers to regular-expression pattern
    if not plate_data['sg_shot_type'] or not plate_data['sg_plate_ver']:
        return
        
    plate_data['type'] = change_int_to_pattern(plate_data['sg_shot_type'])
    plate_data['ver'] = change_int_to_pattern(plate_data['sg_plate_ver'])

    # mapping latest plate version and pattern
    plate_pattern = '{code}_{type}_{ver}'.format(**plate_data)
    plate_ver = '{code}_{sg_shot_type}_{sg_plate_ver}'.format(**plate_data)

    # check all read nodes
    old_read = []
    for node in nuke.allNodes('Read'):
        file_path = node['file'].value()
        file_path_ver = os.path.basename(file_path)

        # only running in plate directory
        if '/plate/' not in file_path:
            continue

        matched_pattern = re.search(plate_pattern, file_path_ver)
        if matched_pattern and not file_path_ver.startswith(plate_ver):
            old_read.append('[%s] %s' % (node.name(), file_path_ver.split('.')[0]))
        if matched_pattern and plate_ver.split('_')[-2] != file_path_ver.split('_')[-2]:
            old_read.append('[%s] %s' % (node.name(), file_path_ver.split('.')[0]))

    # finally, show up the alert
    if old_read:
        comment = 'The following plate version is not up-to-date:\n\n%s' % '\n'.join(sorted(old_read))
        comment += '\n\n\nLatest version: '
        comment += '\n<b><font color=orange>%s</font></b>' % plate_ver
        nuke.message(comment)

def check_cutIO():
    try:
        # get plate version data from shotgun
        filters = [
                      ['project.Project.name', 'is', os.environ.get('SHOW')],
                      ['code', 'is', '{0}_{1}'.format(
                        os.environ.get('SEQ'), os.environ.get('SHOT'))
                      ]
        ]
        plate_data = sg.find_one('Shot',
                                 filters=filters,
                                 fields=['code', 'sg_cut_in', 'sg_cut_out'])
    except:
        return

    # return if couldn't find any field values
    if not plate_data:
        return


    # convert version integers to regular-expression pattern
    if not plate_data['sg_cut_in'] or not plate_data['sg_cut_out']:
        return

    comment_before = []
    comment_after = []
    if plate_data['sg_cut_in'] and plate_data['sg_cut_out']:
        root_cut_in = nuke.root().firstFrame()
        root_cut_out = nuke.root().lastFrame()
        if root_cut_in != int(plate_data['sg_cut_in']):
            comment_before.append('[Cut In] <b>%s</b>' % root_cut_in)
            comment_after.append('[Cut In] <b>%s</b>' % int(plate_data['sg_cut_in']))
        if root_cut_out != int(plate_data['sg_cut_out']):
            comment_before.append('[Cut Out] <b>%s</b>' % root_cut_out)
            comment_after.append('[Cut Out] <b>%s</b>' % int(plate_data['sg_cut_out']))

    if comment_before:
        comment = 'Please check the shotgrid information.\n'
        comment += '<b>(Sync Frame Range with Shotgun)</b>\n\n'
        comment += 'current setting:\n%s' % ' / '.join(comment_before)
        comment += '\n\nLatest info:'
        comment += '\n<font color=orange>%s</font>' % ' / '.join(comment_after)
        nuke.message(comment)

def check_MetaData():
    try:
        # get plate version data from shotgun
        filters = [
                      ['project.Project.name', 'is', os.environ.get('SHOW')],
                      ['code', 'is', '{0}_{1}'.format(
                        os.environ.get('SEQ'), os.environ.get('SHOT'))
                      ]
        ]
        plate_data = sg.find_one('Shot',
                                 filters=filters,
                                 fields=['code', 'sg_shot_type', 'sg_plate_ver', 'sg_cut_in', 'sg_cut_out'])
    except:
        return

    # return if couldn't find any field values
    if not plate_data:
        return

    # convert version integers to regular-expression pattern
    if not plate_data['sg_shot_type'] or not plate_data['sg_plate_ver']:
        return
    if not plate_data['sg_cut_in'] or not plate_data['sg_cut_out']:
        return

    if nuke.toNode('MetadataCopy'):
        Metadata = nuke.toNode('MetadataCopy')
        plate_type = plate_data['sg_shot_type']
        plate_code = '%s_%s_%s' % (plate_data['code'], plate_type, plate_data['sg_plate_ver'])
        plate_path = '%s/plate/%s/%s/%s.%s' % (os.environ.get('SHOTDIR'), plate_type, plate_code, plate_code, '%04d.exr')
        Metadata['org_path'].setValue(plate_path)
        Metadata['first'].setValue(int(plate_data['sg_cut_in']))
        Metadata['last'].setValue(int(plate_data['sg_cut_out']))

def change_int_to_pattern(text):
    """return a regular-expression pattern from given text"""
    digit = [n for n in text if n.isdigit()]
    pattern = text.replace(''.join(digit), '[0-9]{%s}' % len(digit) if digit else '')
    return pattern

