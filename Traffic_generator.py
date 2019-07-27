
# Authors: Victor Martinov, 307835249, Eran Hoffman, 318524410.


#Building a traffic generator
#In this part of the assignment you will be building a python-based traffic generator that will issue
#requests to the service, with variable intensity, as specified below.
#
#The traffic generator should support the following API for running it (all arguments are
#mandatory):
#
#traffic_generator --filename Y --interval X --init Z --ip W --verbose B
#
#Where:
#● Y is a filename (full path) which will contain a single integer. This file can be
#updated/accessed independently of your traffic generator.
#● X is a time interval (in seconds) such that once the traffic_generator starts running, it
#accesses the file specified by Y every X seconds, and reads the integer appearing in Y
#into some internal variable lambda. if X<=0 then the file is never accessed.
#● Z is the initial value for lambda when traffic_generator is executed (note that if X<=0,
#then the value of Z will be used throughout the execution of traffic_generator). This could
#be very useful in testing your traffic generator.
#● W is the exposed IP address (IPv4, in the format a.b.c.d) or the domain name (http://…)
#through which your service can be reached.
#● B is a boolean (should take values in {0,1}). If B=0, this value is ignored. 
#
#If B=1 the traffic generator should produce as output to STDOUT the number of 
#requests generated in each second, in the following format:
#[​s​]: [​k​s​] requests
#Where
#● “[​s​]” is the second number (should be an increasing number, produced for each
#second, without the square brackets)
#● “[​k​s​]” is the number of requests generated in second​s


import sys
import requests
import time
import random
import threading


class trafGen:
    
    #constructor
    def __init__(self, _path, _interval, _lambda, _ip, _verbose):
		# get arguments
        self._file      = open(_path, 'r') #open file for all threads to use
        self._interval  = _interval
        self._lambda    = _lambda
		#add "http://"
        if "http://" not in _ip :
            self._ip = "http://" +  _ip
        else :
            self._ip = _ip
        self._verbose   = _verbose
        
        self._reqs = 0 #to count requests
        self._secNum = 0 #to keep track of passed seconds since start
        self.run_event = threading.Event() #a flag to stop execution
        self.run_event.set()
        self.doYaThang()
        
        
    def update_lambda(self): #every _interval seconds
        if self.run_event.is_set():
            self._lambda = float(self._file.readline())
            self._file.seek(0)
            #print('new lambda: ' + str(self._lambda)) #for debugging
            threading.Timer(self._interval, self.update_lambda).start() #schedule next update
        else:
             self._file.close()
 #           print("thread update_lambda closing")
            
            
    def print_verbose(self): #every second
        if self.run_event.is_set():
            print("{}: {} requests".format(self._secNum, self._reqs))# as requested
            self._reqs = 0
            self._secNum += 1
            threading.Timer(1.0, self.print_verbose).start()  #schedule next print
 #       else:
 #           print("thread print_verbose closing")

    
    def send_request(self):
        #try:
        req = requests.get(url = self._ip, data = "http post request")# send http request with thread
		
			#DEBUG
            #print(req.content)
            #grequests.send(req, grequests.Pool(1))

            #if req.status_code != 200:
               #raise requests.exceptions.HTTPError("Status Code Error! ")
        #except requests.exceptions.HTTPError as e:
            #print("HTTPError: ", e , req.status_code)
        #except Exception as exc:
            #print("exc: ", exc)
        
        
    def doYaThang(self):
        try:
            threading.Timer(self._interval, self.update_lambda).start() #update lambda every _interval secs

            if(self._verbose == 1): # if _verbose == 1 print, else don't.
                threading.Timer(1.0, self.print_verbose).start() #update lambda every 1 sec, if B==1
            
    
            while 1: 
                time_till_next_req = random.expovariate(self._lambda) #sample exp. variable with mean 1/_lambda to generate next "arrival"
				#time_till_next_req = -math.log(1.0 - random.random()) / float(self._lambda) 
                #time_till_next_req =  numpy.random.exponential(1/self._lambda) #exponetial dist. with param 1/_lambda
                time.sleep(time_till_next_req) #wait until needing to send
                threading.Thread(target = self.send_request).start()#send request
                self._reqs += 1 #count requests
            
        except KeyboardInterrupt:
            print ("")
            self.run_event.clear() #clear flag to stop all future threads



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN PROGRAM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    try: #get parameters
    #    print(len(sys.argv))
        if(len(sys.argv) == 11 and str(sys.argv[1]) == "--filename" and
        str(sys.argv[3]) == "--interval" and str(sys.argv[5]) == "--init" and
        str(sys.argv[7]) == "--ip" and str(sys.argv[9]) == "--verbose"): #check that API is OK
            _path       = str(sys.argv[2])    # --filename Y
            _interval   = int(sys.argv[4])    # --interval X to access file and do: lambda <- file content
            _lambda     = int(sys.argv[6])    # --init Z - initial value for lambda
            _ip         = str(sys.argv[8])    # --ip W - exposed IPv4 addr or domain name through which your service can be reached
            _verbose    = int(sys.argv[10])    # --verbose B - If B=0, this value is ignored. if = 1 than print "[​s​]: [​k​s​] requests" every second
            trafGen(_path, _interval, _lambda, _ip, _verbose) #generate http GET requests   
            
        else:
            raise #raise exception if API incorrect
    
    except Exception as e:
        print("MAIN: " ,e) #raise exception if other err

        
if __name__ == '__main__':
    main()
