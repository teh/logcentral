# What is this?

This is a tiny daemon that ships systemd logs to a central
[rethinkdb](https://www.rethinkdb.com/) instance. The daemon tries to
be clever about shipping missing data by storing the last log-cursor
position in rethinkdb.

It doesn't really compete with any of the big central logging
solutions because those offer custom log parsing, while we just send
the raw messages and rely on some clever parsing in a downstream
extraction step.

# How to run?

When testing with the default rethinkdb ports on localhost this should
work:

```
logshipper-daemon.py
```

For a production setup:

```
logshipper-daemon.py --rethinkdb-host central-rethinkdb:28015 --machine-id testmachine.mynetwork.com
```


# To pandas

```
import pandas, rethinkdb as r
r.connect().repl()
log = r.db("logcentral").table("log")
# filter and sort
df = pandas.DataFrame.from_records(l.filter({"_UID": 1000}).order_by(r.row['__REALTIME_TIMESTAMP']).limit(2000).run())


df['__REALTIME_TIMESTAMP'] = df['__REALTIME_TIMESTAMP'].astype('datetime64[us]')
df = df.set_index('__REALTIME_TIMESTAMP')
```
