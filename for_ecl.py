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
import modules.SCM_lib as SCM
import modules.logger as logger
from modules.config_parser import ConfigParse

class configParser(configparser.ConfigParser):
    """
    optinxform in module ConfigParse return optionstr.lower()
    this class for redefine optionxform
    """

    def optionxform(self, optionstr):
        return optionstr.strip()

def shell_cmd(cmd):
    result = subprocess.getstatusoutput(cmd)
    if result[0] == 0:
        return result[1]
    return False

def getPsEnvPath(psVerXml):
    releasenoteTree = parse(psVerXml)
    releasenoteDoc = releasenoteTree.documentElement
    repoUrl = releasenoteDoc.getElementsByTagName("repositoryUrl")[0].\
        childNodes[0].data.strip()
    repoBranch = releasenoteDoc.getElementsByTagName("repositoryBranch")\
        [0].childNodes[0].data.strip()
    psEnvRepoUrlStr = "{}/{}".format(repoUrl,repoBranch)
    log.info(psEnvRepoUrlStr)
    return re.sub(r'https?://[^/]*','',psEnvRepoUrlStr)

def commit_ecl(local_repo):
    os.chdir(local_repo)
    commit_command = 'svn ci . -m "{}" '.format(args.commit)
    log.info('svn commit,wait....\n' + SCM.svn_cmd(commit_command))

def get_pm_counters_cbts(L2Repo, L2Ver):
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

def read_xml(mod, fileName):
    result = dict()
    log.info('mod:%s; fileName:%s' % (mod, fileName))
    DOMTree = xml.dom.minidom.parse(fileName)
    releasenote = DOMTree.documentElement
    baselines = releasenote.getElementsByTagName('baseline')
    if mod == 'baseline':
        for baseline in baselines:
            if baseline.getAttribute("name") == 'GLOBAL_ENV':
                result['GLOBAL_ENV'] = baseline.childNodes[0].data.strip()
                log.info('GLOBAL_ENV:%s' % baseline.childNodes[0].data.strip())
            elif baseline.getAttribute("name") == 'ENV':
                result['ENV'] = baseline.childNodes[0].data.strip()
                log.info('ENV:%s' % baseline.childNodes[0].data.strip())
            elif baseline.getAttribute("name") == 'LTEL2':
                # result['LTEL2'] = baseline.childNodes[0].data.strip()
                L2_repo = baseline.childNodes[0].data.strip().split('@')[0]
                L2_ver = baseline.childNodes[0].data.strip().split('@')[1]
                log.info('LTEL2:%s;version:%s' % (L2_repo, L2_ver))
                if args.branch in ['Trunk', 'Trunk_PSI', 'ecl_test']:
                    result['PM_COUNTERS_CBTS'] = get_pm_counters_cbts(L2_repo, L2_ver)
                    log.info('PM_COUNTERS_CBTS:%s' % result['PM_COUNTERS_CBTS'])
            elif baseline.getAttribute("name") == 'PS_REL':
                result['PS_REL'] = baseline.childNodes[0].data.strip()
                log.info('PS_REL:%s' % baseline.childNodes[0].data.strip())
            elif baseline.getAttribute("name") == 'COMMON_APPL_ENV':
                result['COMMON_APPL_ENV'] = baseline.childNodes[0].data.strip()
                log.info('COMMON_APPL_ENV:%s' % baseline.childNodes[0].data.strip())
        if 'ENV' in result.keys() and 'GLOBAL_ENV' in result.keys() \
            and 'COMMON_APPL_ENV' in result.keys() and 'PS_REL' in result.keys():
            return result
        else:
            log.info('baseline info is incomplete!')
            sys.exit(1)
    if mod == 'ps':
        for baseline in baselines:
            if baseline.getAttribute("name") == 'PS_ENV':
                PS_ENV_tag = baseline.childNodes[0].data.strip()
                log.info('PS_ENV tag:%s' % baseline.childNodes[0].data.strip())
                log.info('get PS_ENV full path.')
                psEnvXml = get_wft_releasenote(PS_ENV_tag)
                result['PS_ENV'] = getPsEnvPath(psEnvXml)
                log.info('PS_ENV:%s' % result['PS_ENV'])
            elif baseline.getAttribute("name") == 'PS_LFS_REL':
                result['LFS_REL'] = baseline.childNodes[0].data.strip()
                log.info('LFS_REL:%s' % baseline.childNodes[0].data.strip())
        if 'LFS_REL' in result.keys() and 'PS_ENV' in result.keys():
            return result
        else:
            log.info('ps info is incomplete!')
            sys.exit(1)

def get_ecl_repo():
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
    return config_mapping.get('ECL_PATH', '{}'.format(args.branch))

def parse_cb_ecl(ecl_ws):
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
    log.info('wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/' +
          tag_name + ".xml -O " + tag_name + '.xml')
    result = shell_cmd(
        'wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/' +
        tag_name +
        ".xml -O " +
        tag_name +
        '.xml')
    if result:
        log.info(tag_name + ".xml get from WFT finish.")
        return tag_name + '.xml'
    else:
        result = shell_cmd(
            'wget -t 3 https://wft.int.net.nokia.com/ext/releasenote/' +
            tag_name +
            ".xml -O " +
            tag_name +
            '.xml')
        if result:
            log.info(tag_name + ".xml get from WFT finish.")
            return tag_name + '.xml'
        else:
            log.error('failed to download ' + tag_name + '.xml')
            sys.exit(1)

