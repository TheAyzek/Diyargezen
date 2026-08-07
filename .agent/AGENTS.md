# AGENTS.MD - Diyargezen Project Rules & Scope

## 1. PRODUCT SCOPE & CORE PURPOSE
- **Strict Role:** Diyargezen is strictly a **Pathfinder 1st Edition (PF1e) Character Creator & Builder**.
- **Out of Scope:** The application is **NOT** a VTT (Virtual Tabletop), combat initiative tracker, map engine, or battle simulator.
## 2. TERMINOLOGY STANDARDIZATION & NAMING CONVENTIONS
- **Strict Rule:** All UI labels, API schemas, DB categories, and model responses MUST strictly follow the standardized terms defined in `diyargezen_kurallari.md` Section 9.
- **Weapon Categories:** Simple (`weapons_simple`), Martial (`weapons_martial`), Exotic (`weapons_exotic`), Firearms & Ammo (`weapons_firearm`), Siege Engines (`weapons_siege`).
- **Armor Categories:** Light (`armor_light`), Medium (`armor_medium`), Heavy (`armor_heavy`), Shields (`armor_shield`).
- **Alignments & Skills:** Standardized 9 alignments (LG, NG, CG, LN, TN, CN, LE, NE, CE) and 25 official PF1e skills.

## 3. WEB STANDARDS & VIBECODING PREVENTIONS
- **Strict Rule:** All web implementations MUST strictly adhere to the 20 web standards and SEO / aesthetic rules defined in `diyargezen_kurallari.md` Section 10.
- **Key Mandatory Requirements:** Dynamic page titles (`document.title`), single `<h1>` hierarchy per view, Open Graph meta tags, Schema.org JSON-LD structured data, `llms.txt`, `robots.txt`, `sitemap.xml`, custom high-fantasy 404 page, `sourcemap: false` in production build, and JS code-splitting (`manualChunks`).

