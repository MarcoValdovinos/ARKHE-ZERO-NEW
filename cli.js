#!/usr/bin/env node
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd !== 'notarize') {
  console.log('Uso: npx kronos-desk-val notarize <archivo> --author "Tu Nombre"');
  process.exit(0);
}

const file = args[1];
const getFlag = (n) => {
  const i = args.indexOf(n);
  return i > -1 ? args[i + 1] : null;
};

const author = getFlag('--author') || 'Marco A. Rojas Valdovinos';
const outDir = getFlag('--out') || './certificados-sycro';

if (!file || !fs.existsSync(file)) {
  console.error('Archivo no encontrado:', file);
  process.exit(1);
}

const buf = fs.readFileSync(file);
const sha256 = crypto.createHash('sha256').update(buf).digest('hex');
const sha512 = crypto.createHash('sha512').update(buf).digest('base64');
const folio = `SYCRO-${Date.now().toString(36).toUpperCase()}-${sha256.slice(0, 8).toUpperCase()}`;
const now = new Date().toISOString();

const cert = {
  protocol: 'ARKHE-ZERO-KRONOS',
  product: 'SYCRO NOTARY ARKHE ZERO',
  folio,
  file: { name: path.basename(file), size_bytes: buf.length, sha256, sha512 },
  author,
  manifest: 'TOLUCA-GLOBAL-e8d9eac8',
  governance: 'SCDR-002 - 51% Humano / 49% IA',
  standards: ['Dublin Core ISO 15836'],
  timestamp: now,
  status: 'HASH_LOCAL_SIN_FIRMA'
};

fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, `${path.basename(file)}.sycro.json`);
fs.writeFileSync(outPath, JSON.stringify(cert, null, 2));

console.log('NOTARIZADO');
console.log('Folio:', folio);
console.log('SHA-256:', sha256);
console.log('Certificado:', outPath);
