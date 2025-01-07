from astropy.io import fits
from astropy.io import ascii as asc
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import pandas as pd
import os
import regex as re
import shutil as sh

import detectionpipeline as dp

def rmr_careful(dir):
    if (os.path.basename(dir) == 'Random_Storage') or (os.path.basename(dir) == 'Random_Storage'):
        print('Error, check path')
    else:
        print('removing', dir)
        sh.rmtree(dir)

def get_filedir(complete_path):
    all_dirs = complete_path.split('/')[1:-1]
    dirof_file = '/' + '/'.join(all_dirs)
    return dirof_file

def lines_lister(file_path):
    with open(file_path) as opened_file:
        lines_in_file = opened_file.readlines()
    return lines_in_file

def add_weight(complete_img_path):
    split_name = os.path.splitext(complete_img_path)
    weight_img_path = split_name[0] + '_weight' + split_name[1]
    return weight_img_path

def find_param(paramfile, param = 'DIR'):
    list_lines = lines_lister(paramfile)

    for line_index in range(len(list_lines)):
        line = list_lines[line_index]
        if (line.startswith(param)) & (line.find('#') > 0):
            element_list = line.split('#')[0].split(': ')
            output_dir = element_list[1]
        elif line.startswith(param):
                element_list = line.strip().split(': ')
                output_dir = element_list[1]
    return output_dir

def create_space(name_str, n_spaces, end_str):
    for i in range(n_spaces):
        name_str = name_str + ' '
    
    final_str = name_str + str(end_str)

    return final_str

def value_change(list_lines, str_to_change, step_size = 0.1):
    new_lines = list_lines.copy()


    for line_index in range(len(list_lines)):
        line = list_lines[line_index]
        if (line.startswith(str_to_change)) & (line.find('#') > 0):
            
            element_list = line.split('#')[0].split()

            # print('Hello', element_list[1])
            
            element_list[1] = round(float(element_list[1]) + step_size, 3)

            new_value = element_list[1]

            n_spaces = 17 - len(element_list[0])
            space_str = create_space(element_list[0], n_spaces, element_list[1])

            final_str = space_str + ' #' + line.split('#')[1]
            new_lines[line_index] = final_str

        elif line.startswith(str_to_change):

            element_list = line.split()

            element_list[1] = round(float(element_list[1]) + step_size, 3)

            new_value = element_list[1]

            n_spaces = 17 - len(element_list[0])

            final_str = create_space(element_list[0], n_spaces, element_list[1])
            
            new_lines[line_index] = final_str
    
    print('NEW VALUE :', new_value)
        
    return new_lines, new_value

# def param_change(list_lines, str_to_change, add_str = 1):
#     new_lines = list_lines.copy()

#     for line_index in range(len(list_lines)):
#         line = list_lines[line_index]
#         if (line.startswith(str_to_change)) & (line.find('#') > 0):
            
#             element_list = line.split('#')[0].split()

#             element_list[1] = element_list[1] + str(add_str)
#             penult_str = create_space(element_list[0], 1, element_list[1])

#             final_str = penult_str + ' #' + line.split('#')[1]
            
#             new_lines[line_index] = final_str

#         elif line.startswith(str_to_change):
            
#             element_list = line.strip().split()

#             element_list[1] = element_list[1] + str(add_str)
#             final_str = create_space(element_list[0], 1, element_list[1]) + '\n'

#             new_lines[line_index] = final_str
        
#     return new_lines

def addreplace_param(file_lines, param_to_replace, new_str, add_str = False, split_condition = ': '):
    new_lines = file_lines.copy()
    for line_index in range(len(file_lines)):
        line = file_lines[line_index]
        if len(line) == 0:
            continue
        
        if (line.startswith(param_to_replace)) & (line.find('#') > 0):
            line_elements = line.split('#')[0].split(split_condition)
            old_str = line_elements[1].strip()
            if add_str == True:
                final_str = line_elements[0] + split_condition + old_str + str(new_str) + ' #' + line.split('#')[1]
            elif add_str == False:
                final_str = line_elements[0] + split_condition + str(new_str) + ' #' + line.split('#')[1]

            new_lines[line_index] = final_str
            
        elif line.startswith(param_to_replace):
            line_elements = line.split(split_condition)
            old_str = line_elements[1].strip()
            if add_str == True:
                final_str = line_elements[0] + split_condition + old_str + str(new_str) + '\n'
            elif add_str == False:
                final_str = line_elements[0] + split_condition + str(new_str) + '\n'

            new_lines[line_index] = final_str  
    
    return new_lines

def value_reset(list_lines, str_to_change, orig_num):
    new_lines = list_lines.copy()
    for line_index in range(len(list_lines)):
        line = list_lines[line_index]
        if (line.startswith(str_to_change)) & (line.find('#') > 0):
            
            element_list = line.split('#')[0].split()
            
            element_list[1] = orig_num

            n_spaces = 17 - len(element_list[0])
            space_str = create_space(element_list[0], n_spaces, element_list[1])

            final_str = space_str + ' #' + line.split('#')[1]
            new_lines[line_index] = final_str

        elif line.startswith(str_to_change):

            element_list = line.split()

            element_list[1] = orig_num
            n_spaces = 17 - len(element_list[0])

            final_str = create_space(element_list[0], n_spaces, element_list[1])
            
            new_lines[line_index] = final_str
        
    return new_lines

def write_file(new_file_dir, updated_line_list):
    with open(new_file_dir, 'w') as overwritten:
        overwritten.writelines(updated_line_list)

