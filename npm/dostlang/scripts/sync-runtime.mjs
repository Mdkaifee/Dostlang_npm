import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const packageDir = path.resolve(scriptDir, "..");
const sourceDir = path.resolve(packageDir, "../../src/worklib");
const targetDir = path.resolve(packageDir, "python/worklib");

if (!existsSync(sourceDir)) {
  console.error(`Source runtime not found: ${sourceDir}`);
  process.exit(1);
}

rmSync(targetDir, { recursive: true, force: true });
mkdirSync(targetDir, { recursive: true });
cpSync(sourceDir, targetDir, { recursive: true });

console.log(`Synced runtime files from ${sourceDir} to ${targetDir}`);
