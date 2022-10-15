import json
import socket
import conn
import call_gen

# Run this first , before running json_read.py
# CODE FOR SERVICE 
sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost',8008))



# Intialize
fp = open("service_result.json","r")
return_data = json.load(fp)
binout = json.dumps(return_data).encode("ascii")
output_file = open("generated_output.json","w")



# Register Service
reg  = call_gen.generate_reg_service("PPtest")
print(f"Reg is {reg}")
test_conn = conn.Conn(sock)
test_conn.send(reg)
regreply = test_conn.recv()
#  validate
if regreply is None:
    print("Breaking This aint working")
    exit(0)
else:
    print(repr(regreply.meta_data))




# Listen 
t_conn = conn.Conn(sock)
result = t_conn.recv()

# validate
if result is not None:
    print(repr(result.meta_data))
    if result.meta_data.data:
        dt = result.meta_data.data
        start = dt[0]
        end = dt[1]
        jo = json.loads((result.data[start:end]))
        output_file.write(json.dumps(jo))
else:
    print("Result was none")
    exit(0)

call_resp_data = call_gen.generate_call_resp(binout,0x71,0x72)
t_conn.send(call_resp_data)


# Listen 
# Some external factor, [preferably a client] has to send a command to shut a service down 
# Here , the service does not care what the message received is, it shuts down anyway 
# But in the real world , some message would be a good idea 
t_conn = conn.Conn(sock)

#get data and do nothing with it 
result = t_conn.recv()

# Send command to close connection
t_conn.send(call_gen.generate_stop_service())
print("Sent data ; Shut down")
