#!/usr/bin/env bash
#统计指定ip:port下数据库中表格名字.
#usage：
#		bash countDbTables.sh ip1 port1 ip2 port2 ip3 port3 


IFS=$' \t\n'

while test $# -ge 2
do
	for i in $(mysql -upgm -ppgmfetion -h $1 -P $2 -e "SELECT \`SCHEMA_NAME\`  FROM \`information_schema\`.\`SCHEMATA\`" | egrep -v '+-|SCHEMA_NAME')
	do
		mysql -upgm -ppgmfetion -h $1 -P $2 -e  "SELECT 	LE_NAME FROM INFORMATION_SCHEMA.	LES WHERE 	LE_SCHEMA = \"${i}\"" | egrep -v '+-|	LE_NAME' | awk -v ip=$1 -v port=$2 -v db=$i 'BEGIN{print ip,port,db}{printf("\t\t%s\n",$0);}'
	done
	shift 2
done

