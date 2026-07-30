/**
 * Central Text Sanitizer Utility for Diyargezen Web & Desktop
 * Purifies raw HTML tags, unescapes HTML entities, fixes concatenated spell words,
 * and strips Foundry VTT @Compendium link syntax.
 */

export function cleanText(rawStr) {
  if (!rawStr) return '';
  let str = String(rawStr).trim();

  // Strip HTML tags first to check plain text content
  const plainLower = str.replace(/<[^>]*>/g, '').trim().toLowerCase();
  if (!plainLower || plainLower === 'contents' || plainLower.startsWith('contents') || plainLower.startsWith('skill:') || plainLower.startsWith('sbc |')) {
    return '';
  }

  let s = str
    // Strip Foundry VTT link tags: @Compendium[world.feat]{Name} -> Name
    .replace(/@Compendium\[[^\]]+\]\{([^}]+)\}/g, '$1')
    .replace(/@Compendium\[[^\]]+\]/g, '')
    // Convert paragraph, list item and break tags to double newlines before stripping HTML
    .replace(/<\/p>|<br\s*\/?>|<\/h[1-6]>|<\/div>|<\/li>/gi, '\n\n')
    // Strip ASP.NET scraper tags
    .replace(/<span[^>]*>/gi, '')
    .replace(/<\/span>/gi, '')
    // Strip broken header descriptions
    .replace(/<h[1-6]>[^<]*Description[^<]*<\/h[1-6]>/gi, '')
    // Strip remaining HTML tags
    .replace(/<[^>]*>/g, ' ')
    // Add spaces around parentheses and punctuation if glued to words e.g. word(Ex) -> word (Ex), (Ex)Word -> (Ex) Word
    .replace(/([a-zA-Z0-9])\(/g, '$1 (')
    .replace(/\)([a-zA-Z0-9])/g, ') $1')
    .replace(/([a-zA-Z0-9]),([a-zA-Z0-9])/g, '$1, $2')
    .replace(/([a-zA-Z0-9])\.([a-zA-Z])/g, '$1. $2')
    .replace(/([a-zA-Z0-9]):([a-zA-Z0-9])/g, '$1: $2')
    // Specific concatenated typos in scraped PF1e descriptions
    .replace(/beparalyzedby/g, 'be paralyzed by')
    .replace(/savingthrow/gi, 'saving throw')
    .replace(/spellattack/gi, 'spell attack')
    .replace(/meleeattack/gi, 'melee attack')
    .replace(/rangedattack/gi, 'ranged attack')
    .replace(/hitpoints/gi, 'hit points')
    .replace(/casterlevel/gi, 'caster level')
    .replace(/spellresistance/gi, 'spell resistance')
    // Split concatenated CamelCase e.g. aWisdom -> a Wisdom
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    // Split word + stat/saving throw e.g. aWisdomsaving -> a Wisdom saving
    .replace(/(\b[a-zA-Z]+)(saving|throw|attack|damage|target|duration|range|radius|paralyzed|poisoned|stunned|blinded|deafened)/gi, '$1 $2')
    .replace(/(saving|throw|attack|damage|target|duration|range|radius|paralyzed|poisoned|stunned|blinded|deafened)(\b[a-zA-Z]+)/gi, '$1 $2')
    // Split number + unit e.g. 10feet -> 10 feet, 1d6damage -> 1d6 damage
    .replace(/(\d+)(feet|ft|d4|d6|d8|d10|d12|d20|rounds?|minutes?|hours?|days?|level|levels|damage)/gi, '$1 $2')
    // Unescape HTML entities
    .replace(/&rsquo;/g, "'")
    .replace(/&lsquo;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&ndash;/g, '-')
    .replace(/&mdash;/g, '—')
    .replace(/&times;/g, '×');

  // Normalize line breaks while maintaining paragraph structure
  const lines = s.split('\n').map(line => line.replace(/[ \t]+/g, ' ').trim()).filter(Boolean);
  return lines.join('\n\n');
}

export function formatTitle(rawStr) {
  if (!rawStr) return '';
  let str = cleanText(rawStr);
  return str
    .split(/[\s_]+/)
    .map(word => {
      if (word.length === 0) return '';
      // Retain standard abbreviations like HP, AC, BAB, SR, INT, DEX, STR, CON, WIS, CHA
      if (['hp', 'ac', 'bab', 'sr', 'int', 'dex', 'str', 'con', 'wis', 'cha', 'id'].includes(word.toLowerCase())) {
        return word.toUpperCase();
      }
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');
}

export function toSentenceCase(rawText) {
  if (!rawText) return '';
  let str = cleanText(rawText);
  // Check if string is predominantly uppercase (more than 65% uppercase letters)
  const letters = str.replace(/[^a-zA-Z]/g, '');
  if (letters.length > 0) {
    const upperCount = (str.match(/[A-Z]/g) || []).length;
    if (upperCount / letters.length > 0.65) {
      // Convert to lower case and capitalize sentence starts
      str = str.toLowerCase();
      // Capitalize first letter of string
      str = str.charAt(0).toUpperCase() + str.slice(1);
      // Capitalize first letter after . ! ?
      str = str.replace(/([.!?]\s+)([a-z])/g, (m, p1, p2) => p1 + p2.toUpperCase());
      // Capitalize race names & standard keywords e.g. half-elves, Pathfinder, RPG
      str = str.replace(/\b(half-elves|half-elf|half-orcs|half-orc|elves|elf|dwarves|dwarf|humans|human|gnomes|gnome|halflings|halfling|aonprd|pathfinder)\b/gi,
        m => m.charAt(0).toUpperCase() + m.slice(1)
      );
    }
  }
  return str;
}

export function parseTraitsDetailed(rawVal) {
  if (!rawVal) return null;
  if (typeof rawVal === 'object' && !Array.isArray(rawVal)) {
    return Object.keys(rawVal).length > 0 ? rawVal : null;
  }
  if (typeof rawVal === 'string') {
    let s = rawVal.trim();
    if (!s) return null;
    
    // Try JSON.parse directly
    try {
      const parsed = JSON.parse(s);
      if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
        return Object.keys(parsed).length > 0 ? parsed : null;
      }
    } catch (e) {}

    // Clean outer parens/braces e.g. ("MEDIUM":"ELVES ARE...", ...)
    if (s.startsWith('(') && s.endsWith(')')) {
      s = '{' + s.slice(1, -1) + '}';
    }
    
    try {
      const jsonLike = s.replace(/'/g, '"');
      const parsed = JSON.parse(jsonLike);
      if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
        return Object.keys(parsed).length > 0 ? parsed : null;
      }
    } catch (e) {}

    // Regex fallback for "KEY": "VALUE" or 'KEY': 'VALUE' or KEY: VALUE
    const result = {};
    const kvRegex = /["']?([\w\s-]+)["']?\s*:\s*["']?([^"'}]+)["']?/g;
    let match;
    while ((match = kvRegex.exec(s)) !== null) {
      const k = match[1].trim();
      const v = match[2].trim();
      if (k && v) {
        result[k] = v;
      }
    }
    if (Object.keys(result).length > 0) return result;
  }
  return null;
}
