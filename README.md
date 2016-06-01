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
