#!/usr/bin/bash
set -e
set -x
IFS=$' \t\n'

send_email(){
    to='feng.2.yu@nokia-sbell.com;irin.zheng@nokia-sbell.com;\
xiaolu-alice.zhao@nokia-sbell.com;tao.8.wang@nokia-sbell.com;\
jane.yu@nokia-sbell.com;peng-angela.liu@nokia-sbell.com;\
jiehua-panda.xiong@nokia-sbell.com;cbts-cb.scm@nokia.com'

    if [ "X$1" == "Xattention" ];then
        subj='Attention please,FDD_baseline daily update for 18 PSI(Trunk_PSI)'
        info='PS_REL have major changes,waiting for your decision to take the PS version to Trunk_PSI ECL.'
    elif [ "X$1" == "Xupdate" ];then
        subj='FDD_baseline daily update for 18 PSI(Trunk_PSI)'
        info='Baseline update successful.'
    else
        echo args status error
        exit 7
    fi

    hVar0='<font face=Courier New, Courier, monospace><pre>Hi, <br/>&#160;&#160;&#160;&#160;\
<font face=verdana>FDD_baseline daily update for 18 PSI(Trunk_PSI).</font><br/>&#160;&#160;'
    hVar2='<br/><table style=margin-left:22.1pt border=1 cellspacing=0 width=730><tr>\
<th>components</th><th>the current version</th><th>\new version</th></tr><tr>\
<td align=center>FDD_Baseline</td><td align=center><font size=4 color=green>'
    hVar4='</font></td><td align=center><font size=4 color=red>'
    hVar6='</font></td></tr><tr><td align=center>PS</td><td align=center><font size=4 color=green>'
    hVar8='</font></td><td align=center><font size=4 color=red>'
    hVar10='</font></td></tr><tr><td align=center>TPI</td><td align=center colspan=2>'
    hVar12='</td></tr><tr><td align=center>NIDD</td><td align=center colspan=2>'
    hVar14='</td></tr></table>Br<br/>cbts-cb<br/></pre></font>'
    msg="${hVar0}${info}${hVar2}${2}${hVar4}${3}${hVar6}${4}${hVar8}${5}${hVar10}${6}${hVar12}${7}${hVar14}"
    
    pushd ../modules
        sed -i '39a \ \ \ \ \ \ \ \ self.smtp.connect("mail.emea.nsn-intra.net", "25")' mail.py
        echo send email...
        python3 -c "from mail import mail;subj = \"${subj}\";msg=\"${msg}\";to = \"${to}\"; mail(subj, msg, None, 'html', to)"
    popd
}

svn_url="https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_LTE_CB_CI/frozen/WMP_FSMR4/"
ecl_url="https://svne1.access.nsn.com/isource/svnroot/BTS_SCM_CLOUD_CB/ECL/CBTS00_MZ_PSI/ECL"
wft_url="https://wft.int.net.nokia.com/ext/builds/?custom_filter[branch]=WMP_trunk&custom_filter\
[baseline]=FL00_FSM4_9999&custom_filter[sorting_direction]=desc&custom_filter[sorting_field]=date&custom_\
filter[items]=1&custom_filter[state][]=released"

if wget $wft_url -O release --no-check-certificate;then
    wftBaseline=$(cat release | grep baseline | sed 's#^ *<baseline>\(.*\)</baseline>#\1#g')
    if [ "X$wftBaseline" = "X" ];then
        echo can not get baeline from release file
        exit 1
    fi
    if wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/${wftBaseline}.xml --no-check-certificate;then
        svn_url=$(cat ${wftBaseline}.xml | awk 'BEGIN{RS="downloadItem"} NR==2' | tr ' ' '\n' | egrep '^http' | sed 's#//.*/isource#//svne1.access.nsn.com/isource#g')
        if [ "X$svn_url" = "X" ];then echo get fdd_baseline svn url failed;exit 1;fi
    else
        echo download fdd_baseline releasenote failed
        exit 1
    fi
else
    echo get newest baseline failed
    exit 1
fi

if ! svn export --force ${ecl_url};then
    echo download ecl failed
    exit 2
fi
eclBaseline=$(cat ECL | egrep '^ECL_FDD_BASELINE' | awk -F= '{print $2}')

if [ "X$wftBaseline" != "X$eclBaseline" ];then
    if ! svn export --force ${svn_url}/.config;then
        echo download baseline config failed
        exit 3
    fi
    ecltpi=$(cat ECL | egrep '^ECL_TPI' | awk -F= '{print $2}')
    eclnidd=$(cat ECL | egrep '^ECL_NIDD_CBTS' | awk -F= '{print $2}')
    eclPsVer=$(cat ECL | egrep '^ECL_PS_REL' | awk -F= '{print $2}')
    wftPsVer=$(cat .config | tr ' ' '\n' | grep _PS_REL_ )
    eclPs=$(cat ECL | egrep '^ECL_PS_REL' | awk -F= '{print $2}' | awk -F_ '{print $5}')
    wftPs=$(cat .config | tr ' ' '\n' | grep _PS_REL_ | awk -F_ '{print $5}')
    echo eclPs=$eclPs wftPs=$wftPs
    if [ "X$eclPs" != "X$wftPs" ];then
        echo Trunk_PSI_ECL $wftBaseline
        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/send_email.py
        # python3 send_email.py --status "attention" --TPI "${ecltpi}" --NIDD "${eclnidd}" --oldBaseline "${eclBaseline}" --newBaseline "${wftBaseline}" --oldPs "${eclPsVer}" --newPs "${wftPsVer}"
        send_email "attention" "${eclBaseline}" "${wftBaseline}" "${eclPsVer}" "${wftPsVer}" "${ecltpi}" "${eclnidd}"
        exit 0
    fi
    echo Trunk_PSI_ECL $wftBaseline
    commit_log="Auto_trgger_Trunk_PSI_ECL_update_$(date -d "+0 month" +%Y_%m_%d_%H%M)"
    curl "http://hzlinb130.china.nsn-net.net:8080/view/tools/job/Modify_ECL/buildWithParameters?token=Auto_Modify_ECL&branch=ecl_test&baseline=${wftBaseline}&commit_log=${commit_log}"
    for((i=0;i<10;i++));do
        sleep 60s
        new_fdd=$(svn cat ${ecl_url} | egrep '^ECL_FDD_BASELINE' | awk -F= '{print $2}')
        if test "X${new_fdd}" = "X$wftBaseline" ;then
            # python3 send_email.py --status "update" --TPI "${ecltpi}" --NIDD "${eclnidd}" --oldBaseline "${eclBaseline}" --newBaseline "${wftBaseline}" --oldPs "${eclPsVer}" --newPs "${wftPsVer}"
            send_email "update" "${eclBaseline}" "${wftBaseline}" "${eclPsVer}" "${wftPsVer}" "${ecltpi}" "${eclnidd}"
            echo update ecl succeed,trigger PSI frozen job
            curl "http://hzlinb130.china.nsn-net.net:8080/job/0_CBTS_FSM3_MZ_PSI_frozen/buildWithParameters?token=Trunk_PSI&force_create=False&check_ecl=True"
            curl "http://hzlinb130.china.nsn-net.net:8080/job/0_CBTS_FSM4_MZ_PSI_frozen/buildWithParameters?token=Trunk_PSI&force_create=False&check_ecl=True"
            if [ "X$?" = "X0" ];then exit 0;fi
        fi
    done
    echo update ecl failed
    exit 5
else
    echo Trunk_PSI_ECL wft baseline no update
    exit 0
fi
