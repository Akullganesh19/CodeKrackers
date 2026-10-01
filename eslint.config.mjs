import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "backend/core/fetch-interceptor.ts",
    "app/components/RobotBackground.tsx",
    "app/components/RobotLandingPage.tsx",
    "app/components/RobotScene.tsx",
    "app/components/OpenClawStatus.tsx",
    "app/mobile/App.js",
    "app/components/Topbar.tsx",
    "app/proxy.ts"
  ]),
]);

export default eslintConfig;
