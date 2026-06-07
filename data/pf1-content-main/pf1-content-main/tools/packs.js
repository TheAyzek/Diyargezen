/* eslint-disable no-undef */
import fsp from "node:fs/promises";
import fs from "node:fs";
import path from "node:path";
import url from "node:url";
import yargs from "yargs";
import { Listr } from "listr2";
import pc from "picocolors";
import yaml from "js-yaml";
import * as fvtt from "@foundryvtt/foundryvtt-cli";

import * as utils from "./utils.mjs";
import {
  getActionDefaultData,
  getChangeDefaultData,
  getTokenDefaultData,
  addMissingItemData,
} from "./pack-default-data.mjs";
import { mkdir, readJSONSync } from "./lib.mjs";

const __dirname = url.fileURLToPath(new URL(".", import.meta.url));
const __filename = url.fileURLToPath(import.meta.url);
const PACK_SRC = "../src";
const PACK_CACHE = "../release/packs";

/**
 * Arrays of dot paths exempt from data trimming; `system.` is implied, as only system data is trimmed.
 * This should include paths to any objects that can contain arbitrary (i.e. not in template) properties.
 */
const TEMPLATE_EXCEPTION_PATHS = {
  Actor: ["attributes.spells.spellbooks", "skills"],
  Item: ["classSkills", "links.supplements", "flags", "properties", "source", "ammo"],
  Component: [],
  Token: [],
};

/**
 * Same as TEMPLATE_EXCEPTION_PATHS but limited to type.
 */
const TEMPLATE_EXCEPTION_PATHS_BY_TYPE = {
  Item: {
    attack: ["weapon"],
    loot: ["recoverChance"],
    container: ["items"],
    class: ["casting", "customHD"],
    spell: ["learnedAt"],
  },
};

/**
 * Alternate exception paths, but only accepted if they validate with {@link utils.isDefined}.
 */
const TEMPLATE_EXCEPTION_PATHS_ALT = {
  Item: ["hp.base", "creatureTypes", "creatureSubtypes"],
};

// Template exceptions only when the document is owned by an actor
const TEMPLATE_ACTOR_EXCEPTION_PATHS = {
  Item: ["class"],
};

/**
 * Inverted exception paths. These must always be cleared unless the document is child of another or in other excemption list.
 */
const TEMPLATE_ENFORCED_CLEARING = {
  Item: [],
};

const templateData = loadDocumentTemplates();
const manifest = loadManifest();

/**
 * Helper function that resolves a path from the pack source directory
 *
 * @param {...string} file - String path segments
 * @returns {string} The resolved path
 */
const resolveSource = (...file) => path.resolve(__dirname, PACK_SRC, ...file);

/**
 * Helper function that resolves a path from the pack build directory
 *
 * @param {...string} file - String path segments
 * @returns {string} The resolved path
 */
const resolveCache = (...file) => path.resolve(__dirname, PACK_CACHE, ...file);

// Only handle commands if this script was executed directly
console.log("argv is ", process.argv);
if (process.argv[1] === __filename || process.argv[2] === "pack") {
  yargs(process.argv.slice(2))
    .demandCommand(1, 1)
    .command({
      command: "pack",
      describe: `Compile all packs (or a pack) into ldb file(s)`,
      handler: async (argv) => {
        let folder = [];
        const folderIndex = argv["_"].indexOf("folder");
        if (folderIndex !== -1) {
          folder = [argv["_"][folderIndex + 1]];
        }

        await compilePacks(folder);
      },
    })
    .command({
      command: "unpack",
      describe: `Extract all packs (or a pack) into source JSONs`,
      handler: async (argv) => {
        let folder = (argv.folder ?? process.argv[3]) ? [process.argv[3]] : [];
        if (["keepDeleted", "cleanSrc"].includes(folder[0])) folder = [];

        let keepDeleted = false;
        let cleanPack = false;

        const keepDeletedIndex = argv["_"].indexOf("keepDeleted");
        if (keepDeletedIndex !== -1) {
          keepDeleted = argv["_"][keepDeletedIndex + 1] === "true";
        }

        const cleanPackIndex = argv["_"].indexOf("cleanSrc");
        console.log("Clean Source: " + cleanPackIndex);
        if (cleanPackIndex !== -1) {
          cleanPack = argv["_"][cleanPackIndex + 1] === "true";
        }

        await extractPacks(folder, { reset: !keepDeleted, cleanPack: cleanPack });
      },
    })
    // Option to overwrite the default `reset` option
    .option("folder", { describe: "Work with a specific pack", type: "string" })
    .option("keepDeleted", {
      describe: "Keep files that are not present in the db. Default: true",
      type: "boolean",
      default: true,
    })
    .option("cleanSrc", {
      describe: "Clean out the src folder for the pack before extracting. Default: false",
      type: "boolean",
      default: false,
      alias: "cleanPack",
    })
    .parse();
}

