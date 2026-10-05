/**
 * favicon.ico writer — packs PNG-compressed frames into a single .ico
 * (supported by every current browser; also fine for Windows shell).
 */
import { writeFileSync } from 'node:fs';

export function writeIco(frames, out) {
  // frames: [{ png: Buffer, size: number }] sorted ascending
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0); // reserved
  header.writeUInt16LE(1, 2); // type: icon
  header.writeUInt16LE(frames.length, 4);

  const dir = Buffer.alloc(16 * frames.length);
  let offset = 6 + dir.length;
  frames.forEach((f, i) => {
    const b = i * 16;
    dir.writeUInt8(f.size >= 256 ? 0 : f.size, b + 0);
    dir.writeUInt8(f.size >= 256 ? 0 : f.size, b + 1);
    dir.writeUInt8(0, b + 2); // palette
    dir.writeUInt8(0, b + 3); // reserved
    dir.writeUInt16LE(1, b + 4); // planes
    dir.writeUInt16LE(32, b + 6); // bpp
    dir.writeUInt32LE(f.png.length, b + 8);
    dir.writeUInt32LE(offset, b + 12);
    offset += f.png.length;
  });

  writeFileSync(out, Buffer.concat([header, dir, ...frames.map((f) => f.png)]));
  return out;
}
