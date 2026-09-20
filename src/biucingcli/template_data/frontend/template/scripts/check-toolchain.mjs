#!/usr/bin/env node
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

const version = spawnSync(
  process.execPath,
  ["./node_modules/@typescript/native/bin/tsc", "--version"],
  { encoding: "utf8" },
);
assert.equal(version.status, 0, version.stderr);
assert.match(version.stdout, /^Version 7\./);
const negative = spawnSync(
  process.execPath,
  [
    "./node_modules/eslint/bin/eslint.js",
    "--stdin",
    "--stdin-filename",
    "app/lib/project.ts",
  ],
  {
    input: 'Promise.resolve("unhandled");\n',
    encoding: "utf8",
  },
);
assert.equal(negative.status, 1, negative.stderr || negative.stdout);
assert.match(negative.stdout, /@typescript-eslint\/no-floating-promises/);
console.log("TS 7 compiler and typed-lint negative control passed.");
