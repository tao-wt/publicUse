#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import copy
import re
import configparser
import argparse
import shutil
import subprocess
from xml.dom.minidom import parse
import xml.dom.minidom
# import cbts_freezer.checkout_cbts_base
sys.path.append("..")
from modules import mail
import modules.SCM_lib as SCM
import modules.logger as logger
from modules.config_parser import ConfigParse


def send_email(status):
    log.info('-' * 54)
    log.info('start send eamil')
    if status == 'attention':
        subj = 'Attention please,FDD_baseline daily update for %s' % args.branch
        info = 'PS_REL have major changes,waiting for your '\
            'decision to take the PS version to Trunk_PSI ECL.'
    elif status == 'update':
        subj = 'FDD_baseline daily update for %s' % args.branch
        info = 'Baseline update successful.'
    else:
        print('args status error')
        sys.exit(1)
    log.info('\n subject is:\n %s\n info is:\n %s' % (subj, info))

    TO = "tao.8.wang@nokia-sbell.com;cbts-cb.scm@nokia.com"
    message = '<font face="Courier New, Courier, monospace"><pre>Hi, <br/>'\
        '&#160;&#160;&#160;&#160;<font face="verdana">FDD_baseline '\
        'daily update.</font><br/>'\
        '&#160;&#160;{}<br/>'\
        '<table style="margin-left:22.1pt" border="1" cellspacing="0"'\
        ' width="730">'\
        '<tr><th>components</th><th>the current version</th><th>new '\
        'version</th>'\
        '</tr><tr><td align="center">FDD_Baseline</td>'\
        '<td align="center"><font size="4" color=green>{}</font></td>'\
        '<td align="center"><font size="4" color=red>{}</font></td>'\
        '</tr><tr><td align="center">PS</td>'\
        '<td align="center"><font size="4" color=green>{}</font></td>'\
        '<td align="center"><font size="4" color=red>{}</font></td>'\
        '</tr><tr><td align="center">TPI</td><td align="center" colspan="2">'\
        '{}</td></tr><tr><td align="center">NIDD</td>'\
        '<td align="center" colspan="2">{}</td></tr></table>'\
        'Br<br/>'\
        'cbts-cb<br/></pre></font>'
    msg = message.format(info, ecl_dict_orig['FDD_BASELINE'],
        new_baseline, ecl_dict_orig['PS_REL'], new_fdd_dict['PS_REL'],
        ecl_dict_orig['TPI'], ecl_dict_orig['NIDD_CBTS'])

    mail.mail(subj, msg, subtype='html', to_addrs=TO)
    

class configParser(configparser.ConfigParser):
    """
    optinxform in module ConfigParse return optionstr.lower()
    this class for redefine optionxform
    """

    def optionxform(self, optionstr):
        return optionstr.strip()


def shell_cmd(cmd):
    """
    run shell cmd
    """
    result = subprocess.getstatusoutput(cmd)
    if result[0] == 0:
        return result[1]
    return False


def getPsEnvPath(psVerXml):
    """
    get ps_env download path
    """
    repoUrl = get_Xml_Item(read_xml(psVerXml), "repositoryUrl")[0].\
        childNodes[0].data.strip()
    repoBranch = get_Xml_Item(read_xml(psVerXml),
        "repositoryBranch")[0].childNodes[0].data.strip()
    psEnvRepoUrlStr = "{}/{}".format(repoUrl, repoBranch)
    log.info(psEnvRepoUrlStr)
    return re.sub(r'https?://[^/]*', '', psEnvRepoUrlStr)


def commit_ecl(local_repo):
    '''
    svn commit function
    '''
    os.chdir(local_repo)
    commit_command = 'svn ci . -m "{} -by {}" '.format(args.commit, args.committer)
    log.info('svn commit,wait....\n' + SCM.svn_cmd(commit_command))


def get_Xml_Item(releasenoteTree, xmlItem):
    '''
    from xmlTree get item
    '''
    return releasenoteTree.getElementsByTagName(xmlItem)


def get_DownloadItem(xmlItem):
    '''
    get downloaditem
    '''
    return re.sub(r'https?://[^/]*', '', xmlItem[0].childNodes[0].data.strip())


