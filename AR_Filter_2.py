
from __future__ import print_function
from time import sleep
from xml.dom import minidom
import struct, os, sys, shutil, itertools, argparse, re

class SearchReport():

    #Argument Parser
    def getArguments(self, args=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input', help="target directory for scanning", required='True')
        parser.add_argument('-o', '--output',  help="Target Output Directory required", default=os.getcwd())
        parser.add_argument('-s', '--search_mode',  help=("Mode 1: Simple List of Files with Issue Items ---- "
                                                        + "Mode 2: Detailed List of Files with Issue Items ---- "
                                                        + "Mode 3: Simple List of Files with Sanitisation Items "
                                                        + "Mode 4: Detailed List of Files with Sanitisation Items"),type=int, choices=[1, 2, 3, 4], required='True')
        args = parser.parse_args()
        return (args.input, args.output, args.search_mode)

    #Read Wav files in a directory
    def ListXMLFiles(self, directory,new):
        filelist = []  
        for root, dirs, files in os.walk(directory):  
            for name in files:
                file2 = name.lower()
                if file2.endswith(".xml".lower()):
                    filepath = os.path.join(root, name)
                    filelist.append(filepath)
            #Output list of files for processing to Processed Files.txt
            os.chdir(new)
            with open('Files To Process.txt', 'w') as filehandle:
                processed_files = len(filelist)
                for listitem in filelist:
                    filehandle.write('%s\n' % listitem)
                filehandle.write("---------------------"+"\r\n"+'Files To Process: '+str(processed_files))
            
            filehandle.close   
        return filelist

    #Create Logs
    def Logs(self, new):
        L = 'Generated_Lists\\'
        os.chdir(new)
        if os.path.exists(L):
            for file in os.listdir(new):
                if file.endswith('.txt'):
                    shutil.move(file, L)
        else:
            os.mkdir(L)
            for file in os.listdir(new):
                if file.endswith('.txt'):
                    shutil.move(file, L)    

    def Detail(self, file_count, files, reference, id_type):
        progress = ProgressBar(file_count, fmt=ProgressBar.FULL)
        item_count = 0
        for file in files:
            if os.stat(file).st_size > 0:
                xmldoc = minidom.parse(file)
                Loop = xmldoc.getElementsByTagName(reference)
                counter = 0
                detail_list = []
                for l in Loop:
                    count = l.getAttribute('itemCount')
                    counter = counter + int(count)
                    TD = l.getElementsByTagName('gw:TechnicalDescription')
                    ID = l.getElementsByTagName(id_type)
                    if (counter > 0):
                        for (t, d) in zip(TD, ID) :
                    #Files which have Issues reported here
                            detail = ('Id: ' + str((d.firstChild.data)) +'     ''Technical Description: ' + str((t.firstChild.data))+"\n")
                            detail_list.append(detail)
                            set(detail_list)
                    else:
                        continue
            else:
                #Files which are not greater than 0kb size are reported here
                with open('Failed Files.txt','a') as errorhandle:
                    errorhandle.write(file+"    -- File Size is zero--"+"\n")
                errorhandle.close()
            if (counter > 0):
                with open('Detailed_List.txt','a+') as filehandle:
                    filehandle.write("\n" + (file) + "\n")
                    filehandle.write('Number of  Items:    ' + str((counter)) + "\n")
                    for dl in detail_list:
                        filehandle.write((dl))
                    item_count += 1
                filehandle.close()
            else:
                continue
            progress.current += 1
            progress()
            sleep(0.1)
        progress.done()
        #Total count of Files reported here
        with open('Detailed_List.txt','a') as filehandle:
            filehandle.write("---------------------"+"\r\n"+'File Count:   ' + str((item_count)))
        filehandle.close()

    def Simple(self, file_count, files, reference):
        progress = ProgressBar(file_count, fmt=ProgressBar.FULL)
        item_count = 0
        for file in files:
            if os.stat(file).st_size > 0:
                xmldoc = minidom.parse(file)
                Loop = xmldoc.getElementsByTagName(reference)
                counter = 0
                for l in Loop:
                    count = l.getAttribute('itemCount')
                    counter = counter + int(count)
            else:
                #Files which are not greater than 0kb size are reported here
                with open('Failed Files.txt','a') as errorhandle:
                    errorhandle.write(file+"    -- File Size is zero--"+"\n")
                errorhandle.close()
            if (counter > 0):
                with open('List.txt','a+') as filehandle:
                    filehandle.write((file) + "\n")
                    item_count += 1
                filehandle.close()
            else:
                #Files with no issues are reported here
                with open('Failed Files.txt','a') as errorhandle:
                    errorhandle.write(file+"    -- File has no items--"+"\n")
                errorhandle.close()
            progress.current += 1
            progress()
            sleep(0.1)
        progress.done()
        #Total count of Files reported here
        with open('List.txt','a') as filehandle:
            filehandle.write("---------------------"+"\r\n"+'File Count:   ' + str((item_count)))
        filehandle.close()

class ProgressBar(object):
    DEFAULT = 'Progress: %(bar)s %(percent)3d%%'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d',
            r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0

    def __call__(self):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining
        }
        print('\r' + self.fmt % args, file=self.output, end='')

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)        

if __name__ == '__main__': 
    source = os.getcwd()
    SR = SearchReport()
    input, output, search_mode = SR.getArguments(sys.argv[1:])
    print("Gathering Files to process...")
    #ListXMLFiles(input, output)
    filelist = SR.ListXMLFiles(input, output)
    count = len(filelist)
    print("Parsing XML Files...")
    if (search_mode == 1):
        print("Mode: Simple Issue List")
        SR.Simple(count, filelist, 'gw:IssueItems')
    elif (search_mode == 2):
        print("Mode: Detailed Issue List")
        SR.Detail(count, filelist, 'gw:IssueItems', 'gw:IssueId')
    elif (search_mode == 3):
        print("Mode: Simple Sanitisation List")
        SR.Simple(count, filelist, 'gw:SanitisationItems')
    elif (search_mode == 4):
        print("Mode: Detailed Sanitisation List")
        SR.Detail(count, filelist, 'gw:SanitisationItems', 'gw:SanitisationId')
    else:
        print("Argument Not Recognised")
    #Collect all text files
    SR.Logs(output)

        
        
        
                        


 




    
