import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BookOpen, Search, Shield, Zap, Sparkles, Scroll, UserCheck, 
  Layers, ChevronRight, X, Info, Filter, ArrowLeft, Crosshair, Sword,
  Dices, Star, Award, Heart, CheckCircle2
} from 'lucide-react';
import { cleanText, formatTitle, toSentenceCase, parseTraitsDetailed } from '../utils/textSanitizer';
import { getEquipmentCategory, EQUIPMENT_CATEGORIES, matchesEquipmentSubfilter } from '../utils/equipmentClassifier';

const CATEGORIES = [
  { id: 'races', label: 'Irklar & Miraslar', icon: UserCheck, endpoint: '/api/rules/pf1e/races' },
  { id: 'classes', label: 'Sınıflar & Arketipler', icon: Layers, endpoint: '/api/rules/pf1e/classes' },
  { id: 'feats', label: 'Featler & Hünerler', icon: Scroll, endpoint: '/api/rules/pf1e/feats' },
  { id: 'spells', label: 'Büyüler & Mucizeler', icon: Sparkles, endpoint: '/api/rules/pf1e/spells' },
  { id: 'equipment', label: 'Ekipmanlar & Eşyalar', icon: Shield, endpoint: '/api/rules/pf1e/equipment' },
  { id: 'class-features', label: 'Sınıf Yetenekleri', icon: Zap, endpoint: '/api/rules/pf1e/class-features' },
  { id: 'traits', label: 'Karakter Traitleri', icon: BookOpen, endpoint: '/api/rules/pf1e/traits' },
  { id: 'mechanics', label: 'Genel Savaş & Kurallar', icon: Sword, endpoint: '/api/rules/pf1e/mechanics' },
];

const STANDARD_PF1E_CLASS_INFO = {
  Barbarian: {
    hit_die: 'd12',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Tüm basit ve savaş silahları, hafif ve orta zırhlar, kalkanlar (kule kalkanı hariç).',
    class_skills: ['Acrobatics', 'Climb', 'Craft', 'Handle Animal', 'Intimidate', 'Knowledge (nature)', 'Perception', 'Ride', 'Survival', 'Swim']
  },
  Bard: {
    hit_die: 'd8',
    skill_ranks: '6 + INT Mod',
    proficiencies: 'Tüm basit silahlar, longsword, rapier, sap, shortsword, shortbow, whip, hafif zırhlar ve kalkanlar.',
    class_skills: ['Acrobatics', 'Appraise', 'Bluff', 'Climb', 'Craft', 'Diplomacy', 'Disguise', 'Escape Artist', 'Intimidate', 'Knowledge (all)', 'Linguistics', 'Perception', 'Perform', 'Profession', 'Sense Motive', 'Sleight of Hand', 'Spellcraft', 'Stealth', 'Use Magic Device']
  },
  Cleric: {
    hit_die: 'd8',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Tüm basit silahlar, tanrısının favori silahı, hafif/orta/ağır zırhlar ve kalkanlar.',
    class_skills: ['Appraise', 'Craft', 'Diplomacy', 'Heal', 'Knowledge (arcana)', 'Knowledge (history)', 'Knowledge (nobility)', 'Knowledge (planes)', 'Knowledge (religion)', 'Linguistics', 'Profession', 'Sense Motive', 'Spellcraft']
  },
  Druid: {
    hit_die: 'd8',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Club, dagger, dart, quarterstaff, scimitar, scythe, sickle, sling, spear, tahta hafif/orta zırhlar ve tahta kalkanlar.',
    class_skills: ['Climb', 'Craft', 'Fly', 'Handle Animal', 'Heal', 'Knowledge (geography)', 'Knowledge (nature)', 'Perception', 'Profession', 'Ride', 'Spellcraft', 'Survival', 'Swim']
  },
  Fighter: {
    hit_die: 'd10',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Tüm basit ve savaş silahları, hafif, orta ve ağır zırhlar, tüm kalkanlar (kule kalkanı dahil).',
    class_skills: ['Climb', 'Craft', 'Handle Animal', 'Intimidate', 'Knowledge (dungeoneering)', 'Knowledge (engineering)', 'Profession', 'Ride', 'Survival', 'Swim']
  },
  Monk: {
    hit_die: 'd8',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Club, crossbow, dagger, handaxe, javelin, kama, nunchaku, quarterstaff, sai, shuriken, siangham, sling.',
    class_skills: ['Acrobatics', 'Climb', 'Craft', 'Escape Artist', 'Intimidate', 'Knowledge (history)', 'Knowledge (religion)', 'Perception', 'Perform', 'Profession', 'Ride', 'Sense Motive', 'Stealth', 'Swim']
  },
  Paladin: {
    hit_die: 'd10',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Tüm basit ve savaş silahları, hafif, orta ve ağır zırhlar ve tüm kalkanlar (kule kalkanı hariç).',
    class_skills: ['Craft', 'Diplomacy', 'Handle Animal', 'Heal', 'Knowledge (nobility)', 'Knowledge (religion)', 'Profession', 'Ride', 'Sense Motive', 'Spellcraft']
  },
  Ranger: {
    hit_die: 'd10',
    skill_ranks: '6 + INT Mod',
    proficiencies: 'Tüm basit ve savaş silahları, hafif ve orta zırhlar, kalkanlar (kule kalkanı hariç).',
    class_skills: ['Climb', 'Craft', 'Handle Animal', 'Heal', 'Intimidate', 'Knowledge (dungeoneering)', 'Knowledge (geography)', 'Knowledge (nature)', 'Perception', 'Profession', 'Ride', 'Spellcraft', 'Stealth', 'Survival', 'Swim']
  },
  Rogue: {
    hit_die: 'd8',
    skill_ranks: '8 + INT Mod',
    proficiencies: 'Tüm basit silahlar, hand crossbow, rapier, sap, shortbow, shortsword, hafif zırhlar.',
    class_skills: ['Acrobatics', 'Appraise', 'Bluff', 'Climb', 'Craft', 'Diplomacy', 'Disable Device', 'Disguise', 'Escape Artist', 'Intimidate', 'Knowledge (dungeoneering)', 'Knowledge (local)', 'Linguistics', 'Perception', 'Perform', 'Profession', 'Sense Motive', 'Sleight of Hand', 'Stealth', 'Swim', 'Use Magic Device']
  },
  Sorcerer: {
    hit_die: 'd6',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Tüm basit silahlar. Zırh veya kalkan yetkinliği yoktur.',
    class_skills: ['Bluff', 'Craft', 'Fly', 'Intimidate', 'Knowledge (arcana)', 'Profession', 'Spellcraft', 'Use Magic Device']
  },
  Wizard: {
    hit_die: 'd6',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Club, dagger, heavy crossbow, light crossbow, quarterstaff. Zırh veya kalkan yetkinliği yoktur.',
    class_skills: ['Appraise', 'Craft', 'Fly', 'Knowledge (all)', 'Linguistics', 'Profession', 'Spellcraft']
  },
  Alchemist: {
    hit_die: 'd8',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Basit silahlar, bomba (bombs), hafif zırhlar.',
    class_skills: ['Appraise', 'Craft', 'Disable Device', 'Heal', 'Knowledge (arcana)', 'Knowledge (nature)', 'Perception', 'Profession', 'Spellcraft', 'Survival', 'Use Magic Device']
  },
  Cavalier: {
    hit_die: 'd10',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Basit ve savaş silahları, hafif/orta/ağır zırhlar, kalkanlar.',
    class_skills: ['Bluff', 'Climb', 'Craft', 'Diplomacy', 'Handle Animal', 'Intimidate', 'Profession', 'Ride', 'Sense Motive', 'Swim']
  },
  Gunslinger: {
    hit_die: 'd10',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Basit ve savaş silahları, tüm ateşli silahlar (firearms), hafif zırhlar.',
    class_skills: ['Acrobatics', 'Craft', 'Heal', 'Intimidate', 'Knowledge (engineering)', 'Knowledge (local)', 'Perception', 'Profession', 'Ride', 'Sleight of Hand', 'Survival']
  },
  Inquisitor: {
    hit_die: 'd8',
    skill_ranks: '6 + INT Mod',
    proficiencies: 'Basit silahlar, hand crossbow, longbow, repeating crossbow, shortbow, tanrı silahı, hafif/orta zırhlar, kalkanlar.',
    class_skills: ['Bluff', 'Climb', 'Craft', 'Diplomacy', 'Disguise', 'Heal', 'Intimidate', 'Knowledge (all)', 'Perception', 'Profession', 'Ride', 'Sense Motive', 'Spellcraft', 'Stealth', 'Survival', 'Swim']
  },
  Magus: {
    hit_die: 'd8',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Basit ve savaş silahları, hafif zırhlar.',
    class_skills: ['Climb', 'Craft', 'Fly', 'Intimidate', 'Knowledge (arcana)', 'Knowledge (dungeoneering)', 'Profession', 'Ride', 'Spellcraft', 'Use Magic Device']
  },
  Oracle: {
    hit_die: 'd8',
    skill_ranks: '4 + INT Mod',
    proficiencies: 'Basit silahlar, hafif ve orta zırhlar, kalkanlar.',
    class_skills: ['Craft', 'Diplomacy', 'Heal', 'Knowledge (history)', 'Knowledge (planes)', 'Knowledge (religion)', 'Profession', 'Sense Motive', 'Spellcraft']
  },
  Summoner: {
    hit_die: 'd8',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Basit silahlar, hafif zırhlar.',
    class_skills: ['Craft', 'Fly', 'Handle Animal', 'Knowledge (all)', 'Linguistics', 'Profession', 'Ride', 'Spellcraft', 'Use Magic Device']
  },
  Witch: {
    hit_die: 'd6',
    skill_ranks: '2 + INT Mod',
    proficiencies: 'Basit silahlar. Zırh yetkinliği yoktur.',
    class_skills: ['Craft', 'Fly', 'Heal', 'Intimidate', 'Knowledge (all)', 'Profession', 'Spellcraft', 'Use Magic Device']
  }
};