/**
 * Loads the document templates file.
 *
 * @returns {object} The document templates object, merged with their respective templates.
 */
function loadDocumentTemplates() {
  const templates = readJSONSync(path.resolve(__dirname, "./template.json"));

  for (const [documentName, doc] of Object.entries(templates)) {
    const isItem = documentName === "Item";

    delete doc.types;

    for (const [type, template] of Object.entries(doc)) {
      if (type === "templates") continue;

      if (template.templates) {
        for (const templateId of template.templates) {
          doc[type] = utils.mergeObject(template, doc.templates?.[templateId] ?? {});
        }
      }
      delete template.templates;

      if (isItem) addMissingItemData(type, doc[type]);
    }

    delete doc.templates;
  }

  return templates;
}

/**
 * Loads the module manifest file.
 *
 * @returns {object} The module manifest file as an object.
 */
function loadManifest() {
  return readJSONSync(path.resolve(__dirname, "../module.json"));
}

/**
 * Extracts dbs from {@link PACK_CACHE} into {@link PACK_SRC}
 * If no packs are specified, all packs are extracted.
 *
 * @param {string[]} packNames - The names of the packs to extract
 * @param {object} [options={}] - Additional options to augment the behavior.
 * @param {boolean} [options.reset=true] - Whether to remove files not present in the db
 * @param {boolean} [options.cleanPack=false] - Whether to clean the pack directory before extracting
 * @returns {Promise<PackResult[]>} An array of pack results
 */
async function extractPacks(packNames = [], options = { reset: true, cleanPack: false }) {
  const packDirs = await fsp.readdir(resolveSource(), { withFileTypes: true });
  const packs = packNames.length ? packDirs.filter((p) => packNames.includes(p.name)) : packDirs;

  const tasks = new Listr(
    packs
      .filter((packDir) => packDir.isDirectory())
      .map((packDir) => {
        return {
          task: async (_, task) => {
            task.title = `Extracting ${packDir.name}`;
            const packResult = await extractPack(packDir.name, options);
            const yellowSign = pc.yellow("\u26a0");
            const redSign = pc.red("\u26a0");
            const notifications = [];

            if (packResult.addedFiles.length) {
              notifications.push(`${pc.green("\u26a0")} Added ${pc.bold(packResult.addedFiles.length)} files:`);
              const addedFiles = packResult.addedFiles.map((f) => path.basename(f)).join(", ");
              notifications.push(`${pc.dim(addedFiles)}`);
            }

            if (packResult.removedFiles.length) {
              if (options.reset) {
                notifications.push(
                  `${yellowSign} Removed ${pc.bold(packResult.removedFiles.length)} files without DB entry:`
                );
              } else {
                notifications.push(
                  `${yellowSign} Found ${pc.bold(packResult.removedFiles.length)} files without DB entry:`
                );
              }
              const removedFiles = packResult.removedFiles.map((f) => path.basename(f)).join(", ");
              notifications.push(`${pc.dim(removedFiles)}`);
            }

            const conflictsNumber = Object.keys(packResult.conflicts).length;
            if (conflictsNumber) {
              notifications.push(`${redSign} Found ${pc.bold(conflictsNumber)} ID conflicts:`);
              for (const [id, files] of Object.entries(packResult.conflicts)) {
                notifications.push(pc.dim(`${id} in ${pc.dim([...files].map((f) => path.basename(f)).join(", "))}`));
              }
            }

            if (notifications.length) {
              task.title = `Extracted ${packDir.name} with notifications:\n${notifications.join(`\n`)}`;
            } else {
              task.title = `Extracted ${packDir.name}`;
            }
          },
        };
      }),
    { concurrent: true }
  );
  return tasks.run();
}

/**
 * @typedef {object} PackResult
 * @property {string} packName - The name of the db
 * @property {string[][]} conflictingFiles - The files containing keys occuring more than once
 * @property {string[]} addedFiles - The files written during the extraction
 * @property {string[]} removedFiles - The files removed during the extraction
 */

