import React, { useState } from 'react';
import { X, Sparkles, Zap, Search } from 'lucide-react';
import { useCharacterStore } from '../store/characterStore';

const ALL_CLASS_PRESETS = [
  {
    id: 'barbarian_amiri',
    name: 'Amiri',
    title: 'İkonik Barbar (Iconic Barbarian)',
    race: 'Human',
    class: 'Barbarian',
    gender: 'Female',
    age: '24',
    alignment: 'Chaotic Good',
    deity: 'Gorum',
    avatar: '🪓',
    description: 'Devasa kılıcı ve durdurulamaz öfkesiyle ön safları darmadağın eden kuzeyli barbar.',
    abilities: { strength: 17, dexterity: 13, constitution: 14, intelligence: 10, wisdom: 12, charisma: 8 },
    skills: { Athletics: 1, Perception: 1, Survival: 1, Intimidate: 1 },
    feats: [{ isim: 'Power Attack', sistem_verisi: {} }, { isim: 'Toughness', sistem_verisi: {} }],
    traits: [{ isim: 'Armor Expert', sistem_verisi: {} }, { isim: 'Reactionary', sistem_verisi: {} }],
    equipment: [{ name: 'Bastard Sword', category: 'weapon' }, { name: 'Hide Armor', category: 'armor' }, { name: 'Explorer\'s Outfit', category: 'gear' }],
    spells: [],
    backstory: 'Kuzeyin Altı Krallığı klanından sürgün edilen Amiri, dev kılıcıyla kendi efsanesini yazmak için diyarları gezer.',
    personality: 'Öfkeli, gururlu, savaşta acımasız ama klan geleneklerine saygılı.'
  },
  {
    id: 'bard_lem',
    name: 'Lem',
    title: 'İkonik Ozan (Iconic Bard)',
    race: 'Halfling',
    class: 'Bard',
    gender: 'Male',
    age: '28',
    alignment: 'Chaotic Good',
    deity: 'Desna',
    avatar: '🪕',
    description: 'Ezgi ve şiirleriyle yoldaşlarına cesaret veren, kıvrak zekalı buçukluk ozan.',
    abilities: { strength: 8, dexterity: 16, constitution: 12, intelligence: 14, wisdom: 10, charisma: 16 },
    skills: { Perform: 1, Stealth: 1, Acrobatics: 1, Diplomacy: 1, Perception: 1 },
    feats: [{ isim: 'Extra Performance', sistem_verisi: {} }, { isim: 'Weapon Finesse', sistem_verisi: {} }],
    traits: [{ isim: 'Savvy Merchant', sistem_verisi: {} }],
    equipment: [{ name: 'Shortsword', category: 'weapon' }, { name: 'Light Crossbow', category: 'weapon' }, { name: 'Leather Armor', category: 'armor' }, { name: 'Flute', category: 'gear' }],
    spells: [{ isim: 'Cure Light Wounds', level: 1 }, { isim: 'Disguise Self', level: 1 }, { isim: 'Daze', level: 0 }, { isim: 'Light', level: 0 }],
    backstory: 'Koleksiyoncu bir efendiden kaçıp özgürlüğüne kavuşan Lem, müziğiyle dünyayı renklendirmek ister.',
    personality: 'Neşeli, esprili, arkadaşlarına bağlı ve tehlikede şarkı söylemekten çekinmeyen bir ozan.'
  },
  {
    id: 'cleric_kyra',
    name: 'Kyra',
    title: 'İkonik Rahip (Iconic Cleric of Sarenrae)',
    race: 'Human',
    class: 'Cleric',
    gender: 'Female',
    age: '26',
    alignment: 'Neutral Good',
    deity: 'Sarenrae',
    avatar: '☀️',
    description: 'Güneş Tanrıçası Sarenrae\'nin kutsal ışığı ve pala kılıcıyla yaraları saran aziz rahip.',
    abilities: { strength: 14, dexterity: 10, constitution: 12, intelligence: 10, wisdom: 16, charisma: 14 },
    skills: { Heal: 1, KnowledgeReligion: 1, Diplomacy: 1, SenseMotive: 1 },
    feats: [{ isim: 'Selective Channeling', sistem_verisi: {} }, { isim: 'Extra Channel', sistem_verisi: {} }],
    traits: [{ isim: 'Sacred Conduit', sistem_verisi: {} }],
    equipment: [{ name: 'Scimitar', category: 'weapon' }, { name: 'Chain Shirt', category: 'armor' }, { name: 'Wooden Shield', category: 'armor' }],
    spells: [{ isim: 'Cure Light Wounds', level: 1 }, { isim: 'Bless', level: 1 }, { isim: 'Shield of Faith', level: 1 }, { isim: 'Guidance', level: 0 }],
    backstory: 'Köyü haramilerce yakıldığında Sarenrae rahipleri tarafından kurtarılan Kyra, masumları korumaya adandı.',
    personality: 'Şefkatli, bağışlayıcı ama kötülük karşısında tavizsiz.'
  },
  {
    id: 'druid_lini',
    name: 'Lini',
    title: 'İkonik Druid (Iconic Druid)',
    race: 'Gnome',
    class: 'Druid',
    gender: 'Female',
    age: '42',
    alignment: 'Neutral Good',
    deity: 'Gozreh',
    avatar: '🌿',
    description: 'Kar leoparı yoldaşı Droogami ile doğanın dengesini koruyan cüce druid.',
    abilities: { strength: 8, dexterity: 14, constitution: 14, intelligence: 12, wisdom: 17, charisma: 12 },
    skills: { Nature: 1, HandleAnimal: 1, Perception: 1, Survival: 1 },
    feats: [{ isim: 'Self-Sufficient', sistem_verisi: {} }],
    traits: [{ isim: 'Green Thumb', sistem_verisi: {} }],
    equipment: [{ name: 'Sickle', category: 'weapon' }, { name: 'Sling', category: 'weapon' }, { name: 'Hide Armor', category: 'armor' }, { name: 'Holly and Mistletoe', category: 'gear' }],
    spells: [{ isim: 'Entangle', level: 1 }, { isim: 'Produce Flame', level: 1 }, { isim: 'Detect Magic', level: 0 }],
    companion: { name: 'Droogami', type: 'Animal Companion (Snow Leopard)', hp: 12, ac: 15, str: 13, dex: 17, con: 13 },
    backstory: 'Doğanın vahşi ormanlarında büyüyen Lini, canlıların kemik koleksiyonunu saklar.',
    personality: 'Meraklı, hayvanlara sevecen, tehdit anında doğanın gazabını yağdıran bir koruyucu.'
  },
  {
    id: 'fighter_valeros',
    name: 'Valeros',
    title: 'İkonik Savaşçı (Iconic Fighter)',
    race: 'Human',
    class: 'Fighter',
    gender: 'Male',
    age: '29',
    alignment: 'Neutral Good',
    deity: 'Cayden Cailean',
    avatar: '⚔️',
    description: 'Ön saflarda çift kılıç ve kalkanla dövüşen ustalaşmış efsanevi savaşçı.',
    abilities: { strength: 16, dexterity: 14, constitution: 14, intelligence: 10, wisdom: 12, charisma: 10 },
    skills: { Athletics: 1, Intimidate: 1, Perception: 1 },
    feats: [{ isim: 'Power Attack', sistem_verisi: {} }, { isim: 'Weapon Focus', sistem_verisi: { weapon: 'Longsword' } }, { isim: 'Toughness', sistem_verisi: {} }],
    traits: [{ isim: 'Armor Expert', sistem_verisi: {} }, { isim: 'Reactionary', sistem_verisi: {} }],
    equipment: [{ name: 'Longsword', category: 'weapon' }, { name: 'Heavy Steel Shield', category: 'armor' }, { name: 'Chainmail', category: 'armor' }],
    spells: [],
    backstory: 'Andoran kırsalında büyüyen Valeros, çiftçilik yerine paralı askerliği ve maceracılığı seçti.',
    personality: 'Neşeli, kadeh kaldırmayı seven, dostları için kendini tehlikeye atan savaşçı.'
  },
  {
    id: 'monk_sajan',
    name: 'Sajan',
    title: 'İkonik Keşiş (Iconic Monk)',
    race: 'Human',
    class: 'Monk',
    gender: 'Male',
    age: '25',
    alignment: 'Lawful Good',
    deity: 'Irori',
    avatar: '🥋',
    description: 'Yalınayak vuruşları ve Flurry of Blows stiliyle düşmanlarını alt eden keşiş.',
    abilities: { strength: 15, dexterity: 15, constitution: 12, intelligence: 10, wisdom: 14, charisma: 8 },
    skills: { Acrobatics: 1, Athletics: 1, Perception: 1, SenseMotive: 1 },
    feats: [{ isim: 'Dodge', sistem_verisi: {} }, { isim: 'Deflect Arrows', sistem_verisi: {} }, { isim: 'Combat Reflexes', sistem_verisi: {} }],
    traits: [{ isim: 'Ascetic Discipline', sistem_verisi: {} }],
    equipment: [{ name: 'Temple Sword', category: 'weapon' }, { name: 'Shuriken', category: 'weapon' }, { name: 'Monk\'s Robes', category: 'gear' }],
    spells: [],
    backstory: 'Kayıp kız kardeşini aramak için Padishah İmparatorluğundan yola çıkan kararlı disiplin ustası.',
    personality: 'Sakin, zihnini ve bedenini sürekli eğiten, adalet sever.'
  },
  {
    id: 'paladin_seelah',
    name: 'Seelah',
    title: 'İkonik Şövalye (Iconic Paladin of Iomedae)',
    race: 'Human',
    class: 'Paladin',
    gender: 'Female',
    age: '27',
    alignment: 'Lawful Good',
    deity: 'Iomedae',
    avatar: '🛡️',
    description: 'Adalet meşalesi, Smite Evil ve ağır zırhıyla kötülüğü yıkan kutsal şövalye.',
    abilities: { strength: 16, dexterity: 10, constitution: 14, intelligence: 10, wisdom: 12, charisma: 15 },
    skills: { Diplomacy: 1, Heal: 1, KnowledgeReligion: 1 },
    feats: [{ isim: 'Power Attack', sistem_verisi: {} }, { isim: 'Weapon Focus', sistem_verisi: { weapon: 'Longsword' } }],
    traits: [{ isim: 'Indomitable Faith', sistem_verisi: {} }],
    equipment: [{ name: 'Longsword', category: 'weapon' }, { name: 'Heavy Shield', category: 'armor' }, { name: 'Scale Mail', category: 'armor' }],
    spells: [],
    backstory: 'Gençliğinde çaldığı bir miğfer yüzünden bir şövalyenin ölümüne sebep olan Seelah, Iomedae yeminiyle vicdanını arındırır.',
    personality: 'Cesur, masumları koruyan, samimi ve sarsılmaz inançlı.'
  },
  {
    id: 'ranger_harsk',
    name: 'Harsk',
    title: 'İkonik Korucu (Iconic Ranger)',
    race: 'Dwarf',
    class: 'Ranger',
    gender: 'Male',
    age: '110',
    alignment: 'Lawful Good',
    deity: 'Torag',
    avatar: '🏹',
    description: 'Ağır taretiyle uzak mesafeden düşman avlayan, iz sürme ustası cüce korucu.',
    abilities: { strength: 14, dexterity: 15, constitution: 16, intelligence: 10, wisdom: 14, charisma: 6 },
    skills: { Perception: 1, Survival: 1, Stealth: 1, KnowledgeNature: 1 },
    feats: [{ isim: 'Point-Blank Shot', sistem_verisi: {} }],
    traits: [{ isim: 'Highlander', sistem_verisi: {} }],
    equipment: [{ name: 'Heavy Crossbow', category: 'weapon' }, { name: 'Battleaxe', category: 'weapon' }, { name: 'Studded Leather', category: 'armor' }],
    spells: [],
    backstory: 'Kardeşi devler tarafından katledilen Harsk, dağlarda iz sürerek dev avına adanmıştır.',
    personality: 'Sert, çay içmeyi seven, az konuşan ve hedefinden şaşmayan.'
  },
  {
    id: 'rogue_merisiel',
    name: 'Merisiel',
    title: 'İkonik Hırsız (Iconic Rogue)',
    race: 'Elf',
    class: 'Rogue',
    gender: 'Female',
    age: '120',
    alignment: 'Chaotic Good',
    deity: 'Calistria',
    avatar: '🗡️',
    description: 'Gölgelerden sıyrılıp Gizli Saldırı (Sneak Attack) yapan çevik elf hırsız.',
    abilities: { strength: 12, dexterity: 18, constitution: 12, intelligence: 12, wisdom: 10, charisma: 10 },
    skills: { Stealth: 1, Acrobatics: 1, Thievery: 1, Perception: 1, SleightOfHand: 1 },
    feats: [{ isim: 'Weapon Finesse', sistem_verisi: {} }, { isim: 'Dodge', sistem_verisi: {} }],
    traits: [{ isim: 'River Rat', sistem_verisi: {} }],
    equipment: [{ name: 'Rapier', category: 'weapon' }, { name: 'Dagger', category: 'weapon' }, { name: 'Leather Armor', category: 'armor' }, { name: 'Thieves\' Tools', category: 'gear' }],
    spells: [],
    backstory: 'İnsan kentlerinin sokaklarında yetim büyüyen Merisiel, özgürlüğüne aşık bir maceracıdır.',
    personality: 'Eğlenceli, tehlikeye gözü kapalı giren, hızlı yaşayan bir hırsız.'
  },
  {
    id: 'sorcerer_seoni',
    name: 'Seoni',
    title: 'İkonik Büyücü (Iconic Sorcerer)',
    race: 'Human',
    class: 'Sorcerer',
    gender: 'Female',
    age: '26',
    alignment: 'Neutral Good',
    deity: 'Pharasma',
    avatar: '🔮',
    description: 'Ejderha kanı ve dövmelerinden güç alan yüksek karizmalı doğuştan büyücü.',
    abilities: { strength: 10, dexterity: 14, constitution: 12, intelligence: 10, wisdom: 10, charisma: 18 },
    skills: { KnowledgeArcana: 1, Spellcraft: 1, Concentration: 1 },
    feats: [{ isim: 'Spell Focus', sistem_verisi: { school: 'Evocation' } }, { isim: 'Combat Casting', sistem_verisi: {} }],
    traits: [{ isim: 'Focused Mind', sistem_verisi: {} }],
    equipment: [{ name: 'Quarterstaff', category: 'weapon' }, { name: 'Spell Component Pouch', category: 'gear' }],
    spells: [{ isim: 'Magic Missile', level: 1 }, { isim: 'Shield', level: 1 }, { isim: 'Mage Hand', level: 0 }, { isim: 'Daze', level: 0 }],
    backstory: 'Varisian dövmeleriyle kaplı bedeninde saklı ejderha soyunun büyülü gücünü keşfetmiştir.',
    personality: 'Ciddi, planlı, lider ruhlu ve büyülü enerjileri titizlikle yönlendiren.'
  },
  {
    id: 'wizard_ezren',
    name: 'Ezren',
    title: 'İkonik Bilgin Büyücü (Iconic Wizard)',
    race: 'Human',
    class: 'Wizard',
    gender: 'Male',
    age: '55',
    alignment: 'Neutral Good',
    deity: 'Nethys',
    avatar: '📜',
    description: 'Yaşlılığında büyü sanatına başlayıp kütüphaneleri yutan Evocation büyücüsü.',
    abilities: { strength: 10, dexterity: 12, constitution: 13, intelligence: 18, wisdom: 12, charisma: 10 },
    skills: { KnowledgeArcana: 1, KnowledgeHistory: 1, Spellcraft: 1, Research: 1 },
    feats: [{ isim: 'Scribe Scroll', sistem_verisi: {} }, { isim: 'Spell Focus', sistem_verisi: { school: 'Evocation' } }, { isim: 'Improved Initiative', sistem_verisi: {} }],
    traits: [{ isim: 'Mathematical Prodigy', sistem_verisi: {} }],
    equipment: [{ name: 'Dagger', category: 'weapon' }, { name: 'Spellbook', category: 'gear' }, { name: 'Scholar\'s Outfit', category: 'gear' }],
    spells: [{ isim: 'Magic Missile', level: 1 }, { isim: 'Color Spray', level: 1 }, { isim: 'Grease', level: 1 }, { isim: 'Detect Magic', level: 0 }],
    companion: { name: 'Arcane Familiar', type: 'Owl Familiar', hp: 4, ac: 15, str: 3, dex: 15, con: 10 },
    backstory: 'Babasının adını temize çıkarmak için yaşlılığında akademiye giren bilgin.',
    personality: 'Sabırlı, meraklı, bilgelik arayan ve genç maceracılara rehberlik eden.'
  },
  {
    id: 'alchemist_damiel',
    name: 'Damiel',
    title: 'İkonik Simyacı (Iconic Alchemist)',
    race: 'Elf',
    class: 'Alchemist',
    gender: 'Male',
    age: '135',
    alignment: 'Neutral',
    deity: 'Norgorber',
    avatar: '🧪',
    description: 'Patlayıcı iksir bombaları ve dönüştürücü Mutagen sıvılarıyla savaşan simyacı.',
    abilities: { strength: 10, dexterity: 16, constitution: 12, intelligence: 17, wisdom: 10, charisma: 8 },
    skills: { CraftAlchemy: 1, Heal: 1, KnowledgeArcana: 1, Perception: 1 },
    feats: [{ isim: 'Brew Potion', sistem_verisi: {} }, { isim: 'Throw Anything', sistem_verisi: {} }],
    traits: [{ isim: 'Chemical Revolutionary', sistem_verisi: {} }],
    equipment: [{ name: 'Light Crossbow', category: 'weapon' }, { name: 'Dagger', category: 'weapon' }, { name: 'Formula Book', category: 'gear' }, { name: 'Alchemy Kit', category: 'gear' }],
    spells: [{ isim: 'Cure Light Wounds', level: 1 }, { isim: 'True Strike', level: 1 }, { isim: 'Shield', level: 1 }],
    backstory: 'Yasak maddeler ve iksir deneyleri yüzünden loncasından atılan dahi simyacı.',
    personality: 'Hesapçı, analitik zekaya sahip ve kimyasal reaksiyonlara tutkulu.'
  },
  {
    id: 'cavalier_alain',
    name: 'Alain',
    title: 'İkonik Süvari (Iconic Cavalier)',
    race: 'Human',
    class: 'Cavalier',
    gender: 'Male',
    age: '26',
    alignment: 'Neutral',
    deity: 'Abadar',
    avatar: '🐎',
    description: 'Mızrağı ve savaş atıyla hücuma kalkan Kılıç Tarikatı soylu süvarisi.',
    abilities: { strength: 16, dexterity: 12, constitution: 14, intelligence: 10, wisdom: 8, charisma: 14 },
    skills: { Athletics: 1, Diplomacy: 1, HandleAnimal: 1, Intimidate: 1 },
    feats: [{ isim: 'Mounted Combat', sistem_verisi: {} }, { isim: 'Ride-By Attack', sistem_verisi: {} }],
    traits: [{ isim: 'Noble Born', sistem_verisi: {} }],
    equipment: [{ name: 'Lance', category: 'weapon' }, { name: 'Longsword', category: 'weapon' }, { name: 'Chainmail', category: 'armor' }, { name: 'Heavy Shield', category: 'armor' }],
    spells: [],
    companion: { name: 'Honor', type: 'Heavy Warhorse Mount', hp: 19, ac: 16, str: 18, dex: 13, con: 15 },
    backstory: 'Soylu ailesinin mirasını geri almak için şövalyelik yemini eden gururlu savaşçı.',
    personality: 'Kibirli, onuruna düşkün ama sözünün eri ve bineğine gözü gibi bakan.'
  },
  {
    id: 'inquisitor_imrijka',
    name: 'Imrijka',
    title: 'İkonik Engizisyoncu (Iconic Inquisitor)',
    race: 'Half-Orc',
    class: 'Inquisitor',
    gender: 'Female',
    age: '23',
    alignment: 'Chaotic Good',
    deity: 'Pharasma',
    avatar: '⚖️',
    description: 'Hüküm (Judgment) yeteneği ve ağır arbaletiyle sapkınları avlayan melez engizisyoncu.',
    abilities: { strength: 15, dexterity: 14, constitution: 12, intelligence: 10, wisdom: 15, charisma: 8 },
    skills: { Intimidate: 1, Perception: 1, SenseMotive: 1, Survival: 1 },
    feats: [{ isim: 'Exotic Weapon Proficiency', sistem_verisi: { weapon: 'Repeating Crossbow' } }],
    traits: [{ isim: 'Inquisitive Mind', sistem_verisi: {} }],
    equipment: [{ name: 'Heavy Crossbow', category: 'weapon' }, { name: 'Greatsword', category: 'weapon' }, { name: 'Breastplate', category: 'armor' }],
    spells: [{ isim: 'Bane', level: 1 }, { isim: 'Divine Favor', level: 1 }, { isim: 'Detect Magic', level: 0 }],
    backstory: 'Pharasma kilisesi yetimhanesinde büyüyüp ölüm tanrıçasının yargıcı olan yarı-ork.',
    personality: 'Sorgulayan, şüpheci, gerçeklerin peşinden amansızca koşan.'
  },
  {
    id: 'magus_seltyiel',
    name: 'Seltyiel',
    title: 'İkonik Büyü Savaşçısı (Iconic Magus)',
    race: 'Half-Elf',
    class: 'Magus',
    gender: 'Male',
    age: '28',
    alignment: 'Lawful Evil',
    deity: 'Asmodeus',
    avatar: '⚔️🔮',
    description: 'Tek elinde kılıç diğer elinde elektrikli büyülerle Spell Combat dövüş stili uygulayan magus.',
    abilities: { strength: 14, dexterity: 14, constitution: 12, intelligence: 16, wisdom: 10, charisma: 10 },
    skills: { KnowledgeArcana: 1, Spellcraft: 1, Athletics: 1 },
    feats: [{ isim: 'Weapon Focus', sistem_verisi: { weapon: 'Longsword' } }],
    traits: [{ isim: 'Spell-Scarred', sistem_verisi: {} }],
    equipment: [{ name: 'Longsword', category: 'weapon' }, { name: 'Leather Armor', category: 'armor' }, { name: 'Spellbook', category: 'gear' }],
    spells: [{ isim: 'Shocking Grasp', level: 1 }, { isim: 'Shield', level: 1 }, { isim: 'Ray of Frost', level: 0 }],
    backstory: 'Üvey babasının ihanetine uğrayıp gücün ve büyünün birleştiği kılıç yolunu seçen melez elf.',
    personality: 'Hırslı, soğukkanlı, güce saygı duyan ve rakiplerini küçümseyen.'
  },
  {
    id: 'oracle_alahazra',
    name: 'Alahazra',
    title: 'İkonik Kahin (Iconic Oracle)',
    race: 'Human',
    class: 'Oracle',
    gender: 'Female',
    age: '45',
    alignment: 'Neutral Good',
    deity: 'Sarenrae',
    avatar: '👁️',
    description: 'Alev Gizemi ve Göz Lanetiyle (Clouded Vision) kaderin ve kehanetlerin sesini duyan kahin.',
    abilities: { strength: 10, dexterity: 12, constitution: 14, intelligence: 10, wisdom: 12, charisma: 17 },
    skills: { Diplomacy: 1, Heal: 1, KnowledgeHistory: 1, SenseMotive: 1 },
    feats: [{ isim: 'Extra Revelation', sistem_verisi: {} }],
    traits: [{ isim: 'Sight Beyond Sight', sistem_verisi: {} }],
    equipment: [{ name: 'Quarterstaff', category: 'weapon' }, { name: 'Leather Armor', category: 'armor' }],
    spells: [{ isim: 'Burning Hands', level: 1 }, { isim: 'Cure Light Wounds', level: 1 }, { isim: 'Guidance', level: 0 }],
    backstory: 'Görüşünü kurban ederek tanrıların kehanetlerini görme yetisi kazanan çöl kahini.',
    personality: 'Gizemli, kehanet dolu sözler söyleyen ve kaderin akışına inanan.'
  },
  {
    id: 'summoner_balazar',
    name: 'Balazar',
    title: 'İkonik Çağırıcı (Iconic Summoner)',
    race: 'Gnome',
    class: 'Summoner',
    gender: 'Male',
    age: '38',
    alignment: 'Neutral',
    deity: 'Nethys',
    avatar: '👹',
    description: 'Öteki düzlemden çağırdığı gölge yaratığı Pazio (Eidolon) ile savaşan cüce çağırıcı.',
    abilities: { strength: 8, dexterity: 14, constitution: 14, intelligence: 12, wisdom: 10, charisma: 17 },
    skills: { KnowledgePlanes: 1, Spellcraft: 1, UseMagicDevice: 1 },
    feats: [{ isim: 'Augment Summoning', sistem_verisi: {} }],
    traits: [{ isim: 'Planar Traveler', sistem_verisi: {} }],
    equipment: [{ name: 'Light Crossbow', category: 'weapon' }, { name: 'Dagger', category: 'weapon' }, { name: 'Leather Armor', category: 'armor' }],
    spells: [{ isim: 'Summon Monster I', level: 1 }, { isim: 'Mage Armor', level: 1 }, { isim: 'Daze', level: 0 }],
    companion: { name: 'Pazio', type: 'Eidolon (Bipedal Shadow Creature)', hp: 11, ac: 15, str: 16, dex: 12, con: 13 },
    backstory: 'Rüyalar düzleminden çağırdığı canavarla dostluk kuran meraklı cüce büyücü.',
    personality: 'Çılgın, yaratığına tutkuyla bağlı ve düzlemler arası portal araştırmacısı.'
  },
  {
    id: 'witch_feiya',
    name: 'Feiya',
    title: 'İkonik Cadı (Iconic Witch)',
    race: 'Human',
    class: 'Witch',
    gender: 'Female',
    age: '22',
    alignment: 'Neutral Good',
    deity: 'Pharasma',
    avatar: '🧹',
    description: 'Lanet Hex yetenekleri ve Siyah Kedi tanıdığı Djael ile düşmanlarını bağlayan cadı.',
    abilities: { strength: 8, dexterity: 14, constitution: 12, intelligence: 18, wisdom: 12, charisma: 10 },
    skills: { KnowledgeArcana: 1, KnowledgeNature: 1, Spellcraft: 1, UseMagicDevice: 1 },
    feats: [{ isim: 'Extra Hex', sistem_verisi: {} }, { isim: 'Improved Initiative', sistem_verisi: {} }],
    traits: [{ isim: 'Hex Crafter', sistem_verisi: {} }],
    equipment: [{ name: 'Dagger', category: 'weapon' }, { name: 'Quarterstaff', category: 'weapon' }, { name: 'Witch\'s Robes', category: 'gear' }],
    spells: [{ isim: 'Sleep', level: 1 }, { isim: 'Command', level: 1 }, { isim: 'Evil Eye Hex', level: 0 }, { isim: 'Slumber Hex', level: 0 }],
    companion: { name: 'Djael', type: 'Black Cat Familiar', hp: 4, ac: 14, str: 3, dex: 15, con: 10 },
    backstory: 'Bir Baba Yaga cadısı tarafından kaçırılıp ormanda vahşi büyüyü öğrenen genç kadın.',
    personality: 'Temkinli, lanetlerini ustaca savuran ve tanıdığı kedisine derin sevgi besleyen.'
  }
];

