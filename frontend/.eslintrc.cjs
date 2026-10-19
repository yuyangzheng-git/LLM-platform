module.exports = {
  root: true,
  env: { browser: true, es2022: true },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', 'node_modules', '.eslintrc.cjs'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: '18.2' } },
  plugins: ['react-refresh'],
  rules: {
    'react/prop-types': 'off',
    // allow `{ node, ...props }` to drop a prop before spreading the rest
    'no-unused-vars': ['error', { ignoreRestSiblings: true }],
    'no-constant-condition': ['error', { checkLoops: false }],
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
  },
  overrides: [
    {
      files: ['*.config.js', 'src/**/*.test.{js,jsx}'],
      env: { node: true },
    },
  ],
}
