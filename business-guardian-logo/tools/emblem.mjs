/**
 * BUSINESS GUARDIAN — emblem geometry engine
 * -------------------------------------------
 * One coherent symbol built from a single construction grid:
 *
 *   1. SHELL .......... outer silhouette = owl head (ear tufts + crown) which
 *                       is simultaneously a shield (vertical walls tapering to
 *                       a single point).
 *   2. SOCKET ......... the carved ring that defines each owl eye.
 *   3. IRIS RING ...... material ring  -> "monitoring ring".
 *   4. SENSOR CORE .... solid island    -> "pupil / sensor".
 *   5. GUARDLINE ...... the facial-disc boundary. It leaves each eye at the
 *                       bottom of the socket, sweeps around it and converges
 *                       to one point: the hidden shield tip. The dark wedge
 *                       between the two guardlines is the owl's beak, so the
 *                       beak, the facial disc and the shield tip are one
 *                       single geometric gesture.
 */

export const n = (v) => Number(v.toFixed(2));

export function circle(cx, cy, r) {
  const x = n(cx - r);
  const d = n(2 * r);
  return `M ${x} ${n(cy)} a ${n(r)} ${n(r)} 0 1 0 ${d} 0 a ${n(r)} ${n(r)} 0 1 0 ${-d} 0 Z`;
}

export function poly(pts) {
  return `M ${n(pts[0][0])} ${n(pts[0][1])} ` + pts.slice(1).map(([x, y]) => `L ${n(x)} ${n(y)}`).join(' ') + ' Z';
}

const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const len = (v) => Math.hypot(v[0], v[1]);
const unit = (v) => {
  const l = len(v) || 1;
  return [v[0] / l, v[1] / l];
};

/**
 * Corner control: builds a silhouette from cubic segments and replaces the
 * chosen sharp vertices with a small tangent arc (`L p_in Q vertex p_out`),
 * so tips stay crisp but never needle-sharp — which is what survives being
 * scaled down to a 16px favicon.
 *
 * segs: [{ p:[x,y], c1, c2 }]  — first entry may carry `m:[x,y]`
 * fillet: { [segIndex]: radius } — radius applied at the END of seg index
 */
export function buildPath(segs, fillet = {}) {
  const out = [];
  const start = segs[0].m || segs[0].p;
  out.push(`M ${n(start[0])} ${n(start[1])}`);

  for (let i = 0; i < segs.length; i++) {
    const s = segs[i];
    const prevEnd = i === 0 ? start : segs[i - 1].p;
    let end = s.p;
    let r = fillet[i];

    if (r) {
      const din = unit(sub(end, s.c2)); // incoming tangent direction at vertex
      const next = segs[(i + 1) % segs.length];
      const dout = unit(sub(next.c1, end)); // outgoing tangent direction
      const pin = [end[0] - din[0] * r, end[1] - din[1] * r];
      const pout = [end[0] + dout[0] * r, end[1] + dout[1] * r];
      out.push(`C ${n(s.c1[0])} ${n(s.c1[1])} ${n(s.c2[0])} ${n(s.c2[1])} ${n(pin[0])} ${n(pin[1])}`);
      out.push(`Q ${n(end[0])} ${n(end[1])} ${n(pout[0])} ${n(pout[1])}`);
      // shift the next segment's start implicitly by shortening its controls
      const nx = segs[(i + 1) % segs.length];
      const d2 = unit(sub(nx.p, nx.c1));
      const back = len(sub(nx.c1, end));
      nx.c1 = [pout[0] + d2[0] * back, pout[1] + d2[1] * back];
      if (i + 1 === segs.length && nx.m) nx.m = [...pout];
      continue;
    }
    out.push(
      `C ${n(s.c1[0])} ${n(s.c1[1])} ${n(s.c2[0])} ${n(s.c2[1])} ${n(end[0])} ${n(end[1])}`
    );
    void prevEnd;
  }
  out.push('Z');
  return out.join(' ');
}

/* ------------------------------------------------------------------ */
/* Construction grid                                                   */
/* ------------------------------------------------------------------ */

export const BASE = {
  W: 512,
  cx: 256,

  /* outer silhouette: owl head + hidden shield */
  top: 'tuft',
  ear: [108, 62], // ear-tuft tip
  notch: [132, 140], // valley where the tuft meets the crown
  domeLift: -10, // crown sits just below the tuft base line (saddle)
  sideMax: [66, 236], // widest point of the shield wall
  sideLow: [80, 330],
  apex: [256, 466], // hidden shield point

  /* eyes */
  ex: 80, // eye offset from the centre line
  ey: 238, // eye centre line
  rSocket: 71, // outer edge of the carved socket
  rRing: 55, // inner edge of the carved socket = outer edge of the monitoring ring
  rGap: 41, // outer edge of the carved pupil gap
  rPupil: 31, // sensor core radius

  /* guardline: facial-disc boundary that doubles as the shield tip */
  guardEnd: 404,
  guardGrow: 4,

  /* corner control */
  tipRound: 7,
  notchRound: 9,
  browModeRound: 30,
  apexRound: 5,
};

