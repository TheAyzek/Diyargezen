let templatePromise;

export function loadPdfTemplate() {
  if (!templatePromise) templatePromise = (async () => {
    for (const path of ['/api/pdf-template/pf1e', '/templates/pf1e_sheet.pdf']) {
      try {
        const response = await fetch(path);
        if (!response.ok) continue;
        const bytes = await response.arrayBuffer();
        if (new TextDecoder().decode(bytes.slice(0, 4)) === '%PDF') return bytes;
      } catch { /* Try the same-origin packaged template. */ }
    }
    throw new Error('Orijinal PF1e PDF şablonu yüklenemedi.');
  })().catch(error => { templatePromise = null; throw error; });
  return templatePromise.then(bytes => bytes.slice(0));
}
