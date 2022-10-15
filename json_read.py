import json
import socket 
import conn
import call_gen

# Install conn.py , call_gen.py and bbb_parser.py globally, [I still have not  packaged this]
# Or copy the files in this directory into the directory containing all those files 

# Important NOTE : Run this only after running json_service.py, 
# In the arbiter, if the caller does not call a valid service , the arbiter (bbb) might crash
# Sequence of operation is thus as follows:
#   -   start BBB
#   -   start json_service.py
#   -   start json_read.py
# What is expected to happen :
# json_read.py calls json_service.py , sends data from generated.json 
# and json_service responds back with data from service_result.json


# Caller CODE 
sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost',8008))
test_conn = conn.Conn(sock)


# Intialise 
fp = open("generated.json","r") 
data = json.load(fp)
binout = json.dumps(data).encode("ascii")

# Register caller, that calls the service named PPtest 
reg  = call_gen.generate_reg_caller(["PPtest"])
print(reg)
test_conn.send(reg)
regreply = test_conn.recv()

# Validate 
# Parse information to get a REGCALLER ACK 
if regreply is None:
    print("Breaking This aint working")
    exit(0)
else:
    print(repr(regreply.meta_data))
print("Ok almost done")

# Each Caller/Service has an ID inside BBB arbiter , calls are performed by calling the ID 
# Get IDs of services called from REGCALLER ACK 
p = regreply.meta_data.data
start = p[0]
end=p[1]
ids = regreply.data[start:end]
id_list = []
ids_iter = iter(ids)
while True:
    try:
        a=next(ids_iter)
        b=next(ids_iter)
        id_list.append((a,b))
    except StopIteration:
        break
print(f"Id List is {id_list}")


t_conn = conn.Conn(sock)
# NOTE : id_list[0] is the ID of the caller (i.e This one, json_read.py) in BBB
# NOTE : id_list[1] is the ID of the service corresponding to the name PPTest
# REGCALLER ACK returns [CALLER_ID| SERVICE_ID1|SERVICE_ID2...]
# The block below calls the service PPTest
call_data = call_gen.generate_call(binout,id_list[1])   # This may break 
t_conn.send(call_data)
result = t_conn.recv()
if result is not None:
    print(repr(result.meta_data))
    if result.meta_data.data:
        p = result.meta_data.data
        start = p[0]
        end = p[1]
        try:
            out = json.loads((result.data[start:end]))
            print(f"Result is : {out}")
        except:
            print("Could not parse json")
else:
    print("Not Working")

# Just FYI, this is what the variable result looks like here:
# Message 
# meta_data
#   ParseResult
#       - result type 
#       - Frame
#           - header 
#           - data_size
#           - result_type
#           - data [start,end]
#           - text [text]
# data 
#   binary data 

# A service cannot shut itself down, [This is a result of a massive design flaw, but it feels Ok for now]
# It must be shutdown either through the arbiter or through the caller 
# The following block , tho it does not send anything of significance , shuts the service down because the service is engineered to work like this 
# So as of now, the service designer is responsible for handling how it will shut down , which I feel is reasonable
t_conn = conn.Conn(sock)
t_conn.send(call_gen.generate_call("AAAAAAA".encode('ascii'),id_list[1])) 

# Doesn't care what response it gets, but, like I said, upto you herr designer 
result = t_conn.recv()

# After this , the caller shuts itself down 
t_conn = conn.Conn(sock)
t_conn.send(call_gen.generate_stop_caller())
