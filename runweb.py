from flask import Flask,jsonify,request,render_template,redirect,url_for 
import os 
import getpass 
import configparser
import json 
import time 
import threading
import subprocess
import requests # Getting the request from the json api of the update version on the microcontroller support version path 
user = getpass.getuser() 
Home_path = '/home/'+str(user)+"/" #Home path to get the config file and project setting outside the node generator

Path = '/home/'+str(user)+"/Roboreactor_projects" # getting the file path 
Path_local = '/home/'+str(user)+"/Roboreactor_Gen_config"  # Generate the main path for config gen and code generator

path_serial = "/sys/class/tty"
mem_dir_create = [] 
app = Flask(__name__) 
serial_count = []


                      
                    
def host_info_callback(path_serial):
       
       list_serial = os.listdir(path_serial)
       for l in range(0,len(list_serial)):
          
           if len(list_serial[l].split("ttyACM")) >1: 
              
              if list_serial[l] not in serial_count: 
                  serial_count.append(list_serial[l])      
           if len(list_serial[l].split("ttyUSB")) >1: 
               if list_serial[l] not in serial_count:
                     serial_count.append(list_serial[l])
       for check_serial in serial_count: 
                       if check_serial not in list_serial: 
                                      serial_count.remove(check_serial) #remove the list of the serial in case not found attach on physical devices connection           

@app.route("/",methods=['GET','POST'])  # Initial page start will collect and send the local machine data to update into the front end local machine data
def index():
      
      return render_template("index.html")
      
@app.route('/filepath',methods=['GET','POST'])
def filepathcreate():
      if request.method == 'POST':
            print('Creating path....')
            print(request.get_json())  # parse as JSON
            code_json = request.get_json()
            print("Creating to this path",code_json.get('path'))
            try: 
                 print("Creating directory path")
                 
                 try:
                     config = configparser.ConfigParser()
                     config.add_section('Project_path')
                     print("Start writing config file......")
                     config.set('Project_path','path',code_json.get('path')) 
                     configfile = open(Path+"/config_project_path.cfg",'w') 
                     config.write(configfile) 
                 except: 
                     print("Start writing config file...")
                 os.mkdir(code_json.get('path'),mode=0o777)    
                
            except:
                print("Directory was created")
                message_status = {'dir_status':'created'}
                mem_dir_create.append(message_status)
                if len(mem_dir_create) >1: 
                     mem_dir_create.remove(mem_dir_create[0])
                print(mem_dir_create)
                 

            print(type(code_json)) 
            return 'OK created path', 200 
      else:
        try:
             config = configparser.ConfigParser()    
             config.read(Path+'/config_project_path.cfg') 
             list_data = os.listdir(Path)
             print(list_data)
             path_config = config['Project_path']['path']
             host_info_callback(path_serial)
             message = {'Local_machine_data':{'local_directory':path_config},'Serial_local':serial_count,'Directory_status':{'dir_status':'created'}}  # Getting the data from local machine by running the usb check loop and other local data components conection 
             return jsonify(message)  # serialize and use JSON headers
        except:
             print("Error in reading the config file")
@app.route('/code', methods=['GET', 'POST'])
def hello():

    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON
        code_json = request.get_json()
        print(type(code_json)) 
        #Start generating the file here 
        json_object = json.dumps(code_json) # getting the json config 
        Generated_node = open(Path+"/"+"node_generated.json", "w") 
        Generated_node.write(json_object) 
        time.sleep(2)
        Generated_node = open(Path+"/"+"node_generated.json", "r") 
        data = json.loads(Generated_node.read())
        print("Node of the code",data)
        os.system("python3 roboreactor_config_gen.py")
        return 'OK', 200

    # GET request
    #else:
    #    message = {'greeting':'Hello from Flask!'}
    #    return jsonify(message)  # serialize and use JSON headers

#if __name__ =="__main__":
app.run(debug=True,threaded=True,host="0.0.0.0",port=8000)