/*
 * Small-size variant. Below ~64px the fine monitoring ring collapses, so the
 * eye is rebuilt with a bolder ring and a larger sensor core, the status point
 * is dropped and the guardline thickens. Same gesture, fewer pixels.
 */
export const ICON = {
  ...BASE,
  ear: [110, 66],
  notch: [134, 144],
  rSocket: 74, // socket widened so the monitoring ring reads at 16px
  rRing: 51,
  rGap: 46,
  rPupil: 36, // larger sensor core
  guardGrow: 12,
};

export const eyeOf = (g, side) => [g.cx + side * g.ex, g.ey];

export function mkG(o = {}) {
  const g = { ...BASE, ...o };
  g.eye = (s) => eyeOf(g, s);
  return g;
}

export const G = mkG();

/* ------------------------------------------------------------------ */
/* 1. Shell                                                            */
/* ------------------------------------------------------------------ */

/**
 * Crown helper: broad arc from `from` to `to` whose apex reaches `apexY`.
 * (For a symmetric cubic the midpoint sits at 1/4 of the control height,
 * hence the 0.75 correction.)
 */
function dome(from, to, apexY) {
  const midY = (from[1] + to[1]) / 2;
  const cy = midY + (apexY - midY) / 0.75;
  const k = 0.52;
  const dx = (to[0] - from[0]) * k;
  return {
    c1: [from[0] + dx, cy],
    c2: [to[0] - dx, cy],
  };
}

export function shellSegments(g = G) {
  const [LTx, LTy] = g.ear;
  const [Nx, Ny] = g.notch;
  const [Sx, Sy] = g.sideMax;
  const [Lx, Ly] = g.sideLow;
  const [Ax, Ay] = g.apex;
  const m = (v) => 2 * g.cx - v;
  const M = (p) => [m(p[0]), p[1]];

  const segs = [
    /* left wall: ear tip -> widest point */
    { m: [LTx, LTy], p: [Sx, Sy], c1: [LTx - 16, LTy + 64], c2: [Sx + 2, Sy - 74] },
    /* lower left wall */
    { p: [Lx, Ly], c1: [Sx - 1, Sy + 50], c2: [Sx + 6, Sy + 82] },
    /* shield taper to the point */
    { p: [Ax, Ay], c1: [Lx + 24, Ly + 62], c2: [g.cx - 72, Ay - 24] },
    /* mirrored taper */
    { p: M([Lx, Ly]), c1: [g.cx + 72, Ay - 24], c2: M([Lx + 24, Ly + 62]) },
    /* lower right wall */
    { p: M([Sx, Sy]), c1: M([Sx + 6, Sy + 82]), c2: M([Sx - 1, Sy + 50]) },
    /* right wall up to the ear tip */
    { p: M([LTx, LTy]), c1: M([Sx + 2, Sy - 74]), c2: M([LTx - 16, LTy + 64]) },
  ];

  /* ---- crown, travelled right -> left, closing on the left ear tip ---- */
  if (g.top === 'dome') {
    const d = dome(M([LTx, LTy]), [LTx, LTy], LTy - g.domeLift);
    segs.push({ p: [LTx, LTy], c1: d.c1, c2: d.c2 });
  } else if (g.top === 'chevron') {
    const peak = [g.cx, Ny - g.domeLift];
    segs.push({ p: M([Nx, Ny]), c1: M([LTx + 8, LTy + 40]), c2: M([Nx - 30, Ny - 6]) });
    segs.push({ p: peak, c1: [M([Nx, Ny])[0] - 34, Ny - 6], c2: [g.cx + 34, peak[1] + 2] });
    segs.push({ p: [Nx, Ny], c1: [g.cx - 34, peak[1] + 2], c2: [Nx + 30, Ny - 6] });
    segs.push({ p: [LTx, LTy], c1: [Nx - 30, Ny - 6], c2: [LTx + 8, LTy + 40] });
  } else {
    /* ear tufts */
    segs.push({ p: M([Nx, Ny]), c1: M([LTx + 10, LTy + 44]), c2: M([Nx - 34, Ny - 26]) });
    if (g.browMode) {
      /* two brow arcs meeting in a shallow forehead dip at the centre line */
      const midY = Ny - g.domeLift + g.browMode;
      const left = dome(M([Nx, Ny]), [g.cx, midY], Ny - g.domeLift);
      const right = dome([g.cx, midY], [Nx, Ny], Ny - g.domeLift);
      segs.push({ p: [g.cx, midY], c1: left.c1, c2: left.c2 });
      segs.push({ p: [Nx, Ny], c1: right.c1, c2: right.c2 });
    } else {
      const d = dome(M([Nx, Ny]), [Nx, Ny], Ny - g.domeLift);
      segs.push({ p: [Nx, Ny], c1: d.c1, c2: d.c2 });
    }
    segs.push({ p: [LTx, LTy], c1: [Nx - 34, Ny - 26], c2: [LTx + 10, LTy + 44] });
  }

  return segs;
}