const CURATED_MECHANICS = [
  {
    isim: "Fırsat Saldırısı (Attack of Opportunity - AoO)",
    kategori: "Combat",
    aciklama: "Bir düşman senin tehdit ettiğin (reach) alandan çıkarken veya savunmasız bir eylem yaparken (büyü okuma, menzilli saldırı, silahsız saldırı) bedelsiz olarak yaptığın ek yakın dövüş saldırısıdır.",
    sistem_verisi: { "Tetikleyiciler": "Tehdit alanından hareket etme, Büyü Okuma, Ranged Attack", "Limit": "Tur başına 1 (Combat Reflexes haricinde)" }
  },
  {
    isim: "Gözleri Görmeyen (Blinded)",
    kategori: "Condition",
    aciklama: "Karakter hiçbir şey göremez. Algı (Perception) zarlarına -20 ceza alır. AC'sine Dex modunu uygulayamaz ve AC'sine -2 ceza alır. Hareket hızı yarıya düşer.",
    sistem_verisi: { "AC Cezası": "-2 ve Dex Mod Sıfırlanır", "Algı Cezası": "-20 (Visual)", "Hareket": "%50 Yavaşlama" }
  },
  {
    isim: "Yakalanmış / Güreşilen (Grappled)",
    kategori: "Condition",
    aciklama: "Karakter bir başkası tarafından tutulmuş veya kilitlenmiştir. Hareket edemez, Dex modunu AC'ye uygulayamaz. Saldırı zarlarına ve Dex temelli zarlara -4 ceza alır. Tek elle yapılamayan veya büyü bileşeni gerektiren eylemler kısıtlanır.",
    sistem_verisi: { "Saldırı Cezası": "-4", "Büyü Atma": "Concentration DC 10 + Grappler's CMB + Spell Level", "Hareket": "0 (Sabit)" }
  },
  {
    isim: "Sersemlemiş (Stunned)",
    kategori: "Condition",
    aciklama: "Karakter eylem yapamaz, elindeki eşyaları düşürür, Dex modunu AC'ye uygulayamaz ve AC'sine -2 ceza alır.",
    sistem_verisi: { "Eylem": "Yapılamaz", "Eşya": "Düşer", "AC": "-2 ve Dex Mod Kaybı" }
  },
  {
    isim: "Yere Düşmüş (Prone)",
    kategori: "Condition",
    aciklama: "Karakter yerde yatmaktadır. Yakın dövüş saldırı zarlarına -4 ceza alır. Yakın dövüş AC'sine -4 ceza alırken, menzilli saldırılara karşı AC'sine +4 bonus kazanır. Ayağa kalkmak Move Action gerektirir ve AoO tetikler.",
    sistem_verisi: { "Melee Attack": "-4", "Melee AC": "-4", "Ranged AC": "+4", "Ayağa Kalkma": "Move Action (AoO tetikler)" }
  },
  {
    isim: "Sarsılmış / Korkmuş (Shaken)",
    kategori: "Condition",
    aciklama: "Karakter hafifçe korkmuştur. Saldırı zarlarına, Kurtarma Atışlarına, Yetenek ve Özellik zarlarına -2 ceza alır.",
    sistem_verisi: { "Tüm Zarlar": "-2 (Attack, Saves, Skill, Ability Checks)" }
  },
  {
    isim: "Yorulmuş (Fatigued)",
    kategori: "Condition",
    aciklama: "Karakter yorulmuştur. Koşamaz veya hücum (charge) edemez. Strength ve Dexterity skorlarına -2 ceza alırlar (-1 modifikatör etkisi).",
    sistem_verisi: { "Stat Cezası": "-2 STR, -2 DEX", "Aksiyon": "Run/Charge yapılamaz" }
  },
  {
    isim: "Güreş Manevrası (Grapple CMB)",
    kategori: "Combat Maneuver",
    aciklama: "Hedefi tutmak ve etkisiz hale getirmek için yapılan Combat Maneuver Check (CMB vs Target CMD). Başarılı olursa hedef Grappled durumuna girer.",
    sistem_verisi: { "Hesaplama": "d20 + CMB vs target CMD", "Sonuç": "Grappled Effect" }
  },
  {
    isim: "Çelme Manevrası (Trip CMB)",
    kategori: "Combat Maneuver",
    aciklama: "Hedefi yere düşürmek için yapılan manevra atışı. Başarılı olursa hedef Prone olur. Başarısızlık 5 veya daha fazla farkla olursa saldıran yere düşebilir.",
    sistem_verisi: { "Karşılaştırma": "CMB vs target CMD", "Sonuç": "Prone Effect" }
  },
  {
    isim: "Konsantrasyon Kontrolü (Concentration Check)",
    kategori: "Spellcasting",
    aciklama: "Büyü okurken hasar alma, güreşilme veya zorlu hava şartlarında büyünün bozulmaması için yapılan zar: 1d20 + Caster Level + Ability Mod vs belirlenen DC.",
    sistem_verisi: { "Hesaplama": "1d20 + CL + Key Ability Mod", "Hasar DC": "10 + Alınan Hasar + Büyü Seviyesi" }
  }
];