def get_pm_counters_cbts(L2Repo, L2Ver):
    '''
    from l2 ecl get pm_counters_cbts
    '''
    log.info('svn export -r {} --force {}{}/ECL/ECL L2_ECL'.format(L2Ver,
        current_svn_server, L2Repo))
    cmd_result = shell_cmd('svn export -r {} --force {}{}/ECL/ECL L2_ECL'.format(L2Ver,
        current_svn_server, L2Repo))
    if cmd_result:
        log.info("get L2'ECL finish.")
        PM = shell_cmd('grep ECL_PM_COUNTERS_CBTS L2_ECL')
        if PM:
            return PM.strip().split('=')[1]
        else:
            log.error('can not get PM_COUNTERS_CBTS from L2 ECL')
            sys.exit(1)
    else:
        cmd_result = shell_cmd('svn export -r {} --force {}{}/ECL/ECL L2_ECL'.format(
            L2Ver, current_svn_server, L2Repo))
        if cmd_result:
            log.info("get L2'ECL finish.")
            PM = shell_cmd('grep ECL_PM_COUNTERS_CBTS L2_ECL')
            if PM:
                return PM.strip().split('=')[1]
            else:
                log.error('can not get PM_COUNTERS_CBTS from L2 ECL')
                sys.exit(1)
        else:
            log.error('failed to download L2 ECL')
            sys.exit(1)


def read_xml(fileName):
    '''
    use minidom module get xml tree
    '''
    result = dict()
    log.info('start read file:%s' % fileName)
    DOMTree = xml.dom.minidom.parse(fileName)
    releasenote = DOMTree.documentElement
    return releasenote


def get_baseline(baselines, mod):
    '''
    from xml tree get specify baseline
    '''
    for baseline in baselines:
        if baseline.getAttribute("name") == mod:
            modValue = baseline.childNodes[0].data.strip()
            log.info('%s:%s' % (mod, modValue))
            return modValue
    else:
        log.info('get %s from baseline failed' % mod)
        sys.exit(1)


def get_ecl_repo():
    '''
    clone ecl repo
    '''
    config_mapping_file = os.path.join(working_root, 'branch_prefixName.ini')
    SCM.svn_cmd(
        'svn export --force {}/isource/svnroot/BTS_SCM_CLOUD_CB/'
        'cbts_ci_script/branch_prefixName.ini '
        '{}'.format(current_svn_server, config_mapping_file))
    log.info('-' * 54)
    log.info('\n' + SCM.subprocess.getoutput('stat ' + config_mapping_file))
    log.info('-' * 54)
    config_mapping = configParser()
    config_mapping.read(config_mapping_file)
    ecl_svn_path = config_mapping.get('ECL_PATH', '{}'.format(args.branch))
    ifdd_mod = config_mapping.get('ECL_PATH', 'baselines').strip().split(',')
    return ecl_svn_path, ifdd_mod


def parse_cb_ecl(ecl_ws):
    '''
    generate ecl dict
    '''
    ECL_path = ecl_ws
    Econtent = SCM.subprocess.getoutput('cat ' + ECL_path)
    log.info('file content:\n%s' % Econtent)
    # log.info('-' * 54)
    i_dict_ori = SCM.parse_ecl(Econtent.split('\n'))
    i_dict = {}
    for item in i_dict_ori.keys():
        i_dict[re.sub('^ECL_', '', item)] = i_dict_ori[item]
    return i_dict


def get_wft_releasenote(tag_name):
    '''
    download releasenote fron wft
    '''
    log.info('wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/' +
          tag_name + ".xml -O " + tag_name + '.xml --no-check-certificate')
    result = shell_cmd(
        'wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/' +
        tag_name +
        ".xml -O " +
        tag_name +
        '.xml --no-check-certificate')
    if result:
        log.info(tag_name + ".xml get from WFT finish.")
        return tag_name + '.xml'
    else:
        result = shell_cmd(
            'wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/' +
            tag_name +
            ".xml -O " +
            tag_name +
            '.xml --no-check-certificate')
        if result:
            log.info(tag_name + ".xml get from WFT finish.")
            return tag_name + '.xml'
        else:
            log.error('failed to download ' + tag_name + '.xml')
            sys.exit(1)