def run_creator(param_file, config_folder, se_knob, start_value, end_value, n_check = 5):
    cwd_out = os.getcwd()

    print(config_folder)

    output_dir = find_param(param_file)
    penultimate_dir = get_filedir(output_dir)
    if os.path.exists(penultimate_dir):
        print('Path exists, deleting')
        rmr_careful(penultimate_dir)
    else:
        print(f'No such path, {penultimate_dir}, continuing')

    os.chdir(config_folder)

    for f in os.listdir():
            if f.endswith('.sex'):
                print(f)
                sex_file_name = f

    os.chdir(cwd_out)

    sex_file = os.path.join(config_folder, sex_file_name)

    og_param_lines = lines_lister(param_file)
    og_sex_lines = lines_lister(sex_file)
    file_n = 1

    for i in np.linspace(start_value, end_value, n_check):
        cwd = os.getcwd()

        new_param_filename = 'use_' + str(os.path.basename(param_file))
        new_sex_filename = 'image.sex'

        os.chdir(config_folder)
        for f in os.listdir():
            if f.endswith('.sex'):
                os.remove(f)
        new_sex_lines, new_value = value_change(og_sex_lines, se_knob, i)
        final_sex_path = os.path.join(config_folder, new_sex_filename)
        write_file(final_sex_path, new_sex_lines)

        # n_index = int(i/(start_value/end_value))
        new_param_lines = addreplace_param(og_param_lines, param_to_replace= 'DIR', new_str= str(new_value), add_str= True) # add_str = file_n

        os.chdir(cwd)
        write_file(new_param_filename, new_param_lines)

        dp.run_pipeline(new_param_filename)

        print(f'DONE: Current {se_knob}: {new_value}, Number: {file_n} \n\n\n\n\n') # {se_knob}: {i} originally: i
        file_n = file_n + 1

    write_file(final_sex_path, og_sex_lines)
    write_file(new_param_filename, og_param_lines)

    print('Completely Done')





def mutlti_image_run(main_paramfile, imgs_dir, outer_dir, loopargs = [1, 3, 3], se_knob = 'DETECT_THRESH'):

    param_lines = lines_lister(main_paramfile)

    starting_val = loopargs[0]
    ending_val = loopargs[1]
    n_steps = loopargs[2]

    sex_param_file = find_param(main_paramfile, 'SEX PARAMETER FILE')

    for file in os.listdir(sex_param_file):
        if file.endswith('.sex'):
            complete_sex_path = os.path.join(sex_param_file, file)
            sex_lines = lines_lister(complete_sex_path)
            SEx_file = complete_sex_path
        else:
            continue
    
    if len(SEx_file) > 0:
        print('Found SEx file in config folder')
    else:
        print('Cannot continue, no SEx param file')
    
    imgs_list = []
    for img_file in os.listdir(imgs_dir):
        if (img_file.find('weight') < 0) & img_file.endswith('.fits'):
            imgs_list.append(img_file)
    
    print(imgs_list)
    
    imgs_indexer = 0
    for img in imgs_list:
        if img == '.DS_Store':
            imgs_indexer = imgs_indexer + 1
            continue
        elif img.find('weight') > 0:
            imgs_indexer = imgs_indexer + 1
            continue
        
        complete_img_path = os.path.join(imgs_dir, img)
        new_lines = addreplace_param(param_lines, param_to_replace= 'IMAGE', new_str= complete_img_path)
        # print(new_lines[3])

        outdir_setter = outer_dir + '/' + os.path.splitext(img)[0] + '/each_run'
        new_lines = addreplace_param(new_lines, param_to_replace= 'DIR', new_str= outdir_setter)


        splitfile = os.path.splitext(main_paramfile)[0]
        cut_name = splitfile.split('_')[0]
        new_paramfile_name = cut_name  + '_main.txt'

        print(sex_param_file)

        write_file(new_paramfile_name, new_lines) #params.txt file for this has been written

        new_weight_path = add_weight(complete_img_path)

        new_sex_lines = addreplace_param(sex_lines, param_to_replace= 'WEIGHT_IMAGE', new_str= new_weight_path, split_condition= '   ')

        write_file(SEx_file, new_sex_lines)

        run_creator(new_paramfile_name, sex_param_file, se_knob, starting_val, ending_val, n_steps)
        print('\n\n')

        imgs_indexer = imgs_indexer + 1
        print(f'DONE WITH IMG: {img}, {imgs_indexer}/{len(imgs_list)}')

    print('COMPLETELY COMPLETELY DONE')
    write_file(SEx_file, sex_lines)

sex_knob = 'DETECT_THRESH'
# starting_value = 0.4
# ending_value = 1
# divs = 7

parameter_file = '/Users/mokshahuja/Desktop/14_RD_pipeline/SEparam_grand.txt'
all_images_dir = '/Users/mokshahuja/Desktop/ASTRES/F606_TestImages'
outer_dir = '/Volumes/Random_Storage/ProtectionLayer/F606_Results_DA1/Thresh'

# # sex_file = '/Users/mokshahuja/Desktop/4p_dark/try_write.txt'
# configuration_folder = '/Users/mokshahuja/Desktop/10-pipeline/config_pipe'

# run_creator(parameter_file, configuration_folder, sex_knob, starting_value, ending_value, divs)

mutlti_image_run(parameter_file, all_images_dir, outer_dir, loopargs = [1, 6, 6], se_knob = 'DETECT_THRESH')