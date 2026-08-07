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

/**
 * Transliterates Turkish special characters to their closest WinAnsi (Latin-1)
 * equivalents. pdf-lib's StandardFonts use WinAnsi encoding which cannot
 * represent İ (0x0130), ı (0x0131), Ş, ş, Ğ, ğ, etc.
 */
function sanitizeTurkishForPDF(text) {
  if (text == null) return '';
  const str = String(text);
  const map = {
    'İ': 'I', 'ı': 'i',
    'Ş': 'S', 'ş': 's',
    'Ğ': 'G', 'ğ': 'g',
    'Ü': 'U', 'ü': 'u',
    'Ö': 'O', 'ö': 'o',
    'Ç': 'C', 'ç': 'c',
  };
  return str.replace(/[İıŞşĞğÜüÖöÇç]/g, ch => map[ch] || ch);
}

export async function exportCharacterPDF(store) {
  try {
    // Phase 1: Robust Multi-Path Template Fetching
    let response;
    const fetchPaths = [
      '/templates/pf1e_sheet.pdf',
      'http://127.0.0.1:8000/templates/pf1e_sheet.pdf',
      '/public/templates/pf1e_sheet.pdf',
      '/sheets/pf1e_sheet.pdf'
    ];
    for (const pathUrl of fetchPaths) {
      try {
        const res = await fetch(pathUrl);
        if (res.ok) {
          response = res;
          break;
        }
      } catch (e) {
        // Try next fallback path
      }
    }
    if (!response || !response.ok) {
      throw new Error('PDF şablonu (/templates/pf1e_sheet.pdf) sunucuda veya yerel dizinde bulunamadı.');
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
          field.setText(sanitizeTurkishForPDF(val));
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
      const wName = w.name || w.isim || 'Silah';
      const isRanged = String(w.type || sys.weaponType || '').toLowerCase().includes('ranged') || String(wName).toLowerCase().includes('bow');
      const attackBonusStr = w.calculated_attack || formatMod(babValue + (isRanged ? dexMod : strMod));
      
      let dmg = w.calculated_damage;
      if (!dmg) {
        const rawDmg = String(sys.actions?.[0]?.damage?.parts?.[0]?.[0] || w.sistem_verisi?.damage?.parts?.[0]?.[0] || sys.damage || '');
        const mSize = rawDmg.match(/sizeRoll\s*\(\s*(\d+)\s*,\s*(\d+)[^)]*\)/i);
        if (mSize) {
          dmg = `${mSize[1]}d${mSize[2]}`;
        } else {
          const mDice = rawDmg.match(/\b\d+d\d+\b/i);
          dmg = mDice ? mDice[0] : '1d8';
        }
      }
      
      const crit = w.crit_range || (sys.critRange ? `${sys.critRange}/${sys.critMult || 'x2'}` : (sys.critical || '20/x2'));
      const dmgType = sys.damageType || sys.damage_type || 'Physical';
      const rangeInc = sys.range || sys.range_increment || '-';

      setField(`Weapon ${idx + 1}`, wName);
      setField(`Attack Bonus ${idx + 1}`, attackBonusStr);
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

    // Detailed Skills Mapping & Class Skill Checkboxes
    const skillPdfMapping = {
      'Acrobatics': { total: 'Bonus 1', mod: 'Mod 33333', ranks: 'undefined_13', misc: 'undefined_14', ab: 'Dexterity' },
      'Appraise': { total: 'Bonus 2', mod: 'Mod 2222', ranks: 'undefined_20', misc: 'undefined_21', ab: 'Intelligence' },
      'Bluff': { total: 'Bonus 3', mod: 'Mod 11111111111', ranks: 'undefined_28', misc: 'undefined_29', ab: 'Charisma' },
      'Climb': { total: 'Bonus 4', mod: 'Mod 111111', ranks: 'undefined_30', misc: 'undefined_31', ab: 'Strength' },
      'Craft': { total: 'Bonus 5', mod: 'Int_2', ranks: 'undefined_32', misc: 'undefined_33', ab: 'Intelligence' },
      'Diplomacy': { total: 'Bonus 8', mod: 'Cha_2', ranks: 'undefined_38', misc: 'undefined_39', ab: 'Charisma' },
      'Disable Device': { total: 'Bonus 9', mod: 'Dex_2', ranks: 'undefined_55', misc: 'undefined_56', ab: 'Dexterity' },
      'Disguise': { total: 'Bonus 10', mod: 'Cha_3', ranks: 'undefined_57', misc: 'undefined_58', ab: 'Charisma' },
      'Escape Artist': { total: 'Bonus 11', mod: 'Dex_3', ranks: 'undefined_59', misc: 'undefined_60', ab: 'Dexterity' },
      'Fly': { total: 'Bonus 12', mod: 'Dex_4', ranks: 'undefined_61', misc: 'undefined_62', ab: 'Dexterity' },
      'Handle Animal': { total: 'Bonus 13', mod: 'Cha_4', ranks: 'undefined_63', misc: 'undefined_64', ab: 'Charisma' },
      'Heal': { total: 'Bonus 14', mod: 'Mod100000', ranks: 'undefined_65', misc: 'undefined_66', ab: 'Wisdom' },
      'Intimidate': { total: 'Bonus 15', mod: 'Cha_5', ranks: 'undefined_67', misc: 'undefined_68', ab: 'Charisma' },
      'Knowledge (arcana)': { total: 'Bonus 16', mod: 'Int_5', ranks: 'undefined_72', misc: 'undefined_73', ab: 'Intelligence' },
      'Knowledge (dungeoneering)': { total: 'Bonus 17', mod: 'Int_6', ranks: 'undefined_74', misc: 'undefined_75', ab: 'Intelligence' },
      'Knowledge (engineering)': { total: 'Bonus 18', mod: 'Int_7', ranks: 'undefined_76', misc: 'undefined_77', ab: 'Intelligence' },
      'Knowledge (geography)': { total: 'Bonus 19', mod: 'Int_8', ranks: 'undefined_82', misc: 'undefined_83', ab: 'Intelligence' },
      'Knowledge (history)': { total: 'Bonus 20', mod: 'Int_9', ranks: 'undefined_84', misc: 'undefined_85', ab: 'Intelligence' },
      'Knowledge (local)': { total: 'Bonus 21', mod: 'Int_10', ranks: 'undefined_86', misc: 'undefined_87', ab: 'Intelligence' },
      'Knowledge (nature)': { total: 'Bonus 22', mod: 'Int_11', ranks: 'undefined_88', misc: 'undefined_89', ab: 'Intelligence' },
      'Knowledge (nobility)': { total: 'Bonus 23', mod: 'Int_12', ranks: 'undefined_90', misc: 'undefined_91', ab: 'Intelligence' },
      'Knowledge (planes)': { total: 'Bonus 24', mod: 'Int_13', ranks: 'undefined_92', misc: 'undefined_93', ab: 'Intelligence' },
      'Knowledge (religion)': { total: 'Bonus 25', mod: 'Int_14', ranks: 'undefined_94', misc: 'undefined_95', ab: 'Intelligence' },
      'Linguistics': { total: 'Bonus 26', mod: 'Int_15', ranks: 'undefined_96', misc: 'undefined_97', ab: 'Intelligence' },
      'Perception': { total: 'Bonus 27', mod: 'Wis_2', ranks: 'undefined_98', misc: 'undefined_99', ab: 'Wisdom' },
      'Perform': { total: 'Bonus 28', mod: 'Cha_6', ranks: 'undefined_100', misc: 'undefined_101', ab: 'Charisma' },
      'Profession': { total: 'Bonus 30', mod: 'Wis_3', ranks: 'undefined_104', misc: 'undefined_105', ab: 'Wisdom' },
      'Ride': { total: 'Bonus 32', mod: 'Dex_5', ranks: 'undefined_108', misc: 'undefined_109', ab: 'Dexterity' },
      'Sense Motive': { total: 'Bonus 33', mod: 'Wis_5', ranks: 'undefined_110', misc: 'undefined_111', ab: 'Wisdom' },
      'Sleight of Hand': { total: 'Bonus 34', mod: 'Dex_6', ranks: 'undefined_112', misc: 'undefined_113', ab: 'Dexterity' },
      'Spellcraft': { total: 'Bonus 35', mod: 'Int_16', ranks: 'undefined_114', misc: 'undefined_115', ab: 'Intelligence' },
      'Stealth': { total: 'Bonus 36', mod: 'Dex_7', ranks: 'undefined_116', misc: 'undefined_117', ab: 'Dexterity' },
      'Survival': { total: 'Bonus 37', mod: 'Wis_6', ranks: 'undefined_118', misc: 'undefined_119', ab: 'Wisdom' },
      'Swim': { total: 'Bonus 38', mod: 'Str_2', ranks: 'undefined_120', misc: 'undefined_121', ab: 'Strength' },
      'Use Magic Device': { total: 'Bonus 39', mod: 'Cha_8', ranks: 'undefined_122', misc: 'undefined_123', ab: 'Charisma' }
    };

    const userSkills = store.skills || {};
    const classSkillsList = (recalcedData.class_skills_active || recalcedData.class_data?.class_skills || [])
      .map(s => String(s).toLowerCase().trim());

    Object.entries(skillPdfMapping).forEach(([skillName, pdfFields]) => {
      const ranks = parseInt(userSkills[skillName]) || 0;
      const abMod = derivedMods[pdfFields.ab] || 0;
      const normSkill = skillName.toLowerCase().trim();
      const isClassSkill = classSkillsList.some(cs => cs === normSkill || cs.includes(normSkill) || normSkill.includes(cs));
      const classSkillBonus = (isClassSkill && ranks > 0) ? 3 : 0;
      const totalBonus = ranks + abMod + classSkillBonus;

      setField(pdfFields.ranks, ranks > 0 ? ranks : '');
      setField(pdfFields.mod, abMod >= 0 ? `+${abMod}` : `${abMod}`);
      setField(pdfFields.total, totalBonus >= 0 ? `+${totalBonus}` : `${totalBonus}`);

      if (isClassSkill) {
        const pdfCheckboxName = skillName.replace(/\(([^)]+)\)/g, '$1').trim();
        try {
          const cb = form.getCheckBox(pdfCheckboxName);
          if (cb) cb.check();
        } catch (e) {
          try {
            const cb2 = form.getCheckBox(skillName);
            if (cb2) cb2.check();
          } catch (err) {}
        }
      }
    });

    // Embed Character Portrait image onto Page 2 clean top-right empty space if available
    const portrait = store.portrait;
    if (portrait && typeof portrait === 'string') {
      try {
        let image;
        if (portrait.startsWith('data:image/png')) {
          image = await pdfDoc.embedPng(portrait);
        } else if (portrait.startsWith('data:image/jpeg') || portrait.startsWith('data:image/jpg')) {
          image = await pdfDoc.embedJpg(portrait);
        }
        if (image) {
          const pages = pdfDoc.getPages();
          const targetPage = pages.length > 1 ? pages[1] : pages[0];
          const maxWidth = 95;
          const maxHeight = 52;
          const scale = Math.min(maxWidth / image.width, maxHeight / image.height);
          const drawWidth = image.width * scale;
          const drawHeight = image.height * scale;
          const drawX = 470 + (maxWidth - drawWidth) / 2;
          const drawY = 718 + (maxHeight - drawHeight) / 2;

          targetPage.drawImage(image, {
            x: drawX,
            y: drawY,
            width: drawWidth,
            height: drawHeight
          });
        }
      } catch (e) {
        console.warn('PDF export portrait embedding note:', e);
      }
    }

    // Phase 3: Appearance Stream Updates & Save
    try {
      form.updateFieldAppearances(font);
    } catch (appearanceErr) {
      console.warn('PDF appearance update partially failed (likely unsupported glyph):', appearanceErr.message);
      // Still attempt to save — fields will have values even without updated appearances
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


