"""Turn tracked COCO-17 keypoints (pose/kp.npy) into per-frame pose parameters for the dancer rig.
Frontal-plane angles come straight from the video (arms, elbows, thighs, knees, torso lean, head tilt); body turn is
estimated from shoulder width and nose offset; vertical bounce from the hips. Curves are smoothed and the last 0.4 s
blends into the first frame so the dance loops cleanly. Writes bl/dance.npz."""
import numpy as np
import os, sys
K = np.load(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/pose/kp.npy')            # (n, 17, 3) x, y, conf
n = len(K); NOSE, LEYE, REYE, LEAR, REAR, LSH, RSH, LEL, REL, LWR, RWR, LHIP, RHIP, LKN, RKN, LAN, RAN = range(17)

# fill low-confidence points by interpolation over time, then smooth (Gaussian, ~2 frames)
P = K[:, :, :2].copy(); C = K[:, :, 2]
for j in range(17):
    ok = C[:, j] > 0.3
    if ok.sum() > 2:
        for d in range(2): P[:, j, d] = np.interp(np.arange(n), np.nonzero(ok)[0], P[ok, j, d])
def smooth(a, s=1.6):
    r = np.arange(-6, 7); w = np.exp(-r ** 2 / (2 * s * s)); w /= w.sum()
    pad = np.concatenate([a[-6:], a, a[:6]]); return np.convolve(pad, w, 'same')[6:-6]
for j in range(17):
    for d in range(2): P[:, j, d] = smooth(P[:, j, d])

v = lambda a, b: P[:, b] - P[:, a]
up = lambda u, side: np.arctan2(-u[:, 1], side * u[:, 0])   # angle above "pointing outward", image y is down
torso = np.linalg.norm((P[:, LSH] + P[:, RSH]) / 2 - (P[:, LHIP] + P[:, RHIP]) / 2, axis=1).mean()

# the subject faces the camera, so the person's left side is on image right (+x) - the same as the rig's .L side
W = lambda a: (a + np.pi) % (2 * np.pi) - np.pi           # wrap to (-pi, pi]
L2 = lambda a: (a + np.pi / 2) % np.pi - np.pi / 2       # a line's angle, direction-free
aL = np.clip(W(up(v(LSH, LEL), +1)), -0.85, 1.9); aR = np.clip(W(up(v(RSH, REL), -1)), -0.85, 1.9)  # stays clear of the round tummy
elbow = lambda b: np.clip(np.where(W(b) < -0.7, W(b) + 2 * np.pi, W(b)), -0.7, 2.7)   # elbows fold one way only
bL = elbow(up(v(LEL, LWR), +1) - aL); bR = elbow(up(v(REL, RWR), -1) - aR)
def knee(h, k, a):
    u, w = P[:, h] - P[:, k], P[:, a] - P[:, k]
    ang = np.arccos(np.clip((u * w).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(w, axis=1) + 1e-6), -1, 1))
    return (np.pi - ang) / 2                              # rig: leg -a, shin +2a, foot -a
kL, kR = knee(LHIP, LKN, LAN), knee(RHIP, RKN, RAN)
thigh = lambda h, a: np.arctan2(P[:, a, 0] - P[:, h, 0], P[:, a, 1] - P[:, h, 1])   # sideways angle of hip->ankle
sL, sR = np.clip(thigh(LHIP, LAN), -0.6, 0.6), np.clip(thigh(RHIP, RAN), -0.6, 0.6)
mid_sh = (P[:, LSH] + P[:, RSH]) / 2; mid_hp = (P[:, LHIP] + P[:, RHIP]) / 2
lean = np.clip(W(np.arctan2(mid_sh[:, 0] - mid_hp[:, 0], mid_hp[:, 1] - mid_sh[:, 1])), -0.45, 0.45)
hipt = np.clip(L2(np.arctan2(P[:, LHIP, 1] - P[:, RHIP, 1], P[:, LHIP, 0] - P[:, RHIP, 0])), -0.4, 0.4)
eye = P[:, LEYE] - P[:, REYE]; tilt = np.clip(L2(np.arctan2(eye[:, 1], eye[:, 0])), -0.5, 0.5)
shw = np.linalg.norm(v(RSH, LSH), axis=1); turn = np.arccos(np.clip(shw / np.percentile(shw, 95), 0, 1))
side = np.sign(P[:, NOSE, 0] - mid_sh[:, 0]); yaw = np.clip(np.where(np.abs(P[:, NOSE, 0] - mid_sh[:, 0]) > 0.04 * torso, side, 0) * turn * 0.3, -0.45, 0.45)
look = np.clip((P[:, NOSE, 0] - (P[:, LEAR, 0] + P[:, REAR, 0]) / 2) / (0.5 * shw + 1e-6), -1, 1) * 0.0  # head turn from the video is unreliable on the plush
bounce = -(mid_hp[:, 1] - np.median(mid_hp[:, 1])) / torso        # + = up, in torso lengths
dx = (mid_hp[:, 0] - (P[:, LAN, 0] + P[:, RAN, 0]) / 2) / torso

D = dict(aL=aL, aR=aR, bL=bL, bR=bR, kL=kL, kR=kR, sL=sL, sR=sR, lean=lean, hipt=hipt, tilt=tilt, yaw=yaw, look=look, bounce=bounce, dx=dx)
for k in D: D[k] = smooth(D[k], 1.2)
blend = int(0.4 * 24)                                     # loop seam: ease the last frames back to frame 0
for k in D:
    a = D[k]; w = np.clip((np.arange(n) - (n - blend)) / blend, 0, 1); w = w * w * (3 - 2 * w)
    D[k] = a * (1 - w) + a[0] * w
np.savez('/home/claude/bl/dance.npz', n=n, **D)
print(n, 'frames;', {k: (round(float(D[k].min()), 2), round(float(D[k].max()), 2)) for k in D})