def update_baseline_info():
    base_dict = read_xml('baseline', get_wft_releasenote(args.baseline))
    ecl_dict['GLOBAL_ENV'] = base_dict['GLOBAL_ENV']
    ecl_dict['ENV'] = base_dict['ENV']
    ecl_dict['COMMON_APPL_ENV'] = base_dict['COMMON_APPL_ENV']
    if args.branch in ['Trunk', 'Trunk_PSI', 'ecl_test']:
        ecl_dict['PM_COUNTERS_CBTS'] = base_dict['PM_COUNTERS_CBTS']
    log.info('-' * 54)
    return base_dict['PS_REL']

def update_ps_info(ps_version):
    ps_dict = read_xml('ps', get_wft_releasenote(ps_version))
    ecl_dict['LFS_REL'] = ps_dict['LFS_REL']
    ecl_dict['PS_ENV'] = ps_dict['PS_ENV']
    log.info('-' * 54)

def parse_arguments():
    parse = argparse.ArgumentParser()
    parse.add_argument('--branch', required=True, help='Which branch`s ECL')
    parse.add_argument('--baseline', required=False, help='Input baseline')
    parse.add_argument('--RCP', required=False, help='RCP version')
    parse.add_argument('--PS', required=False, help='PS version')
    parse.add_argument('--lockVersion', required=False, help='Use specified version')
    parse.add_argument('--delete', required=False, help='Del the specified module')
    parse.add_argument('--NIDD', required=False, help='NIDD version')
    parse.add_argument('--commit', required=False, help='commit to svn')
    args = parse.parse_args()
    return args

def checkout_ecl(cbts_base_branch, folder_name):
    cbts_base_ws = os.path.join(os.getcwd(), folder_name)
    if os.path.exists(cbts_base_ws):
        shutil.rmtree(cbts_base_ws)
    SCM.svn_cmd(
        'svn co ' +
        cbts_base_branch +
        " {} --ignore-externals".format(cbts_base_ws))

    return cbts_base_ws

if __name__ == '__main__':
    args = parse_arguments()
    log = logger.setup_logger(
        filename='update_ecl' + ".log", debug='true')
    log.info('***** Modify ECL start *****')

    current_svn_server = "https://beisop60.china.nsn-net.net"
    working_root = os.getcwd()
    log.info('use folder: %s' % working_root)

    ecl_repo = get_ecl_repo()
    log.info('ECL repo :%s' % ecl_repo)
    ecl_ws = checkout_ecl(ecl_repo, 'ECL')
    log.info('\n' + SCM.subprocess.getoutput('svn info ' + ecl_ws))
    log.info('-' * 54)
    ecl_dict = parse_cb_ecl(ecl_ws + '/ECL')
    ecl_dict_orig = copy.deepcopy(ecl_dict)
    log.info('ecl dict:\n%s' % ecl_dict)
    log.info('-' * 54)

    if args.baseline:
        log.info('use specified baseline version:%s' % args.baseline)
        ecl_dict['FDD_BASELINE'] =  args.baseline
        base_ps = update_baseline_info()

    if args.PS:
        log.info('use specified ps version:%s' % args.PS)
        ecl_dict['PS_REL'] =  args.PS
        update_ps_info(args.PS)
    elif 'base_ps' in locals().keys():
        log.info('use baseline ps version:%s' % base_ps)
        ecl_dict['PS_REL'] =  base_ps
        update_ps_info(base_ps)

    if args.RCP:
        log.info('use specified RCP version:%s' % args.RCP)
        ecl_dict['RCP'] =  args.RCP
        log.info('-' * 54)

    if args.NIDD:
        log.info('use specified NIDD version:%s' % args.NIDD)
        ecl_dict['NIDD_CBTS'] =  args.NIDD
        log.info('-' * 54)

    if args.lockVersion:
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
        log.info('-' * 54)

    if args.delete:
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
            ECL_diff.write(template.format('\n' + item + " added:", '-', \
                ecl_dict[item]))
        for item in list(set(ecl_dict_orig.keys() - ecl_dict.keys())):
            need_commit = True
            log.info(template.format(item + " deleted:", ecl_dict_orig[item], '-'))
            ECL_diff.write(template.format('\n' + item + " deleted:", 
                ecl_dict_orig[item], '-'))
        log.info('-' * 54)

    if need_commit:
        log.info('start modify local repo ECL file:')
        origin_ecl = open('ECL/ECL', 'r').readlines()
        with open('ECL/ECL', 'w') as new_ecl_file:
            for line in origin_ecl:
                line = line.strip()
                # log.info(line)
                if re.match(r'^[\s]*#', line):
                    log.info("comment line keep intact:%s" % line)
                    new_ecl_file.write("{}\n" .format(line))
                    continue
                for item in list(set(ecl_dict.keys() & ecl_dict_orig.keys())):
                    if re.match(r'^[\s]*ECL_{}=.*'.format(item), line):
                        if ecl_dict_orig[item] != ecl_dict[item]:
                            log.info("write ECL_{} to ECL file" .format(item))
                        new_ecl_file.write("ECL_{}={}\n" .format(item, ecl_dict[item]))
                        break
                else:
                    for i in del_list:
                        if re.match(r'^[\s]*ECL_{}=.*'.format(i), line):
                            log.info("delete ECL_%s" % i)
                            break
                    else:
                        log.error('no match:{}'.format(line))
                        sys.exit(1)
            # log.info("add new components . ")
            for item in list(set(ecl_dict.keys() - ecl_dict_orig.keys())):
                log.info("add new components ECL%s. " % item)
                new_ecl_file.write("ECL_{}={}\n" .format(item, ecl_dict[item]))
        if args.commit:
            log.info('-' * 54)
            commit_ecl(ecl_ws)
        else:
            log.info('no commit info,so no need to commit.')
    else:
        log.info("ECL no change. ")