/**
 * Extracts a single LevelDB, creating a directory with the db's name in {@link PACK_SRC},
 * and storing each entry in its own file.
 *
 * @param {string} packName - The directory name from {@link PACK_CACHE}
 * @param {object} [options={}] - Additional options to augment the behavior.
 * @param {boolean} [options.reset=true] - Whether to remove files not present in the db
 * @param {boolean} [options.cleanPack=false] - Whether to clean the pack directory before extracting
 * @returns {Promise<PackResult>} The result of the extraction
 */
async function extractPack(packName, options = { reset: true, cleanPack: false }) {
  // This db directory in PACK_SRC
  const directory = resolveSource(path.basename(packName));
  if (!fs.existsSync(resolveCache(packName))) throw new Error(`${packName} does not exist`);

  // Index of already existing files, to be checked for files not touched with this extraction
  const filesBefore = [];
  const touchedFiles = [];
  /** @type {Map<string, Set<string>>} */
  const ids = new Map();
  let isFirstExtraction = false;
  if (!fs.existsSync(directory)) {
    isFirstExtraction = true;
    await mkdir(directory);
  } else {
    for (const curFile of fs.readdirSync(directory)) {
      filesBefore.push(resolveSource(directory, curFile));
    }
  }

  // Find associated manifest pack data
  const packData = manifest.packs.find((p) => {
    if (p.path) return path.basename(p.path) === packName;
    else return p.name === packName;
  });
  if (!packData) console.warn(`No data found for package ${packName} within the module manifest.`);

  await fvtt.extractPack(resolveCache(packName), resolveSource(directory), {
    transformEntry: (entry) => sanitizePackEntry(entry, packData?.type),
    transformName: (entry) => {
      const filename = `${utils.sluggify(entry.name)}_${entry._id}.yaml`;

      // Abuse the callback to avoid having to read and parse the file later
      const file = resolveSource(directory, filename);
      touchedFiles.push(file);
      if (ids.has(entry._id)) ids.get(entry._id).add(file);
      else ids.set(entry._id, new Set([file]));

      return filename;
    },
    yaml: true,
    yamlOptions: {
      sortKeys: true, // Prevent random key drift
    },
    clean: options.cleanPack,
  });

  const filesAfter = fs.readdirSync(directory).map((f) => resolveSource(directory, f));

  // Find all untouched files whose IDs could not be retrieved while extracting
  await Promise.all(
    filesAfter
      .filter((f) => f.endsWith("yaml") && !touchedFiles.includes(f))
      .map(async (file) => {
        const content = await fsp.readFile(file);
        const parsed = yaml.load(content);
        const { _key, _id } = parsed;
        const idFromKey = _key?.split("!").at(-1);
        if (idFromKey !== _id) throw new Error(`ID mismatch in ${file}: ${idFromKey} !== ${_id}`);
        if (ids.has(_id)) ids.get(_id).add(file);
        else ids.set(_id, new Set([file]));
      })
  );
  // Array of Sets containing conflicting files
  const conflicts = Object.fromEntries([...ids.entries()].filter(([, files]) => files.size > 1));
  const conflictingFileNames = new Set(
    Object.values(conflicts).flatMap((files) => [...files].map((f) => path.basename(f)))
  );

  // Find all files that were added by this run
  const addedFiles = isFirstExtraction ? [] : filesAfter.filter((f) => !filesBefore.includes(f)); //.filter((f) => !conflictingFiles.flat().includes(f));

  // Find all files that were not touched by this run (and thus are candidates for deletion);
  // exclude conflicting files, as they have to be checked manually
  const removedFiles = filesBefore.filter((f) => !touchedFiles.includes(f) && !conflictingFileNames.has(f));
  if (options.reset) {
    await Promise.all(removedFiles.map((f) => fsp.unlink(f)));
  }

  return { packName, addedFiles, removedFiles, conflicts };
}

/**
 * Clean up Foundry's _stats entry to contain only the bare minimum.
 *
 * @param {object} entry - Document object
 * @param {Array<string>} keep - Extra keys to keep
 */
function sanitizeStats(entry, keep = []) {
  if (!entry?._stats) return;

  keep.push("coreVersion"); // Ensure Foundry migration plays nice

  for (const key of Object.keys(entry._stats)) {
    if (keep.includes(key) && entry._stats[key]) continue;
    delete entry._stats[key];
  }

  if (Object.keys(entry._stats).length === 0) delete entry._stats;
}