export function shellPath(g = G) {
  const segs = shellSegments(g);
  const last = segs.length - 1;
  const fillet = { 2: g.apexRound };
  if (g.top === 'dome') {
    fillet[last - 1] = g.tipRound; // right shoulder
    fillet[last] = g.tipRound; // left shoulder
  } else if (g.top === 'chevron') {
    fillet[last] = g.tipRound; // left ear tip
    fillet[last - 1] = g.notchRound;
    fillet[last - 2] = g.tipRound; // crown peak
    fillet[last - 3] = g.notchRound;
    fillet[last - 4] = g.tipRound; // right ear tip
  } else if (g.browMode) {
    fillet[last] = g.tipRound; // left ear tip
    fillet[last - 1] = g.notchRound; // left notch valley
    fillet[last - 2] = g.browModeRound; // forehead dip
    fillet[last - 3] = g.notchRound; // right notch valley
    fillet[last - 4] = g.tipRound; // right ear tip
  } else {
    fillet[last] = g.tipRound; // left ear tip
    fillet[last - 1] = g.notchRound; // left notch valley
    fillet[last - 2] = g.notchRound; // right notch valley
    fillet[last - 3] = g.tipRound; // right ear tip
  }
  return buildPath(segs, fillet);
}


/* ------------------------------------------------------------------ */
/* Geometry helpers                                                    */
/* ------------------------------------------------------------------ */

/** Flatten a shell into point samples (used for tight bounding boxes). */
export function shellBBox(g = G, steps = 48) {
  const segs = shellSegments(g);
  const start = segs[0].m || segs[0].p;
  let prev = start;
  const pts = [start];
  const at = (p0, c1, c2, p1, t) => {
    const u = 1 - t;
    return [
      u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p1[0],
      u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p1[1],
    ];
  };
  for (const s of segs) {
    for (let i = 1; i <= steps; i++) pts.push(at(prev, s.c1, s.c2, s.p, i / steps));
    prev = s.p;
  }
  const xs = pts.map((p) => p[0]);
  const ys = pts.map((p) => p[1]);
  const bb = { x0: Math.min(...xs), y0: Math.min(...ys), x1: Math.max(...xs), y1: Math.max(...ys) };
  return { ...bb, w: bb.x1 - bb.x0, h: bb.y1 - bb.y0, cx: (bb.x0 + bb.x1) / 2, cy: (bb.y0 + bb.y1) / 2 };
}

/* ------------------------------------------------------------------ */
/* 2/3/4. Eyes                                                        */
/* ------------------------------------------------------------------ */

export function socketPath(side, g = G) {
  const [cx, cy] = eyeOf(g, side);
  return `${circle(cx, cy, g.rSocket)} ${circle(cx, cy, g.rRing)}`;
}
export function pupilGapPath(side, g = G) {
  const [cx, cy] = eyeOf(g, side);
  return `${circle(cx, cy, g.rGap)} ${circle(cx, cy, g.rPupil)}`;
}
export function pupilPath(side, g = G) {
  const [cx, cy] = eyeOf(g, side);
  return circle(cx, cy, g.rPupil);
}

/* ------------------------------------------------------------------ */
/* 5. Guardline                                                       */
/* ------------------------------------------------------------------ */

