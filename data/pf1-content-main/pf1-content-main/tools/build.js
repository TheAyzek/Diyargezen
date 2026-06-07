/* eslint-disable no-undef */
import fsp from "node:fs/promises";
import path from "node:path";
import url from "node:url";
import yargs from "yargs";
import { readJSON, writeJSON } from "./lib.mjs";

const __dirname = url.fileURLToPath(new URL(".", import.meta.url));
const __filename = url.fileURLToPath(import.meta.url);
const PACK_CACHE = "../release/";

/**
 * Helper function that resolves a path from the pack build directory
 *
 * @param {...string} file - String path segments
 * @returns {string} The resolved path
 */
const resolveCache = (...file) => path.resolve(__dirname, PACK_CACHE, ...file);

[
  "module.json",
  "OGL.txt",
  "Legal.txt",
  "LICENSE.md",
  "CREDITS.md",
  "CHANGELOG.md",
  "CONTRIBUTING.md",
  "README.md",
  "pf-content.js",
].forEach(async (file) => {
  await fsp.copyFile(path.resolve(`${__dirname}/../${file}`), resolveCache(file));
});

// Copy the module assets
await fsp.cp(path.resolve(`${__dirname}/../assets`), resolveCache("assets"), { recursive: true });

// Only handle commands if this script was executed directly
console.log("argv is ", process.argv);
if (process.argv[1] === __filename || process.argv[2] === "upgrade") {
  yargs(process.argv.slice(2))
    .demandCommand(0, 1)
    .command({
      command: "upgrade",
      describe: "When run, this command will upgrade the module version in the module.json file as it's building",
      handler: async (argv) => {
        let tier = "patch";
        const tierIndex = argv["_"].indexOf("upgrade");
        if (tierIndex !== -1) {
          tier = argv["_"][tierIndex + 1];
        }

        console.log("Upgrading version to ", tier);
        await upgradeVersion(tier);
      },
    })
    .parse();
}

/**
 * Loads the module manifest file.
 *
 * @param {string} tier - The tier of the upgrade
 * @returns {Promise<*>} The module manifest
 */
async function upgradeVersion(tier = "patch") {
  const manifest = await readJSON(resolveCache("module.json"));
  const version = manifest.version;
  const parts = version.split(".");
  const major = parseInt(parts[0]);
  const minor = parseInt(parts[1]);
  const patch = parseInt(parts[2] || 0);

  switch (tier) {
    case "major":
      manifest.version = `${major + 1}.0.0`;
      break;
    case "minor":
      manifest.version = `${major}.${minor + 1}.0`;
      break;
    case "patch":
      manifest.version = `${major}.${minor}.${patch + 1}`;
      break;
  }

  await writeJSON(resolveCache("module.json"), manifest);
}
