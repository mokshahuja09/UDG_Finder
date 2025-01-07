import os
import shutil as sh
import gal_inserter2 as gi 
import finder
import detection_rates as dr
from astropy.io import fits

# This runs only for one mag and 2 sizes, 20 and 5-6 respectively.
# This is going to be used to develop a checking mechanism for the code. 


def extract_params(paramfile):
        '''
    This function extracts the parameters the user has set for
    the program from a text file.

    ------

    Parameters:

    paramfile (string): The path to the text file containing the 
    user's preferred parameters.

    ------

    Outputs:

    dir (string): the path to the directory all of the program's 
    output will be sent to.

    image (string): the path to the image to be used as a 
    base for inserting fake galaxies.

    startsize (integer): the smallest size of galaxy to be
    generated, in arcseconds.

    endsize (integer): the largest size of galaxy to be
    generated, in arcseconds.

    sizestep (integer): the step size for the program to
    use as it increments through galaxy sizes, in 
    arcseconds.

    startmag (integer): the lowest magnitude of galaxy to
    be generated.

    endmag (integer): the highest magnitude of galaxy to be
    generated.

    magstep (integer): the step size for the program to
    use as it increments through galaxy magnitudes.

    ext (integer): fits files have data in either extension 0,
    or extension 1. This defines that number.

    sexparams (string): the path to the Source Extractor
    parameter file to be used.
    '''
        def get_sex_params(config_folder):# This function extracts the
            n_param_file = 0              #   config file to run the SExtractor
            sex_params = None
            for file in os.listdir(config_folder):
                if file.endswith('.sex'):
                    # print(file)
                    sex_params = os.path.join(config_folder, file)
                    n_param_file = n_param_file + 1
            if n_param_file == 0:
                print('param file not found')
            return sex_params
        
        file = open(paramfile)
        params = []
        lines = file.readlines()
        file.close()

        for n_line in  range(2, len(lines)):
            line_list = lines[n_line].strip().split(': ')
            # print(f'{n_line} : {line_list}')
            # for word in line_list:
            #     print(word)
            # print('\n')
            try:
                req_num = int(line_list[1])
                params.append(req_num)
                #print('stuff', type(req_num))
            except:
                params.append(line_list[1])
                continue
        # print(params)

        dir = params[0]
        image = params[1]
        startsize = params[2]
        endsize = params[3]
        sizestep = params[4]
        startmag = params[5]
        endmag = params[6]
        magstep = params[7]
        ext = params[8]
        config_folder = params[9]
        sexparams = get_sex_params(params[9])

        #print(*(param for param in params), sep ='\n\n')
        return dir, image, startsize, endsize, sizestep, startmag, endmag, magstep, ext, sexparams, config_folder


def run_sextr(dir, sexparams):

    '''
    This function runs the images with inserted galaxies through Source
    Extractor.

    -----

    Parameters:

    dir (string): the path to the directory that image to be used is
    located in.

    -----

    Outputs:

    None
    '''

    for img in os.listdir(dir): #runs through every file in the directory
        if img.endswith('.fits'): #and checks if it's a .fits file
            print(img) #tells the user which images is being run 
            imgname = os.path.splitext(os.path.basename(img))[0] #removes the .fits from the filename
            catname = dir + '/output_cold_' + imgname + '.cat' #the name for the SEx catalog output file
            checkname = dir + '/check_' + imgname + '.fits' #the name for the SEx check image

            #Assembling the command to be passed to Source Extractor
            basecmd = 'sex ' + dir+'/'+img + ' -c '+sexparams
            catcmd = '-catalog_name ' + catname 
            checkcmd = '-checkimage_name ' + checkname
            sexcmd = basecmd + ' ' + catcmd + ' ' + checkcmd
            
            print(sexcmd)
            os.system(sexcmd) #passing the command to the operating system 


def run_pipeline(paramfile):
    '''
    This function runs the whole pipeline.

    -----

    Parameters:

    paramfile (string): The path to the text file containing the 
    user's preferred parameters.

    -----

    Outputs:

    None
    '''

    #extracting the parameters
    dir, image, startsize, endsize, sizestep, startmag, endmag, magstep, ext, sexparams, config_dir = extract_params(paramfile)
    print('Parameters read')

    def rm_copy(config_folder, out_folder):
        if os.path.exists(out_folder):
            if (os.path.basename(out_folder) == 'desktop') or (os.path.basename(out_folder) == 'Desktop'):
                print('Error, check path \n\n\n\n\n\n\n\n')
            else:
                sh.rmtree(out_folder)
                print('Deleted old', out_folder)
                sh.copytree(config_folder, out_folder)
                print('Inserted config folder', config_folder) # Inserts the configuration and param files for Source Extractor into
                                                           # a Folder in which it can be accessed 
        elif not os.path.exists(out_folder): #makes the directory if it doesn't exist
            sh.copytree(config_folder, out_folder)
            print('Inserted config folder:', config_folder,  'made new out folder')
    
    rm_copy(config_dir, dir)
    os.chdir(dir) #switches to it

    #inserting galaxies
    print('Starting galaxy insertion')
    # imgdata = fits.getdata(image, ext)
    # print(f"Loaded image data with shape: {imgdata.shape}")
    gi.run_range(image, startsize, endsize, sizestep, startmag, endmag, magstep, ext)



    #iterating through the subdirectories to find images 
    for container in os.listdir(dir):
        #print('CWD START', os.getcwd())
        check_dir = os.path.join(dir, container)
        if not os.path.isdir(check_dir): # Checks if it isn't a directory, ie if it's a file, it continues. 
            continue
        for subcont in os.listdir(dir + '/' + container):
            print("Running SEx for:") #running Source Extractor on the image
            #print('CWD MID', os.getcwd())
            run_sextr(dir + "/" + container + "/" + subcont, sexparams)
            for img in os.listdir(dir + '/' + container + '/' + subcont):
                if img.endswith('.fits') and not img.startswith('check'):
                    print('Finding matches for', img)
                    finder.find_matches(dir + '/' + container + '/' + subcont, img) #find matches for the image
                    os.chdir(dir)
                    #print('CWD END', os.getcwd())
    
    #get and record detection rates for the images
    print("Getting detection rates")
    rates_list, sizemag_pairs = dr.get_rates(dir)
    dr.record_rates(rates_list, sizemag_pairs, dir, startsize, endsize, sizestep, startmag, endmag, magstep)
    print('Finished')


# run_pipeline(paramfile='image2params.txt')