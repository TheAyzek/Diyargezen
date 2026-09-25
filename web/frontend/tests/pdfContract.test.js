import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { PDFDocument } from 'pdf-lib';
import { generateCharacterPDFBytes } from '../src/utils/pdfExportUtil.js';

test('shared live/download generator preserves original AcroForm fields and caches template', async () => {
  const template = await readFile(new URL('../public/templates/pf1e_sheet.pdf', import.meta.url));
  let requests = 0;
  globalThis.fetch = async () => { requests++; return {
    ok: true, arrayBuffer: async () => template.buffer.slice(template.byteOffset, template.byteOffset + template.byteLength),
  }; };
  const state = { name: 'Valeros', race: 'Human', class: 'Fighter', level: 3, equipment: [],
    feats: [], traits: [], spells: [], recalcedData: { total_weight: 12.5, ability_scores: { Strength: 16 } } };
  const bytes = await generateCharacterPDFBytes(state);
  const doc = await PDFDocument.load(bytes);
  const form = doc.getForm();
  assert.equal(form.getTextField('Character Name').getText(), 'Valeros');
  assert.equal(form.getTextField('Race').getText(), 'Human');
  assert.equal(form.getTextField('modifier').getText(), '+3');
  assert.equal(form.getTextField('Base').getText(), '30');
  assert.equal(form.getTextField('Squares1').getText(), '6');
  assert.deepEqual(state.recalcedData.ability_scores, { Strength: 16 });
  assert.equal(form.getTextField('TOTAL WEIGHT').getText(), '12.5 lbs');
  assert.ok(form.getFields().length > 100);
  const zeroDoc = await PDFDocument.load(await generateCharacterPDFBytes({ ...state, name: 'Seoni',
    hit_points: 0, recalcedData: { speed: 0, armor_class: 0 } }));
  assert.equal(zeroDoc.getForm().getTextField('Base').getText(), '0');
  assert.equal(zeroDoc.getForm().getTextField('hit points').getText(), '0');
  assert.equal(zeroDoc.getForm().getTextField('armor class').getText(), '0');
  assert.equal(requests, 1);
  if (process.env.DIYARGEZEN_PDF_QA_DIR) {
    await mkdir(process.env.DIYARGEZEN_PDF_QA_DIR, { recursive: true });
    await writeFile(process.env.DIYARGEZEN_PDF_QA_DIR + '/pf1e-contract.pdf', bytes);
  }
});
