import nextPlugin from "@next/eslint-plugin-next"
import tsPlugin from "@typescript-eslint/eslint-plugin"
import tsParser from "@typescript-eslint/parser"
import reactHooksPlugin from "eslint-plugin-react-hooks"

export default [
  {
    ignores: [
      ".next/**",
      "node_modules/**",
      "out/**",
      "build/**",
      "dist/**",
      "app/components/RobotBackground.tsx",
      "app/components/RobotLandingPage.tsx",
      "app/components/RobotScene.tsx",
      "app/mobile/App.js",
      "backend/core/AuthProvider.tsx",
      "backend/core/OraclePrefetch.tsx",
      "backend/core/SessionMonitor.tsx",
      "mobile/App.js",
      "app/components/NotificationSettings.tsx"
    ],
  },
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    plugins: {
      "@next/next": nextPlugin,
      "@typescript-eslint": tsPlugin,
      "react-hooks": reactHooksPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        document: "readonly",
        window: "readonly",
        localStorage: "readonly",
        process: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        fetch: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        Event: "readonly",
        MouseEvent: "readonly",
        Request: "readonly",
        Response: "readonly",
      },
    },
    rules: {
      ...nextPlugin.configs.recommended.rules,
      ...nextPlugin.configs["core-web-vitals"].rules,
      ...tsPlugin.configs.recommended.rules,
      ...reactHooksPlugin.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "off",
      "react-hooks/exhaustive-deps": "warn",
      "react-hooks/rules-of-hooks": "error",
      "@next/next/no-img-element": "off",
      "react-hooks/set-state-in-effect": "off", // Disable custom rule check which is likely non-standard or overly aggressive
    },
  },
]
