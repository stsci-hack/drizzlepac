"""Primary interface for generating single-visit products.

Basic outline of processing: 

# Interpret poller input
# This creates the list of new input exposures and the relationships
# between the single exposures and the combined products, while defining their
# filenames according to approved naming conventions.
obs_dict_info = gfpf.interpret_obset_input('j9es06.out')
for obs_category in obs_dict_info:
    obs_dict_info[obs_category]['product filenames'] = gfpf.run_generator(obs_category, obs_dict_info[obs_category]["info"])

# Align all images in obset to each other
# This insures all exposures are aligned to each other and (with greater
# chance of success) to a GAIA frame regardless of what occurred in the 
# cal pipeline with each ASN/singleton separately.
#
results = alignimages(files, update_hdr_wcs=True, output=False)
# WCSNAME would need to be set to 'FIT-VISIT-<catalog>' if successful 
#   as called by this code relative fit through new 'output_frame' parameter.
# alignimages updates needed for single-visit and multi-visit support:
#    * add optional 'output_frame' parameter to allow user to specify the name of the final fit 
#    * add optional 'refcatalog' parameter to allow user to provide their own 
#         astrometric reference catalog with WCSNAME of catalog in metadata.
#    * ['refcatalog' parameter only needed for multi-visit support]
#    * update code to define output WCSNAME based on output_frame and/or refcatalog frame
#
#
# Generate a simple total detection product in order to define the full output
# WCS for the single-visit, with rot=0. and scale set for the detector.
# This will generate 'total_drc.fits' as the reference WCS for all products.
# Parameters can be:
# final_rot=0, final_scale=<detector default>
# all steps turned off except final drizzle
#
astrodrizzle.AstroDrizzle('*flc.fits', output='total', configobj='astrodrizzle.cfg')

# Generate the filter level products with (at least):
# resetbits=4096, final_fillval=0., skymethod='match+globalmin',
# final_refimage='total_drc.fits[1]', 
# final_outnx=total_drc.fits[1].header['naxis1'], 
# final_outny=total_drc.fits[1].header['naxis2']
# 
astrodrizzle.AstroDrizzle('@f1files',output=f1name,configobj='astrodrizzle_filter.cfg')
astrodrizzle.AstroDrizzle('@f2files',output=f2name,configobj='astrodrizzle_filter.cfg')
astrodrizzle.AstroDrizzle('@f3files',output=f3name,configobj='astrodrizzle_filter.cfg')

# Generate a total detection product from the CR-flagged exposures
# Parameters would be:
#  resetbits=0, skymethod='match+globalmin', final_fillval=0
# final_refimage, final_outnx, final_outny set the same as filter products
astrodrizzle.AstroDrizzle('*flc.fits', resetbits=0, configobj='astrodrizzle.cfg')

# Create the CR-flagged (based on filter products) single exposure products
# Parameters would be:
#  resetbits=0, skymethod='match+globalmin', final_fillval=0
# final_refimage, final_outnx, final_outny set the same as filter products
for f in files: 
    fname = dpu.get_acs_filters(fits.open(f),delimiter='-') 
    expname = expname_str.format(fname.lower(), f[:8]) 
    astrodrizzle.AstroDrizzle(f,output=expname,resetbits=0, final_fillval=0.,
                              configobj='astrodrizzle_single.cfg')
# Source catalog generation would finish processing
# Create background image (with stats)
# Use background image to create segment-based catalog
# Use background image to create point-based catalog
# catalogs would need to include WCSNAME in meta data 
#  (this would allow these catalogs to be used to generate sky cells)

"""
from mosaic_products import select_product
#
#
# Primary user interface for processing an obset
#
#
def process_obset(obs_info, mosaic=True, cell=True):

    # find total product, regardless of exact label
    # this assumes only 1 total product per obs_info dictionary
    for k in obs_info:
        if 'total' in k:
            total_product = select_product(obs_info[k])
            break
    # Generate total mosaic and single exposure Products
    total_product.generate_mosaic()
    total_wcs = total_product.mosaic_wcs
    # Process all members
    total_product.process_members(mosaic=mosaic, cell=cell)
  
