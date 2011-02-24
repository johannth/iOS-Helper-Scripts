import os
import os.path
from optparse import OptionParser


if __name__ == "__main__":
    parser = OptionParser()
    options, args = parser.parse_args()
    folder_path = args[0]
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            newfilename = filename.replace("-hd","")
            if newfilename != filename:
                os.rename(os.path.join(root, filename), os.path.join(root, newfilename))
                print filename, "->",  newfilename
    