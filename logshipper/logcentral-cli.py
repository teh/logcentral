#!/usr/bin/python
import rethinkdb as r
import argparse
import json
import subprocess
import socket
import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rethinkdb-host", default="localhost:28015")
    parser.add_argument("command")
    args = parser.parse_args()
    host, port = args.rethinkdb_host.split(":")
    r.connect(host, port).repl()
    log = r.db("logcentral").table('log')

    if args.command == 'follow':
        for c in log.changes().run():
            ts = datetime.datetime.utcfromtimestamp(int(c['new_val']['__REALTIME_TIMESTAMP'])/1000/1000)
            print ts, c['new_val']['MESSAGE']


if __name__ == '__main__':
    main()
