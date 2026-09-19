#!/usr/bin/env node
/**
 * Render the favicon PNG fallbacks from client/favicon.svg.
 *
 *     node client-measurements/favicon/render.mjs
 *
 * Writes client/favicon-32.png and client/apple-touch-icon.png in place, then
 * prints what changed. Run it after any edit to favicon.svg: iPhone Safari
 * ignores SVG favicons and takes the PNGs instead, so an SVG-only change ships
 * a viewer whose icon is right on the desktop and stale on the phone.
 *
 * It exists because the last favicon left its regeneration path in a code
 * comment, which is the same shape as the bug that let the social card drift
 * for six weeks: a committed raster that nothing can rebuild and nothing
 * checks. The renderer is headless Chrome, which is already how this thread
 * photographs the client, and the only thing on the machine that rasterizes
 * SVG (no rsvg, no ImageMagick, no Inkscape).
 *
 * The touch icon is NOT the same drawing. iOS masks its own rounded corners
 * over whatever it is given, so it is rendered from a full-bleed variant of
 * the same file: the card's rounded rect becomes the whole square and the
 * meadow runs to the edges. The substitution is asserted, not attempted --
 * if favicon.svg is restyled such that either shape stops matching, this
 * stops rather than quietly shipping a rounded card inside Apple's mask.
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const CLIENT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'client');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

// The card, and what it becomes when it has to fill the square. The card
// rect is matched literally; the meadow's HORIZON is read out rather than
// written down, because the horizon is a dial the icon gets tuned on and a
// build step you have to remember to edit is a build step that ships wrong.
const CARD = '<rect x="1" y="1" width="62" height="62" rx="14" fill="#fdf6ec"/>';
const SQUARE = '<rect width="64" height="64" fill="#fdf6ec"/>';
const MEADOW = /<path d="M1 ([\d.]+) L63 \1 L63 49 Q63 63 49 63 L15 63 Q1 63 1 49 Z" fill="(#[0-9a-f]{6})"\/>/;

const svg = readFileSync(join(CLIENT, 'favicon.svg'), 'utf8');
const tmp = mkdtempSync(join(tmpdir(), 'favicon-'));

if (!svg.includes(CARD)) {
  throw new Error(`favicon.svg no longer contains the card rect the full-bleed variant replaces:\n  ${CARD}`);
}
const meadow = svg.match(MEADOW);
if (!meadow) {
  throw new Error('favicon.svg no longer contains a meadow band of the shape the full-bleed variant replaces');
}
const [band, horizon, green] = meadow;
const bleed = svg
  .replace(CARD, SQUARE)
  .replace(band, `<path d="M0 ${horizon} H64 V64 H0 Z" fill="${green}"/>`);
console.log(`full-bleed variant: horizon ${horizon}, meadow ${green}`);
writeFileSync(join(tmp, 'bleed.svg'), bleed);

function render(source, size, out) {
  // An <img> at an explicit size rather than the SVG itself: Chrome's
  // screenshot honours the window, and a viewBox-only document would be
  // rasterized at whatever intrinsic size it felt like first.
  const page = join(tmp, `page-${out}.html`);
  writeFileSync(page, '<!DOCTYPE html><html><head><meta charset="utf-8">'
    + `<style>html,body{margin:0}img{display:block;width:${size}px;height:${size}px}</style>`
    + `</head><body><img src="file://${source}"></body></html>`);
  const target = join(CLIENT, out);
  const before = statSync(target, { throwIfNoEntry: false })?.size ?? 0;
  execFileSync(CHROME, [
    '--headless', '--disable-gpu', '--no-sandbox',
    `--screenshot=${target}`, `--window-size=${size},${size}`,
    '--default-background-color=00000000', '--allow-file-access-from-files',
    `file://${page}`,
  ], { stdio: ['ignore', 'ignore', 'ignore'] });
  const after = statSync(target).size;
  console.log(`${out.padEnd(21)} ${size}x${size}  ${before} -> ${after} bytes`);
}

render(join(CLIENT, 'favicon.svg'), 32, 'favicon-32.png');
render(join(tmp, 'bleed.svg'), 180, 'apple-touch-icon.png');
