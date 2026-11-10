"""Rewrite the multicam track of a Resolve .drt with an angle cut list (no UI).
usage: drt_cuts.py SRC.drt OUT.drt NEW_TIMELINE_NAME "A:0-300,B:300-600,..."
Angle letter -> 'Camera 1'/'Camera 2' (A/B). Frames are timeline frames, [start,end)."""
import sys, re, uuid, zipfile, io
src, out, newname, spec = sys.argv[1:5]
CAM = {"A": b"Camera 1", "B": b"Camera 2"}
cuts = []
for part in spec.split(","):
    ang, rng = part.split(":"); s, e = map(int, rng.split("-")); cuts.append((ang, s, e))
assert all(cuts[i][2] == cuts[i+1][1] for i in range(len(cuts)-1)), "cuts must be contiguous"
zin = zipfile.ZipFile(src); files = {n: zin.read(n) for n in zin.namelist()}
seq_name = [n for n in files if n.startswith("SeqContainer/") and b"Sm2TiVideoClip" in files[n] and b"<MediaFilePath/>" in files[n]]
assert len(seq_name) == 1, seq_name
t = files[seq_name[0]].decode()
clips = re.findall(r"     <Element>\n      <Sm2TiVideoClip.*?</Sm2TiVideoClip>\n     </Element>\n", t, re.S)
assert len(clips) >= 1
tmpl = clips[0]
new = []
for ang, s, e in cuts:
    c = re.sub(r'Sm2TiVideoClip DbId="[^"]+"', f'Sm2TiVideoClip DbId="{uuid.uuid4()}"', tmpl)
    c = re.sub(r'BtThumnail DbId="[^"]+"', f'BtThumnail DbId="{uuid.uuid4()}"', c)
    blob = bytes.fromhex(re.search(r"<FieldsBlob>([0-9a-f]+)</FieldsBlob>", c).group(1))
    assert blob.count(b"Camera 1") + blob.count(b"Camera 2") == 1
    blob = blob.replace(b"Camera 1", CAM[ang]).replace(b"Camera 2", CAM[ang])
    c = re.sub(r"<FieldsBlob>[0-9a-f]+</FieldsBlob>", f"<FieldsBlob>{blob.hex()}</FieldsBlob>", c, count=1)
    c = re.sub(r"<Start>\d+</Start>", f"<Start>{s}</Start>", c)
    c = re.sub(r"<Duration>\d+</Duration>", f"<Duration>{e-s}</Duration>", c, count=1)
    c = re.sub(r"<In>\d*</In>|<In/>", f"<In>{s}</In>" if s else "<In/>", c)
    new.append(c)
first = t.index(clips[0]); last = t.index(clips[-1]) + len(clips[-1])
t = t[:first] + "".join(new) + t[last:]
files[seq_name[0]] = t.encode()
# rename timeline in media pool folder + project
old = re.search(rb"<Sm2MpTimelineClip.*?<Name>([^<]*)</Name>", files["MediaPool/Master/MpFolder.xml"], re.S).group(1)
for n in files:
    if n.endswith(".xml"): files[n] = files[n].replace(old, newname.encode())
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist(): z.writestr(n, files[n])
print("old name:", old.decode(), "->", newname); print("cuts:", cuts)
