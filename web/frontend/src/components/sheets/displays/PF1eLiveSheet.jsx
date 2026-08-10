/**
 * Diyargezen Pathfinder 1st Edition Live PDF View & Form Synchronizer
 * 
 * Architecture & Performance Design:
 * ----------------------------------
 * This component handles real-time rendering of active Pathfinder 1e character sheets using `pdf-lib`.
 * It embeds an interactive `<iframe src={pdfDataUri}>` container alongside tabbed HTML displays
 * for parchment sheet summary and spellbook management.
 * 
 * Performance Loop:
 * 1. Debounced Re-render (300ms): Reacts to Zustand store mutations (attributes, equipment, skills, feats, traits)
 *    and throttles PDF generation to prevent main thread rendering bottlenecks.
 * 2. Embedded Font Stream: Embeds standard Helvetica typefaces for AcroForm field appearance generation.
 * 3. Reactive Data URI Streaming: Encodes filled PDF bytes into Base64 Data URI streams for instant `<iframe />` rendering.
 * 4. Image Canvas Embedding: Scales character portraits into PDF canvas coordinate space if portrait Data URI exists.
 */

import React, { useEffect, useState, useRef } from 'react';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import { FileText, RefreshCw, Download, Shield, Heart, Sword, Sparkles, Activity, Wand2, Scroll } from 'lucide-react';

