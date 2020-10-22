#!/usr/bin/env python3.6
import os
import sys
import re
import argparse
import paramiko
import time
import logging
import jenkins
import requests
import threading
import multiprocessing
from xml.etree import ElementTree
from bs4 import BeautifulSoup


SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
jenkins_server = 'http://{}:9090/'.format(os.environ['JENKINS_HOST'])
IP_REGEX = re.compile(r'10\.\d+\.\d+\.\d+')
ID_REGEX = re.compile(r'-(\d+)_\d$')
# Get the userdata id form http://wrlinb147.emea.nsn-net.net:9090/configfiles/
docker_userdata_id = ["61fce6c0-24c3-4b8e-9bff-5719ac47145c"]
MAX_PROCESS = 3


def setup_logger(debug=False):
    if debug:
        message_string = '%(processName)s.%(threadName)s %(levelname)s:\t%(module)s@%(lineno)s:\t%(message)s'
    else:
        message_string = '%(processName)s.%(threadName)s %(levelname)s:\t%(message)s'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(message_string)
    stream_handler = logging.StreamHandler()
    if debug:
        stream_handler.setLevel(logging.DEBUG)
    else:
        stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def update_container_node(node, version):
    if not version:
        log.info(f"container {node['name']} no change")
        return
    script = "update_container.sh"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private = paramiko.RSAKey.from_private_key_file(
        '{}/.ssh/{}'.format(
            os.path.expanduser('~'),
            node['key']
        )
    )
    client.connect(hostname=node['ip'], port=22, username='root', pkey=private)
    transport = client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put("{}/{}".format(SCRIPT_DIR, script), "/root/{}".format(script))
    _, output, error = client.exec_command(
        "bash /root/{} {}".format(script, version),
        timeout=210
    )
    log.debug(f"output: {str(output.read())}")
    log.debug(f"error: {str(error.read())}")
    log.info(f"container {node['name']} update ok")


def process_node(task_queue, result_queue):
    log.info("thread start")
    server = jenkins.Jenkins(jenkins_server, username=args.user, password=args.password)
    for node in iter(task_queue.get, None):
        node_info = process_function(server.get_node_info, "get node info", node, get_result=True)
        if not node_info:
            result_queue.put(("get node info failed", node))
            continue
        if not node_info['offline']:
            if not process_function(server.disable_node, "disable", node):
                result_queue.put(("disable failed", node))
                continue
        node_info = process_function(server.get_node_info, "get node info", node, get_result=True)
        if not node_info:
            result_queue.put(("get node info failed", node))
            continue
        if node_info['idle']:
            log.info(f"process node {node['name']}")
            if node['type'] == 'container':
                try:
                    update_container_node(node, args.version)
                except Exception:
                    log.info(f"{node['name']} update container failed")
                    result_queue.put(("update container failed", node))
                    continue
                if not process_function(server.enable_node, "enable", node):
                    result_queue.put(("online failed", node))
                    continue
                result_queue.put(("success", node))
            else:
                if process_function(server.delete_node, "delete", node):
                    log.info(f"delete node {node['name']} finish")
                    result_queue.put(("success", node))
                else:
                    result_queue.put(("delete failed", node))
        else:
            result_queue.put(("in use", node))
            log.info(f"node {node['name']} is in use.")
    log.info("thread exit.")


def process_function(function, operation, node, get_result=False):
    for _ in range(0, 3):
        try:
            result = function(node['name'])
            log.debug(f"node {node['name']} {operation} finish.")
            if get_result:
                return result
            return True
        except Exception:
            log.error(f"node {node['name']} {operation} failed, try again.")
    else:
        log.warning(f"{operation} node {node['name']} failed, no more try left")
        return False


def arguments():
    parse = argparse.ArgumentParser()
    parse.add_argument("--label", "-l", required=False, help="Jenkins node label, like cores-beast")
    parse.add_argument("--node", "-n",required=False, help="Comma separated nodes list,like node1,...")
    parse.add_argument("--version", "-v", required=False, help="Docker image version, like 3.21.2")
    parse.add_argument("--user", "-u", required=True, help="Jenkins username")
    parse.add_argument("--password", "-p", required=True, help="Jenkins password")
    parameters = parse.parse_args()
    if not (parameters.node or parameters.label):
        raise Exception("Please provide label or node parameter.!")
    return parameters


