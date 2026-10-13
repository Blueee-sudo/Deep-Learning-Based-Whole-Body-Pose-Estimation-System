const BODY_LINKS = [
  [0, 1], [0, 2], [1, 3], [2, 4],
  [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],
  [5, 11], [6, 12], [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
];

const FOOT_LINKS = [
  [15, 19], [19, 17], [17, 18],
  [16, 22], [22, 20], [20, 21],
];

const FACE_LINKS = (() => {
  const base = 23;
  const links = [];
  for (let i = 0; i < 16; i++) links.push([base + i, base + i + 1]);
  for (let i = 17; i < 21; i++) links.push([base + i, base + i + 1]);
  for (let i = 22; i < 26; i++) links.push([base + i, base + i + 1]);
  for (let i = 27; i < 30; i++) links.push([base + i, base + i + 1]);
  for (let i = 31; i < 35; i++) links.push([base + i, base + i + 1]);
  links.push([base + 35, base + 31]);
  for (let i = 36; i < 41; i++) links.push([base + i, base + i + 1]);
  links.push([base + 41, base + 36]);
  for (let i = 42; i < 47; i++) links.push([base + i, base + i + 1]);
  links.push([base + 47, base + 42]);
  for (let i = 48; i < 59; i++) links.push([base + i, base + i + 1]);
  links.push([base + 59, base + 48]);
  for (let i = 60; i < 67; i++) links.push([base + i, base + i + 1]);
  links.push([base + 67, base + 60]);
  return links;
})();

function handLinks(start) {
  const links = [];
  const fingerBases = [start + 1, start + 5, start + 9, start + 13, start + 17];
  for (const mcp of fingerBases) {
    links.push([start, mcp]);
    links.push([mcp, mcp + 1], [mcp + 1, mcp + 2], [mcp + 2, mcp + 3]);
  }
  return links;
}

const L_HAND_LINKS = handLinks(91);
const R_HAND_LINKS = handLinks(112);

function drawLinks(ctx, kps, links, color, scaleX, scaleY, minScore) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  for (const [a, b] of links) {
    if (a >= kps.length || b >= kps.length) continue;
    const pa = kps[a];
    const pb = kps[b];
    if (!pa || !pb) continue;
    const [xa, ya, sa = 0] = pa;
    const [xb, yb, sb = 0] = pb;
    if (sa < minScore || sb < minScore) continue;
    ctx.beginPath();
    ctx.moveTo(xa * scaleX, ya * scaleY);
    ctx.lineTo(xb * scaleX, yb * scaleY);
    ctx.stroke();
  }
}

function drawPoints(ctx, kps, start, end, color, scaleX, scaleY, minScore, radius = 2.5) {
  ctx.fillStyle = color;
  for (let i = start; i < end; i++) {
    if (i >= kps.length) continue;
    const p = kps[i];
    if (!p) continue;
    const [x, y, s = 0] = p;
    if (s < minScore) continue;
    ctx.beginPath();
    ctx.arc(x * scaleX, y * scaleY, radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawBbox(ctx, bbox, scaleX, scaleY, color = "rgba(78, 126, 255, 0.95)") {
  if (!Array.isArray(bbox) || bbox.length < 4) return;
  const [x1, y1, x2, y2] = bbox;
  const w = (x2 - x1) * scaleX;
  const h = (y2 - y1) * scaleY;
  if (w <= 1 || h <= 1) return;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.strokeRect(x1 * scaleX, y1 * scaleY, w, h);
}

export function drawRealtimePose(ctx, persons, opts = {}) {
  const {
    scaleX = 1,
    scaleY = 1,
    minScore = 0.2,
    withBbox = true,
    withFaceHands = false,
  } = opts;

  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  if (!Array.isArray(persons) || !persons.length) return;

  for (const person of persons) {
    const kps = person?.keypoints || [];
    if (!kps.length) continue;

    if (withBbox) drawBbox(ctx, person?.bbox, scaleX, scaleY);

    drawLinks(ctx, kps, BODY_LINKS, "#ff9018", scaleX, scaleY, minScore);
    drawPoints(ctx, kps, 0, 17, "#ff9018", scaleX, scaleY, minScore);

    drawLinks(ctx, kps, FOOT_LINKS, "#d12e72", scaleX, scaleY, minScore);
    drawPoints(ctx, kps, 17, 23, "#d12e72", scaleX, scaleY, minScore);

    if (withFaceHands) {
      drawLinks(ctx, kps, FACE_LINKS, "#1ac452", scaleX, scaleY, minScore);
      drawPoints(ctx, kps, 23, 91, "#1ac452", scaleX, scaleY, minScore, 1.6);
      drawLinks(ctx, kps, L_HAND_LINKS, "#168cfa", scaleX, scaleY, minScore);
      drawPoints(ctx, kps, 91, 112, "#168cfa", scaleX, scaleY, minScore, 1.8);
      drawLinks(ctx, kps, R_HAND_LINKS, "#2d22f5", scaleX, scaleY, minScore);
      drawPoints(ctx, kps, 112, 133, "#2d22f5", scaleX, scaleY, minScore, 1.8);
    }
  }
}
