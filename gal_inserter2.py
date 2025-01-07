import os
import numpy as np
from astropy.io import fits
import pandas as pd


# Changes[0]: Removed the generator. Used randint[14, 67] 


# Changes[1]: Location: def add_udg, line [86] 
# Changes[1]: updimg was only the original image + the final galaxy
# Changes[1]: So I made sure that it updates each time 

# rng = np.random.default_rng(123) #sets the rng #orig seed = 1234

# print(rng)

def add_udg(container, ogimg, imgnum, size_as, mag, rng, C=26.2299, B=0.06):
    '''
    This function inserts 3 ultra diffuse galaxies into random spots
    in an image.

    -----

    Parameters:

    container (string): the path to the directory the image will
    be saved in.

    ogimg (string): the path to the image to be used as a base.

    imgnum (string): the name of the new image.

    size_as (integer): the size in arcseconds of the galaxy to
    be inserted.

    mag (integer): the magnitude of the galaxy to be inserted.

    C (float): the reference magnitude for converting magnitude
    to flux. Default value is 26.2299.

    B (float): scale factor between arcseconds and pixels. Default
    value is 0.13.

    -----

    Outputs:

    updimg (array): the image with galaxies inserted.
    '''

    #for storing info
    gals = []
    xpos = []
    ypos = []
    fluxes = []
    sizes = []
    sizes_as = []
    fwhms = []
    mags = []

    #   print('OGIMG: ', ogimg)

    y, x = np.mgrid[0:ogimg.shape[0], 0:ogimg.shape[1]] #get the size of the image

    ##############
    updimg = None
    
    ###############
    for z in range(3): #inserts 3 galaxies
        #Changes[0]
        rngx = rng.integers(low=0, high=ogimg.shape[1]) #chooses an x
        rngy = rng.integers(low=0, high=ogimg.shape[0]) #and y coordinate


        # Nan values are white spaces, and are not on the actual image.
        # Void spaces in the image are actually have 0 as the value, producing a dark spot.
        while not np.isfinite(ogimg[rngy, rngx]): #Checks to see if the image has a NAN value at those coordinates
            rngx = rng.integers(low=0, high=ogimg.shape[1]) #chooses an x
            rngy = rng.integers(low=0, high=ogimg.shape[0])

        s = size_as/B                             #converts size from as to px (0.06 as/px)
        flux = 10**((C-mag)/2.5)                  #converts mag to flux (m = C - 2.5log(F))
        a = flux/(2*np.pi)                        #for later use (flux = 2*pi*a)
        r = np.sqrt((x-rngx)**2+(y-rngy)**2)      #calulates radius
        gal = (a/s**2)*np.exp(-r/s)               #makes the galaxy
        fwhm = -s*np.log(0.5)*2                   #calculates fwhm
        
        ##############
        #Changes[1]
        if updimg is None:
            updimg = ogimg + gal                    
        else:
            updimg = updimg + gal                     #adds the galaxy
        
        #stores all the important generated values
        gals.append(z+1)
        xpos.append(rngx)
        ypos.append(rngy)
        fluxes.append(flux)
        mags.append(mag)
        sizes_as.append(size_as)
        sizes.append(s)
        fwhms.append(fwhm)

    #saves everything to a csv file
    bork = {'galaxy #': gals, 'x value': xpos, 'y value': ypos, 'flux (e-/s)': fluxes, 'magnitudes': mags, 'size (as)': sizes_as, 'size (px)': sizes, 'FWHM (px)': fwhms}
    chad = pd.DataFrame(bork)
    chad.to_csv(container + "/" + imgnum + "/" + str(imgnum) + '_ag'+ str(size_as) + '_' + str(mag)+'.csv')
        
    return updimg



def run_5_times_1_img(image, size_as, mag, rngen, extension = 0):

    '''
    This function creates 5 images with 3 inserted galaxies each of the
    same magnitude and size, and puts each into its own folder.

    -----

    Parameters:

    image (string): the path to the image to be used as a base.

    size_as (integer): the size in arcseconds of the galaxy to
    be inserted.

    mag (integer): the magnitude of the galaxy to be inserted.
    
    -----

    Outputs:

    None
    '''

    imgname = os.path.splitext(os.path.basename(image))[0] #get the image's filename
    img = fits.open(image) #open the image and get the relevant data
    imgdata = img[extension].data
    imghdr = img[extension].header
    img.close()

    #makes sure the size identifier in the image name is always 2 characters long
    strsize_as = str(size_as)
    if len(strsize_as) < 2:
        strsize_as = '0' + strsize_as

    container =imgname + "_" + strsize_as + "-" + str(mag) #make an output folder
    os.mkdir(container)

    z = 1

    for i in range(5): #runs the galaxy insertion function 5 times -- CHANGED TO 2

        imgnum = imgname + "_" + str(z) #make a numbered name for the new image
        os.mkdir(container + '/' + imgnum) #make a folder for it

        img_w_gals = add_udg(container, imgdata, imgnum, size_as, mag, rngen) #add galaxies

        final_img = fits.PrimaryHDU(img_w_gals, imghdr) #save the final image
        final_img.writeto(container + "/" + imgnum + "/" + imgnum + "_ag" + str(size_as) + '_' + str(mag)+ ".fits")

        z += 1


def run_range(image, startsize, endsize, sizestep, startmag, endmag, magstep, ext):
    '''
    This function runs the galaxy insertion code for the full range of 
    sizes and magnitudes specified by the user.

    -----

    Parameters:

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

    -----

    Outputs:

    None
    '''
    rng = np.random.default_rng(12345) #sets the rng #orig seed = 1234
    for mag in range(startmag, endmag+1, magstep): #iterates through the magnitudes
        for size in range(startsize, endsize+1, sizestep): #iterates through the sizes
            print('Currently on magnitude', mag, 'and size', size)
            run_5_times_1_img(image, size, mag, rng, ext)