/**
 * Sanitize and prune Active Effect data
 *
 * @param {Array<object>} effects - Active Effects data
 */
function sanitizeActiveEffects(effects) {
  for (const ae of effects) {
    delete ae.changes;
    delete ae.origin;
    delete ae.transfer;
    delete ae.disabled;

    utils.pruneObject(ae);
  }
}

/**
 * Sanitize folder data
 *
 * @param {object} folder - Folder data
 */
function sanitizeFolder(folder) {
  if (!folder.description) delete folder.description;
  if (!folder.color) delete folder.color;
  if (!folder.folder) delete folder.folder;
  if (utils.isEmpty(folder.flags)) delete folder.flags;
}

/**
 * Sanitize HTML
 *
 * Replace unicode non-breaking spaces that are poorly supported by yaml.
 *
 * @param {string} text - The text to sanitize
 * @param {boolean} html  - Whether to replace with HTML entities
 * @returns {string} The sanitized text
 */
function sanitizeHTML(text, html = true) {
  return text.replaceAll(" ", html ? "&nbsp;" : " ");
}

/**
 * Santize pack entry.
 *
 * This resets an entry's permissions to default and removes all non-pf1 flags.
 *
 * @param {object} entry Loaded compendium content.
 * @param {string} [documentType] The document type of the entry, determining which data is scrubbed.
 * @param {object} [options] - Additional options
 * @param {boolean} [options.childDocument] - Is this document within another?
 * @param {object} [options.parent] - Parent entry for child documents
 * @returns {object} The sanitized content.
 */
function sanitizePackEntry(entry, documentType = "", { childDocument = false, parent } = {}) {
  // Delete unwanted fields
  delete entry.ownership;

  // Move core Foundry document source
  if (entry.flags?.core?.sourceId && !entry._stats?.compendiumSource)
    utils.setProperty(entry, "_stats.compendiumSource", entry.flags.core.sourceId);
  // Remove core Foundry duplication of source. Happens even without the above.
  // We don't care if they match, they should, and if they don't, something's broken.
  if (entry._stats?.compendiumSource !== undefined && entry.flags?.core?.sourceId !== undefined) {
    delete entry.flags?.core?.sourceId;
  }

  sanitizeStats(entry, childDocument ? ["compendiumSource"] : undefined);

  if ("effects" in entry) {
    if (entry.effects.length === 0) delete entry.effects;
    else sanitizeActiveEffects(entry.effects);
  }

  // Special handling for folders
  if (entry._key?.startsWith("!folders")) {
    sanitizeFolder(entry);
    return entry;
  }

  // Always delete system migration marker
  delete entry.flags?.pf1?.migration;

  // Delete lingering abundant flag
  delete entry.flags?.pf1?.abundant;

  // Remove non-system/non-core flags
  if (entry.flags) {
    utils.pruneObject(entry.flags);
    for (const key of Object.keys(entry.flags)) {
      if (!["pf1", "core"].includes(key)) delete entry.flags[key];
    }
    if (utils.isEmpty(entry.flags)) delete entry.flags;
  }

  // Remove Actor/Item top-level keys not part of Foundry's core data model
  // For usual documents, this is enforced by Foundry. For inventoy items, it is not.
  const allowedCoreFields = [
    "name",
    "type",
    "img",
    "data",
    "flags",
    "items",
    "effects",
    "system",
    "prototypeToken",
    "_id",
    "_key",
    "_stats",
    "folder",
  ];

  const htmlFieldsByType = {
    Actor: ["system.details.biography.value", "system.details.notes.value"],
    Item: ["system.description.value", "system.description.unidentified"],
    JournalEntryPage: ["text.content"],
  };

  const htmlFields = htmlFieldsByType[documentType] ?? [];
  for (const field of htmlFields) {
    const text = utils.getProperty(entry, field);
    if (typeof text === "string") {
      utils.setProperty(entry, field, sanitizeHTML(text));
    }
  }

  switch (documentType) {
    case "Actor":
    case "Item": {
      for (const key of Object.keys(entry)) {
        if (!allowedCoreFields.includes(key)) delete entry[key];
      }
      break;
    }
    case "JournalEntry": {
      if (entry.pages?.length > 0) {
        for (const page of entry.pages) {
          sanitizePackEntry(page, "JournalEntryPage", { childDocument: true, parent: entry });
        }
      }
      break;
    }
    case "JournalEntryPage": {
      if (utils.isEmpty(entry.image)) delete entry.image;
      if (utils.isEmpty(entry.system)) delete entry.system;
      if (entry.src === null) delete entry.src;
      if (!entry.text?.markdown) delete entry.text?.markdown;
      if (!entry.text?.content) delete entry.text?.content;

      delete entry.video; // System doesn't include video
      break;
    }
    case "RollTable": {
      for (const result of entry.results) {
        sanitizePackEntry(result, "TableResult", { childDocument: true, parent: entry });
      }
      break;
    }
    case "TableResult": {
      delete entry.drawn; // Drawn state should never be saved
      if (!entry.documentCollection) delete entry.documentCollection;
      if (!entry.img) delete entry.img;
      if (!entry.documentId) delete entry.documentId;
      break;
    }
  }

  // Remove folders anyway if null or document is in actor
  if (entry.folder === null || childDocument) delete entry.folder;

  // Adhere to template data
  if (templateData) {
    const systemData = entry.system;
    const template = templateData[documentType]?.[entry.type];
    if (systemData && template) {
      entry.system = enforceTemplate(systemData, template, {
        documentName: documentType,
        type: entry.type,
        childDocument,
      });
    }
    if (documentType === "Actor") {
      if (entry.items?.length > 0) {
        // Treat embedded items like normal items for sanitization
        entry.items = entry.items.map((i) => sanitizePackEntry(i, "Item", { childDocument: true, parent: entry }));
      }
      if (entry.prototypeToken) {
        entry.prototypeToken = sanitizePackEntry(entry.prototypeToken, "Token", { childDocument: true, parent: entry });
      }
    }
    if (["Actor", "Item"].includes(documentType)) {
      if (entry.effects?.length > 0) {
        for (const effect of entry.effects) {
          sanitizePackEntry(effect, "ActiveEffect", { childDocument: true, parent: entry });
        }
      }
    }
    if (documentType === "Item" && entry.system.items && Object.keys(entry.system.items).length > 0) {
      // Treat embedded items like normal items for sanitization
      for (const [itemId, itemData] of Object.entries(entry.system.items)) {
        entry.system.items[itemId] = sanitizePackEntry(itemData, "Item", { childDocument: true, parent: entry });
      }
    }
  }

  if (documentType === "Token") {
    const defaultData = getTokenDefaultData();
    return enforceTemplate(entry, defaultData, { documentName: "Token", childDocument: true, parent: entry });
  }

  return entry;
}

