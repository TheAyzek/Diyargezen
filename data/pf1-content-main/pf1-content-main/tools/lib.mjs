import fsp from "node:fs/promises";
import fs from "node:fs";
import path from "node:path"; // Can't use posix paths since watcher doesn't heed that

/**
 * Debounce Function
 *
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
export const debounce = (fn, delay) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
};

/**
 * Create folder. Ignore errors from it already existing.
 *
 * @param {string} path - Path to create
 * @returns {Promise<undefined>}
 * @throws
 */
export async function mkdir(path) {
  return fsp.mkdir(path, { recursive: true }).catch((err) => {
    if (err.code !== "EEXIST") throw err;
  });
}

/**
 * @param {string} path
 * @returns {object|undefined} - JSON object or undefined on read error.
 */
export function readJSONSync(path) {
  let data;
  try {
    data = fs.readFileSync(path, { encoding: "utf-8" });
  } catch {
    return;
  }
  return JSON.parse(data);
}

/**
 * @param {string} path
 * @returns {object|undefined} - JSON object or undefined on read error.
 */
export async function readJSON(path) {
  let data;
  try {
    data = await fsp.readFile(path, { encoding: "utf-8" });
  } catch {
    return;
  }
  return JSON.parse(data);
}

/**
 * Write JSON to file
 *
 * @param {string} path   The path to write the JSON file to
 * @param {object} data   The data to write to the file
 * @returns {Promise<void>}
 */
export async function writeJSON(path, data) {
  return fsp.writeFile(path, JSON.stringify(data, null, 2));
}

/**
 * readdir() but always returns posix paths
 *
 * @param {string} path
 * @param {object} [options]
 * @param {boolean} [options.recursive]
 */
export async function readdir(path, { recursive = false } = {}) {
  try {
    const results = await fsp.readdir(path, { recursive });
    if (process.platform === "win32") {
      return results.map((p) => p.replaceAll("\\", "/"));
    }
    return results;
  } catch (err) {
    //console.error(err); // Happens when the folder doesn't exist, we don't care
    return [];
  }
}
