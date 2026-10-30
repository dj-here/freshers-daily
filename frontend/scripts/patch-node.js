const fs = require('fs');
const path = require('path');

const candidates = [
  path.resolve(__dirname, '../node_modules/next/dist/bin/next'),
  path.resolve(__dirname, '../node_modules/.pnpm/next@14.2.35_react-dom@18.3.1_react@18.3.1__react@18.3.1/node_modules/next/dist/bin/next'),
  path.resolve(__dirname, '../node_modules/.pnpm/next@14.2.35_react-dom@18.3.1_react@18.3.1/node_modules/next/dist/bin/next')
];

let patched = false;
for (const p of candidates) {
  if (fs.existsSync(p)) {
    let content = fs.readFileSync(p, 'utf8');
    if (content.includes('"18.17.0"')) {
      content = content.replace('"18.17.0"', '"18.13.0"');
      fs.writeFileSync(p, content, 'utf8');
      console.log(`[FreshersDaily] Patched ${p} for Node 18.13+`);
      patched = true;
    }
  }
}

// Find any remaining next/dist/bin/next
const pnpmDir = path.resolve(__dirname, '../node_modules/.pnpm');
if (fs.existsSync(pnpmDir)) {
  const dirs = fs.readdirSync(pnpmDir);
  for (const d of dirs) {
    if (d.startsWith('next@')) {
      const bin = path.join(pnpmDir, d, 'node_modules/next/dist/bin/next');
      if (fs.existsSync(bin)) {
        let content = fs.readFileSync(bin, 'utf8');
        if (content.includes('"18.17.0"')) {
          content = content.replace('"18.17.0"', '"18.13.0"');
          fs.writeFileSync(bin, content, 'utf8');
          console.log(`[FreshersDaily] Patched ${bin} for Node 18.13+`);
          patched = true;
        }
      }
    }
  }
}

if (!patched) {
  console.log('[FreshersDaily] Next.js bin was already patched or not found.');
}
