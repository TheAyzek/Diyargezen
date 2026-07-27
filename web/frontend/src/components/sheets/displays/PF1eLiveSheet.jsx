import React, { useEffect, useState, useRef } from 'react';
import { PDFDocument, StandardFonts } from 'pdf-lib';
import { FileText, RefreshCw, Download, Shield, Heart, Sword, Sparkles, Activity } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

export default function PF1eLiveSheet() {
  const store = useCharacterStore();
  const { name, level, race, class: charClass, feat, recalcedData, portrait, raceData, skills } = store;
  const traits = store.traits || [];
  const feats = store.feats || (feat ? [{ isim: feat }] : []);
  
  const [pdfUrl, setPdfUrl] = useState(null);
  const [rendering, setRendering] = useState(false);
  const [viewMode, setViewMode] = useState('pdf'); // 'pdf' or 'summary'
  const [activeEqTab, setActiveEqTab] = useState('weapons');
  const debounceTimerRef = useRef(null);

  // Core PDF fill function using pdf-lib
  const renderLivePdf = async () => {
    try {
      setRendering(true);
      const response = await fetch('/templates/pf1e_sheet.pdf');
      if (!response.ok) {
        throw new Error(`PDF template loading failed: HTTP ${response.status}`);
      }
      const existingPdfBytes = await response.arrayBuffer();

      const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
      const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const form = pdfDoc.getForm();

      const setField = (fieldName, textValue) => {
        try {
          const field = form.getField(fieldName);
          if (field && typeof field.setText === 'function') {
            field.setText(String(textValue ?? ''));
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

      // Ability Scores (exact pf1e_sheet.pdf AcroForm field names)
      const derivedScores = recalcedData.ability_scores || {};
      const derivedMods = recalcedData.ability_modifiers || {};

      setField('strength', derivedScores.Strength || 10);
      setField('dexterity', derivedScores.Dexterity || 10);
      setField('constitution', derivedScores.Constitution || 10);
      setField('intelligence', derivedScores.Intelligence || 10);
      setField('WIS', derivedScores.Wisdom || 10);
      setField('charisma', derivedScores.Charisma || 10);

      // Armor Class & Combat Stats
      setField('hit points', recalcedData.hit_points || 8);
      setField('armor class', recalcedData.armor_class || 10);
      setField('TOUCH', recalcedData.touch_ac || 10);
      setField('FLATFOOTED', recalcedData.flat_footed_ac || 10);
      setField('BASE ATTACK BONUS', recalcedData.bab >= 0 ? `+${recalcedData.bab}` : recalcedData.bab || 0);
      setField('CMB', recalcedData.cmb >= 0 ? `+${recalcedData.cmb}` : recalcedData.cmb || 0);
      setField('CMD', recalcedData.cmd || 10);
      setField('INITIATIVE', recalcedData.initiative >= 0 ? `+${recalcedData.initiative}` : recalcedData.initiative || 0);

      // Saves
      const saves = recalcedData.saving_throws || {};
      setField('FORTITUDE', saves.fortitude >= 0 ? `+${saves.fortitude}` : saves.fortitude || 0);
      setField('REFLEX', saves.reflex >= 0 ? `+${saves.reflex}` : saves.reflex || 0);
      setField('WILL', saves.will >= 0 ? `+${saves.will}` : saves.will || 0);

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
      const classSkills = recalcedData.class_data?.class_skills || [];

      Object.entries(skillPdfMapping).forEach(([skillName, pdfFields]) => {
        const ranks = parseInt(userSkills[skillName]) || 0;
        const abMod = derivedMods[pdfFields.ab] || 0;
        const isClassSkill = classSkills.includes(skillName);
        const classSkillBonus = (isClassSkill && ranks > 0) ? 3 : 0;
        const totalBonus = ranks + abMod + classSkillBonus;

        setField(pdfFields.ranks, ranks > 0 ? ranks : '');
        setField(pdfFields.mod, abMod >= 0 ? `+${abMod}` : `${abMod}`);
        setField(pdfFields.total, totalBonus >= 0 ? `+${totalBonus}` : `${totalBonus}`);

        // Class Skill Checkbox
        if (isClassSkill) {
          try {
            const btnField = form.getCheckBox(skillName);
            if (btnField) btnField.check();
          } catch (e) {}
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
          const ranks = parseInt(userSkills[skillName]) || 0;
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
      // Weapons Mapping
      const weapons = recalcedData.weapons || [];
      weapons.slice(0, 5).forEach((w, idx) => {
        const sys = w.sistem_verisi?.system || {};
        const dmg = sys.actions?.[0]?.damage?.parts?.[0]?.[0] || w.sistem_verisi?.damage?.parts?.[0]?.[0] || '-';
        setField(`Weapon ${idx + 1}`, w.name);
        setField(`Damage ${idx + 1}`, dmg);
      });

      // General Equipment Mapping
      const items = [
        ...(recalcedData.armor_shields || []),
        ...(recalcedData.consumables || []),
        ...(recalcedData.gear || [])
      ];
      items.slice(0, 26).forEach((item, idx) => {
        setField(`Item ${idx + 1}`, item.name);
        setField(`WT ${idx + 1}`, `${item.sistem_verisi?.weight?.value || 0} lb`);
      });

      // Update appearance streams so entered text is rendered visually without needing to click on fields
      try {
        form.updateFieldAppearances(font);
      } catch (e) {
        // Fallback gracefully if any individual field has unsupported appearance properties
      }

      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, updateFieldAppearances: false });
      setPdfUrl(pdfDataUri);
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
            </h3>
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Reaktif `pdf-lib` Form Görselleştirici (300ms Debounce)
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
            📊 Özet Görünüm
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
      ) : (
        /* Summary view alternative */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Combat Summary Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '12px' }}>
            <div style={{ background: '#16213e', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Heart size={18} style={{ color: '#e94560' }} />
              <div style={{ fontSize: '10px', color: '#8b949e' }}>HP</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>{recalcedData.hit_points || 8}</div>
            </div>
            <div style={{ background: '#16213e', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Shield size={18} style={{ color: '#3fb950' }} />
              <div style={{ fontSize: '10px', color: '#8b949e' }}>AC</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>{recalcedData.armor_class || 10}</div>
            </div>
            <div style={{ background: '#16213e', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Sword size={18} style={{ color: 'var(--accent-gold)' }} />
              <div style={{ fontSize: '10px', color: '#8b949e' }}>BAB</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>+{recalcedData.bab || 0}</div>
            </div>
            <div style={{ background: '#16213e', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Sparkles size={18} style={{ color: 'var(--accent-gold)' }} />
              <div style={{ fontSize: '10px', color: '#8b949e' }}>CMB / CMD</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>+{recalcedData.cmb || 0} / {recalcedData.cmd || 10}</div>
            </div>
          </div>

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
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', marginBottom: '10px' }}>Categorized Inventory</h4>
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
      )}

    </div>
  );
}
