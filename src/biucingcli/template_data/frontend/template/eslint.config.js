import tseslint from "typescript-eslint";
import hooks from "eslint-plugin-react-hooks";
import prettier from "eslint-config-prettier";
export default tseslint.config(
  {
    ignores: [
      "build/**",
      ".react-router/**",
      "node_modules/**",
      ".pnpm-store/**",
      ".pnpm-home/**",
      "playwright-report/**",
      "test-results/**",
    ],
  },
  {
    files: ["**/*.{ts,tsx}"],
    extends: [...tseslint.configs.recommendedTypeChecked],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: { "react-hooks": hooks },
    rules: hooks.configs.recommended.rules,
  },
  prettier,
);