export function buildPresetForTier(basePreset, tier = 1) {
  const p = JSON.parse(JSON.stringify(basePreset));
  const t = parseInt(tier) || 1;
  p.level = t;

  if (t === 5) {
    p.title = `${p.title.replace('İkonik', 'Kıdemli İkonik')} (Seviye 5)`;
    // Scale abilities (+1 to primary)
    if (p.class === 'Fighter' || p.class === 'Barbarian' || p.class === 'Paladin') p.abilities.strength += 1;
    else if (p.class === 'Rogue' || p.class === 'Monk' || p.class === 'Ranger') p.abilities.dexterity += 1;
    else if (p.class === 'Wizard' || p.class === 'Alchemist') p.abilities.intelligence += 1;
    else if (p.class === 'Cleric' || p.class === 'Druid') p.abilities.wisdom += 1;
    else if (p.class === 'Sorcerer' || p.class === 'Bard') p.abilities.charisma += 1;

    // Extra feats
    if (p.class === 'Fighter') {
      p.feats.push({ isim: 'Weapon Specialization', sistem_verisi: { weapon: 'Longsword' } }, { isim: 'Iron Will' }, { isim: 'Cleave' });
    } else if (p.class === 'Wizard') {
      p.feats.push({ isim: 'Empower Spell' }, { isim: 'Craft Wondrous Item' });
    } else {
      p.feats.push({ isim: 'Iron Will' }, { isim: 'Combat Casting' });
    }

    // Upgraded equipment
    p.equipment.push({ name: 'Cloak of Resistance +1', category: 'gear' });
    p.equipment.push({ name: 'Potion of Cure Moderate Wounds', category: 'gear' });

    // Extra spells for casters
    if (p.spells && p.spells.length > 0) {
      if (p.class === 'Wizard') {
        p.spells.push({ isim: 'Fireball', level: 3 }, { isim: 'Haste', level: 3 }, { isim: 'Invisibility', level: 2 }, { isim: 'Scorching Ray', level: 2 });
      } else if (p.class === 'Cleric') {
        p.spells.push({ isim: 'Prayer', level: 3 }, { isim: 'Dispel Magic', level: 3 }, { isim: "Bull's Strength", level: 2 }, { isim: 'Spiritual Weapon', level: 2 });
      } else if (p.class === 'Sorcerer') {
        p.spells.push({ isim: 'Lightning Bolt', level: 3 }, { isim: 'Mirror Image', level: 2 });
      } else if (p.class === 'Bard') {
        p.spells.push({ isim: 'Heroism', level: 3 }, { isim: 'Glitterdust', level: 2 });
      }
    }
  } else if (t === 10) {
    p.title = `${p.title.replace('İkonik', 'Efsanevi Şampiyon')} (Seviye 10)`;
    // Scale abilities (+2 to primary, +1 to secondary)
    if (p.class === 'Fighter' || p.class === 'Barbarian' || p.class === 'Paladin') {
      p.abilities.strength += 2;
      p.abilities.constitution += 1;
    } else if (p.class === 'Rogue' || p.class === 'Monk' || p.class === 'Ranger') {
      p.abilities.dexterity += 2;
      p.abilities.constitution += 1;
    } else if (p.class === 'Wizard' || p.class === 'Alchemist') {
      p.abilities.intelligence += 2;
      p.abilities.dexterity += 1;
    } else if (p.class === 'Cleric' || p.class === 'Druid') {
      p.abilities.wisdom += 2;
      p.abilities.constitution += 1;
    } else if (p.class === 'Sorcerer' || p.class === 'Bard') {
      p.abilities.charisma += 2;
      p.abilities.dexterity += 1;
    }

    // Extra high-level feats
    p.feats.push({ isim: 'Greater Weapon Focus' }, { isim: 'Improved Critical' }, { isim: 'Quicken Spell' }, { isim: 'Maximize Spell' });

    // Upgraded magic equipment
    p.equipment.push({ name: 'Belt of Physical Might +2', category: 'gear' });
    p.equipment.push({ name: 'Cloak of Resistance +3', category: 'gear' });
    p.equipment.push({ name: 'Ring of Protection +2', category: 'gear' });

    // High level spells
    if (p.spells && p.spells.length > 0) {
      if (p.class === 'Wizard') {
        p.spells.push({ isim: 'Cone of Cold', level: 5 }, { isim: 'Teleport', level: 5 }, { isim: 'Stoneskin', level: 4 }, { isim: 'Dimension Door', level: 4 }, { isim: 'Fireball', level: 3 }, { isim: 'Haste', level: 3 });
      } else if (p.class === 'Cleric') {
        p.spells.push({ isim: 'Flame Strike', level: 5 }, { isim: 'Righteous Might', level: 5 }, { isim: 'Restoration', level: 4 }, { isim: 'Divine Power', level: 4 });
      } else if (p.class === 'Sorcerer') {
        p.spells.push({ isim: 'Telekinesis', level: 5 }, { isim: 'Greater Invisibility', level: 4 }, { isim: 'Lightning Bolt', level: 3 });
      }
    }
  }
  return p;
}