export default function RulesCompendium({ onBack }) {
  const [activeTab, setActiveTab] = useState('races');
  const [query, setQuery] = useState('');
  const [subFilter, setSubFilter] = useState('');
  const [spellLevel, setSpellLevel] = useState('');
  const [sortBy, setSortBy] = useState('level_asc');
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [coldStartMsg, setColdStartMsg] = useState('');

  useEffect(() => {
    fetchEntities();
  }, [activeTab]);

  const fetchEntities = async (retryCount = 0) => {
    setLoading(true);
    const catObj = CATEGORIES.find(c => c.id === activeTab);
    if (!catObj) return;

    try {
      if (activeTab === 'mechanics') {
        const res = await axios.get(catObj.endpoint).catch(() => ({ data: [] }));
        if (res.data && res.data.length > 0) {
          setEntities(res.data);
        } else {
          setEntities(CURATED_MECHANICS);
        }
      } else {
        const params = {};
        if (activeTab === 'spells' && spellLevel !== '') {
          params.level = spellLevel;
        }
        if (subFilter) {
          if (activeTab === 'spells') params.school = subFilter;
          else params.category = subFilter;
        }
        const res = await axios.get(catObj.endpoint, { params });
        setEntities(res.data || []);
      }
      setColdStartMsg('');
    } catch (err) {
      console.error('Error fetching compendium entities:', err);
      const status = err?.response?.status;
      // Render free tier cold start: retry on 502/503 up to 3 times
      if ((status === 502 || status === 503 || !err.response) && retryCount < 3) {
        const waitMs = (retryCount + 1) * 2000; // 2s, 4s, 6s
        setColdStartMsg(`Sunucu uyanıyor... (Deneme ${retryCount + 2}/4) — Render ücretsiz plan ilk istekte ~30 saniye sürebilir.`);
        setTimeout(() => fetchEntities(retryCount + 1), waitMs);
        return; // Don't clear loading
      }
      setColdStartMsg('');
      if (activeTab === 'mechanics') {
        setEntities(CURATED_MECHANICS);
      } else {
        setEntities([]);
      }
    } finally {
      if (retryCount === 0 || retryCount >= 3) {
        setLoading(false);
      }
    }
  };

  const getItemLevel = (item) => {
    const sv = item.sistem_verisi || {};
    if (sv.level !== undefined && sv.level !== null) return parseInt(sv.level);
    if (sv.spell_level !== undefined && sv.spell_level !== null) return parseInt(sv.spell_level);
    if (item.seviye !== undefined && item.seviye !== null) return parseInt(item.seviye);
    if (item.level !== undefined && item.level !== null) return parseInt(item.level);
    if (sv.levels && typeof sv.levels === 'object') {
      const vals = Object.values(sv.levels).map(v => parseInt(v)).filter(n => !isNaN(n));
      if (vals.length > 0) return Math.min(...vals);
    }
    return null;
  };

  const isGarbageEntity = (item) => {
    const name = (item.isim || item.name || '').trim();
    if (name.startsWith('#') || name.startsWith('*') || name.startsWith('[CF_') || name.startsWith('†')) return true;
    if (name.includes('TEMPENTITY') || name.includes('GENERATE') || name.includes('MAJOR MAGIC') || name.includes('MINOR MAGIC')) return true;
    return false;
  };

  const filteredEntities = entities.filter(item => {
    if (isGarbageEntity(item)) return false;

    const nameMatch = (item.isim && item.isim.toLowerCase().includes(query.toLowerCase())) ||
                      (item.aciklama && item.aciklama.toLowerCase().includes(query.toLowerCase()));
    
    if (!nameMatch) return false;

    if (activeTab === 'spells') {
      if (spellLevel !== '') {
        const itemLvl = getItemLevel(item);
        if (itemLvl === null || itemLvl !== parseInt(spellLevel)) return false;
      }
      if (subFilter && item.sistem_verisi?.school) {
        if (!item.sistem_verisi.school.toLowerCase().includes(subFilter.toLowerCase())) return false;
      }
    } else if (activeTab === 'equipment') {
      if (subFilter && subFilter !== 'all') {
        const cat = getEquipmentCategory(item);
        if (!matchesEquipmentSubfilter(cat, subFilter)) return false;
      }
    } else if (activeTab === 'class-features') {
      if (subFilter) {
        const sv = item.sistem_verisi || {};
        const cfClass = (sv.class || sv.class_name || sv.assoc_class || item.kategori || '').toLowerCase();
        const cfText = `${item.isim || ''} ${item.aciklama || ''}`.toLowerCase();
        const searchCls = subFilter.toLowerCase();
        if (!cfClass.includes(searchCls) && !cfText.includes(searchCls)) return false;
      }
    } else if (activeTab === 'feats' || activeTab === 'traits' || activeTab === 'mechanics') {
      if (subFilter) {
        const featCat = item.sistem_verisi?.feat_category || item.sistem_verisi?.trait_category || item.sistem_verisi?.category || item.kategori || '';
        if (!featCat.toLowerCase().includes(subFilter.toLowerCase())) return false;
      }
    }

    return true;
  });

  const sortedEntities = [...filteredEntities].sort((a, b) => {
    if (sortBy === 'level_asc' || sortBy === 'level_desc') {
      const lvlA = getItemLevel(a) ?? (sortBy === 'level_asc' ? 99 : -1);
      const lvlB = getItemLevel(b) ?? (sortBy === 'level_asc' ? 99 : -1);
      if (lvlA !== lvlB) {
        return sortBy === 'level_asc' ? lvlA - lvlB : lvlB - lvlA;
      }
    }
    if (sortBy === 'name_desc') {
      return (b.isim || b.name || '').localeCompare(a.isim || a.name || '');
    }
    return (a.isim || a.name || '').localeCompare(b.isim || b.name || '');
  });

  const renderEntityBadges = (item) => {
    const data = item.sistem_verisi || {};
    const catBadge = data.feat_category || data.trait_category || (data.category !== item.kategori ? data.category : null);

    return (
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
        {item.kategori && (
          <span style={{ fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(201,168,76,0.15)', border: '1px solid rgba(201,168,76,0.3)', color: 'var(--gold-light)' }}>
            {item.kategori.toUpperCase()}
          </span>
        )}
        {catBadge && (
          <span style={{ fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(78,201,176,0.15)', border: '1px solid rgba(78,201,176,0.4)', color: '#7ee787' }}>
            {catBadge.toUpperCase()}
          </span>
        )}
        {data.level !== undefined && (
          <span style={{ fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(120,40,200,0.2)', border: '1px solid rgba(160,80,240,0.4)', color: '#d8b4fe' }}>
            Seviye {data.level}
          </span>
        )}
        {data.school && (
          <span style={{ fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(30,120,180,0.2)', border: '1px solid rgba(60,160,220,0.4)', color: '#93c5fd' }}>
            {data.school}
          </span>
        )}
        {data.prerequisites && (
          <span style={{ fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(180,60,60,0.2)', border: '1px solid rgba(220,80,80,0.4)', color: '#fca5a5' }}>
            Ön Koşullu
          </span>
        )}
      </div>
    );
  };

  const renderDetailContent = (item) => {
    const isClass = (activeTab === 'classes' || item.kategori === 'class' || item.kategori === 'archetype') && activeTab !== 'races';
    const sv = item.sistem_verisi || {};

    if (isClass) {
      // Find fallback info for class
      let classFallback = null;
      for (const [clsKey, clsObj] of Object.entries(STANDARD_PF1E_CLASS_INFO)) {
        if (item.isim.toLowerCase().includes(clsKey.toLowerCase())) {
          classFallback = clsObj;
          break;
        }
      }

      const hitDie = sv.hit_die || sv.hit_dice || classFallback?.hit_die || 'd8';
      const skillRanks = sv.skill_ranks_per_level || classFallback?.skill_ranks || '4 + INT Mod';
      const spellcasting = sv.spellcasting_type || (sv.spellcasting ? 'Var' : 'Yok');

      // Class Skills (Ensure non-empty fallback)
      let classSkills = (Array.isArray(sv.class_skills) && sv.class_skills.length > 0) ? sv.class_skills : (classFallback?.class_skills || []);
      if (typeof classSkills === 'string') {
        classSkills = [classSkills];
      }

      // Proficiencies (Ensure non-empty fallback)
      let proficiencies = (sv.proficiencies && (!Array.isArray(sv.proficiencies) || sv.proficiencies.length > 0)) ? sv.proficiencies : (classFallback?.proficiencies || 'Sınıfa özel yetkinlikler');

      // Saving Throws
      let savingThrows = sv.saving_throws || classFallback?.saving_throws || { fort: 'İyi (+2)', ref: 'Zayıf (+0)', will: 'Zayıf (+0)' };
      if (Array.isArray(savingThrows) && savingThrows.length === 0) {
        savingThrows = classFallback?.saving_throws || { fort: 'İyi (+2)', ref: 'Zayıf (+0)', will: 'Zayıf (+0)' };
      }

      // Features extraction & cleaning
      let rawFeatures = [];
      if (sv.features?.class_features && Array.isArray(sv.features.class_features)) {
        rawFeatures = sv.features.class_features;
      } else if (Array.isArray(sv.features)) {
        rawFeatures = sv.features;
      } else if (Array.isArray(sv.class_features)) {
        rawFeatures = sv.class_features;
      }

      const IGNORED_TERMS = ['class skills', 'class features', 'weapon and armor proficiency', 'discuss!', 'latest pathfinder products in the open gaming store', 'open gaming store'];
      const cleanFeatures = rawFeatures.filter(f => {
        const str = String(f).toLowerCase().trim();
        return !IGNORED_TERMS.some(term => str.includes(term));
      });

      return (
        <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Class Overview Description Banner */}
          {item.aciklama && (
            <div style={{
              padding: '14px 16px',
              background: 'rgba(201,168,76,0.06)',
              border: '1px solid rgba(201,168,76,0.25)',
              borderRadius: '6px',
              fontSize: '0.88rem',
              color: '#f0e6d2',
              lineHeight: '1.55',
              fontFamily: 'Outfit, sans-serif'
            }}>
              <h4 style={{ margin: '0 0 6px 0', fontFamily: 'Cinzel, serif', color: 'var(--gold-bright)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BookOpen size={16} /> {item.isim} Sınıf Tanımı & Genel Bakış
              </h4>
              {cleanText(item.aciklama)}
            </div>
          )}

          {/* Core Stat Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
            <div style={{ padding: '12px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.25)', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Dices size={24} style={{ color: 'var(--gold-bright)' }} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Can Zarı (Hit Die)</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--gold-light)' }}>{hitDie}</div>
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.25)', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Star size={24} style={{ color: 'var(--gold-bright)' }} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Beceri Puanı (Per Level)</div>
                <div style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--gold-light)' }}>{skillRanks}</div>
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.25)', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Shield size={24} style={{ color: 'var(--gold-bright)' }} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Kurtarma Atışları (Saves)</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--gold-light)', display: 'flex', gap: '4px', marginTop: '2px' }}>
                  <span style={{ color: '#4ec9b0', fontWeight: 'bold' }}>F: {typeof savingThrows === 'object' ? (savingThrows.fort || 'İyi') : 'İyi'}</span> | 
                  <span style={{ color: '#7c6ef7', fontWeight: 'bold' }}>R: {typeof savingThrows === 'object' ? (savingThrows.ref || 'Zayıf') : 'Zayıf'}</span> | 
                  <span style={{ color: '#ce9178', fontWeight: 'bold' }}>W: {typeof savingThrows === 'object' ? (savingThrows.will || 'Zayıf') : 'Zayıf'}</span>
                </div>
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.25)', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Sparkles size={24} style={{ color: 'var(--gold-bright)' }} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Büyü Kullanımı</div>
                <div style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--gold-light)' }}>{spellcasting}</div>
              </div>
            </div>
          </div>

          {/* Proficiencies */}
          <div style={{ padding: '14px', background: 'rgba(10,8,20,0.6)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Shield size={16} /> Silah & Zırh Yetkinlikleri (Proficiencies)
            </h4>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
              {typeof proficiencies === 'object' ? JSON.stringify(proficiencies) : String(proficiencies)}
            </div>
          </div>

          {/* Class Skills */}
          {classSkills && classSkills.length > 0 && (
            <div style={{ padding: '14px', background: 'rgba(10,8,20,0.6)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px' }}>
              <h4 style={{ margin: '0 0 10px 0', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Award size={16} /> Sınıf Becerileri (Class Skills)
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {classSkills.map((sk, idx) => (
                  <span key={idx} style={{ fontSize: '0.75rem', padding: '4px 10px', borderRadius: '12px', background: 'rgba(201,168,76,0.12)', border: '1px solid rgba(201,168,76,0.3)', color: 'var(--gold-light)' }}>
                    {sk}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Class Features */}
          {sv.features_detailed && sv.features_detailed.length > 0 ? (
            <div style={{ padding: '14px', background: 'rgba(10,8,20,0.6)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px' }}>
              <h4 style={{ margin: '0 0 12px 0', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={16} /> Sınıf Yetenekleri ve Kural Açıklamaları (Class Features)
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {sv.features_detailed.map((featObj, idx) => (
                  <div key={idx} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(201,168,76,0.18)', borderRadius: '6px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 'bold', color: 'var(--gold-bright)', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <CheckCircle2 size={13} style={{ color: 'var(--gold)' }} />
                        {featObj.name}
                      </span>
                      {featObj.level && (
                        <span style={{ fontSize: '0.68rem', padding: '2px 8px', borderRadius: '10px', background: 'rgba(201,168,76,0.15)', border: '1px solid rgba(201,168,76,0.3)', color: 'var(--gold-pale)' }}>
                          Seviye {featObj.level}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-main)', lineHeight: '1.45', marginTop: '4px' }}>
                      {featObj.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : cleanFeatures && cleanFeatures.length > 0 ? (
            <div style={{ padding: '14px', background: 'rgba(10,8,20,0.6)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px' }}>
              <h4 style={{ margin: '0 0 10px 0', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={16} /> Sınıf Yetenekleri (Class Features)
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
                {cleanFeatures.map((featName, idx) => (
                  <div key={idx} style={{ fontSize: '0.8rem', padding: '6px 10px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-main)' }}>
                    <CheckCircle2 size={12} style={{ color: 'var(--gold-bright)' }} />
                    {featName}
                  </div>
                ))}
              </div>
            </div>
          ) : null}

        </div>
      );
    }

    // Blacklist internal VTT schema keys
    const VTT_INTERNAL_KEYS = new Set([
      'description', 'name', 'system', 'aciklama', 'flags', 'data', 'img', '_id',
      'chat', 'unidentified', 'tags', 'actions', 'uses', 'per', 'maxformula',
      'autodeductchargescost', 'attacknotes', 'effectnotes', 'changes', 'changeflags',
      'losedextoac', 'noencumbrance', 'mediumarmorfullspeed', 'heavyarmorfullspeed',
      'links', 'charges', 'tag', 'usecustomtag', 'armorprof', 'weaponprof', 'languages',
      'scriptcalls', 'feattype', 'associations', 'classes', 'showinquickbar',
      'abilitytype', 'croffset', 'disabled', 'classskills', 'activation',
      'unchainedaction', 'actiontype', 'ability', 'damagemult', 'critmult',
      'maxincrements', 'standard_mechanics', 'source', 'source_ref', 'schema_version'
    ]);

    const isSpell = item.kategori === 'spell' || activeTab === 'spells';

    if (isSpell) {
      const school = sv.school || 'Universal';
      const level = sv.level !== undefined ? `Seviye ${sv.level}` : 'Seviye ?';
      const castingTime = sv.casting_time || sv.time || '1 Standard Action';
      const range = sv.range || 'Menzilli';
      const savingThrow = sv.saving_throw || sv.save || 'Yok';
      const spellResist = sv.spell_resistance || sv.sr || 'Hayır';

      return (
        <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
            <div style={{ padding: '10px 12px', background: 'rgba(124,110,247,0.1)', border: '1px solid rgba(124,110,247,0.3)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: '#a594ff', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Büyü Okulu & Seviye</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: '#d8b4fe' }}>{school} ({level})</div>
            </div>

            <div style={{ padding: '10px 12px', background: 'rgba(201,168,76,0.1)', border: '1px solid rgba(201,168,76,0.3)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Okuma Süresi</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: 'var(--gold-light)' }}>{castingTime}</div>
            </div>

            <div style={{ padding: '10px 12px', background: 'rgba(78,201,176,0.1)', border: '1px solid rgba(78,201,176,0.3)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: '#7ee787', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Menzil</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: '#a5d6a7' }}>{range}</div>
            </div>

            <div style={{ padding: '10px 12px', background: 'rgba(233,69,96,0.1)', border: '1px solid rgba(233,69,96,0.3)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: '#fca5a5', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>Kurtarma Atışı (Save)</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: '#f87171' }}>{savingThrow}</div>
            </div>
          </div>
        </div>
      );
    }

    // Clean Helper to check if a value is non-empty
    const isNotEmpty = (val) => {
      if (val === null || val === undefined) return false;
      if (typeof val === 'string') {
        const s = val.trim().toLowerCase();
        return s !== '' && s !== 'none' && s !== 'null' && s !== '[]' && s !== '{}';
      }
      if (Array.isArray(val)) return val.length > 0;
      if (typeof val === 'object') return Object.keys(val).length > 0;
      return true;
    };

    const IGNORED_KEYS = new Set([
      'description', 'name', 'system', 'aciklama', 'flags', 'data', 'img', '_id',
      'chat', 'unidentified', 'tags', 'actions', 'uses', 'per', 'maxformula',
      'autodeductchargescost', 'attacknotes', 'effectnotes', 'changes', 'changeflags',
      'losedextoac', 'noencumbrance', 'mediumarmorfullspeed', 'heavyarmorfullspeed',
      'links', 'charges', 'tag', 'usecustomtag', 'armorprof', 'weaponprof',
      'scriptcalls', 'feattype', 'associations', 'classes', 'showinquickbar',
      'abilitytype', 'croffset', 'disabled', 'classskills', 'activation',
      'unchainedaction', 'actiontype', 'ability', 'damagemult', 'critmult',
      'maxincrements', 'standard_mechanics', 'source_ref', 'schema_version',
      'data_source', 'ability_score_increase_text', 'languages_bonus',
      'weapon_proficiencies', 'armor_proficiencies', 'racial_spells', 'favored_classes', 'skill_bonuses'
    ]);

    // Normalize all keys of sv to lowercase for seamless casing support
    const normSv = {};
    Object.entries(sv).forEach(([k, v]) => {
      normSv[k.toLowerCase()] = v;
    });

    const parsedTraitsObj = parseTraitsDetailed(normSv.traits_detailed);
    const hasTraitsDetailed = isNotEmpty(parsedTraitsObj);

    const validEntries = Object.entries(normSv).filter(([k, v]) => {
      const kLower = k.toLowerCase();
      if (IGNORED_KEYS.has(kLower)) return false;
      if (kLower === 'traits' && hasTraitsDetailed) return false; // Avoid duplicating traits title array when detailed traits exist
      if (kLower === 'speed_special' && hasTraitsDetailed) return false; // Avoid repeating trait text wall in speed_special
      return isNotEmpty(v);
    });

    if (validEntries.length === 0) return null;

    const renderFieldValue = (key, val) => {
      const kLower = key.toLowerCase();

      // Ability score increase badges
      if (kLower === 'ability_score_increase') {
        let entries = [];
        if (typeof val === 'object' && !Array.isArray(val)) {
          entries = Object.entries(val).map(([st, n]) => `${n >= 0 ? '+' : ''}${n} ${st.charAt(0).toUpperCase() + st.slice(1).toLowerCase()}`);
        } else if (typeof val === 'string') {
          entries = [val];
        }
        return (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
            {entries.map((txt, i) => (
              <span key={i} style={{
                fontSize: '0.78rem', fontWeight: 'bold',
                background: 'linear-gradient(135deg, rgba(201,168,76,0.2) 0%, rgba(130,95,25,0.3) 100%)',
                color: 'var(--gold-bright)', border: '1px solid var(--border-gold)',
                padding: '3px 10px', borderRadius: '12px'
              }}>
                ⚡ {txt}
              </span>
            ))}
          </div>
        );
      }

      // Languages badges
      if (kLower === 'languages' || kLower === 'languages_automatic') {
        let list = Array.isArray(val) ? val : String(val).split(',').map(s => s.trim());
        return (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
            {list.map((lang, i) => (
              <span key={i} style={{
                fontSize: '0.75rem', background: 'rgba(124,110,247,0.15)',
                color: '#a594ff', border: '1px solid rgba(124,110,247,0.3)',
                padding: '2px 8px', borderRadius: '10px'
              }}>
                🗣️ {lang}
              </span>
            ))}
          </div>
        );
      }

      // Traits list badges (fallback when traits_detailed absent)
      if (kLower === 'traits' && Array.isArray(val)) {
        return (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
            {val.map((tr, i) => (
              <span key={i} style={{
                fontSize: '0.75rem', background: 'rgba(201,168,76,0.1)',
                color: 'var(--gold-light)', border: '1px solid rgba(201,168,76,0.2)',
                padding: '2px 8px', borderRadius: '8px'
              }}>
                ✦ {formatTitle(tr)}
              </span>
            ))}
          </div>
        );
      }

      // Traits detailed cards in a multi-column responsive grid
      if (kLower === 'traits_detailed') {
        const traitsObj = parseTraitsDetailed(val) || parsedTraitsObj;
        if (!traitsObj) return null;
        const entries = Object.entries(traitsObj);
        return (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '12px',
            marginTop: '10px',
            gridColumn: '1 / -1'
          }}>
            {entries.map(([title, desc], i) => (
              <div key={i} style={{
                background: 'linear-gradient(135deg, rgba(20,16,35,0.9) 0%, rgba(12,10,22,0.95) 100%)',
                border: '1px solid rgba(201,168,76,0.25)',
                borderLeft: '4px solid var(--gold-bright)',
                borderRadius: '8px',
                padding: '12px 14px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}>
                <div style={{
                  fontSize: '0.88rem',
                  fontFamily: 'Cinzel, serif',
                  fontWeight: 'bold',
                  color: 'var(--gold-bright)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  borderBottom: '1px dashed rgba(201,168,76,0.2)',
                  paddingBottom: '6px'
                }}>
                  <span style={{ color: 'var(--gold)', fontSize: '0.8rem' }}>✦</span>
                  {formatTitle(title)}
                </div>
                <div style={{
                  fontSize: '0.82rem',
                  color: '#f0e6d2',
                  lineHeight: '1.5',
                  fontFamily: 'Outfit, sans-serif'
                }}>
                  {toSentenceCase(cleanText(String(desc)))}
                </div>
              </div>
            ))}
          </div>
        );
      }

      // Source URL link
      if (kLower === 'source' && typeof val === 'string' && val.startsWith('http')) {
        return (
          <div style={{ marginTop: '4px' }}>
            <a href={val} target="_blank" rel="noreferrer" style={{ fontSize: '0.78rem', color: 'var(--gold-bright)', textDecoration: 'underline' }}>
              🔗 AonPRD Kaynak Sayfası ↗
            </a>
          </div>
        );
      }

      // Default string/number
      if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean') {
        return <div style={{ color: 'var(--text-main)', fontSize: '0.82rem', marginTop: '2px', lineHeight: '1.4' }}>{toSentenceCase(cleanText(String(val)))}</div>;
      }

      // Array fallback
      if (Array.isArray(val)) {
        return <div style={{ color: 'var(--text-main)', fontSize: '0.82rem', marginTop: '2px' }}>{val.join(', ')}</div>;
      }

      // Object fallback
      return <div style={{ color: 'var(--text-main)', fontSize: '0.8rem', marginTop: '2px' }}>{JSON.stringify(val)}</div>;
    };

    const FIELD_LABELS = {
      ability_score_increase: 'Yetenek Puanı Artışları',
      speed: 'Hareket Hızı',
      speed_special: 'Özel Hareket Yetenekleri',
      traits: 'Irksal Özellikler',
      traits_detailed: 'Irksal Özellik Detayları',
      languages: 'Diller',
      languages_automatic: 'Otomatik Diller',
      size: 'Boyut',
      type: 'Tür (Type)',
      subtype: 'Alt Tür (Subtype)',
      vision: 'Görüş Yeteneği',
      vision_range: 'Görüş Menzili (ft)',
      spell_resistance: 'Büyü Direnci (SR)',
      source: 'Kural Kaynağı',
      favored_class_bonus: 'Favori Sınıf Bonusu'
    };

    return (
      <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(10,8,20,0.7)', border: '1px solid rgba(201,168,76,0.25)', borderRadius: '8px' }}>
        <h4 style={{ margin: '0 0 12px 0', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '0.95rem', letterSpacing: '0.05em' }}>
          🛡️ Sistem & İstatistik Verileri
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          {validEntries.map(([key, val]) => {
            const label = FIELD_LABELS[key.toLowerCase()] || key.replace(/_/g, ' ').toUpperCase();
            const isFullWidth = key.toLowerCase() === 'traits_detailed' || key.toLowerCase() === 'speed_special';

            return (
              <div
                key={key}
                style={{
                  gridColumn: isFullWidth ? '1 / -1' : 'auto',
                  background: 'rgba(20,16,35,0.6)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  padding: '10px 12px',
                  borderRadius: '6px'
                }}
              >
                <div style={{ fontSize: '0.7rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontFamily: 'Cinzel, serif', fontWeight: 'bold' }}>
                  {label}
                </div>
                {renderFieldValue(key, val)}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto', padding: '0 16px' }}>
      
      {/* Header Banner */}
      <div className="sheet-card" style={{ marginBottom: '20px', padding: '20px 24px', background: 'linear-gradient(135deg, rgba(20,16,35,0.95) 0%, rgba(10,8,20,0.98) 100%)', border: '1px solid var(--border-gold)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ padding: '10px', background: 'rgba(201,168,76,0.1)', border: '1px solid var(--border-gold)', borderRadius: '6px' }}>
              <BookOpen size={28} style={{ color: 'var(--gold-bright)' }} />
            </div>
            <div>
              <h1 style={{ margin: 0, fontSize: '1.5rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', letterSpacing: '0.05em' }}>
                PATHFINDER 1e KURAL KÜTÜPHANESİ
              </h1>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Irklar, Sınıflar, Featler, Büyüler, Ekipmanlar ve Savaş Kurallarının Kategorize İndeksi (SRD Compendium)
              </p>
            </div>
          </div>
          {onBack && (
            <button className="gold-btn" onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', fontSize: '0.8rem' }}>
              <ArrowLeft size={14} /> Karakterlerime Dön
            </button>
          )}
        </div>
      </div>

      {/* Category Tabs */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '20px' }}>
        {CATEGORIES.map(cat => {
          const Icon = cat.icon;
          const isActive = activeTab === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => {
                setActiveTab(cat.id);
                setSubFilter('');
                setSpellLevel('');
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: '6px',
                whiteSpace: 'nowrap',
                fontFamily: 'Cinzel, serif',
                fontSize: '0.82rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                background: isActive ? 'linear-gradient(180deg, rgba(201,168,76,0.25) 0%, rgba(130,95,25,0.3) 100%)' : 'rgba(15,12,28,0.7)',
                border: isActive ? '1px solid var(--gold-bright)' : '1px solid rgba(251,219,129,0.15)',
                color: isActive ? 'var(--gold-bright)' : 'var(--text-muted)',
                boxShadow: isActive ? '0 0 12px rgba(201,168,76,0.2)' : 'none'
              }}
            >
              <Icon size={16} />
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Filters Bar */}
      <div className="sheet-card" style={{ padding: '14px 18px', marginBottom: '20px', display: 'flex', flexWrap: 'wrap', gap: '14px', alignItems: 'center' }}>
        
        {/* Search Input */}
        <div style={{ flex: '1 1 240px', position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--gold-light)' }} />
          <input
            type="text"
            className="sheet-input"
            placeholder={`${CATEGORIES.find(c => c.id === activeTab)?.label} içinde ara...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ paddingLeft: '36px', width: '100%', fontSize: '0.85rem' }}
          />
        </div>

      {/* Subcategory Pills Bar (Replaces Dropdown Selects) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
        {activeTab === 'spells' && (
          <>
            {/* Spell Levels Pills */}
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', alignItems: 'center' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--gold-pale)', fontFamily: 'Cinzel, serif', fontWeight: 'bold', whiteSpace: 'nowrap', marginRight: '4px' }}>Seviye:</span>
              <button
                onClick={() => setSpellLevel('')}
                style={{
                  padding: '4px 12px', borderRadius: '12px', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                  background: spellLevel === '' ? 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)' : 'rgba(15,12,28,0.7)',
                  border: spellLevel === '' ? '1px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.2)',
                  color: spellLevel === '' ? 'var(--gold-bright)' : 'var(--text-muted)'
                }}>Tüm Seviyeler</button>
              {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(lvl => (
                <button key={lvl} onClick={() => setSpellLevel(String(lvl))}
                  style={{
                    padding: '4px 10px', borderRadius: '12px', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                    background: spellLevel === String(lvl) ? 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)' : 'rgba(15,12,28,0.7)',
                    border: spellLevel === String(lvl) ? '1px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.2)',
                    color: spellLevel === String(lvl) ? 'var(--gold-bright)' : 'var(--text-muted)'
                  }}>Lvl {lvl}</button>
              ))}
            </div>

            {/* Spell Schools Pills */}
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', alignItems: 'center' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--gold-pale)', fontFamily: 'Cinzel, serif', fontWeight: 'bold', whiteSpace: 'nowrap', marginRight: '4px' }}>Okul:</span>
              {['', 'Abjuration', 'Conjuration', 'Divination', 'Enchantment', 'Evocation', 'Illusion', 'Necromancy', 'Transmutation'].map(sch => (
                <button key={sch} onClick={() => setSubFilter(sch)}
                  style={{
                    padding: '4px 12px', borderRadius: '12px', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                    background: subFilter === sch ? 'linear-gradient(135deg, rgba(78,201,176,0.25) 0%, rgba(30,100,90,0.35) 100%)' : 'rgba(15,12,28,0.7)',
                    border: subFilter === sch ? '1px solid #4ec9b0' : '1px solid rgba(78,201,176,0.2)',
                    color: subFilter === sch ? '#7ee787' : 'var(--text-muted)'
                  }}>{sch || 'Tüm Okullar'}</button>
              ))}
            </div>
          </>
        )}

        {activeTab === 'equipment' && (
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', alignItems: 'center' }}>
            {EQUIPMENT_CATEGORIES.map(cat => (
              <button key={cat.id} onClick={() => setSubFilter(cat.id)}
                style={{
                  padding: '5px 14px', borderRadius: '12px', fontSize: '0.78rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                  background: (subFilter === cat.id || (!subFilter && cat.id === 'all')) ? 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)' : 'rgba(15,12,28,0.7)',
                  border: (subFilter === cat.id || (!subFilter && cat.id === 'all')) ? '1px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.2)',
                  color: (subFilter === cat.id || (!subFilter && cat.id === 'all')) ? 'var(--gold-bright)' : 'var(--text-muted)'
                }}>{cat.label}</button>
            ))}
          </div>
        )}

        {activeTab === 'feats' && (
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', alignItems: 'center' }}>
            {['', 'Combat', 'Metamagic', 'Teamwork', 'Item Creation', 'Racial', 'General', 'Mythic', 'Style', 'Critical'].map(fCat => (
              <button key={fCat} onClick={() => setSubFilter(fCat)}
                style={{
                  padding: '5px 14px', borderRadius: '12px', fontSize: '0.78rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                  background: subFilter === fCat ? 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)' : 'rgba(15,12,28,0.7)',
                  border: subFilter === fCat ? '1px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.2)',
                  color: subFilter === fCat ? 'var(--gold-bright)' : 'var(--text-muted)'
                }}>{fCat ? fCat : 'Tüm Featler'}</button>
            ))}
          </div>
        )}

        {activeTab === 'traits' && (
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', alignItems: 'center' }}>
            {['', 'Combat', 'Social', 'Faith', 'Magic', 'Racial', 'Regional', 'Campaign', 'Equipment'].map(tCat => (
              <button key={tCat} onClick={() => setSubFilter(tCat)}
                style={{
                  padding: '5px 14px', borderRadius: '12px', fontSize: '0.78rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                  background: subFilter === tCat ? 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)' : 'rgba(15,12,28,0.7)',
                  border: subFilter === tCat ? '1px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.2)',
                  color: subFilter === tCat ? 'var(--gold-bright)' : 'var(--text-muted)'
                }}>{tCat ? tCat : 'Tüm Traitler'}</button>
            ))}
          </div>
        )}

        {activeTab === 'class-features' && (
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', alignItems: 'center' }}>
            {['', 'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Wizard', 'Alchemist', 'Inquisitor', 'Magus', 'Oracle', 'Summoner', 'Witch'].map(cls => (
              <button key={cls} onClick={() => setSubFilter(cls)}
                style={{
                  padding: '5px 14px', borderRadius: '12px', fontSize: '0.78rem', fontFamily: 'Cinzel, serif', cursor: 'pointer', whiteSpace: 'nowrap',
                  background: subFilter === cls ? 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)' : 'rgba(15,12,28,0.7)',
                  border: subFilter === cls ? '1px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.2)',
                  color: subFilter === cls ? 'var(--gold-bright)' : 'var(--text-muted)'
                }}>{cls ? cls : 'Tüm Sınıflar'}</button>
            ))}
          </div>
        )}
      </div>


      </div>

      {/* Main Grid */}
      {loading ? (
        <div className="sheet-card" style={{ padding: '60px', textAlign: 'center', color: 'var(--gold-light)' }}>
          <Sparkles className="spin" size={32} style={{ marginBottom: '12px' }} />
          <p style={{ fontFamily: 'Cinzel, serif', fontSize: '1rem', margin: '0 0 6px 0' }}>Kural Kütüphanesi Yükleniyor...</p>
          {coldStartMsg && (
            <p style={{ fontSize: '0.82rem', color: '#ffd700', fontFamily: 'Inter, sans-serif', margin: 0 }}>
              {coldStartMsg}
            </p>
          )}
        </div>
      ) : sortedEntities.length === 0 ? (
        <div className="sheet-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <Info size={32} style={{ color: 'var(--border-gold)', marginBottom: '8px' }} />
          <p>Aradığınız kritere uygun kural varlığı bulunamadı.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px', marginBottom: '30px' }}>
          {sortedEntities.map((item, idx) => (
            <div
              key={idx}
              className="sheet-card hover-glow"
              onClick={() => setSelectedEntity(item)}
              style={{
                padding: '16px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justify: 'space-between',
                transition: 'all 0.2s ease',
                border: '1px solid rgba(201,168,76,0.2)'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <h3 style={{ margin: 0, fontSize: '1.05rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)' }}>
                    {item.isim}
                  </h3>
                  <ChevronRight size={16} style={{ color: 'var(--gold-bright)', opacity: 0.7 }} />
                </div>

                {renderEntityBadges(item)}

                <p style={{
                  fontSize: '0.82rem',
                  color: 'var(--text-muted)',
                  marginTop: '10px',
                  lineHeight: '1.4',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {(() => {
                    const rawText = item.aciklama || item.description || (item.sistem_verisi?.description);
                    const cleaned = cleanText(rawText);
                    if (cleaned && cleaned.toLowerCase() !== 'contents' && !cleaned.toLowerCase().startsWith('subpages')) {
                      return cleaned;
                    }
                    return `${item.isim || item.name} sınıfı Pathfinder 1e temel kural ve yetenek şablonu.`;
                  })()}
                </p>
              </div>

              <div style={{ marginTop: '12px', paddingTop: '8px', borderTop: '1px dashed rgba(201,168,76,0.15)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--gold-pale)' }}>
                  Detayları İncele
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--border-gold)', textTransform: 'uppercase' }}>
                  PF1e SRD
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detailed Modal */}
      {selectedEntity && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(5, 4, 10, 0.85)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justify: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div className="sheet-card" style={{
            maxWidth: '680px',
            width: '100%',
            maxHeight: '85vh',
            overflowY: 'auto',
            padding: '24px',
            position: 'relative',
            border: '1px solid var(--gold-bright)',
            boxShadow: '0 0 30px rgba(0,0,0,0.9), 0 0 15px rgba(201,168,76,0.2)'
          }}>
            <button
              onClick={() => setSelectedEntity(null)}
              style={{
                position: 'absolute', top: '16px', right: '16px',
                background: 'none', border: 'none', color: 'var(--gold-light)',
                cursor: 'pointer'
              }}
            >
              <X size={20} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <BookOpen size={22} style={{ color: 'var(--gold-bright)' }} />
              <h2 style={{ margin: 0, fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '1.35rem' }}>
                {selectedEntity.isim}
              </h2>
            </div>

            {renderEntityBadges(selectedEntity)}

            <hr style={{ borderColor: 'rgba(201,168,76,0.2)', margin: '16px 0' }} />

            {!(activeTab === 'classes' || selectedEntity.kategori === 'class' || selectedEntity.kategori === 'archetype') && (
              <div style={{ fontSize: '0.9rem', lineHeight: '1.65', color: 'var(--text-main)', whiteSpace: 'pre-line', fontFamily: 'var(--font-body)', wordBreak: 'break-word' }}>
                {cleanText(selectedEntity.aciklama) || `${selectedEntity.isim} kural detayları ve yetenek bilgisi.`}
              </div>
            )}

            {renderDetailContent(selectedEntity)}

            <div style={{ marginTop: '24px', textAlign: 'right' }}>
              <button className="gold-btn" onClick={() => setSelectedEntity(null)} style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
                Kapat
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
