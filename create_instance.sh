#!/usr/bin/env bash
# set -e
IFS=$' \t\n'

helpinfo(){
    echo "------------------------------------------------------"
    echo "-o indicate the operation type:create/delete"
    echo "-i indicate image id"
    echo "-f indicate instance flavor"
    echo "-k indicate the keypair  to inject into this server"
    echo "-n indicate net id"
    echo "-N indicate the number of the instance"
    echo "-s indicate instance name"
    echo "------------------------------------------------------"
    exit 1
}

args_check(){
    if [ "X${operation}" = "Xcreate" ];then
        if [ -z "$image" -o -z "$flavor" -o -z "$key" -o -z "$net" -o -z "$num" -o -z "$server" ];then
            echo The create operation need other args.
            helpinfo
        fi
    elif [ "X${operation}" = "Xdelete" ];then
        if [ -z "$server" ];then
            echo The delete operation need other args.
            helpinfo
        fi
    else
        helpinfo
    fi
}

check_image(){
    #Check whether image exists
    local image_get=$(openstack image list | grep -w $image | wc -l)
    if [ $image_get -eq 1 ];then
        echo image:$image is correct.
    else
        echo image:$image error.
        exit 1
    fi
}

check_flavor(){
    #Check whether the selected specifications exist
    local flavor_get=$(openstack flavor list | grep -w $flavor | wc -l)
    if [ $flavor_get -eq 1 ];then
        echo flavor:$flavor is correct.
    else
        echo flavor:$flavor error.
        exit 1
    fi
}

check_net(){
    #Check whether Net - ID is correct
    local net_get=$(openstack network list | grep -w $net | wc -l)
    if [ $net_get -eq 1 ];then
        echo net:$net is correct.
    else
        echo net:$net error.
        exit 1
    fi
}

check_key(){
    #Check the presence of the key for the presence of the key
    local key_get=$(openstack keypair list | grep -w $key | wc -l)
    if [ $key_get -eq 1 ];then
        echo key:$key is correct.
    else
        echo key:$key error.
        exit 1
    fi
}

get_available_flavor(){
    #local available_core,max_core
    while test $# -ge 3
    do
        if [ $flavor_core -le $3 -o $# -le 3 ];then
            break
        fi
        shift 3
    done
    flavor=$1
    if test $3 -ge 24 ;then
        volume_size=1024
    else
        volume_size=$(($2+10))
    fi
    echo flavor name is $1 and volume size is $volume_size
}

get_floating_ip(){
    #Get the number of available floating IP
    local now_floating_ip=$(openstack floating ip list | grep -w None | sed -e 's/^|//g' -e 's/|$//g' -e 's/ //g' | awk -F \| '{print $2}' | wc -l)
    if [ $now_floating_ip -lt $num ];then
        #If the number of floating IP is less than the number of instances to be created, a new IP is created.
        echo There is not enough IP,create new floating ip.
        local create_num=$((num-now_floating_ip))
        for ((i=1;i<=$create_num;i++));do
            openstack floating ip create datacentre &
        done
        wait
        #Check whether IP is created ok
        for ((x=1; x<=12; x++));do
            sleep 10s
            local new_floating_ip=$(openstack floating ip list | grep -w None | sed -e 's/^|//g' -e 's/|$//g' -e 's/ //g' | awk -F \| '{print $2}' | wc -l)
            if [ $new_floating_ip -ge $num ];then
                echo The number of IP is sufficient
                break
            else
                #Timeout time 2min
                if [ $x -eq 12 ];then
                    echo create floating ip timeout!
                    exit 1
                fi
            fi
        done
    fi
    #Prepare arrays, bind when creating instance
    for ((i=1;i<=$num;i++));do
        float_ip[$i]=$(openstack floating ip list | grep -w None | sed -e 's/^|//g' -e 's/|$//g' -e 's/ //g' | awk -F \| '{print $2}' | head -$i | tail -1)
        echo "float_ip[$i]:${float_ip[$i]}"
    done
}

create_vm(){
    check_image
    check_net
    # check_flavor
    check_key
    >volume_info
    #Error_log for error recording and detection
    if [ -f "error_log" ];then rm -rf error_log;fi
    for ((i=1; i<=$num; i++));do
        #A line of data is read from the pipeline; 
        #if the pipeline is not readable, the process is blocked until a child process completes and writes data to the pipeline.
        read -u 777
        echo $REPLY start
        {
            local my_random=$(head  /dev/urandom  |  tr -dc A-Za-z0-9  | head -c 5)
            local volume_name=${server}${i}_volume$my_random
            local server_name=${server}${i}_$my_random
            echo  create volume ${volume_name}
            # echo ${volume_name} >>volume_info
            #Create a startup volume with a size of 1024G
            openstack volume create --image $image --size $volume_size ${volume_name} || {
                echo "[$volume_name]create volume command error" | tee error_log
                exit 2
            }
            for ((x=1; x<=120; x++));do
                #Wait for volume to create success, timeout time 1H
                echo waitting...
                sleep 30s
                isready=$(openstack volume list | grep ${volume_name} | grep available | wc -l)
                if [ $isready -eq 1 ];then
                    echo the volume ${volume_name} is ready
                    break
                else
                    if [ $x -eq 120 ];then
                        echo the volume ${volume_name} create timeout. | tee error_log
                        exit 2
                    fi
                fi
            done
            echo starting creating $server_name
            #create instance
            openstack server create --flavor $flavor --volume ${volume_name} --user-data build_env.sh --key-name $key --nic "net-id=$net" --wait $server_name || {
                echo "[$server_name] create instance command error" | tee error_log
                exit 3
            }
            echo instance $server_name is ready
            sleep 10s
            echo add floating IP ${float_ip[$i]} to $server_name
            #bind floating ip
            openstack server add floating ip $server_name ${float_ip[$i]} || {
                echo "[${float_ip[$i]}] add floatting ip command error" | tee error_log
                exit 3
            }
            #Write data to the pipe
            echo "The $((i+maxProc))th process" >&777
            echo create instance $server_name finish.
        }&
    done
    wait
    if [ -f "error_log" ];then
        echo there is is some error ,please check!
        exit 5
    fi
    echo all instance create finish.
}

while getopts ":o:i:f:k:n:N:s:" opt; do
    case $opt in
    o)  
        echo "operation is $OPTARG"
        operation=$OPTARG
        ;;
    i)
        echo "image is $OPTARG"
        image=$OPTARG
        ;;
    f)
        echo "flavor is $OPTARG core"
        flavor_core=$OPTARG
        ;;
    k)
        echo "key is $OPTARG"
        key=$OPTARG
        ;;
    n)
        echo "net is $OPTARG"
        net=$OPTARG
        ;;
    N)
        echo "num is $OPTARG"
        num=$OPTARG
        ;;
    s)
        echo "server is $OPTARG"
        server=$OPTARG
        ;;
    \?)
        helpinfo
        ;;
    esac
done

#Create pipeline file FIFO and bind to file descriptor 777
maxProc=3
mkfifo ./fifo.$$ && exec 777<> ./fifo.$$ && rm -f ./fifo.$$
#Set the initial data quantity of the pipeline to determine the maximum concurrent process.
for ((y=1;y<=$maxProc;y++)){
    echo "The ${y}th process" >&777
}

flavor_list=$(openstack flavor list | grep True | \
sed -e 's/^|//g' -e 's/|$//g' -e 's/ //g' | \
awk -F \| '{print $2,$4,$6}' | sort -k3n,3 | tr '\n' ' ')
get_available_flavor $flavor_list
get_floating_ip
create_vm
