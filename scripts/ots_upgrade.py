"""Upgrade an OpenTimestamps proof (.ots) once the calendars have put it into Bitcoin.

The official `ots` client crashes on this Windows box (python-bitcoinlib can't find an
OpenSSL DLL), so this uses the opentimestamps library directly.

    py -I scripts/ots_upgrade.py analysis/prediction-2026-11-06-abundance.sealed.md.ots
"""
import sys
from opentimestamps.core.timestamp import DetachedTimestampFile
from opentimestamps.core.notary import PendingAttestation, BitcoinBlockHeaderAttestation
from opentimestamps.core.serialize import StreamDeserializationContext, StreamSerializationContext
from opentimestamps.calendar import RemoteCalendar

path = sys.argv[1]
with open(path, 'rb') as f:
    dtf = DetachedTimestampFile.deserialize(StreamDeserializationContext(f))

changed = False
for msg, att in list(dtf.timestamp.all_attestations()):
    if isinstance(att, PendingAttestation):
        try:
            got = RemoteCalendar(att.uri).get_timestamp(msg, timeout=15)
        except Exception as e:
            print("still pending:", att.uri, "-", type(e).__name__)
            continue
        # merge into the matching sub-timestamp
        stack = [dtf.timestamp]
        while stack:
            ts = stack.pop()
            if ts.msg == msg:
                ts.merge(got); changed = True; print("upgraded:", att.uri); break
            stack.extend(ts.ops.values())

blocks = sorted({a.height for _, a in dtf.timestamp.all_attestations()
                 if isinstance(a, BitcoinBlockHeaderAttestation)})
print("Bitcoin block attestations:", blocks or "none yet")
if changed:
    with open(path, 'wb') as out:
        dtf.serialize(StreamSerializationContext(out))
    print("saved", path)
