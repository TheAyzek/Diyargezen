/**
 * Central Text Sanitizer Utility for Diyargezen Web & Desktop
 * Purifies raw HTML tags, unescapes HTML entities, fixes concatenated spell words,
 * and strips Foundry VTT @Compendium link syntax.
 */

export function cleanText(rawStr) {
  if (!rawStr) return '';
  let str = String(rawStr);
  
  if (str.startsWith('Contents') || str.startsWith('Skill:') || str.startsWith('sbc |')) {
    return '';
  }

  let s = str
    // Strip Foundry VTT link tags: @Compendium[world.feat]{Name} -> Name
    .replace(/@Compendium\[[^\]]+\]\{([^}]+)\}/g, '$1')
    .replace(/@Compendium\[[^\]]+\]/g, '')
    // Strip ASP.NET scraper tags
    .replace(/<span[^>]*>/gi, '')
    .replace(/<\/span>/gi, '')
    // Strip broken header descriptions
    .replace(/<h[1-6]>[^<]*Description[^<]*<\/h[1-6]>/gi, '')
    // Strip HTML tags
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
    // Normalize whitespace
    .replace(/\s+/g, ' ')
    .trim();

  return s;
}