/**
 * Enforce a template on an object.
 *
 * @param {object} object - The data object to be trimmed
 * @param {object} template - The template to enforce
 * @param {object} [options={}] - Additional options to augment the behavior.
 * @param {"Actor" | "Item" | "Component"} [options.documentName] - The document(-like) name to which this template belongs.
 * @param {"Action" | "Change"} [options.componentName] - The component name to which this template belongs.
 * @param {boolean} [options.childDocument] - Is this child document of an actor?
 * @param {string} [options.type] - The document type of the object, if it is not already present.
 * @returns {object} A data object which has been trimmed to match the template
 */
function enforceTemplate(object, template, options = {}) {
  // Do not enforce templates on documents which do not have them
  if (!object || !template || !["Actor", "Item", "Token", "Component"].includes(options.documentName)) return object;

  // Create a diff of the object and template to remove all default values
  const diff = utils.diffObject(template, object);
  const flattened = utils.flattenObject(diff);
  for (const path of Object.keys(flattened)) {
    // Delete additional properties unless in template or in the exception list
    // ... but remove exceptions anyway if they're null or empty string.
    const inTemplate = utils.hasProperty(template, path);
    let isExempt =
      options.documentName &&
      TEMPLATE_EXCEPTION_PATHS[options.documentName].some((exceptionPath) => path.startsWith(exceptionPath));

    // Excemptions when this document is in actor
    if (options.childDocument && !isExempt)
      isExempt =
        TEMPLATE_ACTOR_EXCEPTION_PATHS[options.documentName]?.some((exceptionPath) => path.startsWith(exceptionPath)) ??
        false;

    // Additional exceptions that want some kind of content instead of any value
    if (!isExempt && options.documentName) {
      isExempt =
        utils.isDefined(flattened[path]) &&
        (TEMPLATE_EXCEPTION_PATHS_ALT[options.documentName]?.some((exceptionPath) => path.startsWith(exceptionPath)) ??
          false);
    }

    if (!isExempt && options.documentName && options.type) {
      isExempt ||=
        TEMPLATE_EXCEPTION_PATHS_BY_TYPE[options.documentName]?.[options.type]?.some((exception) =>
          path.startsWith(exception)
        ) ?? false;
    }

    // Force removal of certain data that is never desired to be stored
    if (options.childDocument !== true && !isExempt) {
      if (TEMPLATE_ENFORCED_CLEARING[options.documentName]?.some((exception) => path.startsWith(exception))) {
        delete flattened[path];
        continue;
      }
    }

    const value = flattened[path];
    if (!inTemplate && (!isExempt || (isExempt && (value === "" || value === null)))) {
      delete flattened[path];
      continue;
    }

    // Delete null values if template has empty string
    const currentValue = utils.getProperty(object, path);
    const templateValue = utils.getProperty(template, path);
    if (templateValue === "" && currentValue === null) delete flattened[path];
    // Delete empty strings in general if they don't default to something more specific
    if (currentValue === "" && !(templateValue?.length > 0)) delete flattened[path];

    const templateHasArray = Array.isArray(templateValue);
    if (templateHasArray) {
      const isEmptyArray = flattened[path] instanceof Array && flattened[path].length === 0;
      if (isEmptyArray) delete flattened[path];
    }
  }

  /* -------------------------------------------- */
  /*  Handling special cases/cleanup              */
  /* -------------------------------------------- */
  for (const path of Object.keys(flattened)) {
    // Delete erroneous keys containing paths to delete
    if (path.includes(".-=")) {
      delete flattened[path];
    }

    // Item cleanup
    if (options.documentName === "Item") {
      // Delete ammo type when empty
      if (!flattened["system.ammo.type"]) {
        delete flattened["system.ammo.type"];
      }

      // Delete non-set class skills
      if (path.startsWith("classSkills.") && flattened[path] === false) {
        delete flattened[path];
      }

      // Delete non-set properties in weapons
      if (options.type === "weapon" && path.startsWith("properties.") && flattened[path] === false) {
        delete flattened[path];
      }
    }
  }

  /* -------------------------------------------- */
  /*  Handling components                         */
  /* -------------------------------------------- */
  if ("actions" in flattened && Array.isArray(flattened.actions)) {
    const defaultData = getActionDefaultData();
    flattened.actions = flattened.actions.map((action) => {
      action = enforceTemplate(action, defaultData, { documentName: "Component", componentName: "Action" });

      // Special cleanup
      if (!action.ability?.damage) delete action.ability?.damageMult;
      if (utils.isEmpty(action.ability)) delete action.ability;

      return action;
    });
  }
  if ("changes" in flattened && Array.isArray(flattened.changes)) {
    const defaultData = getChangeDefaultData();
    flattened.changes = flattened.changes.map((change) =>
      enforceTemplate(change, defaultData, { documentName: "Component", componentName: "Change" })
    );
    // Delete special cases
    flattened.changes.forEach((ch) => {
      if (ch.priority === null) delete ch.priority;
    });
  }

  return utils.expandObject(flattened);
}

