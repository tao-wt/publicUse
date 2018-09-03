#!/usr/bin/env bash

SCRIPT_PATH=`dirname "${BASH_SOURCE[0]}"`
source ${SCRIPT_PATH}/../../modules/env.sh
if [ -f "fdt.file" ];then rm -f fdt.file;fi
trap "sig_func;" SIGTERM SIGINT SIGHUP SIGABRT

sig_func(){
    echo capture exit signal and start clean operation. | tee clean.log
    if [ -f "fdt.file" ];then
        fdt_ip=$(grep "fdt_ip" fdt.file | awk -F= '{print $NF}')
        fdt_dest=$(grep "fdt_dest" fdt.file | awk -F= '{print $NF}')
        echo fdt_ip=$fdt_ip,fdt_dest=$fdt_dest | tee -a clean.log
        if [ "X$fdt_dest" != "X" -a "X$fdt_ip" != "X" ];then
            sed -i "s/^#*\([^#]*${fdt_ip}$\)/\1/g" ${FDT_HOME}/.fdt_server_${fdt_dest} && echo clean up finish. | tee -a clean.log
        else
            echo info incomplete,no need to clean up. | tee -a clean.log
        fi
    else
        echo no need to clean up. | tee -a clean.log
    fi
    exit 0
}

help(){
    echo "****************************************************************"
    echo "------------upload package using FDT tool -- for CBTS------------"
    echo "./fdt_uploader.sh help             // show help message"
    echo
    echo "./fdt_uploader.sh -t|-tag_name  //required  exp: CBTS00_FSM4_MZ_9999_000682_000000"
    echo "./fdt_uploader.sh -d|-dest    //required    only support HZ|ESPOO "
    echo "./fdt_uploader.sh -s|-src    //not required,folder address need to be uploaded exp: \n
                /xxx/xxx/CBTS00_FSM4_MZ_9999_000682_000000"
    echo 
    echo "****************************************************************"
}

error(){
    echo -e "\033[31;2m$1\033[0m"
    exit 1
}

while (($#>0)); do
    case $1 in
        -t|-tag_name) shift; TAG_NAME=$1; shift;;
        -d|-dest) shift; DEST=$1; shift;;
        -s|-src) shift; SRC=$1; shift;;
        help) help; exit 0;;
        *) error "unsupport parameter: $1";;
    esac
done

# need parameter check
check_parameter(){
    if [ x"${TAG_NAME}" = x ];then
        error "parameter tag_name is required"
    elif [ x"${DEST}" = x ];then
        error "parameter dest is required"
    fi
   
    if [ x"${SRC}" = x ]; then
        echo "user didn't input SRC path, will auto get it from share folder"
    else
        if [ -d ${SRC} ]; then
            echo "use user specific path as SRC: ${SRC}"
        else
            error "user input a invalid src path :${SRC}"
        fi
    fi

}
check_parameter
echo fdt_dest=$DEST >fdt.file
echo "upload ${TAG_NAME} to ${DEST}"
# get DEST path
PRE_PATH=$(get_from_branch_mapping "STORAGE" "${TAG_NAME%_*_*}" | sed 's#,#\/#g')
if [ x${PRE_PATH} = x ]; then
    error "can't find PRE_PATH for ${TAG_NAME} in $BRANCH_MAPPING"
fi

# check if share folder is mounted
if [ "$DEST" == "HZ" ]; then
    #check_share_mount "${HZ_SHARE}" "${HZ_SHARE_LINK}"
    DEST_SHARE=${HZ_SHARE}
    SRC_SHARE=${ESPOO_SHARE}
    if [[ ! -d "${SRC_SHARE}/${PRE_PATH}/${TAG_NAME}" ]]; then
        SRC_SHARE=${ESPOO_MNT_SHARE}
    fi
elif [ "$DEST" == "ESPOO" ]; then
    #check_share_mount "${ESPOO_SHARE}" "${ESPOO_SHARE_LINK}"
    DEST_SHARE=${ESPOO_SHARE}
    SRC_SHARE=${HZ_SHARE}
    if [[ ! -d "${SRC_SHARE}/${PRE_PATH}/${TAG_NAME}" ]]; then
        SRC_SHARE=${HZ_MNT_SHARE}
    fi
else
    error "DEST should be HZ or ESPOO"
fi

if [ x${SRC} = x ]; then
    SRC_PATH=${SRC_SHARE}/${PRE_PATH}/${TAG_NAME}
else
    SRC_PATH=$SRC
fi
echo ${SRC_PATH}| grep -E "${TAG_NAME}[/]?$"
if [ $? -ne 0 ]; then
    error "SRC_PATH must end with same name with tag name: ${TAG_NAME}"
fi

DEST_PATH=${DEST_SHARE}/${PRE_PATH}/${TAG_NAME}
echo "SRC_PATH is: ${SRC_PATH}"
echo "DEST_PATH is: ${DEST_PATH}"
mkdir -p ${DEST_SHARE}/${PRE_PATH}

#if [ -d ${DEST_PATH} ]; then
 #   echo "${DEST_PATH} already exist, move it to a backup folder"
  #  mv ${DEST_PATH} ${DEST_PATH}_bk`date "+%Y%m%d_%H%M"`
    # should wait some time for it really moved to backup folder in share folder
   # sleep 60
#fi

# get a fdt server
FDT_SERVER=""
while true; do
    FDT_SERVER=`grep -E "^server_ip=" ${FDT_HOME}/.fdt_server_${DEST} |head -n 1|awk -F "=" '{print $2}'`
    if [ x${FDT_SERVER} = x ]; then
        echo "no available FDT server now, wait for 1 min and check again"
        sleep 60
    else
        echo "get an idle ${DEST} fdt server: ${FDT_SERVER}, use it!"
        ## use this SERVER and comment it from server list
        sed -i "s/\(.*$FDT_SERVER.*\)/\#\1/g" ${FDT_HOME}/.fdt_server_${DEST} && echo fdt_ip=$FDT_SERVER >>fdt.file
        break
    fi
done

# start FDT transfer
java -jar ${FDT_HOME}/fdt.jar -P 35 -md5 -r -c ${FDT_SERVER} ${SRC_PATH} -d `dirname ${DEST_PATH}`
if [ $? -eq 0 ]; then
    sed -i "s/^\#*\(.*${FDT_SERVER}.*\)$/\1/g" ${FDT_HOME}/.fdt_server_${DEST} && rm -f fdt.file
    if [ -d ${DEST_PATH} ]; then
        echo "${TAG_NAME} has been successfully uploaded to $DEST as ${DEST_PATH}"
    else
        error "FDT show pass, but ${DEST_PATH} doesn't exist on $DEST share folder"
    fi
else
    sed -i "s/^\#*\(.*${FDT_SERVER}.*\)$/\1/g" ${FDT_HOME}/.fdt_server_${DEST} && rm -f fdt.file
    error "error occur when upload ${TAG_NAME} to ${DEST}"
fi
