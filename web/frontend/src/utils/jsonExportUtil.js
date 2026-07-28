export function exportCharacterJSON(store) {
  try {
    const charData = {
      name: store.name || 'İsimsiz Kahraman',
      system: 'pf1e',
      level: store.level || 1,
      race: store.race || '',
      class: store.class || '',
      alignment: store.alignment || '',
      gender: store.gender || '',
      age: store.age || '',
      height: store.height || '',
      weight: store.weight || '',
      deity: store.deity || '',
      homeland: store.homeland || '',
      hair: store.hair || '',
      eyes: store.eyes || '',
      abilities: store.abilities || {},
      skills: store.skills || {},
      feats: store.feats || [],
      traits: store.traits || [],
      equipment: store.equipment || [],
      spells: store.spells || [],
      backstory: store.backstory || '',
      personality: store.personality || '',
      allies: store.allies || '',
      notes: store.notes || '',
      portrait: store.portrait || '',
      companion: store.companion || null,
      preparedSpells: store.preparedSpells || {},
      usedSpellSlots: store.usedSpellSlots || {}
    };

    const jsonString = JSON.stringify(charData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    const safeName = (store.name || 'Karakter').replace(/[^a-zA-Z0-9_\-]/g, '_');
    link.download = `${safeName}_Diyargezen.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    return true;
  } catch (error) {
    console.error('JSON Export Error:', error);
    alert('JSON aktarılırken hata oluştu: ' + error.message);
    return false;
  }
}

export function copyCharacterJSONToClipboard(store) {
  try {
    const charData = {
      name: store.name || 'İsimsiz Kahraman',
      system: 'pf1e',
      level: store.level || 1,
      race: store.race || '',
      class: store.class || '',
      alignment: store.alignment || '',
      abilities: store.abilities || {},
      feats: store.feats || [],
      equipment: store.equipment || [],
      spells: store.spells || []
    };

    const jsonString = JSON.stringify(charData, null, 2);
    navigator.clipboard.writeText(jsonString);
    alert('📋 Karakter verisi panoya kopyalandı! Arkadaşlarınızla paylaşabilirsiniz.');
    return true;
  } catch (error) {
    console.error('Clipboard Copy Error:', error);
    alert('Panoya kopyalanırken hata oluştu: ' + error.message);
    return false;
  }
}

export function importCharacterJSONFile(file, loadPresetCallback) {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('Dosya seçilmedi.'));
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        if (!parsed || typeof parsed !== 'object') {
          throw new Error('Geçersiz JSON formatı.');
        }

        if (!parsed.name && !parsed.class) {
          throw new Error('Geçerli bir Diyargezen karakter dosyası değil.');
        }

        if (loadPresetCallback) {
          loadPresetCallback(parsed);
        }
        resolve(parsed);
      } catch (err) {
        alert('JSON okuma hatası: ' + err.message);
        reject(err);
      }
    };
    reader.readAsText(file);
  });
}
