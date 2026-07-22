const fs = require('fs');
const path = require('path');

function replaceInFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  if (!content.includes('fetch(') || filePath.includes('lib/fetch.ts')) return;

  const originalContent = content;

  // Replace fetch with phantomFetch
  content = content.replace(/\bfetch\s*\(/g, 'phantomFetch(');

  // Add import if not present and if phantomFetch was used
  if (content.includes('phantomFetch(') && !content.includes('import { phantomFetch }')) {
    const importStmt = "import { phantomFetch } from '@/app/lib/fetch';\n";
    if (content.startsWith("'use client'") || content.startsWith('"use client"')) {
      content = content.replace(/^(["']use client["'];?\s*)/, `$1${importStmt}`);
    } else {
      content = importStmt + content;
    }
  }

  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Updated ${filePath}`);
  }
}

function traverseDir(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      traverseDir(fullPath);
    } else if (fullPath.endsWith('.ts') || fullPath.endsWith('.tsx')) {
      replaceInFile(fullPath);
    }
  }
}

traverseDir('app');
traverseDir('components');