def update_baseline_info_all():
    '''
    according the fdd_baseline update all compements
    '''
    fdd_baselines = get_Xml_Item(read_xml(get_wft_releasenote(args.baseline)),
        'baseline')
    for item in ecl_dict.keys():
        if item in fdd_mod_list:
            ecl_dict['item'] = get_baseline(fdd_baselines, item)
    if args.branch in ['Trunk', 'Trunk_PSI', 'ecl_test']:
        LTEL2 = get_baseline(fdd_baselines, 'LTEL2')
        ecl_dict['PM_COUNTERS_CBTS'] = get_pm_counters_cbts(LTEL2.split('@')[0],
            LTEL2.split('@')[1])
    log.info('-' * 54)
    return ecl_dict['PS_REL']


def update_baseline_info_wft():
    '''
    update ecl module according releasenote
    '''
    fdd_baselines = get_Xml_Item(read_xml(get_wft_releasenote(args.baseline)),
        'baseline')
    ecl_dict['GLOBAL_ENV'] = get_baseline(fdd_baselines, 'GLOBAL_ENV')
    ecl_dict['PS_REL'] = get_baseline(fdd_baselines, 'PS_REL')
    ecl_dict['ENV'] = get_baseline(fdd_baselines, 'ENV')
    ecl_dict['COMMON_APPL_ENV'] = get_baseline(fdd_baselines, 'COMMON_APPL_ENV')
    if '/' in get_baseline(fdd_baselines, 'LOM'):
        ecl_dict['LOM'] = get_baseline(fdd_baselines, 'LOM')
    else:
        ecl_dict['LOM'] = get_DownloadItem(get_Xml_Item(read_xml(get_wft_releasenote
            (get_baseline(fdd_baselines, 'LOM'))), 'downloadItem'))
    if '/' in get_baseline(fdd_baselines, 'ISAR_XML'):
        ecl_dict['ISAR_XML'] = get_baseline(fdd_baselines, 'ISAR_XML')
    else:
        ecl_dict['ISAR_XML'] = get_DownloadItem(get_Xml_Item(read_xml(
            get_wft_releasenote(get_baseline(fdd_baselines,
            'ISAR_XML'))), 'downloadItem'))
    if args.branch in ['Trunk', 'Trunk_PSI', 'ecl_test']:
        LTEL2 = get_baseline(fdd_baselines, 'LTEL2')
        LTEL2_VERSION = LTEL2.split('@')[1]
        if LTEL2_VERSION == '':
            LTEL2_VERSION = 'HEAD'
        ecl_dict['PM_COUNTERS_CBTS'] = get_pm_counters_cbts(LTEL2.split('@')[0],
            LTEL2_VERSION)
        log.info('PM_COUNTERS_CBTS:%s' % ecl_dict['PM_COUNTERS_CBTS'])
    log.info('-' * 54)
    return ecl_dict['PS_REL']


def read_baseline_config(url):
    fdd_content = SCM.subprocess.getoutput('svn cat ' + url +
        '/.config').split('\n')
    fdd_dict = SCM.parse_config(fdd_content, simple=True)
    return fdd_dict


def update_baseline_info():
    '''
    from fdd_baseline frozen path get update
    '''
    fdd_svn = re.sub(r'https?://[^/]*', current_svn_server,
        get_Xml_Item(read_xml(get_wft_releasenote(args.baseline)),
        'downloadItem')[0].childNodes[0].data.strip())
    fdd_dict = read_baseline_config(fdd_svn)
    ecl_dict['GLOBAL_ENV'] = fdd_dict['GLOBAL_ENV']
    ecl_dict['PS_REL'] = fdd_dict['PS_REL']
    ecl_dict['ENV'] = fdd_dict['ENV']
    ecl_dict['COMMON_APPL_ENV'] = fdd_dict['COMMON_APPL_ENV']
    ecl_dict['LOM'] = fdd_dict['LOM']
    ecl_dict['ISAR_XML'] = fdd_dict['ISAR_XML']
    if args.branch in ['Trunk', 'Trunk_PSI', 'ecl_test']:
        LTEL2 = fdd_dict['LTEL2']
        LTEL2_VERSION = LTEL2.split('@')[1]
        if LTEL2_VERSION == '':
            LTEL2_VERSION = 'HEAD'
        ecl_dict['PM_COUNTERS_CBTS'] = get_pm_counters_cbts(LTEL2.split('@')[0],
            LTEL2_VERSION)
        log.info('PM_COUNTERS_CBTS:%s' % ecl_dict['PM_COUNTERS_CBTS'])
    log.info('-' * 54)
    return ecl_dict['PS_REL']


