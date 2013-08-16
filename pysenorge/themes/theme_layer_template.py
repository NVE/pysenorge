'''
Theme layer template.

New Section
===========
    Additional information goes here.

@warning: THIS IS A TEMPLATE SHOWING THE BASIC STRUCTURE OF A THEME_LAYER SCRIPT! DO NOT OVERWRITE!
    ALWAYS USE "SAVE AS..."!


@todo: point one
@todo: point two

@author: kmu
@since: 6. sep. 2010
'''
# Built-in

# Adds folder containing the "pysenorge" package to the PYTHONPATH
import set_pysenorge_path

# Additional

# Own

def model(input_one, input_two):
    '''
    Main algorithm that produces the theme.
    
    @param input_one: description of the first input parameter
    @type input_one: data-type of input_one
    @param input_two: description of the second input parameter
    @type input_two: data-type of input_two
    
    @note: Only the model() function is verified in the corresponding unittest.
    '''
    pass


def main():
    '''
    Loads and verifies input data, calls the model, and controls the output stream. 
    '''
    
    themedir  = 'tmp'
    themename = 'Template theme'
    
    
    usage = "usage: python //~HOME/pysenorge/theme_layers/... [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outdir", 
                      action="store", dest="outdir", type="string",
                      metavar="DIR", default=os.path.join(PNGdir, 'tm_diff_daily'),
                      help="Output directory for PNG file - default: $PNGdir/tm_diff_daily/$YEAR")

    
    # Comment to suppress help
    parser.print_help()

    (options, args) = parser.parse_args()
    
    # Verify input parameters
    

    # Load input data
    
    
    # Setup outputs
    
    
    # If necessary apply unit conversions
    
    
    # Apply model
    THEME = model()
    
    
    # Write to netCDF/BIL/PNG file
    
    
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"
    
if __name__ == "__main__":
    main()
