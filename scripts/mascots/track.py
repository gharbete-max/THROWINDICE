"""Track 2D body keypoints (COCO-17) through the reference clip at 24 fps. Saves kp.npy: (frames, 17, 3) = x, y, conf
in pixels of the cropped frame, plus a few overlay images for checking."""
import sys, cv2, numpy as np
from ultralytics import YOLO
V = sys.argv[1]; FPS = 24
cap = cv2.VideoCapture(V); src = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
model = YOLO('/home/claude/pose/yolo11x-pose.pt')
out, k, t = [], 0, 0.0
idx = set(int(round(i * src / FPS)) for i in range(int(n * FPS / src)))
while True:
    ok, fr = cap.read()
    if not ok: break
    if k in idx:
        r = model(fr, verbose=False, imgsz=960)[0]
        if r.keypoints is not None and len(r.keypoints):
            b = int(np.argmax(r.boxes.conf.cpu().numpy()))
            kp = np.c_[r.keypoints.xy[b].cpu().numpy(), r.keypoints.conf[b].cpu().numpy()]
        else: kp = np.zeros((17, 3))
        out.append(kp)
        if len(out) in (1, 60, 150, 260, 380):
            im = fr.copy()
            for x, y, c in kp:
                if c > .3: cv2.circle(im, (int(x), int(y)), 14, (0, 0, 255), -1)
            cv2.imwrite(f'/home/claude/pose/ov_{len(out):03d}.jpg', cv2.resize(im, (im.shape[1] // 4, im.shape[0] // 4)))
        if len(out) % 40 == 0: np.save("/home/claude/pose/kp_partial.npy", np.array(out))
    k += 1
K = np.array(out); np.save('/home/claude/pose/kp.npy', K)
print('frames', len(K), 'mean conf per joint', K[:, :, 2].mean(0).round(2))
