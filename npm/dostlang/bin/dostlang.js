#!/usr/bin/env node

const { spawnSync } = require("node:child_process");
const path = require("node:path");

function resolvePython() {
  const candidates = [
    ["python3", []],
    ["python", []],
    ["py", ["-3"]]
  ];

  for (const [cmd, args] of candidates) {
    const check = spawnSync(cmd, [...args, "--version"], { stdio: "ignore" });
    if (check.status === 0) {
      return { cmd, args };
    }
  }
  return null;
}

const python = resolvePython();
if (!python) {
  console.error(
    "dostlang error: Python 3 is required but was not found. Install Python 3 and retry."
  );
  process.exit(1);
}

const packageRoot = path.resolve(__dirname, "..");
const runtimePath = path.join(packageRoot, "python");
const existingPythonPath = process.env.PYTHONPATH;
const mergedPythonPath = existingPythonPath
  ? `${runtimePath}${path.delimiter}${existingPythonPath}`
  : runtimePath;

const result = spawnSync(
  python.cmd,
  [...python.args, "-m", "worklib.cli", ...process.argv.slice(2)],
  {
    stdio: "inherit",
    env: {
      ...process.env,
      PYTHONPATH: mergedPythonPath
    }
  }
);

if (result.error) {
  console.error(`dostlang error: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
