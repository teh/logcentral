import rethinkdb as r
import argparse
import json
import subprocess
import socket


def yield_log_lines(cursor=None):
    cursor_args = [] if cursor is None else ['-c', cursor]
    p = subprocess.Popen(['sudo', 'journalctl', '-f', '-o', 'json'] + cursor_args, stdout=subprocess.PIPE, bufsize=1)

    # xreadlines blocks after a while for reasons unknown
    while True:
        l = p.stdout.readline()
        yield json.loads(l)


def prepare_for_table(data):
    """We don't want to store certain fields in the DB, e.g. the _BOOT_ID
    or the __CURSOR because they don't add any value in the central
    log index.

    """
    to_keep = ['MESSAGE', 'PRIORITY', '__REALTIME_TIMESTAMP', '_PID', '_UID', '_SYSTEMD_UNIT', 'SYSLOG_IDENTIFIER', '_COMM']
    result = dict((key, data.get(key, '')) for key in to_keep)
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
        cursor, data = prepare_for_table(line)
        cursor_table.insert({"id": args.machine_id, "cursor": cursor}, durability="soft", conflict="replace").run()
        log_table.insert(data).run()


if __name__ == '__main__':
    main()
