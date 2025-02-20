// Licensed under the MIT License
// https://github.com/craigahobbs/javascript-build/blob/main/LICENSE

import globals from 'globals';
import js from '@eslint/js';


export default [
    js.configs.all,
    {
        'languageOptions': {
            'ecmaVersion': 2022,
            'globals': {
                ...globals.browser
            }
        },
        'rules': {
            // Override
            'func-style': ['error', 'declaration', {'allowArrowFunctions': true}],
            'function-paren-newline': ['error', 'consistent'],
            'max-len': ['error', {'code': 140, 'tabWidth': 4}],
            'no-unused-vars': ['error', {'argsIgnorePattern': '^_'}],
            'padded-blocks': ['error', 'never'],
            'quotes': ['error', 'single', {'avoidEscape': true, 'allowTemplateLiterals': true}],

            // Disabled
            'array-bracket-newline': 'off',
            'array-element-newline': 'off',
            'capitalized-comments': 'off',
            'complexity': 'off',
            'function-call-argument-newline': 'off',
            'init-declarations': 'off',
            'lines-around-comment': 'off',
            'max-classes-per-file': 'off',
            'max-depth': 'off',
            'max-lines': 'off',
            'max-lines-per-function': 'off',
            'max-params': 'off',
            'max-statements': 'off',
            'multiline-comment-style': 'off',
            'multiline-ternary': 'off',
            'newline-per-chained-call': 'off',
            'no-await-in-loop': 'off',
            'no-continue': 'off',
            'no-extra-parens': 'off',
            'no-implicit-coercion': 'off',
            'no-inline-comments': 'off',
            'no-lonely-if': 'off',
            'no-magic-numbers': 'off',
            'no-mixed-operators': 'off',
            'no-negated-condition': 'off',
            'no-nested-ternary': 'off',
            'no-plusplus': 'off',
            'no-ternary': 'off',
            'no-undefined': 'off',
            'no-underscore-dangle': 'off',
            'no-use-before-define': 'off',
            'object-curly-newline': 'off',
            'object-property-newline': 'off',
            'object-shorthand': 'off',
            'one-var': 'off',
            'prefer-named-capture-group': 'off',
            'require-unicode-regexp': 'off',
            'sort-keys': 'off',
            'sort-vars': 'off',
            'space-before-function-paren': 'off'
        }
    }
];