def get_node_from_html():
    '''
    get nodes form a label html
    search all <a href="/computer/XXX/" class="model-link inside">XXX</a> items
    :return: node list
    '''
    label_node = list()
    response = requests.get(os.path.join(jenkins_server, "label/{}".format(args.label)))
    if response.ok:
        log.info(f"get node from label {args.label}")
        soup = BeautifulSoup(response.text, 'html.parser')
        for nobr in soup.find_all('nobr'):
            label_node.append(nobr.find("a", class_="model-link inside").get_text())
    log.info(label_node)
    return label_node


def get_node_list():
    if args.label:
        node_list = get_node_from_html()
    elif args.node:
        node_list = args.node.split(',')
    else:
        log.error("Please provide label or node parameter.")
        sys.exit(1)
    log.info(node_list)
    return node_list


def get_node_info_list():
    server = jenkins.Jenkins(jenkins_server, username=args.user, password=args.password)
    nodes_info = list()
    for node in nodes:
        node_info = dict()
        node = node.strip()
        if not node:
            continue
        node_info['name'] = node
        node_config = server.get_node_config(node)
        xml_root = ElementTree.fromstring(node_config)
        if xml_root.tag != 'jenkins.plugins.openstack.compute.JCloudsSlave':
            log.info(f"{node} is not cloud instance, skip")
            continue
        if IP_REGEX.match(node):
            log.warnning(f"{node}, not support ip, skip")
            continue
        node_info['id'] = xml_root.find('nodeId').text.strip()
        cloud = ID_REGEX.findall(xml_root.find('.//availabilityZone').text)[0]
        node_info['cloud'] = 'cloud_{}'.format(cloud)
        node_info['key'] = 'ca-5gcv-key-{}.pem'.format(cloud)
        # Handle node in the type of instance
        node_info['type'] = "instance"
        # The immediate update of the jenkins-slave container will cause problems
        # but temporarily retain this function
        if xml_root.find('.//userDataId').text in docker_userdata_id:
            node_info['type'] = "container"
        for item in xml_root.findall('.//string'):
            if item.text and IP_REGEX.match(item.text):
                node_info['ip'] = item.text.strip()
                break
        else:
            log.info(f"can not find {node}'s ip address, skip")
            continue
        log.info(node_info)
        nodes_info.append(node_info)
    if not nodes_info:
        log.info("No jenkins node find")
        sys.exit(213)
    return nodes_info


def child_process(task_queue, result_queue):
    log.info("sub process start")
    thread_list = list()
    for loop in range(0, MAX_PROCESS):
        thread = threading.Thread(
            target=process_node,
            args=(task_queue, result_queue)
        )
        thread.name = str(loop)
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    log.info("sub process exit.")


def update_jenkins_node():
    prosess_list = list()
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    process_number = (len(node_info_list) - 1) // MAX_PROCESS + 1
    if process_number > MAX_PROCESS:
        process_number = MAX_PROCESS
    for loop in range(0, process_number):
        process = multiprocessing.Process(
            target=child_process,
            args=(task_queue, result_queue)
        )
        process.name = str(loop)
        process.deamon = True
        process.start()
        prosess_list.append(process)

    for node_info in node_info_list:
        task_queue.put(node_info)

    failed_list = list()
    while True:
        try:
            result, node = result_queue.get(timeout=300)
            if result == "in use":
                time.sleep(10)
                task_queue.put(node)
                continue
            node_info_list.remove(node)
            if result != "success":
                failed_list.append("{}: {}".format(node['name'], result))
            if not node_info_list:
                log.info("all node process finish.")
                break
        except Exception:
            for process in prosess_list:
                if process.is_alive():
                    process.terminate()
                    log.critical(f"process {process.name} be aborted")
            sys.exit(1)
    for _ in range(0, process_number * 3):
        task_queue.put(None)
    return failed_list


if __name__ == "__main__":
    args = arguments()
    log = setup_logger(debug=False)
    nodes = get_node_list()
    node_info_list = get_node_info_list()
    log.debug(node_info_list)
    failed_node_list = update_jenkins_node()
    for line in failed_node_list:
        log.error(line)
