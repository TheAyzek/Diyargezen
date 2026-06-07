import globals from "globals";
import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";
import jsdoc from "eslint-plugin-jsdoc";

export default [
  js.configs.recommended,
  eslintConfigPrettier,
  jsdoc.configs["flat/recommended-typescript-flavor"],
  {
    ignores: [
      "**/node_modules",

      // Potential Foundry files
      "foundry.js",
      "foundry/",
      "common/",
      "client/",
      "client-esm/",

      // Built files
      "dist/",
      "docs/",
      "packs/",
      "help/",

      // Non-scripts
      "public/templates/",
      "public/lang/",
      "less/",
    ],
  },
  {
    files: ["vite.config.mjs", "tools/**/*.mjs", "getChangelog.js"],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
  },
  {
    languageOptions: {
      globals: {
        ...globals.jquery,
        ...globals.browser,
        AudioHelper: "readonly",
        Collection: "readonly",
        Hooks: "readonly",
        KeyboardManager: "readonly",
        SortingHelpers: "readonly",
        Application: "readonly",
        FormApplication: "readonly",
        Localization: "readonly",
        Game: "readonly",
        Roll: "readonly",
        MersenneTwister: "readonly",
        Compendium: "readonly",
        Canvas: "readonly",
        ContextMenu: "readonly",
        Dialog: "readonly",
        Draggable: "readonly",
        DragDrop: "readonly",
        TextEditor: "readonly",
        FilePicker: "readonly",
        ActorSheet: "readonly",
        ImagePopout: "readonly",
        ItemSheet: "readonly",
        JournalSheet: "readonly",
        Hotbar: "readonly",
        AmbientLightConfig: "readonly",
        TokenConfig: "readonly",
        TokenHUD: "readonly",
        Sidebar: "readonly",
        SidebarTab: "readonly",
        Actor: "readonly",
        ActorDelta: "readonly",
        Actors: "readonly",
        Combat: "readonly",
        Combatant: "readonly",
        Folder: "readonly",
        Item: "readonly",
        Items: "readonly",
        ActiveEffect: "readonly",
        Journal: "readonly",
        JournalEntry: "readonly",
        Macro: "readonly",
        ChatMessage: "readonly",
        Scene: "readonly",
        RollTable: "readonly",
        User: "readonly",
        Ray: "readonly",
        AmbientLight: "readonly",
        MeasuredTemplate: "readonly",
        MeasuredTemplateDocument: "readonly",
        TemplateLayer: "readonly",
        Tile: "readonly",
        Token: "readonly",
        Wall: "readonly",
        ActorDirectory: "readonly",
        ChatLog: "readonly",
        CompendiumDirectory: "readonly",
        CompendiumCollection: "readonly",
        ItemDirectory: "readonly",
        Settings: "readonly",
        Handlebars: "readonly",
        PIXI: "readonly",
        fromUuid: "readonly",
        fromUuidSync: "readonly",
        getTemplate: "readonly",
        loadTemplates: "readonly",
        renderTemplate: "readonly",
        CONST: "readonly",
        FormDataExtended: "readonly",
        CONFIG: "readonly",
        ui: "readonly",
        canvas: "readonly",
        keyboard: "readonly",
        game: "readonly",
        foundry: "readonly",
        TokenDocument: "readonly",
        DocumentSheet: "readonly",
        getDocumentClass: "readonly",
        KeybindingsConfig: "readonly",
        quench: "readonly",
        JQuery: "readonly",
        VisionMode: "readonly",
        Color: "readonly",
        JournalEntryPage: "readonly",
        JournalTextPageSheet: "readonly",
        pf1: "readonly",
        RollPF: "readonly",
        DetectionMode: "readonly",
        DetectionModeInvisibility: "readonly",
        DocumentSheetConfig: "readonly",
        DetectionModeTremor: "readonly",
        OutlineOverlayFilter: "readonly",
        SearchFilter: "readonly",
        TooltipManager: "readonly",
        showdown: "readonly",
        Tour: "readonly",
      },

      ecmaVersion: 2022,
      sourceType: "module",
    },

    settings: {
      jsdoc: {
        mode: "typescript",

        structuredTags: {
          group: {
            type: "text",
          },

          remarks: {
            type: "text",
          },
        },
      },
    },

    rules: {
      "no-useless-call": "error",
      "no-underscore-dangle": "off",
      "import/extensions": "off",
      "class-methods-use-this": "off",
      "linebreak-style": "off",
      "no-mixed-operators": "off",
      "no-param-reassign": "off",
      "no-continue": "off",
      "no-console": "off",

      "prefer-const": [
        "error",
        {
          destructuring: "all",
        },
      ],

      "no-var": "error",

      "no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
        },
      ],

      "newline-per-chained-call": "off",
      "no-plusplus": "off",
      "valid-jsdoc": "off",

      "jsdoc/tag-lines": [
        "error",
        "any",
        {
          startLines: 1,
        },
      ],

      "jsdoc/no-defaults": ["off"],

      "jsdoc/require-jsdoc": [
        "warn",
        {
          enableFixer: false,
        },
      ],

      "jsdoc/no-blank-blocks": [
        "error",
        {
          enableFixer: true,
        },
      ],
    },
  },
];
