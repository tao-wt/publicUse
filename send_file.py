import os
import sys
import threading
import multiprocessing
import hashlib
import argparse
import socket


def send(sockfd, data):
    send_size = 0
    while send_size < len(data):
        send_size += sockfd.send(data[send_size:])


def recv(sockfd, size):
    data = b''
    left_size = size
    while left_size > 0:
        data += self.sockfd.recv(left_size)
        left_size -= len(data)
    return data


def set_sock_opt(sockfd):
    pass


class send_thread(threading.Thread):
    def __init__(self, server, queue):
        self.queue = queue
        self.server = server
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_sock_opt(self.sockfd)
        self.sockfd.connect(self.server)
        self.deamon = True

    def init_conn(self):
        file_bytes = bytes(self.file, encoding='utf-8')
        name_length_str = str(len(file_bytes))
        if len(name_length_str) <= 5:
            name_length_str = "0" * (5 - len(name_length_str)) + name_length_str
        else:
            print('file {} too long!')
            sys.exit(2)

        size_str = str(self.size)
        if len(size_str) <= 12:
            size_str = "0" * (12 - len(size_str)) + size_str
        else:
            print('data size {} too long!')
            sys.exit(2)

        offset_str = str(self.offset)
        if len(offset_str) <= 12:
            offset_str = "0" * (12 - len(offset_str)) + offset_str
        else:
            print('offset {} too long!')
            sys.exit(2)

        data = b'w' \
                + bytes(name_length_str, encoding='utf-8') \
                + file_bytes \
                + bytes(offset_str, encoding='utf-8') \
                + bytes(size_str, encoding='utf-8')
        send(self.sockfd, data)

    def send_data(self):
        self.init_conn()
        retry = 0
        while retry < 3:
            retry += 1
            md5 = hashlib.md5()
            buf = 8192
            left_size = self.size
            with open(self.file, 'rb') as f:
                f.seek(self.offset)
                while left_size > 0:
                    if left_size < buf:
                        buf = left_size
                        left_size = 0
                    else:
                        left_size -= buf
                    data = f.read(buf)
                    if not data:
                        break
                    md5.update(data)
                    send(self.sockfd, data)
            # self.sockfd.shutdown(1)
            md5_value = md5.hexdigest()
            if check_result(md5_value):
                break

    def run(self):
        while True:
            file = self.queue.get()
            if file is None:
                break
            self.file, self.offset, self.size = file
            self.send_data()
        self.sockfd.close()
        print("thread finish.")

    def check_result(self, md5_value):
        data = recv(self.sockfd, 32)
        data_str = str(data, encoding='utf-8')
        if data_str != md5_value:
            return False
        return True


def send_process(server, get_queue, thread_num):
    thread_list = list()
    for loop in range(0, thread_num):
        thread = send_thread(server, get_queue)
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()


def parse_arguments():
    '''
    get args
    '''
    parse = argparse.ArgumentParser()
    parse.add_argument('--server', required=True, help='server ip/name')
    parse.add_argument('--port', required=True, help='server port')
    parse.add_argument('--file', required=True, help='file or path')
    parse.add_argument('--length', required=True, help='file block length')
    parse.add_argument('--process_num', type=int, help='process num')
    parse.add_argument('--thread_num', type=int, help='thread num')
    args = parse.parse_args()
    return args


def generate_queue_item(queue, files):
    for file in files:
        stat_obj = os.stat(file)
        for offset in range(0, stat_obj.st_size, int(args.length)):
            queue.put((file, offset, args.length))


def get_file_list():
    file_list = list()
    init_data = b''
    for root, dirs, files in os.walk(".", topdown=True):
        for name in files:
            file_list.append(name)
            init_data += b'f' + bytes(name, encoding='utf-8') + b'\n'
        for name in dirs:
            init_data += b'd' + bytes(name, encoding='utf-8') + b'\n'
    return file_list, init_data


if __name__ == '__mian__':
    args = parse_arguments()
    args.file = args.file.strip()
    if os.path.isdir(args.file):
        print("{} is a directory".format(args.file))
        args.file = [os.path.basename(args.file)]
        os.chdir('/'.join(args.file.split('/')[:-1]))
    elif os.path.isfile(args.file):
        print("{} is a normal file".format(args.file))
        os.chdir(args.file)
        args.file, init_data = get_file_list()
    else:
        print("Error {} is a special file".format(args.file))
        sys.exit(1)

    queue = multiprocessing.Queue()
    server = (args.server, args.port)
    if not args.thread_num:
        args.thread_num = 3
    if not args.process_num:
        args.process_num = multiprocessing.cpu_count()

    process_list = list()
    for loop in range(0, args.process_num):
        process = multiprocessing.Process(
            target=send_process,
            args=(server, queue, args.thread_num)
        )
        process.deamon = True
        process.start()
        process_list.append(process)

    generate_queue_item(queue, args.file)

    for process in process_list:
        process.join()

    print('Send {} finish.'.format(args.file))
