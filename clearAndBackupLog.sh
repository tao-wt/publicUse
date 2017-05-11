#!/bin/bash
# writer SY60216
# 脚本功能:nohup.out日志文件的备份,只保留3个月log,不带参数

IFS=$' \t\n'

logBackDelte(){
	path_file=$1
	if [ ! -d "${path_file%nohup.out}logBackup" ];then
		mkdir ${path_file%nohup.out}logBackup
	fi
	rm -rf ${path_file%nohup.out}logBackup/nohup_$(date -d "-4 month" +%Y%m).out
	cp $1 ${path_file%nohup.out}logBackup/nohup_$(date -d "-1 month" +%Y%m).out && : > $1
}

for i in $(find /opt/innerapp -mindepth 2 -maxdepth 2 -name nohup.out)
do
	logBackDelte $i
done

