from logging import NullHandler
import os
import os.path
import saleae
import argparse
import mysql.connector
import csv
from csv import writer
from csv import reader
import time

def validate_path( path, argument_name ):
    if path != None:
        if os.path.isdir(path) == False:
            print('the specified ' + argument_name + ' directory does not exist or is invalid')
            print('you specified: ' + path)
            quit()

parser = argparse.ArgumentParser(description='Saleae Command Line Interface Capture Utility')
parser.add_argument('--capture-count', required=True, type=int, metavar='COUNT', help='number of captures to repeat')
parser.add_argument('--capture-duration', required=True, type=float, metavar='SECONDS', help='duration of each capture in seconds')
parser.add_argument('--save-captures', metavar='PATH', help='if specified, saves each capture to the specified directory')
parser.add_argument('--export-data', metavar='PATH', help='if specified, exports the raw capture to the sepcified directory')
parser.add_argument('--export-analyzers', metavar='PATH', help='if specified, exports each analyzer to the specified directory')
parser.add_argument('--ip', metavar='IP', default='localhost', help='optional, IP address to connect to. Default localhost')
parser.add_argument('--port', metavar='PORT', default=10429, help='optional, Port to connect to. Default 10429')
parser.add_argument('--exit', action='store_true', help='optional, use to close the Logic software once complete')

args = parser.parse_args()

validate_path(args.save_captures, '--save-captures')
validate_path(args.export_data, '--export-data')
validate_path(args.export_analyzers, '--export-analyzers')


s = saleae.Saleae(args.ip, args.port)

for x in range(args.capture_count):
    #set capture duration
    s.set_capture_seconds(args.capture_duration)
    #start capture. Only save to disk if the --save-captures option was specified.
    if args.save_captures != None:
        file_name = '{0}.logicdata'.format(x)
        save_path = os.path.join(args.save_captures, file_name)
        print('starting capture and saving to ' + save_path)
        s.capture_to_file(save_path)
    else:
        #currently, the python library doesn't provide a CAPTURE command that blocks until an ACK is received
        s._cmd('CAPTURE')

    #raw export
    if args.export_data != None:
        file_name = '{0}.csv'.format(x)
        save_path = os.path.join(args.export_data, file_name)
        print('exporting data to ' + save_path)
        s.export_data2(save_path)

    #analyzer export
    if args.export_analyzers != None:
        analyzers = s.get_analyzers()
        if analyzers.count == 0:
            print('Warning: analyzer export path was specified, but no analyzers are present in the capture')
        for analyzer in analyzers:
            file_name = '{0}_CAN.csv'.format(x, analyzer[0])
            save_path = os.path.join(args.export_analyzers, file_name)
            print('exporting analyzer ' + analyzer[0] + ' to ' + save_path)
            s.export_analyzer(analyzer[1], save_path)
        
if args.exit is True:
    print('closing Logic software')
    try:
        s.exit()
    except:
        # ignore errors from exit command, since it will raise due to socket disconnect.
        pass


# Timing code
numoffiles1 = 0
turnoffbit1 = 0
while turnoffbit1 == 0:
    thefilepath = "C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\{}_CAN.csv" .format(numoffiles1)
    file_exists = os.path.exists(thefilepath)
    if file_exists:
        # Open the input_file in read mode and output_file in write mode
        thefile = "C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\{}_CAN.csv" .format(numoffiles1)
        the2ndfile = "C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\{}.csv" .format(numoffiles1) 
        with open(thefile, 'r') as read_obj, \
        open(the2ndfile, 'w', newline="") as write_obj:
        # Create a csv.reader object from the input file object
            csv_reader = reader(read_obj)
            next(csv_reader)
        # Create a csv.writer object from the output file object
            csv_writer = writer(write_obj)
        # Write the Field
            mydict =['Time[s]', 'Packet', 'Type', 'Identifier', 'Control', 'Data', 'CRC', 'ACK', 'RealTime']
            csv_writer.writerow(mydict)
            counter = 0
        # Read each row of the input csv file as list
            for row in csv_reader:
                if row:
        # Append the default text in the row / list
                    default_text = time.time()
                    timestamp = str(default_text)
                    row.append(timestamp)
        # Add the updated row / list to the output file
                    noobj = str(row)
                    a = noobj.replace(" ","")
                    b= a.replace("]","")
                    c = b.replace("[","")
                    write_obj.write(c)
                    write_obj.write('\n')
        numoffiles1 = numoffiles1 + 1

            #csv_writer.writerow("Buffer012")
    else:
        turnoffbit1 = 1
        print("No More files")


"""

     #Eliminate extra line at the end
# Find the number of rows
with open("C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\\0.csv",'r', newline="") as inFile:
    numRows=0
    while(inFile.readline()):
        numRows+=1
    numRows-=1
    print("Num Rows: {}".format(numRows))
    inFile.close()

  
    # Read and Write only the Datalines
    # Opening a file
    inFile = open('C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\\0.csv','r')
    outFile = open('C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\\1.csv', 'w')

    lineNumber=0;
    while lineNumber < numRows:
        if lineNumber==0:
            tempLine=inFile.read()
            tempLine.strip('\n')
            outFile.write(tempLine)
        else:
            outFile.write('\n')
            tempLine=inFile.read()
            tempLine.strip('\n')
            outFile.write(tempLine)
        lineNumber+=1
    inFile.close()
    outFile.close()


"""

# MYSQL code
print("Hello World")
conn = mysql.connector.connect(
    host="localhost",
    database="candata",
    user="root",
    password="morenog" )

# conn = pyodbc.connect(conn_str)
#Trying to figure out the file manipulation here
numoffiles = 0
turnoffbit = 0
while turnoffbit == 0:
    thefilepath = "C:\ProgramData\MySQL\MySQL Server 8.0\Data\candata\{}.csv" .format(numoffiles)
    file_exists = os.path.exists(thefilepath)
    if file_exists:
        createtable = "CREATE TABLE captures{} (Time varchar(255), Packet varchar(255), Type varchar(255), Identifier varchar(255), Control varchar(255), Data varchar(255), CRC varchar(255), ACK varchar(255), RealTime varchar(255));" .format(numoffiles)
        cursor = conn.cursor()
        cursor.execute(createtable)
        display = 'Importing capture number {}'.format(numoffiles)
        print(display)
        with open(thefilepath, 'r') as read_obj:
            csv_reader = reader(read_obj)
            next(csv_reader)
            for row in csv_reader:
                noobj = str(row)
                a = noobj.replace(" ","")
                b = a.replace("[","")
                c = b.replace("]","")
                query = "INSERT INTO captures{} VALUES ({});" .format(numoffiles, c)

                cursor.execute(query)
        numoffiles = numoffiles + 1
    else:
        turnoffbit = 1
        print("No More files") 