def update_ps_info(ps_version):
    ps_baselines = get_Xml_Item(read_xml(get_wft_releasenote(ps_version)),
        'baseline')
    ecl_dict['LFS_REL'] = get_baseline(ps_baselines, 'PS_LFS_REL')
    ecl_dict['PS_ENV'] = getPsEnvPath(get_wft_releasenote(get_baseline(
        ps_baselines, 'PS_ENV')))
    log.info('-' * 54)


def checkout_ecl(cbts_base_branch, folder_name):
    '''
    get ecl repo
    '''
    cbts_base_ws = os.path.join(os.getcwd(), folder_name)
    if os.path.exists(cbts_base_ws):
        shutil.rmtree(cbts_base_ws)
    SCM.svn_cmd(
        'svn co ' +
        cbts_base_branch +
        " {} --ignore-externals".format(cbts_base_ws))

    return cbts_base_ws


def get_sc_tag(scVar):
    '''
    return sc tag
    '''
    if scVar.find('/isource/svnroot/'):
        return scVar.rstrip('/').split('/')[-1]
    return scVar


def get_diff():
    '''
    check the local ecl whether changed
    '''
    need_commit = False
    with open('ECL_diff.txt', 'w') as ECL_diff:
        template = "{0:20} {1:>60} --> {2:60}"
        log.info("changed components as below:")
        ECL_diff.write("changed components as below:")
        for item in list(set(ecl_dict.keys() & ecl_dict_orig.keys())):
            if ecl_dict_orig[item] != ecl_dict[item]:
                need_commit = True
                log.info(template.format(item + " changed:",
                    ecl_dict_orig[item], ecl_dict[item]))
                ECL_diff.write(template.format('\n' + item + " changed:",
                    ecl_dict_orig[item], ecl_dict[item]))
        for item in list(set(ecl_dict.keys() - ecl_dict_orig.keys())):
            need_commit = True
            log.info(template.format(item + " added:", '-', ecl_dict[item]))
            ECL_diff.write(template.format('\n' + item + " added:", '-',
                ecl_dict[item]))
        for item in list(set(ecl_dict_orig.keys() - ecl_dict.keys())):
            need_commit = True
            log.info(template.format(item + " deleted:", ecl_dict_orig[item], '-'))
            ECL_diff.write(template.format('\n' + item + " deleted:",
                ecl_dict_orig[item], '-'))
        log.info('-' * 54)
    return need_commit


def write_ecl():
    log.info('start modify local repo ECL file:')
    # the list mormal_ecl_list define the scs that can be in ecl permanent
    mormal_ecl_list = ['FDD_BASELINE', 'GLOBAL_ENV', 'ENV', 'COMMON_APPL_ENV',
        'PS_REL', 'LFS_REL', 'PS_ENV', 'RCP', 'NIDD_CBTS', 'TRS_COMMON',
        'TPI', 'PM_COUNTERS_CBTS', 'LOM', 'ISAR_XML']
    # origin_ecl = open('ECL/ECL', 'r').readlines()
    with open('ECL/ECL', 'w') as new_ecl_file:
        for item in mormal_ecl_list:
            if item in ecl_dict.keys():
                log.info("write {} to ECL file" .format(item))
                new_ecl_file.write("ECL_{}={}\n" .format(item, ecl_dict[item]))
                del ecl_dict[item]
            else:
                log.info("attention please {} not in ECL file" .format(item))
        new_ecl_file.write('# below scs should be kept in ECL temporary.\n')
        for item in ecl_dict.keys():
            log.info("write {} to ECL file" .format(item))
            new_ecl_file.write("ECL_{}={}\n" .format(item, ecl_dict[item]))