/**
 * Transliterates Turkish special characters to WinAnsi-safe equivalents.
 * pdf-lib StandardFonts cannot encode İ (0x0130), ı (0x0131), Ş, ş, Ğ, ğ, etc.
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

import { useCharacterStore } from '../../../store/characterStore';
import SpellCard from '../../SpellCard';
import ParchmentSheetDisplay from './ParchmentSheetDisplay';

export default function PF1eLiveSheet() {
  const store = useCharacterStore();
  const { name, level, race, class: charClass, feat, recalcedData, portrait, raceData, skills } = store;
  const traits = store.traits || [];
  const feats = store.feats || (feat ? [{ isim: feat }] : []);
  
  const [pdfUrl, setPdfUrl] = useState(null);
  const [rendering, setRendering] = useState(false);
  const [viewMode, setViewMode] = useState('pdf'); // 'pdf', 'summary', 'spells'
  const [activeEqTab, setActiveEqTab] = useState('weapons');
  const debounceTimerRef = useRef(null);

  // Core PDF fill function using pdf-lib
  const renderLivePdf = async () => {
    try {
      setRendering(true);
      let existingPdfBytes = null;
      const fetchPaths = [
        '/api/pdf-template/pf1e',
        '/templates/pf1e_sheet.pdf',
        'http://127.0.0.1:8000/api/pdf-template/pf1e',
        'http://127.0.0.1:8000/templates/pf1e_sheet.pdf',
        '/public/templates/pf1e_sheet.pdf',
        '/sheets/pf1e_sheet.pdf'
      ];
      for (const pathUrl of fetchPaths) {
        try {
          const res = await fetch(pathUrl);
          if (res.ok) {
            const buf = await res.arrayBuffer();
            const header = new TextDecoder().decode(buf.slice(0, 4));
            if (header === '%PDF') {
              existingPdfBytes = buf;
              break;
            }
          }
        } catch (e) {
          // Try next fallback path
        }
      }
      if (!existingPdfBytes) {
        throw new Error('PDF şablonu (/api/pdf-template/pf1e) yüklenemedi.');
      }

      const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
      const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const form = pdfDoc.getForm();

      const setField = (fieldName, textValue) => {
        try {
          const field = form.getField(fieldName);
          if (field && typeof field.setText === 'function') {
            field.setText(sanitizeTurkishForPDF(textValue));
          }
        } catch (e) {
          // Ignore missing or non-text fields gracefully
        }
      };

      // Fill Character General Header Info (Top header boxes on Pathfinder Sheet)
      setField('Character Name', name || 'İsimsiz Kahraman');
      setField('Classes & Levels', `${charClass || 'Bilinmiyor'} (Seviye ${level || 1})`);
      setField('Race', race || '');
      setField('Size', raceData?.size || store.size || 'Medium');
      setField('Gender', store.gender || '');
      setField('Age', store.age || '');
      setField('Height', store.height || '');
      setField('Weight', store.weight || '');
      setField('Hair', store.hair || '');
      setField('Eyes', store.eyes || '');
      setField('Alignment', store.alignment || '');
      setField('Deity', store.deity || '');
      setField('Homeland', store.homeland || '');

      // Ability Scores & Modifiers (exact pf1e_sheet.pdf AcroForm field names)
      const derivedScores = recalcedData.ability_scores || {};
      const derivedMods = recalcedData.ability_modifiers || {};
      const formatMod = (val) => (val >= 0 ? `+${val}` : `${val}`);

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

      // Initiative & Breakdown Fields
      const totalInit = recalcedData.initiative || 0;
      const dexInitMod = derivedMods.Dexterity || 0;
      const miscInitMod = totalInit - dexInitMod;
      setField('INITIATIVE', formatMod(totalInit));
      setField('undefined_18', formatMod(dexInitMod));
      setField('undefined_19', miscInitMod !== 0 ? formatMod(miscInitMod) : '');

      // Armor Class & Breakdown Fields
      const totalAC = recalcedData.armor_class || 10;
      const dexAcMod = derivedMods.Dexterity || 0;
      const armorBonus = recalcedData.armor_bonus || 0;
      const shieldBonus = recalcedData.shield_bonus || 0;
      const miscAcMod = totalAC - 10 - dexAcMod - armorBonus - shieldBonus;

      setField('hit points', recalcedData.hit_points || 8);
      setField('armor class', totalAC);
      setField('10', '10');
      setField('undefined_22', armorBonus || '');
      setField('undefined_23', shieldBonus || '');
      setField('undefined_24', formatMod(dexAcMod));
      setField('undefined_25', '');
      setField('undefined_26', '');
      setField('undefined_27', miscAcMod !== 0 ? formatMod(miscAcMod) : '');

      setField('TOUCH', recalcedData.touch_ac || 10);
      setField('FLATFOOTED', recalcedData.flat_footed_ac || 10);
      setField('SPEED', `${recalcedData.speed || 30} ft`);
      setField('BASE ATTACK BONUS', recalcedData.bab >= 0 ? `+${recalcedData.bab}` : recalcedData.bab || 0);

      // Saves Breakdown Fields
      const saves = recalcedData.saving_throws || {};
      const baseFort = recalcedData.class_data?.base_saves?.fortitude || 0;
      const baseRef = recalcedData.class_data?.base_saves?.reflex || 0;
      const baseWill = recalcedData.class_data?.base_saves?.will || 0;

      const fortTotal = saves.Fortitude ?? saves.fortitude ?? 0;
      const refTotal = saves.Reflex ?? saves.reflex ?? 0;
      const willTotal = saves.Will ?? saves.will ?? 0;

      const fortConMod = derivedMods.Constitution || 0;
      const refDexMod = derivedMods.Dexterity || 0;
      const willWisMod = derivedMods.Wisdom || 0;

      const fortMiscMod = fortTotal - baseFort - fortConMod;
      const refMiscMod = refTotal - baseRef - refDexMod;
      const willMiscMod = willTotal - baseWill - willWisMod;

      setField('FORTITUDE', formatMod(fortTotal));
      setField('undefined_40', formatMod(baseFort));
      setField('undefined_41', formatMod(fortConMod));
      setField('undefined_43', fortMiscMod !== 0 ? formatMod(fortMiscMod) : '');

      setField('REFLEX', formatMod(refTotal));
      setField('undefined_45', formatMod(baseRef));
      setField('undefined_46', formatMod(refDexMod));
      setField('undefined_48', refMiscMod !== 0 ? formatMod(refMiscMod) : '');

      setField('WILL', formatMod(willTotal));
      setField('undefined_50', formatMod(baseWill));
      setField('undefined_51', formatMod(willWisMod));
      setField('undefined_53', willMiscMod !== 0 ? formatMod(willMiscMod) : '');

      // CMB & CMD Breakdown Fields
      const totalCmb = recalcedData.cmb || 0;
      const totalCmd = recalcedData.cmd || 10;
      const babVal = recalcedData.bab || 0;
      const strModVal = derivedMods.Strength || 0;
      const dexModVal = derivedMods.Dexterity || 0;

      setField('CMB', formatMod(totalCmb));
      setField('undefined_69', formatMod(babVal));
      setField('undefined_70', formatMod(strModVal));
      setField('undefined_71', '');

      setField('CMD', totalCmd);
      setField('undefined_78', formatMod(babVal));
      setField('undefined_79', formatMod(strModVal));
      setField('undefined_80', formatMod(dexModVal));
      setField('undefined_81', '');

      // Encumbrance & Capacity
      const totalWeight = recalcedData.total_weight || 0;
      const capacity = recalcedData.carrying_capacity || { light: 33, medium: 66, heavy: 100 };
      setField('TOTAL WEIGHT', `${totalWeight} lbs`);
      setField('Light', `${capacity.light} lbs`);
      setField('Medium', `${capacity.medium} lbs`);
      setField('Heavy', `${capacity.heavy} lbs`);

      // Skill Field Mapping Dictionary for pf1e_sheet.pdf
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

      const userSkills = skills || {};
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

        // Class Skill Checkbox checking in PDF
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

      // Fill Feats (FEATS 1, FEATS 2, ...)
      feats.forEach((f, idx) => {
        const fname = f.isim || f.name || (typeof f === 'string' ? f : '');
        if (fname) {
          setField(`FEATS ${idx + 1}`, fname);
        }
      });

      // Apply trait bonuses to PDF fields
      // Collect all trait bonuses from selected traits
      let initiativeBonus = 0;
      let fortitudeBonus = 0;
      let reflexBonus = 0;
      let willBonus = 0;
      let concentrationBonus = 0;
      const traitSkillBonuses = {}; // { skillName: { value, makeClassSkill } }
      const traitNames = [];

      traits.forEach(trait => {
        traitNames.push(trait.isim);
        const bonuses = trait.sistem_verisi?.bonuses || [];
        bonuses.forEach(b => {
          if (b.type === 'initiative') initiativeBonus += (b.value || 0);
          else if (b.type === 'save_fortitude') fortitudeBonus += (b.value || 0);
          else if (b.type === 'save_reflex') reflexBonus += (b.value || 0);
          else if (b.type === 'save_will') willBonus += (b.value || 0);
          else if (b.type === 'save_all') {
            fortitudeBonus += (b.value || 0);
            reflexBonus += (b.value || 0);
            willBonus += (b.value || 0);
          }
          else if (b.type === 'concentration') concentrationBonus += (b.value || 0);
          else if (b.type === 'skill' && b.skill && b.skill !== 'any') {
            if (!traitSkillBonuses[b.skill]) traitSkillBonuses[b.skill] = { value: 0, makeClassSkill: false };
            traitSkillBonuses[b.skill].value += (b.value || 0);
            if (b.makes_class_skill) traitSkillBonuses[b.skill].makeClassSkill = true;
          }
        });
      });

      // Apply trait initiative bonus on top of base
      if (initiativeBonus !== 0) {
        const baseInit = recalcedData.initiative || 0;
        const totalInit = baseInit + initiativeBonus;
        setField('INITIATIVE', totalInit >= 0 ? `+${totalInit}` : `${totalInit}`);
      }

      // Apply trait save bonuses on top of base
      if (fortitudeBonus !== 0 || reflexBonus !== 0 || willBonus !== 0) {
        const saves = recalcedData.saving_throws || {};
        if (fortitudeBonus) setField('FORTITUDE', (saves.fortitude + fortitudeBonus) >= 0 ? `+${saves.fortitude + fortitudeBonus}` : `${saves.fortitude + fortitudeBonus}`);
        if (reflexBonus) setField('REFLEX', (saves.reflex + reflexBonus) >= 0 ? `+${saves.reflex + reflexBonus}` : `${saves.reflex + reflexBonus}`);
        if (willBonus) setField('WILL', (saves.will + willBonus) >= 0 ? `+${saves.will + willBonus}` : `${saves.will + willBonus}`);
      }

      // Apply trait skill bonuses and re-compute totals
      if (Object.keys(traitSkillBonuses).length > 0) {
        const traitClassSkills = Object.entries(traitSkillBonuses)
          .filter(([, v]) => v.makeClassSkill)
          .map(([k]) => k);
        const mergedClassSkills = [...(recalcedData.class_data?.class_skills || []), ...traitClassSkills];

        Object.entries(traitSkillBonuses).forEach(([skillName, bonus]) => {
          const pdfFields = skillPdfMapping[skillName];
          if (!pdfFields) return;
          const ranks = parseInt(skills[skillName]) || 0;
          const abMod = derivedMods[pdfFields.ab] || 0;
          const isClassSkill = mergedClassSkills.includes(skillName);
          const classSkillBonus = (isClassSkill && ranks > 0) ? 3 : 0;
          const totalBonus = ranks + abMod + classSkillBonus + (bonus.value || 0);
          setField(pdfFields.total, totalBonus >= 0 ? `+${totalBonus}` : `${totalBonus}`);
        });
      }

      // Write selected traits into Special Abilities field
      if (traitNames.length > 0) {
        setField('Special Attacks', traitNames.join(', '));
      }
      
      // Weapons AcroForm Detailed Mapping (Weapon 1..5)
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

      // Armor & Protective Items Mapping
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

      // General Equipment Mapping (Gear & Consumables)
      const items = [
        ...(recalcedData.consumables || []),
        ...(recalcedData.gear || [])
      ];
      items.slice(0, 26).forEach((item, idx) => {
        setField(`Item ${idx + 1}`, item.name);
        const wVal = item.sistem_verisi?.weight?.value || item.weight || item.agirlik || 0;
        setField(`WT ${idx + 1}`, `${wVal} lb`);
      });

      // Pathfinder 1e Spellcasting PDF AcroForm Mapping & Calculation Engine
      const fillSpellcastingPdfFields = () => {
        const charClass = String(charClassProp || store.class || recalcedData.class_name || '').trim().toLowerCase();
        const charLvl = parseInt(level || store.level || recalcedData.level || 1, 10);
        const derivedScores = recalcedData.ability_scores || {};
        const derivedMods = recalcedData.ability_modifiers || {};

        // AcroForm field name dictionary for Page 2 SPELLS Table (Levels 0 to 9)
        const spellLevelPdfFields = [
          { level: 0, known: 'KNOWN', dc: 'SAVE DC', perDay: '0', bonus: null },
          { level: 1, known: 'undefined_124', dc: 'undefined_125', perDay: '1st', bonus: 'undefined_126' },
          { level: 2, known: 'undefined_127', dc: 'undefined_128', perDay: '2nd', bonus: 'undefined_129' },
          { level: 3, known: 'undefined_130', dc: 'undefined_131', perDay: '3rd', bonus: 'undefined_132' },
          { level: 4, known: 'undefined_133', dc: 'undefined_134', perDay: '4th', bonus: 'undefined_135' },
          { level: 5, known: 'undefined_136', dc: 'undefined_137', perDay: '5th', bonus: 'undefined_138' },
          { level: 6, known: 'undefined_139', dc: 'undefined_140', perDay: '6th', bonus: 'undefined_141' },
          { level: 7, known: 'undefined_142', dc: 'undefined_143', perDay: '7th', bonus: 'undefined_144' },
          { level: 8, known: 'undefined_145', dc: 'undefined_146', perDay: '8th', bonus: 'undefined_147' },
          { level: 9, known: 'undefined_148', dc: 'undefined_149', perDay: '9th', bonus: 'undefined_150' },
        ];

        // Primary casting ability lookup for PF1e spellcasting classes
        const classCastingAbilityMap = {
          wizard: 'Intelligence', witch: 'Intelligence', magus: 'Intelligence', alchemist: 'Intelligence', arcanist: 'Intelligence', psychic: 'Intelligence', occultist: 'Intelligence',
          cleric: 'Wisdom', druid: 'Wisdom', inquisitor: 'Wisdom', ranger: 'Wisdom', shaman: 'Wisdom', warpriest: 'Wisdom', hunter: 'Wisdom', spiritualist: 'Wisdom',
          sorcerer: 'Charisma', oracle: 'Charisma', bard: 'Charisma', paladin: 'Charisma', summoner: 'Charisma', bloodrager: 'Charisma', skald: 'Charisma', medium: 'Charisma', mesmerist: 'Charisma'
        };

        const primaryAbilityName = classCastingAbilityMap[charClass];
        const is4LvlCaster = ['paladin', 'ranger', 'bloodrager', 'medium'].includes(charClass);
        const isSpellcaster = Boolean(primaryAbilityName) && (!is4LvlCaster || charLvl >= 4);

        if (!isSpellcaster) {
          spellLevelPdfFields.forEach((row) => {
            setField(row.known, '');
            setField(row.dc, '');
            setField(row.perDay, '');
            if (row.bonus) setField(row.bonus, '');
          });
          setField('DOMAINSSPECIALTY SCHOOL 1', '');
          setField('DOMAINSSPECIALTy SCHOOL 2', '');
          return;
        }

        const keyStatMod = derivedMods[primaryAbilityName] || 0;
        const keyStatScore = derivedScores[primaryAbilityName] || 10;

        // Spell Focus feat check
        const feats = store.feats || recalcedData.feats || [];
        const hasSpellFocus = feats.some(f => String(typeof f === 'string' ? f : (f.isim || f.name || '')).toLowerCase().includes('spell focus'));
        const dcMiscBonus = hasSpellFocus ? 1 : 0;

        // Class base spell slots per day
        const fullCasterSlots = {
          1: {0: 3, 1: 1}, 2: {0: 4, 1: 2}, 3: {0: 4, 1: 2, 2: 1}, 4: {0: 4, 1: 3, 2: 2},
          5: {0: 4, 1: 3, 2: 2, 3: 1}, 6: {0: 4, 1: 3, 2: 3, 3: 2}, 7: {0: 4, 1: 4, 2: 3, 3: 2, 4: 1},
          8: {0: 4, 1: 4, 2: 3, 3: 3, 4: 2}, 9: {0: 4, 1: 4, 2: 4, 3: 3, 4: 2, 5: 1}, 10: {0: 4, 1: 4, 2: 4, 3: 3, 4: 3, 5: 2},
          11: {0: 4, 1: 4, 2: 4, 3: 4, 4: 3, 5: 2, 6: 1}, 12: {0: 4, 1: 4, 2: 4, 3: 4, 4: 3, 5: 3, 6: 2},
          13: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 3, 6: 2, 7: 1}, 14: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 3, 6: 3, 7: 2},
          15: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3, 7: 2, 8: 1}, 16: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3, 7: 3, 8: 2},
          17: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 2, 9: 1}, 18: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 3, 9: 2},
          19: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 3, 9: 3}, 20: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4}
        };

        const midCasterSlots = {
          1: {0: 4, 1: 1}, 2: {0: 5, 1: 2}, 3: {0: 5, 1: 3}, 4: {0: 6, 1: 3, 2: 1},
          5: {0: 6, 1: 4, 2: 2}, 6: {0: 6, 1: 4, 2: 3}, 7: {0: 6, 1: 4, 2: 3, 3: 1},
          8: {0: 6, 1: 4, 2: 4, 3: 2}, 9: {0: 6, 1: 5, 2: 4, 3: 3}, 10: {0: 6, 1: 5, 2: 4, 3: 3, 4: 1},
          11: {0: 6, 1: 5, 2: 5, 3: 4, 4: 2}, 12: {0: 6, 1: 5, 2: 5, 3: 4, 4: 3},
          13: {0: 6, 1: 5, 2: 5, 3: 4, 4: 3, 5: 1}, 14: {0: 6, 1: 5, 2: 5, 3: 4, 4: 4, 5: 2},
          15: {0: 6, 1: 5, 2: 5, 3: 5, 4: 4, 5: 3}, 16: {0: 6, 1: 5, 2: 5, 3: 5, 4: 4, 5: 3, 6: 1},
          17: {0: 6, 1: 5, 2: 5, 3: 5, 4: 4, 5: 4, 6: 2}, 18: {0: 6, 1: 5, 2: 5, 3: 5, 4: 5, 5: 4, 6: 3},
          19: {0: 6, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 4}, 20: {0: 6, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5}
        };

        const cl = Math.max(1, Math.min(20, charLvl));
        let baseSlots = {};
        if (['wizard', 'cleric', 'druid', 'sorcerer', 'witch', 'oracle', 'arcanist', 'shaman', 'psychic'].includes(charClass)) {
          baseSlots = fullCasterSlots[cl] || {};
        } else if (['bard', 'magus', 'alchemist', 'inquisitor', 'summoner', 'skald', 'warpriest', 'hunter', 'mesmerist', 'occultist', 'spiritualist'].includes(charClass)) {
          baseSlots = midCasterSlots[cl] || {};
        } else if (is4LvlCaster) {
          if (cl >= 4) {
            const idx = cl - 3;
            const raw = midCasterSlots[idx] || {};
            Object.entries(raw).forEach(([lvl, count]) => {
              const lNum = parseInt(lvl, 10);
              if (lNum >= 1 && lNum <= 4) baseSlots[lNum] = count;
            });
          }
        }

        // User's selected spells by level count
        const userSpells = store.spells || recalcedData.spells || [];
        const userSpellsByLevel = {};
        if (Array.isArray(userSpells)) {
          userSpells.forEach(s => {
            const sLevel = typeof s === 'object' ? (s.level ?? s.seviye ?? 0) : 0;
            userSpellsByLevel[sLevel] = (userSpellsByLevel[sLevel] || 0) + 1;
          });
        }

        // Fill SPELLS Table (Levels 0 to 9)
        spellLevelPdfFields.forEach(({ level: sLvl, known: knownField, dc: dcField, perDay: perDayField, bonus: bonusField }) => {
          // 1. Bonus Spells per Day
          let bonusCount = 0;
          if (sLvl >= 1) {
            if (keyStatScore >= 10 + sLvl && keyStatMod >= sLvl) {
              bonusCount = Math.max(0, Math.ceil((keyStatMod - sLvl + 1) / 4));
            }
          }

          // Accessibility check
          const baseCount = baseSlots[sLvl] ?? (is4LvlCaster && sLvl === 1 && charLvl >= 4 && bonusCount > 0 ? 0 : null);
          const isAccessible = baseCount !== null || (userSpellsByLevel[sLvl] > 0);

          if (!isAccessible) {
            setField(knownField, '');
            setField(dcField, '');
            setField(perDayField, '');
            if (bonusField) setField(bonusField, '');
            return;
          }

          // 2. Spell Save DC: 10 + Spell Level + Key Mod + Misc Bonus
          const dcValue = (keyStatScore >= 10 + sLvl) ? (10 + sLvl + keyStatMod + dcMiscBonus) : '';
          setField(dcField, dcValue ? String(dcValue) : '');

          // 3. Spells Per Day (Base)
          setField(perDayField, String(baseCount ?? 0));

          // 4. Bonus Spells Per Day
          if (bonusField) {
            setField(bonusField, bonusCount > 0 ? String(bonusCount) : '-');
          }

          // 5. Spells Known
          let knownStr = '';
          if (userSpellsByLevel[sLvl] > 0) {
            knownStr = String(userSpellsByLevel[sLvl]);
          } else if (['cleric', 'druid', 'shaman', 'warpriest'].includes(charClass)) {
            knownStr = 'All';
          } else if (['wizard', 'witch'].includes(charClass)) {
            knownStr = sLvl === 0 ? 'All' : String(Math.max(2, (baseCount || 1) + 2));
          } else {
            knownStr = String(Math.max(1, (baseCount || 1) + 1));
          }
          setField(knownField, knownStr);
        });

        // Domains / Specialty School
        const specSchool = store.specialty_school || recalcedData.specialty_school || store.domain || recalcedData.domain || '';
        if (specSchool) {
          setField('DOMAINSSPECIALTY SCHOOL 1', specSchool);
        }
      };

      fillSpellcastingPdfFields();

      // Embed Character Portrait image over the top-left Pathfinder logo on Page 1 if available
      if (portrait && typeof portrait === 'string') {
        try {
          let image;
          if (portrait.startsWith('data:image/png')) {
            image = await pdfDoc.embedPng(portrait);
          } else if (portrait.startsWith('data:image/jpeg') || portrait.startsWith('data:image/jpg')) {
            image = await pdfDoc.embedJpg(portrait);
          }
          if (image) {
            const page1 = pdfDoc.getPages()[0];
            const boxX = 25;
            const boxY = 680;
            const boxW = 212;
            const boxH = 88;

            // 1. Draw clean white background rectangle with gold border over the Pathfinder logo
            page1.drawRectangle({
              x: boxX,
              y: boxY,
              width: boxW,
              height: boxH,
              color: rgb(1, 1, 1),
              borderColor: rgb(0.78, 0.65, 0.3),
              borderWidth: 1.5
            });

            // 2. Compute proportional scaling to fit inside the portrait frame
            const padding = 2;
            const availW = boxW - (padding * 2);
            const availH = boxH - (padding * 2);
            const scale = Math.min(availW / image.width, availH / image.height);
            const drawW = image.width * scale;
            const drawH = image.height * scale;
            const drawX = boxX + padding + (availW - drawW) / 2;
            const drawY = boxY + padding + (availH - drawH) / 2;

            // 3. Draw portrait image cleanly centered
            page1.drawImage(image, {
              x: drawX,
              y: drawY,
              width: drawW,
              height: drawH
            });
          }
        } catch (e) {
          console.warn('PDF portrait image embedding note:', e);
        }
      }

      try {
        form.updateFieldAppearances(font);
      } catch (appearanceErr) {
        console.warn('PDF appearance update partially failed:', appearanceErr.message);
        // Still attempt to save — fields will have values even without updated appearances
      }

      const pdfBytes = await pdfDoc.save();
      const blob = new Blob([pdfBytes], { type: 'application/pdf' });
      const blobUrl = URL.createObjectURL(blob);
      setPdfUrl((prevUrl) => {
        if (prevUrl && prevUrl.startsWith('blob:')) {
          URL.revokeObjectURL(prevUrl);
        }
        return blobUrl;
      });

    } catch (err) {
      console.error('pdf-lib Canlı PDF Oluşturma Hatası:', err);
    } finally {
      setRendering(false);
    }
  };

  // 300ms Debounce Function for Performance
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      renderLivePdf();
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [
    name, level, race, charClass, feat,
    store.alignment, store.gender, store.age, store.height, store.weight,
    store.deity, store.homeland, store.hair, store.eyes,
    JSON.stringify(raceData), JSON.stringify(recalcedData),
    JSON.stringify(store.abilities), JSON.stringify(skills),
    JSON.stringify(traits), JSON.stringify(feats)
  ]);

  const handleDownloadPdf = () => {
    if (!pdfUrl) return;
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = `${name || 'Diyargezen_Karakter'}_PF1e_Sheet.pdf`;
    link.click();
  };

  return (
    <div className="glass-card" style={{ 
      borderColor: 'var(--accent-gold)', 
      background: 'rgba(15, 15, 26, 0.9)',
      boxShadow: '0 0 25px rgba(201, 168, 76, 0.15)',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      borderRadius: '12px'
    }}>
      
      {/* Header bar with controls and view mode toggles */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '2px solid var(--accent-gold)', 
        paddingBottom: '14px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {portrait && (
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '8px',
              border: '2px solid var(--accent-gold)',
              overflow: 'hidden',
              background: '#0f0f1a'
            }}>
              <img src={portrait} alt="Portrait" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          )}
          <div>
            <h3 style={{ fontSize: '1.4rem', color: '#f0e6d2', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} style={{ color: 'var(--accent-gold)' }} />
              Canlı Karakter Kağıdı (PDF AcroForm)
              {rendering ? (
                <span style={{ fontSize: '11px', background: 'rgba(201,168,76,0.2)', color: 'var(--accent-gold)', padding: '2px 8px', borderRadius: '10px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <RefreshCw size={10} className="animate-spin" /> Güncelleniyor...
                </span>
              ) : (
                <span style={{ fontSize: '11px', background: 'rgba(63,185,80,0.15)', color: '#3fb950', border: '1px solid rgba(63,185,80,0.3)', padding: '2px 8px', borderRadius: '10px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  ● Canlı Senkronize
                </span>
              )}
            </h3>
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Reaktif `pdf-lib` Form Görselleştirici
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button 
            onClick={() => setViewMode('pdf')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid var(--accent-gold)',
              background: viewMode === 'pdf' ? 'var(--accent-gold)' : 'transparent',
              color: viewMode === 'pdf' ? '#0f0f1a' : 'var(--accent-gold)',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            📄 Canlı PDF
          </button>
          <button 
            onClick={() => setViewMode('summary')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid var(--accent-gold)',
              background: viewMode === 'summary' ? 'var(--accent-gold)' : 'transparent',
              color: viewMode === 'summary' ? '#0f0f1a' : 'var(--accent-gold)',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            📊 Midnight Obsidian
          </button>
          <button 
            onClick={() => setViewMode('parchment')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid #d4c5a9',
              background: viewMode === 'parchment' ? '#d4c5a9' : 'transparent',
              color: viewMode === 'parchment' ? '#2a1f0e' : '#d4c5a9',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Scroll size={13} /> 📜 Eskiz Parşömen
          </button>

          <button 
            onClick={() => setViewMode('spells')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid #7c6ef7',
              background: viewMode === 'spells' ? '#7c6ef7' : 'transparent',
              color: viewMode === 'spells' ? '#ffffff' : '#a594ff',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Wand2 size={13} /> Büyü Kitabı ({(store.spells || []).length})
          </button>
          <button 
            onClick={handleDownloadPdf}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
            disabled={!pdfUrl}
            title="Doldurulmuş PDF'i İndir"
          >
            <Download size={14} /> İndir
          </button>
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'pdf' ? (
        <div style={{ width: '100%', height: '700px', borderRadius: '8px', overflow: 'hidden', background: '#1e1e2f', position: 'relative', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
          {rendering && (
            <div style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              background: 'rgba(15, 15, 26, 0.9)',
              border: '1px solid var(--accent-gold)',
              padding: '6px 12px',
              borderRadius: '20px',
              color: 'var(--accent-gold)',
              fontSize: '11px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              zIndex: 10
            }}>
              <RefreshCw size={12} className="animate-spin" /> PDF Güncelleniyor...
            </div>
          )}
          
          {pdfUrl ? (
            <iframe 
              src={pdfUrl} 
              title="PF1e Live AcroForm PDF Sheet" 
              style={{ width: '100%', height: '100%', border: 'none' }}
            />
          ) : (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#8b949e', fontSize: '14px' }}>
              <RefreshCw size={20} className="animate-spin" style={{ marginRight: '8px' }} /> PDF Şablonu Yükleniyor...
            </div>
          )}
        </div>
      ) : viewMode === 'parchment' ? (
        <ParchmentSheetDisplay />
      ) : viewMode === 'summary' ? (

        /* Summary view alternative with detailed mathematical stat breakdowns */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Ability Scores Breakdown Grid */}
          <div>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={16} /> Yetenek Puanları ve Katkıları (Ability Breakdown)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
              {Object.entries(recalcedData.ability_scores || store.abilities || {}).map(([abName, totalScore]) => {
                if (abName === 'power_points') return null;
                const normName = abName.charAt(0).toUpperCase() + abName.slice(1);
                const baseScore = store.abilities[normName.toLowerCase()] || store.abilities[abName] || totalScore;
                const mod = recalcedData.ability_modifiers?.[normName] ?? Math.floor((totalScore - 10) / 2);
                const diff = totalScore - baseScore;
                const modSign = mod >= 0 ? `+${mod}` : `${mod}`;
                return (
                  <div key={abName} style={{ background: '#141426', border: '1px solid rgba(201,168,76,0.2)', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontWeight: 'bold', textTransform: 'uppercase' }}>{normName}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--accent-gold)', margin: '2px 0' }}>
                      {totalScore} <span style={{ fontSize: '13px', color: '#3fb950' }}>({modSign})</span>
                    </div>
                    <div style={{ fontSize: '10px', color: '#8b949e' }}>
                      {baseScore} Taban {diff !== 0 ? `${diff >= 0 ? '+' : ''}${diff} Bonusu` : ''}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Combat Summary Grid with Math Breakdown */}
          <div>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Shield size={16} /> Dövüş ve Savunma Detayları (Stat Breakdown)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
              
              {/* HP Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(233,69,96,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Heart size={14} style={{ color: '#e94560' }} /> CAN PUANI (HP)
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#f0e6d2' }}>{recalcedData.hit_points || 8}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Formül: <b>{recalcedData.class_data?.hit_die ? `d${recalcedData.class_data.hit_die}` : 'd10'} Taban</b> + <b>{(recalcedData.ability_modifiers?.Constitution || 0) * level} Con Mod</b>
                  {(recalcedData.applied_modifiers || []).filter(m => m.target === 'hp' && m.value > 0).map((m, i) => (
                    <span key={i} style={{ color: '#3fb950' }}> + {m.value} ({m.source})</span>
                  ))}
                </div>
              </div>

              {/* AC Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(63,185,80,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Shield size={14} style={{ color: '#3fb950' }} /> ZIRH SINIFI (AC)
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#f0e6d2' }}>{recalcedData.armor_class || 10}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Formül: <b>10 Taban</b> + <b>{recalcedData.ability_modifiers?.Dexterity || 0} Dex Mod</b>
                  {(recalcedData.applied_modifiers || []).filter(m => m.target === 'ac' && m.value > 0).map((m, i) => (
                    <span key={i} style={{ color: '#3fb950' }}> + {m.value} ({m.source})</span>
                  ))}
                  <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '4px' }}>
                    Touch AC: <b>{recalcedData.touch_ac || 10}</b> | Flat-Footed: <b>{recalcedData.flat_footed_ac || 10}</b>
                  </div>
                </div>
              </div>

              {/* Initiative Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(201,168,76,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} /> İNİSİYATİF
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--accent-gold)' }}>
                    {recalcedData.initiative >= 0 ? `+${recalcedData.initiative}` : recalcedData.initiative || 0}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Formül: <b>{recalcedData.ability_modifiers?.Dexterity >= 0 ? `+${recalcedData.ability_modifiers?.Dexterity}` : recalcedData.ability_modifiers?.Dexterity || 0} Dex Mod</b>
                  {(recalcedData.applied_modifiers || []).filter(m => m.target === 'initiative' && m.value !== 0).map((m, i) => (
                    <span key={i} style={{ color: '#38bdf8' }}> + {m.value} ({m.source})</span>
                  ))}
                </div>
              </div>

              {/* BAB & Combat Attacks Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(124,110,247,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sword size={14} style={{ color: '#7c6ef7' }} /> BAB & SALDIRI
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#7c6ef7' }}>+{recalcedData.bab || 0}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Yakın Dövüş (Melee): <b>+{(recalcedData.melee_attack_bonus ?? (recalcedData.bab || 0) + (recalcedData.ability_modifiers?.Strength || 0))}</b> (+{recalcedData.bab || 0} BAB + {recalcedData.ability_modifiers?.Strength || 0} Str)
                  <br />
                  Menzilli (Ranged): <b>+{(recalcedData.ranged_attack_bonus ?? (recalcedData.bab || 0) + (recalcedData.ability_modifiers?.Dexterity || 0))}</b> (+{recalcedData.bab || 0} BAB + {recalcedData.ability_modifiers?.Dexterity || 0} Dex)
                  <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '4px' }}>
                    CMB: <b>+{recalcedData.cmb || 0}</b> | CMD: <b>{recalcedData.cmd || 10}</b>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Saving Throws Math Breakdown */}
          <div style={{ background: '#141426', border: '1px solid rgba(255,255,255,0.08)', padding: '14px', borderRadius: '8px' }}>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1rem', marginBottom: '10px' }}>Kurtarma Zarları Detayı (Saving Throws)</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
              {['Fortitude', 'Reflex', 'Will'].map(saveKey => {
                const totalSave = recalcedData.saving_throws?.[saveKey] || 0;
                const abKey = saveKey === 'Fortitude' ? 'Constitution' : saveKey === 'Reflex' ? 'Dexterity' : 'Wisdom';
                const abMod = recalcedData.ability_modifiers?.[abKey] || 0;
                const featSaveMods = (recalcedData.applied_modifiers || []).filter(m => m.target === `saving_throws.${saveKey}` || m.target === 'saving_throws.All');
                return (
                  <div key={saveKey} style={{ background: '#1a1a2e', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 'bold' }}>
                      <span>{saveKey}</span>
                      <span style={{ color: 'var(--accent-gold)' }}>{totalSave >= 0 ? `+${totalSave}` : totalSave}</span>
                    </div>
                    <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '4px' }}>
                      Mod: {abMod >= 0 ? `+${abMod}` : abMod} ({abKey.slice(0, 3)})
                      {featSaveMods.map((m, i) => (
                        <span key={i} style={{ color: '#38bdf8' }}> +{m.value} ({m.source})</span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Applied Modifiers Breakdown List */}
          {(recalcedData.applied_modifiers || []).length > 0 && (
            <div style={{ background: 'rgba(201,168,76,0.04)', border: '1px solid rgba(201,168,76,0.2)', padding: '14px', borderRadius: '8px' }}>
              <h4 style={{ color: 'var(--accent-gold)', fontSize: '1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={16} /> Aktif Modifikatörler ve Kaynakları ({recalcedData.applied_modifiers.length})
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
                {recalcedData.applied_modifiers.map((mod, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#141426', padding: '6px 10px', borderRadius: '6px', fontSize: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <span>
                      <b style={{ color: '#f0e6d2' }}>{mod.source}</b>
                      <span style={{ fontSize: '10px', color: '#8b949e', marginLeft: '6px' }}>({mod.type})</span>
                    </span>
                    <span style={{ fontWeight: 'bold', color: mod.value >= 0 ? '#3fb950' : '#e94560' }}>
                      {mod.description || `${mod.value >= 0 ? '+' : ''}${mod.value} to ${mod.target}`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Encumbrance */}
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
              <span>Toplam Ağırlık: <b>{recalcedData.total_weight || 0} lbs</b></span>
              <span style={{ color: 'var(--accent-gold)', fontWeight: 'bold' }}>
                Yük Durumu: {recalcedData.encumbrance_status || 'Light'}
              </span>
            </div>
          </div>

          {/* Categorized Equipment List */}
          <div>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', marginBottom: '10px' }}>Kategorize Envanter (Inventory)</h4>
            <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: '8px', marginBottom: '12px' }}>
              {['weapons', 'armor_shields', 'consumables', 'gear'].map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveEqTab(cat)}
                  style={{
                    flex: 1,
                    padding: '6px',
                    fontSize: '11px',
                    borderRadius: '6px',
                    border: 'none',
                    background: activeEqTab === cat ? 'var(--accent-gold)' : 'transparent',
                    color: activeEqTab === cat ? '#0f0f1a' : '#8b949e',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  {cat.toUpperCase()}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '250px', overflowY: 'auto' }}>
              {(recalcedData[activeEqTab] || []).length === 0 ? (
                <p style={{ fontSize: '12px', color: '#8b949e', fontStyle: 'italic' }}>Bu kategoride eşya yok.</p>
              ) : (
                (recalcedData[activeEqTab] || []).map((item, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#16213e', borderRadius: '6px', fontSize: '12px' }}>
                    <span><b>{item.name}</b></span>
                    <span style={{ color: '#8b949e' }}>{item.sistem_verisi?.weight?.value || 0} lb</span>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      ) : (
        /* Spellbook & Interactive Spell Cards View Area */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(124,110,247,0.08)', padding: '14px 18px', borderRadius: '10px', border: '1px solid rgba(124,110,247,0.3)' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#a594ff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Wand2 size={20} />
                Büyü Kitabı & Etkileşimli Büyü Kartları ({name})
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#8b949e' }}>
                Hazırlanan veya bilinen büyüleri kart şeklinde görüntüleyin, zar atın veya büyü etkisi uygulayın.
              </p>
            </div>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#a594ff', background: 'rgba(124,110,247,0.2)', padding: '4px 12px', borderRadius: '12px', border: '1px solid rgba(124,110,247,0.4)' }}>
              Seviye {level || 1} {charClass || 'Büyücü'} (CL {recalcedData.spellcasting?.caster_level || level || 1})
            </div>
          </div>

          {/* Spellcasting Engine Stat Header (DCs, Concentration, CL) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px', background: '#121124', padding: '14px', borderRadius: '8px', border: '1px solid rgba(124,110,247,0.25)' }}>
            <div style={{ textAlign: 'center', padding: '6px', background: 'rgba(124,110,247,0.1)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#a594ff', fontWeight: 'bold' }}>BÜYÜCÜ SEVİYESİ (CL)</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#ffffff' }}>+{recalcedData.spellcasting?.caster_level || level || 1}</div>
            </div>

            <div style={{ textAlign: 'center', padding: '6px', background: 'rgba(124,110,247,0.1)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#a594ff', fontWeight: 'bold' }}>ODAKLANMA (CONCENTRATION)</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#38bdf8' }}>
                {(recalcedData.spellcasting?.concentration_bonus ?? 0) >= 0 ? `+${recalcedData.spellcasting?.concentration_bonus || 0}` : recalcedData.spellcasting?.concentration_bonus || 0}
              </div>
            </div>

            {/* Spell DC Cards per Level (0..5) */}
            {[0, 1, 2, 3, 4, 5].map(lvlIdx => {
              const dcVal = recalcedData.spellcasting?.spell_dcs?.[String(lvlIdx)] || (10 + lvlIdx + (recalcedData.ability_modifiers?.Intelligence || 0));
              return (
                <div key={lvlIdx} style={{ textAlign: 'center', padding: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-secondary)' }}>{lvlIdx}. SEVİYE DC</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--accent-gold)' }}>{dcVal}</div>
                </div>
              );
            })}
          </div>

          {(!store.spells || store.spells.length === 0) ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', background: 'rgba(0,0,0,0.25)', borderRadius: '10px', border: '1px dashed rgba(124,110,247,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <Wand2 size={40} style={{ color: '#7c6ef7' }} />
              <div style={{ fontSize: '15px', color: '#f0e6d2', fontWeight: 'bold' }}>Henüz Büyü Eklemediniz</div>
              <p style={{ fontSize: '13px', color: '#8b949e', maxWidth: '400px', margin: 0 }}>
                Sol paneldeki <b>Büyü Seçimi</b> alanından Pathfinder 1e veritabanındaki 3.000+ büyü arasından karakterinize büyü ekleyebilirsiniz.
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
              {store.spells.map((sp, idx) => (
                <SpellCard
                  key={idx}
                  spell={sp}
                  characterLevel={level}
                  characterClass={charClass}
                  onRemoveSpell={(spellNameToRemove) => store.removeSpell(spellNameToRemove)}
                  compact={false}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Companion Live Stat Block Card */}
      {store.companion && (
        <div style={{ marginTop: '20px', padding: '20px', background: 'linear-gradient(135deg, rgba(201,168,76,0.08) 0%, rgba(10,8,20,0.9) 100%)', border: '2px solid var(--accent-gold)', borderRadius: '12px', boxShadow: '0 0 20px rgba(0,0,0,0.5)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.4rem' }}>🐾</span>
              <div>
                <h4 style={{ margin: 0, color: 'var(--accent-gold)', fontFamily: 'Cinzel, serif', fontSize: '1.2rem' }}>
                  {store.companion.name || 'Yoldaş'} ({store.companion.species})
                </h4>
                <span style={{ fontSize: '12px', color: '#8b949e' }}>
                  {store.companion.type === 'animal_companion' ? 'Hayvan Yoldaş (Animal Companion)' :
                   store.companion.type === 'eidolon' ? 'Summoner Eidolon' :
                   store.companion.type === 'familiar' ? 'Sihirli Familiar' : 'Binek (Mount)'}
                </span>
              </div>
            </div>
            <div style={{ fontSize: '12px', background: 'rgba(201,168,76,0.15)', color: 'var(--accent-gold)', padding: '4px 12px', borderRadius: '12px', border: '1px solid rgba(201,168,76,0.3)', fontWeight: 'bold' }}>
              Seviye {store.companion.level || 1} Stat Bloğu
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#8b949e', textTransform: 'uppercase' }}>Can Puanı (HP)</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#3fb950' }}>{store.companion.hp} HP</div>
              <div style={{ fontSize: '10px', color: '#8b949e' }}>{store.companion.hd}d8 HD</div>
            </div>

            <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#8b949e', textTransform: 'uppercase' }}>Zırh Sınıfı (AC)</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#e94560' }}>{store.companion.ac} AC</div>
              <div style={{ fontSize: '10px', color: '#8b949e' }}>Doğal Zırh</div>
            </div>

            <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#8b949e', textTransform: 'uppercase' }}>Saldırı (Attacks)</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: 'var(--accent-gold)' }}>{store.companion.attacks}</div>
              <div style={{ fontSize: '10px', color: '#8b949e' }}>BAB: {store.companion.bab}</div>
            </div>
          </div>

          {store.companion.tricks && store.companion.tricks.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <span style={{ fontSize: '12px', color: 'var(--accent-gold)', fontWeight: 'bold' }}>Komut Numaraları (Tricks): </span>
              <span style={{ fontSize: '12px', color: '#f0e6d2' }}>{store.companion.tricks.join(', ')}</span>
            </div>
          )}

          {store.companion.evolutions && store.companion.evolutions.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <span style={{ fontSize: '12px', color: '#c4beff', fontWeight: 'bold' }}>Eidolon Evrimleri: </span>
              <span style={{ fontSize: '12px', color: '#f0e6d2' }}>{store.companion.evolutions.join(', ')}</span>
            </div>
          )}

          {store.companion.masterBonus && (
            <div style={{ marginTop: '8px' }}>
              <span style={{ fontSize: '12px', color: '#52b788', fontWeight: 'bold' }}>Efendi Bonusu: </span>
              <span style={{ fontSize: '12px', color: '#ffffff', fontWeight: 'bold' }}>{store.companion.masterBonus}</span>
            </div>
          )}

          {store.companion.notes && (
            <div style={{ marginTop: '8px', fontSize: '11px', color: '#8b949e', fontStyle: 'italic' }}>
              Notlar: {store.companion.notes}
            </div>
          )}
        </div>
      )}

    </div>
  );
}
