#!/usr/bin/python
import rethinkdb as r
import argparse
import json
import subprocess
import socket


def yield_log_lines(cursor=None):
    cursor_args = [] if cursor is None else ['-c', cursor]
    p = subprocess.Popen(['journalctl', '-f', '-o', 'json'] + cursor_args, stdout=subprocess.PIPE, bufsize=1)

    # Skip line with the cursor (we already sent that as witnessed by
    # the entry in the cursor table).
    if cursor is not None:
        p.stdout.readline()

    # xreadlines blocks after a while for reasons unknown
    while True:
        l = p.stdout.readline()
        yield json.loads(l)


def prepare_for_table(data, machine_id):
    """We don't want to store certain fields in the DB, e.g. the _BOOT_ID
    or the __CURSOR because they don't add any value in the central
    log index.
    """

    defint = lambda x: 0 if x == '' else int(x)

    keep_and_convert = {
        'MESSAGE': str,
        'PRIORITY': defint,
        '__REALTIME_TIMESTAMP': defint,
        '_PID': defint,
        '_UID': defint,
        '_SYSTEMD_UNIT': str,
        'SYSLOG_IDENTIFIER': str,
        '_COMM': str,
    }
    result = dict((key, converter(data.get(key, ''))) for key, converter in keep_and_convert.items())
    result['MACHINE_ID'] = machine_id
    return data['__CURSOR'], result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rethinkdb-host", default="localhost:28015")
    parser.add_argument("-m", "--machine-id", default=socket.gethostname())
    args = parser.parse_args()
    host, port = args.rethinkdb_host.split(":")

    r.connect(host, port).repl()
    try:
        r.db("logcentral")
    except r.ReqlOpFailedError:
        r.db_create("logcentral").run()

    db = r.db("logcentral")

    if 'cursor_state' not in db.table_list().run():
        r.db("logcentral").table_create("cursor_state").run()

    if 'log' not in db.table_list().run():
        r.db("logcentral").table_create("log").run()

    cursor_table = r.db("logcentral").table('cursor_state')
    log_table = r.db("logcentral").table('log')

    c = cursor_table.get(args.machine_id).run()
    c = None if c is None else c['cursor']

    for line in yield_log_lines(c):
        cursor, data = prepare_for_table(line, args.machine_id)
        log_table.insert(data).run()
        cursor_table.insert({"id": args.machine_id, "cursor": cursor}, durability="soft", conflict="replace").run()


if __name__ == '__main__':
    main()
