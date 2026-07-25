import fs from 'fs';

let content = fs.readFileSync('components/PhantomInfrastructure.tsx', 'utf-8');

const targetMethod = `      const method = (init?.method || 'GET').toUpperCase();`;
const replaceMethod = `      const method = (input instanceof Request ? input.method : init?.method || 'GET').toUpperCase();`;
content = content.replace(targetMethod, replaceMethod);

const targetUrl = `      // 2. Normalize URL (safest way across types)\n      const url = new Request(input, init).url;`;
const replaceUrl = `      // 2. Normalize URL safely without consuming Request body\n      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;`;
content = content.replace(targetUrl, replaceUrl);

fs.writeFileSync('components/PhantomInfrastructure.tsx', content);
