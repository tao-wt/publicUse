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


