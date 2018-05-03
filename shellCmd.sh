virt-filesystems --parts -a CBTS18_FSM3_MZ_0700_000081_000000_OAM.qcow2
guestmount -a CBTS18_FSM4_MZ_0700_000155_000001_OAM.qcow2 -m /dev/sda1 --rw ./iso
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
SNAT: Source Network Address Translation，是修改网络包源ip地址的。
DNAT: Destination Network Address Translation,是修改网络包目的ip地址的。
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#du参数
du -sch *
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# rsync数据和文件同步
rsync -arvz --delete --exclude '相对路径' -e "ssh -p 22" ~/test/ zhuser@99.12.90.8:/home/zhuser/test
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
tcpdump src host 99.12.69.165 and dst 99.12.90.100 and udp  -vx -i eth0 -e 
tcpdump dst host 99.12.69.165 and icmp  -vx -i eth0 -e
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 查看物理CPU个数
cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l
# 查看每个物理CPU中core的个数(即核数)
cat /proc/cpuinfo| grep "cpu cores"| uniq
# 查看逻辑CPU的个数
cat /proc/cpuinfo| grep "processor"| wc -l
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
zip bak_conf.zip ./dbconfiglogger.properties ./dbconfig.properties ./webmgr.properties ./WEB-INF/classes/dbconfig.properties ./WEB-INF/classes/config/spring.xml
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 设置硬件时钟及同步系统时间
date
hwclock --show
hwclock --set --date="2017-04-13 08:28:00"
hwclock --hctosys
hwclock --show
date
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#sqlie3语法：字符串链接
update public set publicpath=publicpath||publicname; 
update public where publicname=pub_groupmsg set publicpath=publicpath||"_jboss"; 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# top以批处理发布方式执行
top -b -n 1 | head -5
top -b -n2 -p 27059
netstat -anp | grep 9086 | grep ES	LISHED | grep java | wc -l
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 注意语法格式。
# 备份源中版本
list="msc ucc configcenter eyesight mdbc cmp omc trc mpp"
for i in $list;do ls -ld /home/zhuser/innerapp/$i/$i.jar;done
for i in $list;do mv /home/zhuser/innerapp/$i/$i.jar /home/zhuser/backup/bak_$(date +%F);done
for i in $list;do ls -ld /home/zhuser/backup/bak_$(date +%F)/$i.jar;done
for i in $list;do ls -ld /home/zhuser/innerapp/$i/${i}_lib;done
for i in $list;do mv /home/zhuser/innerapp/$i/${i}_lib /home/zhuser/backup/bak_$(date +%F);done
for i in $list;do ls /home/zhuser/backup/bak_$(date +%F)/${i}_lib;done
# 更新源中版本
for i in $list;do find /tmp/$(date +%m%d) -name $i.jar;done|wc -l
for i in $list;do cp -r $(find /tmp/$(date +%m%d) -name $i.jar) /home/zhuser/innerapp/$i/;done
for i in $list;do ls -ld /home/zhuser/innerapp/$i/$i.jar;done
for i in $list;do find /tmp/$(date +%m%d) -name ${i}_lib;done|wc -l
for i in $list;do cp -r $(find /tmp/$(date +%m%d) -name ${i}_lib) /home/zhuser/innerapp/$i;done
for i in $list;do ls /home/zhuser/innerapp/$i/${i}_lib;done
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#查找正在删除的文件（有进程在使用）
lsof | grep deleted
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 格式化日期输出，可以进行日期的加减计算
date -d "+0 month -1 day" +%Y-%m-%d
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#mysql查询所有表名：
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '数据库名'；
#mysql查询所有数据库名：
SELECT `SCHEMA_NAME`  FROM `information_schema`.`SCHEMATA`;
#远程执行上述查询命令
mysql -upgm -ppgmfetion -h 99.12.90.1 -P 3307 -e  "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'urapport_config'"
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 查看脚本当前目录
dir=$( cd "$( dirname "$0"  )" && pwd  )
dir=$(dirname $0)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#当后台命令使用管道符，并采用nohup命令时，必须对管道符后的每个命令分别使用nohup命令
nohup ls -R|nohup grep dt>/tmp/lsdt.out &
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# sed替换多行
sed '354,355c org.apache.catalina.startup.Bootstrap  "$@"  start   2  >& 1   \\\n     | /usr/local/sbin/cronolog  "$CATALINA_BASE" /logs/catalina.%Y-%m-%d.out >> /dev/ null  &\n' tomcat_pub_cmbc_interface/bin/catalina.sh | egrep -C 1 'org\.apache\.catalina\.startup\.Bootstrap "\$@" start '
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#tcpdump高级语法:多条件配合
tcpdump '(udp and dst host 99.6.150.84) or (icmp and dst host 99.12.90.102)' -vv -x -e
#截获主机210.27.48.1 和主机210.27.48.2 或210.27.48.3的通信
tcpdump host 210.27.48.1 and \ (210.27.48.2 or 210.27.48.3 \)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#linux PS1变量：
#\d ：代表日期，格式为weekday month date
#\H ：完整的主机名
#\h ：主机的第一个名字
#\t ：显示时间为24小时格式(HH:MM:SS)
#\T ：显示时间为12小时格式
#\A ：显示时间为24小时格式(HH:MM)
#\u ：当前用户的账户名
#\v ：BASH的版本信息
#\w ：完整的工作目录名
#\W ：利用basename取得工作目录名称，所以只会列出最后一个目录
#\# ：第几个命令
#\$ ：提示字符，如果是root时，提示符为：#;普通用户为：$
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
python -m flake8 -v '--filename=*.py' . --config=./toolsCheck/flake8/setup.cfg