/**
 * Extracts dbs from {@link PACK_CACHE} into {@link PACK_SRC}
 * If no packs are specified, all packs are extracted.
 *
 * @param {string[]} packNames - The names of the packs to extract
 * @returns {Promise<void>} A promise that resolves when all packs have been extracted
 */
async function compilePacks(packNames = []) {
  const packDirs = await fsp.readdir(resolveSource(), { withFileTypes: true });
  const packs = packNames.length ? packDirs.filter((p) => packNames.includes(p.name)) : packDirs;

  const tasks = new Listr(
    packs
      .filter((packDir) => packDir.isDirectory())
      .map((packDir) => {
        return {
          task: async (_, task) => {
            task.title = `Compiling ${packDir.name}`;
            await fsp.rm(resolveCache(packDir.name), {
              recursive: true,
              force: true,
            });
            await compilePack(packDir.name);
            task.title = `Compiled ${packDir.name}`;
          },
        };
      }),
    { concurrent: true }
  );
  return tasks.run();
}

/**
 * Compiles a directory containing yaml files into a leveldb
 * with the directory's name in {@link PACK_CACHE}
 *
 * @param {string} name - Name of the db
 * @returns {Promise<void>}
 */
async function compilePack(name) {
  console.info(`Creating pack ${resolveCache(name)}`);
  await mkdir(resolveCache(name));
  return fvtt.compilePack(resolveSource(name), resolveCache(name), { yaml: true });
}
