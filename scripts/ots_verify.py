"""Check an OpenTimestamps proof against real Bitcoin block headers (via blockstream.info).

    py -I scripts/ots_verify.py <file> <file>.ots
"""
import sys, json, urllib.request, datetime
from opentimestamps.core.timestamp import DetachedTimestampFile
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
from opentimestamps.core.serialize import StreamDeserializationContext
data_path, ots_path = sys.argv[1], sys.argv[2]
with open(ots_path,'rb') as f: dtf = DetachedTimestampFile.deserialize(StreamDeserializationContext(f))
with open(data_path,'rb') as f: actual = DetachedTimestampFile.from_fd(OpSHA256(), f).file_digest
print("file digest matches proof:", actual == dtf.file_digest)
get = lambda u: urllib.request.urlopen(u, timeout=20).read().decode()
for msg, att in dtf.timestamp.all_attestations():
    if isinstance(att, BitcoinBlockHeaderAttestation):
        h = get(f"https://blockstream.info/api/block-height/{att.height}")
        b = json.loads(get(f"https://blockstream.info/api/block/{h}"))
        ok = msg[::-1].hex() == b["merkle_root"]
        t = datetime.datetime.fromtimestamp(b["timestamp"], datetime.UTC)
        print(f"block {att.height}: merkle root match={ok}, block time {t:%Y-%m-%d %H:%M} UTC")
