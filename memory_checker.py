import os
import os.path
import re
from optparse import OptionParser


INSTANCE_VARIABLE_REGEX = re.compile("\s+\S+\s*\*\s*(\w+);")
RELEASE_SIGNAL_REGEX = re.compile("\s*\[(\w+)\s+release\];")
DEALLOC_REGEX = re.compile("^\s*-\s*\(void\)\s*dealloc")

if __name__ == "__main__":
    print "---- Analyzing memory usage ----"
    parser = OptionParser()
    options, args = parser.parse_args()
    
    folderpath = args[0]
    
    for root, dirs, files in os.walk(folderpath):
        for filename in files:
            classname, extension = os.path.splitext(filename)
            if extension == ".h":
                head_filename = "%s.h" % classname
                impl_filename = "%s.m" % classname
                
                headfile = open(os.path.join(root, head_filename), "r")
                try:
                    implfile = open(os.path.join(root, impl_filename), "r")
                except IOError:
                    continue
                
                instance_variables = {}
                
                is_checking_for_variables = False
                for line in headfile:
                    if line.startswith("@interface"):
                        is_checking_for_variables = True
                        continue
                        
                    if line == "\n" or line.strip() == "" or line.startswith("-"):
                        continue
                        
                    if is_checking_for_variables and line.startswith("}"):
                        is_checking_for_variables = False
                        break
                        
                    if is_checking_for_variables:
                        try:
                            matches = INSTANCE_VARIABLE_REGEX.findall(line)
                            
                            if line.lower().find("weak") == -1:
                                instance_variables[matches[0]] = False
                        except IndexError, e:
                            pass
                        
                is_inside_the_dealloc_method = False
                has_dealloc_method = False
                for line in implfile: 
                    if DEALLOC_REGEX.match(line):
                        is_inside_the_dealloc_method = True
                        has_dealloc_method = True
                        continue
                        
                    if is_inside_the_dealloc_method and line.startswith("}"):
                        is_inside_the_dealloc_method = False
                        break
                        
                    if is_inside_the_dealloc_method:
                        try:
                            matches = RELEASE_SIGNAL_REGEX.findall(line)
                            instance_variable = matches[0]
                            if instance_variable in instance_variables:
                                instance_variables[instance_variable] = True
                        except IndexError, e:
                            pass
                            
                is_forgetting_dealloc = not has_dealloc_method and len(instance_variables)
                if not all(instance_variables.values()) or is_forgetting_dealloc:
                    print "-------------------------------------------"
                    print "MEMORY LEAK", classname
                    if is_forgetting_dealloc:
                        print "Class hasn't got a dealloc method"
                    
                    for key, value in instance_variables.iteritems():
                        if not value:
                            print key
                    
                        
                    
                    