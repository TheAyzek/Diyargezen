/**
 * Diyargezen Pathfinder 1st Edition (PF1e) PDF Export Engine
 * 
 * Architecture & Data Pipeline:
 * -----------------------------
 * This utility handles browser-side rendering and export of official fillable AcroForm PDF character sheets.
 * Utilizing the `pdf-lib` web assembly & pure JS library, it maps active Zustand character store state
 * and server-calculated statistics into canonical PF1e AcroForm fields.
 * 
 * Pipeline Phases:
 * 1. Template Resolution: Attempts fetching official `/templates/pf1e_sheet.pdf` with fallback to `/sheets/pf1e_sheet.pdf`.
 * 2. Form Field Ingestion: Loads AcroForm field dictionary and maps core attributes, ability scores, combat stats,
 *    weapons, armor breakdown, skills, and encumbrance totals.
 * 3. Typography & Appearance Stream Updates: Updates field appearances to ensure visual fidelity without user edit focus.
 * 4. Blob Stream Generation: Serializes PDF array buffer into a downloadable MIME `application/pdf` Blob URL.
 */

import { PDFDocument, StandardFonts } from 'pdf-lib';

export async function exportCharacterPDF(store) {
  try {
    // Phase 1: Template Fetch with Fallback
    let response = await fetch('/templates/pf1e_sheet.pdf');
    if (!response.ok) {
      response = await fetch('/sheets/pf1e_sheet.pdf');
    }
    if (!response.ok) {
      throw new Error('PDF şablonu (/templates/pf1e_sheet.pdf) sunucuda bulunamadı.');
    }
    const existingPdfBytes = await response.arrayBuffer();

    // Phase 2: PDF Document Loading & AcroForm Mapping
    const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
    const form = pdfDoc.getForm();

    const setField = (fieldName, val) => {
      try {
        const field = form.getField(fieldName);
        if (field && typeof field.setText === 'function') {
          field.setText(String(val ?? ''));
        }
      } catch (e) {
        // Field not present in template dictionary
      }
    };

    const recalcedData = store.recalcedData || {};
    const formatMod = (val) => (val >= 0 ? `+${val}` : `${val}`);

    // General Header Info
    setField('Character Name', store.name || 'İsimsiz Kahraman');
    setField('Class', store.class || '');
    setField('Classes & Levels', `${store.class || 'Bilinmiyor'} (Seviye ${store.level || 1})`);
    setField('Level', store.level || 1);
    setField('Race', store.race || '');
    setField('Gender', store.gender || '');
    setField('Age', store.age || '');
    setField('Height', store.height || '');
    setField('Weight', store.weight || '');
    setField('Hair', store.hair || '');
    setField('Eyes', store.eyes || '');
    setField('Alignment', store.alignment || '');
    setField('Deity', store.deity || '');
    setField('Homeland', store.homeland || '');

    // Ability Scores & Modifiers
    const derivedScores = recalcedData.ability_scores || {};
    const derivedMods = recalcedData.ability_modifiers || {};

    setField('strength', derivedScores.Strength || 10);
    setField('modifier', formatMod(derivedMods.Strength || 0));

    setField('dexterity', derivedScores.Dexterity || 10);
    setField('undefined', formatMod(derivedMods.Dexterity || 0));

    setField('constitution', derivedScores.Constitution || 10);
    setField('undefined_4', formatMod(derivedMods.Constitution || 0));

    setField('intelligence', derivedScores.Intelligence || 10);
    setField('undefined_7', formatMod(derivedMods.Intelligence || 0));

    setField('WIS', derivedScores.Wisdom || 10);
    setField('undefined_10', formatMod(derivedMods.Wisdom || 0));

    setField('charisma', derivedScores.Charisma || 10);
    setField('undefined_15', formatMod(derivedMods.Charisma || 0));

    // Combat Stats
    setField('INITIATIVE', formatMod(recalcedData.initiative || 0));
    setField('hit points', recalcedData.hit_points || 8);
    setField('armor class', recalcedData.armor_class || 10);
    setField('TOUCH', recalcedData.touch_ac || 10);
    setField('FLATFOOTED', recalcedData.flat_footed_ac || 10);
    setField('SPEED', `${recalcedData.speed || 30} ft`);
    setField('BASE ATTACK BONUS', formatMod(recalcedData.bab || 0));
    setField('CMB', formatMod(recalcedData.cmb || 0));
    setField('CMD', recalcedData.cmd || 10);

    const saves = recalcedData.saving_throws || {};
    setField('FORTITUDE', formatMod(saves.Fortitude ?? saves.fortitude ?? 0));
    setField('REFLEX', formatMod(saves.Reflex ?? saves.reflex ?? 0));
    setField('WILL', formatMod(saves.Will ?? saves.will ?? 0));

    // Detailed Weapons Mapping (Weapon 1..5)
    const weapons = recalcedData.weapons || [];
    const babValue = recalcedData.bab || 0;
    const strMod = derivedMods.Strength || 0;
    const dexMod = derivedMods.Dexterity || 0;

    weapons.slice(0, 5).forEach((w, idx) => {
      const sys = w.sistem_verisi?.system || {};
      const isRanged = String(w.type || sys.weaponType || '').toLowerCase().includes('ranged') || String(w.name).toLowerCase().includes('bow');
      const attackBonus = babValue + (isRanged ? dexMod : strMod);
      const dmg = sys.actions?.[0]?.damage?.parts?.[0]?.[0] || w.sistem_verisi?.damage?.parts?.[0]?.[0] || sys.damage || '-';
      const crit = sys.critRange ? `${sys.critRange}/${sys.critMult || 'x2'}` : (sys.critical || '20/x2');
      const dmgType = sys.damageType || sys.damage_type || 'Physical';
      const rangeInc = sys.range || sys.range_increment || '-';

      setField(`Weapon ${idx + 1}`, w.name);
      setField(`Attack Bonus ${idx + 1}`, formatMod(attackBonus));
      setField(`Damage ${idx + 1}`, dmg);
      setField(`Critical ${idx + 1}`, crit);
      setField(`Type ${idx + 1}`, dmgType);
      setField(`Range ${idx + 1}`, rangeInc);
    });

    // Detailed Armor & Protective Items Mapping
    const armorItems = recalcedData.armor_shields || [];
    armorItems.slice(0, 3).forEach((item, idx) => {
      const sys = item.sistem_verisi?.system || item.sistem_verisi || {};
      const armorName = item.name;
      const ab = sys.armor_bonus || sys.armorClass?.value || 0;
      const acp = sys.armorCheckPenalty || sys.armor_check_penalty || 0;
      setField(`Armor/Protective Item ${idx + 1}`, armorName);
      setField(`Armor Bonus ${idx + 1}`, ab ? `+${ab}` : '');
      setField(`Armor Check Penalty ${idx + 1}`, acp ? `${acp}` : '');
    });

    // Equipment Weight, Encumbrance & Carrying Capacity
    const totalWeight = recalcedData.total_weight ?? (store.equipment ? store.equipment.reduce((sum, item) => sum + (parseFloat(item.weight || 0) * (parseInt(item.quantity || 1, 10))), 0) : 0);
    setField('TOTAL WEIGHT', `${totalWeight.toFixed(1)} lbs`);

    const enc = recalcedData.encumbrance || {};
    const cap = recalcedData.carrying_capacity || enc.carrying_capacity || {};
    setField('Light', `${cap.light ?? cap.light_max ?? 33} lbs`);
    setField('Medium', `${cap.medium ?? cap.medium_max ?? 66} lbs`);
    setField('Heavy', `${cap.heavy ?? cap.heavy_max ?? 100} lbs`);
    setField('LIGHT LOAD', `${cap.light ?? cap.light_max ?? 33} lbs`);
    setField('MEDIUM LOAD', `${cap.medium ?? cap.medium_max ?? 66} lbs`);
    setField('HEAVY LOAD', `${cap.heavy ?? cap.heavy_max ?? 100} lbs`);
    setField('ARMOR CHECK PENALTY', recalcedData.armor_check_penalty ?? enc.encumbrance_acp ?? 0);
    setField('MAX DEX', recalcedData.max_dex_bonus ?? enc.max_dex_bonus ?? 'None');

    const featsList = store.feats ? store.feats.map(f => typeof f === 'string' ? f : (f.isim || f.name)).join(', ') : (store.feat || '');
    setField('FEATS', featsList);

    const traitsList = store.traits ? store.traits.map(t => typeof t === 'string' ? t : (t.isim || t.name)).join(', ') : '';
    setField('SPECIAL ABILITIES', traitsList);

    // Languages & Spells Known
    if (store.languages) {
      const langText = Array.isArray(store.languages) ? store.languages.join(', ') : store.languages;
      setField('LANGUAGES', langText);
    }
    if (store.spells) {
      const spellText = store.spells.map(s => typeof s === 'string' ? s : (s.name || s.isim)).join(', ');
      setField('SPELLS KNOWN', spellText);
    }

    // Skills Mapping
    if (recalcedData.skills) {
      Object.entries(recalcedData.skills).forEach(([skillName, bonus]) => {
        setField(skillName.toUpperCase(), formatMod(bonus));
      });
    }

    // Phase 3: Appearance Stream Updates & Save
    try {
      form.updateFieldAppearances(font);
    } catch (e) {
      // Graceful fallback for custom PDF field definitions
    }

    const pdfBytes = await pdfDoc.save();

    // Phase 4: Download Blob URL Creation
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    const safeName = (store.name || 'Karakter').replace(/[^a-zA-Z0-9_\-]/g, '_');
    link.download = `${safeName}_PF1e_Sheet.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    return true;
  } catch (error) {
    console.error('PDF Export Error:', error);
    alert('PDF indirilirken hata oluştu: ' + error.message);
    return false;
  }
}