def update_ecl():
    # update fdd_baseline
    if args.baseline:
        log.info('use specified baseline version:%s' % args.baseline)
        ecl_dict['FDD_BASELINE'] = args.baseline
        base_ps = update_baseline_info()

    #update PS version
    if args.PS and args.dailyUpdate == "False":
        log.info('use specified ps version:%s' % args.PS)
        ecl_dict['PS_REL'] = args.PS
        update_ps_info(args.PS)
    elif 'base_ps' in locals().keys():
        log.info('use baseline ps version:%s' % base_ps)
        ecl_dict['PS_REL'] = base_ps
        update_ps_info(base_ps)

    if args.RCP and args.dailyUpdate == "False":
        log.info('use specified RCP version:%s' % args.RCP)
        ecl_dict['RCP'] = args.RCP
        log.info('-' * 54)

    if args.NIDD and args.dailyUpdate == "False":
        log.info('use specified NIDD version:%s' % args.NIDD)
        ecl_dict['NIDD_CBTS'] = args.NIDD
        log.info('-' * 54)

    if args.TPI and args.dailyUpdate == "False":
        tpi_tag = get_sc_tag(args.TPI)
        log.info('use specified TPI version:%s' % tpi_tag)
        tpi_url = re.sub(r'https?://[^/]*', current_svn_server,
            get_Xml_Item(read_xml(get_wft_releasenote(tpi_tag)),
            'downloadItem')[0].childNodes[0].data.strip())
        ecl_dict['TPI'] = tpi_url
        log.info('-' * 54)

    if args.TRS and args.dailyUpdate == "False":
        trs_tag = get_sc_tag(args.TRS)
        log.info('use specified TRS version:%s' % trs_tag)
        trs_url = re.sub(r'https?://[^/]*', current_svn_server,
            get_Xml_Item(read_xml(get_wft_releasenote(trs_tag)),
            'downloadItem')[0].childNodes[0].data.strip())
        ecl_dict['TRS_COMMON'] = trs_url
        log.info('-' * 54)

    if args.lockVersion and args.dailyUpdate == "False":
        log.info('use specified lockVersion file:%s' % args.lockVersion)
        lockVer_dict = parse_cb_ecl(args.lockVersion)
        log.info(lockVer_dict)
        if 'FDD_BASELINE' in lockVer_dict.keys() or 'PS_REL' in \
                lockVer_dict.keys():
            log.error('FDD_BASELINE or PS_REL should not be in this variable.')
            sys.exit(1)
        for item in lockVer_dict.keys():
            if item in ecl_dict.keys():
                log.info('Change %s to:%s' % (item, lockVer_dict[item]))
            else:
                log.info('Add %s in ECL:%s' % (item, lockVer_dict[item]))
            ecl_dict[item] = lockVer_dict[item]
            # get PM_COUNTERS_CBTS fron l2 ecl
            if item == 'LTEL2' and args.branch in ['Trunk', 'Trunk_PSI', 'ecl_test']:
                LTEL2_VERSION = ecl_dict[item].split('@')[1]
                if LTEL2_VERSION == '':
                    LTEL2_VERSION = 'HEAD'
                ecl_dict['PM_COUNTERS_CBTS'] = get_pm_counters_cbts(ecl_dict[item].
                split('@')[0], LTEL2_VERSION)
        log.info('-' * 54)

    if args.delete and args.dailyUpdate == "False":
        log.info('delete specified version:%s' % args.delete)
        del_list = list()
        del_list_orig = args.delete.strip().split(',')
        for item in del_list_orig:
            del_list.append(re.sub('^ECL_', '', item))
        if 'FDD_BASELINE' in del_list or 'PS_REL' in del_list or 'NIDD_CBTS' \
                in del_list or 'RCP' in del_list:
            log.error('FDD_BASELINE NIDD_CBTS PS_REL RCP should not be in this var')
            sys.exit(1)
        for item in del_list:
            if item in ecl_dict.keys():
                log.info('del %s' % item)
                del ecl_dict[item]
            else:
                log.info('%s not in ECL' % item)
        log.info('-' * 54)

    if get_diff():
        write_ecl()
        log.info('-' * 54)
        log.info('start commit ecl change:\n %s -by %s' % (args.commit, args.committer))
        if args.commit and args.committer:
            # log.info('-' * 54)
            commit_ecl(ecl_ws)
            if args.dailyUpdate == "True":
                send_email("update")
        else:
            log.info('no commit info,so no need to commit.')
            sys.exit(1)
    else:
        log.info("ECL no change. ")
        sys.exit(9)