export default function PresetCharactersModal({ isOpen, onClose, onSelectPreset }) {
  const { loadPresetCharacter } = useCharacterStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTier, setSelectedTier] = useState(1); // 1, 5, 10

  if (!isOpen) return null;

  const handleSelect = (rawPreset) => {
    const tieredPreset = buildPresetForTier(rawPreset, selectedTier);
    loadPresetCharacter(tieredPreset);
    if (onSelectPreset) onSelectPreset(tieredPreset);
    onClose();
  };

  const filteredPresets = ALL_CLASS_PRESETS.filter(p => {
    return p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           p.class.toLowerCase().includes(searchTerm.toLowerCase()) ||
           p.race.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(7, 6, 15, 0.96)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#12101f', border: '1px solid var(--border-gold)', borderRadius: '14px',
        width: '100%', maxWidth: '940px', maxHeight: '92vh', overflowY: 'auto',
        boxShadow: '0 20px 50px rgba(0,0,0,0.85)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'
      }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(201,168,76,0.3)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={22} color="var(--gold-bright)" />
            <h2 style={{ fontFamily: 'Cinzel Decorative, serif', fontSize: '1.25rem', color: 'var(--gold-bright)', margin: 0 }}>
              İkonik Karakter Şablonları Galerisi ({ALL_CLASS_PRESETS.length} Sınıf)
            </h2>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Tier Selector & Search Bar */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap', justifyContent: 'space-between' }}>
          {/* Search Box */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#19162a', border: '1px solid var(--border-gold)', borderRadius: '6px', padding: '6px 12px', flex: 1, minWidth: '240px' }}>
            <Search size={16} color="var(--gold-light)" />
            <input
              type="text"
              placeholder="Sınıf veya isim ara (Örn: Wizard, Fighter, Amiri)..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#fff', outline: 'none', width: '100%', fontSize: '0.85rem' }}
            />
          </div>

          {/* Tier Pills */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: '#a594ff', fontWeight: 'bold' }}>Karakter Kademesi:</span>
            {[
              { tier: 1, label: '🌱 Seviye 1 (Başlangıç)' },
              { tier: 5, label: '⚔️ Seviye 5 (Kıdemli)' },
              { tier: 10, label: '👑 Seviye 10 (Şampiyon)' }
            ].map(tObj => (
              <button
                key={tObj.tier}
                type="button"
                onClick={() => setSelectedTier(tObj.tier)}
                style={{
                  padding: '5px 12px', borderRadius: '6px', fontSize: '0.75rem', cursor: 'pointer',
                  backgroundColor: selectedTier === tObj.tier ? 'var(--accent-gold)' : 'rgba(255,255,255,0.05)',
                  border: `1px solid ${selectedTier === tObj.tier ? 'var(--accent-gold)' : 'rgba(255,255,255,0.15)'}`,
                  color: selectedTier === tObj.tier ? '#0f0f1a' : '#f0e6d2',
                  fontWeight: 'bold',
                  transition: 'all 0.15s ease'
                }}
              >
                {tObj.label}
              </button>
            ))}
          </div>
        </div>

        {/* Preset Character Cards Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '14px' }}>
          {filteredPresets.map((rawChar) => {
            const char = buildPresetForTier(rawChar, selectedTier);

            return (
              <div
                key={char.id}
                style={{
                  backgroundColor: '#181528', border: '1px solid rgba(201,168,76,0.3)', borderRadius: '10px',
                  padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px',
                  boxShadow: '0 4px 15px rgba(0,0,0,0.3)'
                }}
              >
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <div style={{
                    width: '48px', height: '48px', borderRadius: '50%', backgroundColor: 'rgba(201,168,76,0.15)',
                    border: '1px solid var(--border-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.6rem', flexShrink: 0
                  }}>
                    {char.avatar}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h3 style={{ fontFamily: 'Cinzel, serif', fontSize: '1.1rem', color: 'var(--gold-bright)', margin: 0 }}>
                        {char.name} ({char.class})
                      </h3>
                      <span style={{ fontSize: '0.65rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(124,110,247,0.2)', border: '1px solid #7c6ef7', color: '#d8b4fe', fontWeight: 'bold' }}>
                        Seviye {selectedTier}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--gold-light)', fontFamily: 'Cinzel, serif' }}>
                      {char.title} • {char.race}
                    </div>
                  </div>
                </div>

                <p style={{ fontSize: '0.78rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
                  {char.description}
                </p>

                {/* Detailed Loadouts Summary */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.72rem', backgroundColor: '#0f0d1a', padding: '8px', borderRadius: '6px', border: '1px solid #2a2540' }}>
                  <div><b style={{ color: 'var(--gold-bright)' }}>Statlar:</b> STR {char.abilities.strength} | DEX {char.abilities.dexterity} | CON {char.abilities.constitution} | INT {char.abilities.intelligence} | WIS {char.abilities.wisdom} | CHA {char.abilities.charisma}</div>
                  <div><b style={{ color: 'var(--gold-bright)' }}>Hünerler (Feats):</b> {char.feats.map(f => f.isim || f.name).join(', ')}</div>
                  <div><b style={{ color: 'var(--gold-bright)' }}>Ekipman:</b> {char.equipment.map(e => e.name).join(', ')}</div>
                  {char.spells?.length > 0 && <div><b style={{ color: '#a594ff' }}>Büyüler:</b> {char.spells.map(s => s.isim || s.name).join(', ')}</div>}
                  {char.companion && <div><b style={{ color: '#4ec9b0' }}>Yoldaş:</b> {char.companion.name} ({char.companion.type})</div>}
                </div>

                {/* Action Button */}
                <button
                  type="button"
                  onClick={() => handleSelect(rawChar)}
                  style={{
                    marginTop: 'auto', padding: '10px 14px', backgroundColor: 'rgba(201,168,76,0.2)',
                    border: '1px solid var(--border-gold)', borderRadius: '6px', color: 'var(--gold-bright)',
                    fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', gap: '6px', fontFamily: 'Cinzel, serif',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <Zap size={15} /> ⚡ {char.name} ({selectedTier}. Seviye) Yükle
                </button>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
