#!/usr/bin/env node
/**
 * Post-generation fixup for hooks.ts.
 * Removes unused imports that the template generator emits unconditionally.
 */
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const hooksFile = join(__dirname, '../src/lib/api/generated/hooks.ts');

let content = readFileSync(hooksFile, 'utf-8');

// Check which imports are actually used in the file body (beyond the import line itself)
const importLine = content.match(/^import \{[^}]+\} from '@tanstack\/react-query';$/m);
if (importLine) {
  const usedImports = [];
  const possibleImports = ['useQuery', 'useMutation', 'useQueryClient'];

  for (const imp of possibleImports) {
    // Count occurrences beyond the import line
    const regex = new RegExp(`\\b${imp}\\b`, 'g');
    const allMatches = content.match(regex);
    const importMatches = importLine[0].match(regex);
    const bodyCount = (allMatches?.length || 0) - (importMatches?.length || 0);
    if (bodyCount > 0) {
      usedImports.push(imp);
    }
  }

  if (usedImports.length > 0 && usedImports.length < possibleImports.length) {
    const newImportLine = `import { ${usedImports.join(', ')} } from '@tanstack/react-query';`;
    content = content.replace(importLine[0], newImportLine);
  }
}

// Remove unused type imports
if (!content.includes('components[') && !content.includes('components.')) {
  // Check if 'components' is used anywhere besides the import
  const componentUses = content.match(/\bcomponents\b/g);
  if (componentUses && componentUses.length <= 1) {
    content = content.replace(
      /import type \{ paths, components \} from '\.\/types';/,
      "import type { paths } from './types';"
    );
  }
}

// Re-export types needed by infrastructure hooks
if (!content.includes("export type { paths, components }") &&
    !content.includes("Re-export types")) {
  content = content.replace(
    /import type \{ paths(?:, components)? \} from '\.\/types';/,
    (match) => `${match}\n\n// Re-export types used by infrastructure hooks\nexport type { paths, components } from './types';`
  );
}

writeFileSync(hooksFile, content);
