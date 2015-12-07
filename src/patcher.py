import os
import threading

import file_hash
import file_process
import file_parser

# # # # # # # # # # # # # # # # # # # # # # # # #
# This is the core of the script.
#  Calls all of the other functions that were
#  were created.
# # # # # # # # # # # # # # # # # # # # # # # # #

config = file_parser.conf_read()
if 'xml_url' in config['Files']:                    # If xml is defined in configuration file..
    update_xml = config['Files']['xml_url']         #   use that one.
else:
    update_xml = "http://www.uoforever.com/patches/UOP/Updates.xml" # Else, use a pre-defined.

if not config['Files']['uo_directory']:
    dir_list = file_process.getUOPath()             # Just ya. Full path.
    uo_path = ""                                    # Null out uo_path

    for directory in dir_list:
        if not os.path.exists(directory): # Verify that the UO path does indeed exist.. otherwise exit.
            pass
        else:
            print("Updating \"config.ini\" with new directory:")
            config['Files']['uo_directory'] = directory             # Use the uo_directory in configuration
            file_parser.conf_write(config)                          # Write changes to config file.
            print(" Ultima Directory:\n    %s\n" % directory)       # Pretty, pretty display of directory.
            uo_path = directory                                     # Set the path
else:
    uo_path = config['Files']['uo_directory']                       # Use the path in configuration file.
    print(" Ultima Directory:\n    %s\n" % uo_path)

if not uo_path:
    print("Directory not found for Ultima Online.")
    print("You need to add your path to the configuration file called: \"config.ini\"")
    if os.name == "nt":
        input("   Press any key to exit...")        # A pause for windows users.
    exit()

#   Pull the Update(s).xml   #
THREADS = []                    # Empty list for thread names. This is to combine at end.
file_process.cwdPatchDir()      # Changes the directory to the patching directory

le_file = file_process.grab_file(update_xml)            # Downloads the Updater.xml file.
if not le_file:                                         # If it doesn't download, it will simply be skipped.
    print("An error occured with: %s" % update_xml)
else:
    print()
    file_dict = file_parser.xmlparse(le_file)        # Parse the XML file. 
    file_list = file_dict['files']              # Assign the list of files from file_dict (see file_parser.py)
    for le_file in file_list:
        T = threading.Thread(target=file_process.taskFile, args=(config, file_dict[le_file], uo_path, ) ) # Create a thread per update file to leverage bandwidth
        THREADS.append(T)       # Add the thread to the list for joining...

for x in THREADS:
    x.start()       # Start all of the threads.

for x in THREADS:
    x.join()        # Wait for thread to finish before exiting.

if os.name == 'nt':
    input("\nPress any key to continue...")