def get_newest_fdd():
    '''
    get the newest fdd_baseline
    '''
    wft_url = 'https://wft.int.net.nokia.com/ext/builds/?custom_filter[branch]=WMP_'\
        'trunk&custom_filter[baseline]=FL00_FSM4_9999&custom_filter'\
        '[sorting_direction]=desc&custom_filter[sorting_field]=date&custom_'\
        'filter[items]=1&custom_filter[state][]=released'
    log.info('wget -t 3 "' + wft_url + '" -O release --no-check-certificate')
    result = shell_cmd('wget -t 3 "' + wft_url + '" -O release --no-check-certificate')
    if result:
        log.info("newest released baseline get from WFT finish.")
        return 'release'
    else:
        log.error('failed to download newest baseline')
        sys.exit(1)


def check_new_ps():
    '''
    check the ps version whether available
    '''
    new_ps_var = new_fdd_dict['PS_REL'].split('_')[-2]
    ecl_ps_var = ecl_dict['PS_REL'].split('_')[-2]
    log.info('new:%s <---> PS:%s' % (new_fdd_dict['PS_REL'], ecl_dict['PS_REL']))
    if new_ps_var != ecl_ps_var:
        return False
    return True


def parse_arguments():
    '''
    get args
    '''
    parse = argparse.ArgumentParser()
    parse.add_argument('--branch', required=True, help='Which branch`s ECL')
    parse.add_argument('--dailyUpdate', required=True, help='dailyUpdate')
    parse.add_argument('--commit', required=True, help='commit to svn')
    parse.add_argument('--committer', required=True, help='committer')
    parse.add_argument('--baseline', required=False, help='Input baseline')
    parse.add_argument('--RCP', required=False, help='RCP version')
    parse.add_argument('--PS', required=False, help='PS version')
    parse.add_argument('--TPI', required=False, help='TPI version')
    parse.add_argument('--TRS', required=False, help='TRS version')
    parse.add_argument('--lockVersion', required=False, help='Use specified version')
    parse.add_argument('--delete', required=False, help='Del the specified module')
    parse.add_argument('--NIDD', required=False, help='NIDD version')
    args = parse.parse_args()
    return args


if __name__ == '__main__':
    args = parse_arguments()
    log = logger.setup_logger(
        filename='update_ecl' + ".log", debug='true')
    log.info('***** Modify ECL start *****')

    current_svn_server = "https://beisop60.china.nsn-net.net"
    working_root = os.getcwd()
    log.info('use folder: %s' % working_root)

    # get ecl repo
    ecl_repo, fdd_mod_list = get_ecl_repo()
    log.info('ECL repo :%s' % ecl_repo)
    ecl_ws = checkout_ecl(ecl_repo, 'ECL')
    log.info('\n' + SCM.subprocess.getoutput('svn info ' + ecl_ws))
    log.info('-' * 54)
    ecl_dict = parse_cb_ecl(ecl_ws + '/ECL')
    ecl_dict_orig = copy.deepcopy(ecl_dict)
    log.info('ecl dict:\n%s' % ecl_dict)
    log.info('-' * 54)

    if args.dailyUpdate == "True":
        # if dailyUpdate is be setted true,get the newest baseline
        # and check the ps version
        new_baseline = get_Xml_Item(read_xml(get_newest_fdd()),
            'baseline')[0].childNodes[0].data.strip()
        log.info('The newest baseline is %s' % new_baseline)
        new_fdd_svn = re.sub(r'https?://[^/]*', current_svn_server,
            get_Xml_Item(read_xml(get_wft_releasenote(new_baseline)),
            'downloadItem')[0].childNodes[0].data.strip())
        new_fdd_dict = read_baseline_config(new_fdd_svn)
        if new_baseline != ecl_dict['FDD_BASELINE']:
            if check_new_ps():
                log.info('The newest baseline is available')
                args.baseline = new_baseline
            else:
                log.info('The newest baseline is not available')
                send_email("attention")
                sys.exit(9)
        else:
            log.info('The ecl fdd_baseline is up to date')
            sys.exit(9)

    update_ecl()
