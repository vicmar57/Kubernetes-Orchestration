# Authors: Victor Martinov, 307835249, Eran Hoffman, 318524410.


import os
import time
from threading import Thread


def check_cpu_utilization(name):
    #print("getting cpu from: " + name)
    cmd = "kubectl exec " + name + " -t -- top -b -n1 | grep 'Cpu(s)' | awk '{print $2+$4}' | tail -n1 >> cpu.txt"
    os.system(cmd) #execute

# cpu.txt will be the file that save theh current cpu utilization of each pod.
# pods.txt is the temporary text file that will save all the pods existing
t_in = 20       # thereshold for scaling in
t_out = 50      # thereshold for scaling out
QUANTA = 5      # time between checks for scaling (in seconds)
target_service = "php-apache2" # the service that we will autoscale


# before starting the autoscaler the program will ensure that it starts with 2 replicas running
cmd = "kubectl scale deployment/" + target_service + " --replicas=2"
os.system(cmd) #execute

time.sleep(QUANTA) # wait for scaling
 
while 1:
    open('pods.txt', 'w').close()   # clears the pods.txt and cpu.txt files
    open('cpu.txt', 'w').close()
    
    # get the pod list into the text file
    cmd = 'kubectl get pods | grep ' + target_service+ ' >> pods.txt'
    os.system(cmd)
    pods = open("pods.txt",'r').read()   
    pod_line = pods.split('\n') #get pod names
    pod_line.pop() # get rid of last "\n"
    
    threads = []
   
    for row in pod_line:
        # foreach pod we will open a thread that will check its own cpu utlization
        pod_name = row.split(' ')[0] 
        #print(pod_name)
        num_pods = len(pod_line)
        temp_thread = Thread(target = check_cpu_utilization, args = (pod_name,))
        temp_thread.start() #check_cpu_utilization
        threads.append(temp_thread) #thread list to know what's running
    
    #print("got " + str(num_pods) + "pods")
    time.sleep(QUANTA)  
    
    # wait until all the threads closed
    flag_all_threads_dead = 0
    
    while not flag_all_threads_dead:
        flag_all_threads_dead = 1
        
        for thread in threads:
            if thread.isAlive() == 1:
                flag_all_threads_dead = 0
        time.sleep(1)
                
    #print("all threads are dead")
    
    # read the cpu utilizations from the cpu.txt file
    cpus = open("cpu.txt",'r').read()
    cpu_lines = cpus.split("\n")
    cpu_lines.pop() # get rid of last "\n"
    num_cpus = len(cpu_lines)      
    #print(cpus)
    
    # all pods submitted cpu, now calculting avg. cpu and deciding to scale out or scale in
    # or kipping it the same.
    sum_cpu = 0
    for cpu in cpu_lines:
        sum_cpu += float(cpu)
        
    avg_cpu = sum_cpu / num_cpus #calc avg utilization
    flag_scale = 0
    
    if(avg_cpu > t_out): #need to scale UP
        flag_scale = 1
        num_pods += 1
        
    if((avg_cpu < t_in) and (num_pods > 2)): # #need to scale DOWN. 2 pods is the minimal number of running pods 
        flag_scale = 1
        num_pods -= 1
        
    if flag_scale:
        # execute scale in/out
        cmd = "kubectl scale deployment/" + target_service + " --replicas=" + str(num_pods)
        os.system(cmd)
        print( "scaling to: " + str(num_pods))     
        print("Because the average cpu is:" + str(avg_cpu) + "%" ) #reason
    
    
         
cmd = 'rm pods.txt' #cleaning up
os.system(cmd)
cmd = 'rm cpu.txt'
os.system(cmd)