export function guardPath(g = G) {
  const { cx } = g;
  const grow = g.guardGrow;
  const tip = [cx, g.guardEnd];
  const [lx, ly] = eyeOf(g, -1);
  const [rx, ry] = eyeOf(g, 1);

  /* start points sit at the bottom of each eye circle, and the curve leaves
     them tangentially — so the guardline continues the eye socket instead of
     kinking away from it */
  const oL = [lx, ly + g.rSocket];
  const oR = [rx, ry + g.rSocket];
  const iL = [lx, ly + g.rRing - grow];
  const iR = [rx, ry + g.rRing - grow];
  const t = 40; // tangential lead-out

  return [
    `M ${n(oL[0])} ${n(oL[1])}`,
    `C ${n(oL[0] + t)} ${n(oL[1] + 2)} ${n(cx - 30)} ${n(tip[1] - 40)} ${n(tip[0])} ${n(tip[1])}`,
    `C ${n(cx + 30)} ${n(tip[1] - 40)} ${n(oR[0] - t)} ${n(oR[1] + 2)} ${n(oR[0])} ${n(oR[1])}`,
    `L ${n(iR[0])} ${n(iR[1])}`,
    `C ${n(iR[0] - t)} ${n(iR[1] + 2)} ${n(cx + 26)} ${n(tip[1] - 48)} ${n(tip[0])} ${n(tip[1])}`,
    `C ${n(cx - 26)} ${n(tip[1] - 48)} ${n(iL[0] + t)} ${n(iL[1] + 2)} ${n(iL[0])} ${n(iL[1])}`,
    'Z',
  ].join(' ');
}

/**
 * Reticle break: voids cut across the monitoring ring so the eye reads as a
 * monitoring/target indicator at large sizes. Deliberately excluded from the
 * small-icon variant.
 */
export function ringGapPath(side, g = G, angles = [45, 135, 225, 315], hw = 10, pad = 3) {
  const [cx, cy] = eyeOf(g, side);
  const ri = g.rRing - pad;
  const ro = g.rSocket + pad;
  const pt = (r, a) => [
    cx + r * Math.cos((a * Math.PI) / 180),
    cy + r * Math.sin((a * Math.PI) / 180),
  ];
  return angles
    .map((a) => poly([pt(ri, a - hw), pt(ro, a - hw), pt(ro, a + hw), pt(ri, a + hw)]))
    .join(' ');
}

/** Status point inside the sensor core (the "I am actively watching" dot). */
export function statusPath(side, g = G, a = -45, r = 17, rad = 8.5) {
  const [cx, cy] = eyeOf(g, side);
  const x = cx + r * Math.cos((a * Math.PI) / 180);
  const y = cy + r * Math.sin((a * Math.PI) / 180);
  return circle(x, y, rad);
}

/* ------------------------------------------------------------------ */
/* Assembly                                                           */
/* ------------------------------------------------------------------ */

export function emblemParts(g = G, opts = {}) {
  const { simple = false, guard = true, reticle = 0, status = 0 } = opts;
  const holes = [];
  const voids = [];

  if (simple) {
    for (const s of [-1, 1]) {
      const [cx, cy] = eyeOf(g, s);
      holes.push(circle(cx, cy, g.rSocket * 0.8));
    }
  } else {
    for (const s of [-1, 1]) {
      holes.push(socketPath(s, g));
      holes.push(pupilGapPath(s, g));
    }
    if (guard) holes.push(guardPath(g));
    if (reticle) {
      for (const s of [-1, 1]) {
        holes.push(
          ringGapPath(s, g, reticle === 1 ? [0, 90, 180, 270] : [45, 135, 225, 315], reticle === 1 ? 13 : 11)
        );
      }
    }
  }

  const pupils = [-1, 1]
    .map((s) => {
      const [cx, cy] = eyeOf(g, s);
      return circle(cx, cy, simple ? g.rPupil * 0.92 : g.rPupil);
    })
    .join(' ');

  if (status) for (const s of [-1, 1]) voids.push(statusPath(s, g, status === 2 ? -90 : -45));

  return {
    viewBox: `0 0 ${g.W} ${g.W}`,
    shell: shellPath(g),
    holes: holes.join(' '),
    pupils,
    voids: voids.join(' '),
  };
}

/** Full emblem mark as standalone SVG (light or dark). */
export function emblemSVG(
  g = G,
  { fill = '#0B1220', accent, simple = false, bg, reticle = 0, status = 0 } = {}
) {
  const p = emblemParts(g, { simple, reticle, status });
  const body = bg
    ? `<rect width="${g.W}" height="${g.W}" fill="${bg}"/>`
    : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${p.viewBox}">
<defs><mask id="bgm" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
<path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/>
</mask></defs>
${body}<g mask="url(#bgm)"><rect width="${g.W}" height="${g.W}" fill="${fill}"/></g>${
    p.voids ? `\n<path d="${p.voids}" fill="${bg || '#fff'}"/>` : ''
  }${accent ? `\n<path d="${p.pupils}" fill="${accent}"/>` : ''}</svg>`;
}
