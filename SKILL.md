---
name: usccb
description: Find Catholic churches, get daily Mass readings, and search Catholic prayers from the United States Conference of Catholic Bishops
version: 2.0.0
user-invocable: true
slash-command: usccb

metadata:
  openclaw:
    requires:
      bins: [python3, pip]
    emoji: "⛪"
    category: spiritual
    tags: [usccb, bible, catholic, prayers, readings, scripture, mass, church, parish]
    network: true

  parameters:
    type: object
    properties:
      action:
        type: string
        enum: [mass-times, readings, search-prayers, get-prayer]
        description: "'mass-times' to find churches, 'readings' for daily Bible readings, 'search-prayers' to search prayers, 'get-prayer' to retrieve full prayer text"
      location:
        type: string
        description: "Required for mass-times. City, address, or ZIP code to search near"
      date:
        type: string
        description: "Optional for readings. Date in YYYY-MM-DD format (defaults to today)"
      titles:
        type: array
        items:
          type: string
        description: "Optional for readings. Filter to return only specific readings (e.g., ['Gospel', 'Reading 1'])"
      query:
        type: string
        description: "Required for search-prayers. Search term for prayers"
      url:
        type: string
        description: "Required for get-prayer. Full URL to the prayer page on USCCB.org"
      page:
        type: integer
        description: "Optional for mass-times. Page number for pagination (default: 1)"
      limit:
        type: integer
        description: "Optional for mass-times and search-prayers. Maximum number of results to return"
      language:
        type: string
        enum: [en, es]
        description: "Optional for search-prayers. Language filter - 'en' for English (default), 'es' for Spanish"
      json_output:
        type: boolean
        description: "Optional for all commands. Set to true to get JSON output instead of markdown (default: false for markdown)"
    required: [action]

  examples:
    - prompt: "Find Catholic churches near Boston"
      call: usccb
      args:
        action: mass-times
        location: "Boston, MA"

    - prompt: "Where can I go to Mass in New York?"
      call: usccb
      args:
        action: mass-times
        location: "New York, NY"
        limit: 5

    - prompt: "What are today's Bible readings?"
      call: usccb
      args:
        action: readings

    - prompt: "Show me the Mass readings for Christmas 2026"
      call: usccb
      args:
        action: readings
        date: "2026-12-25"

    - prompt: "What's the Gospel reading for today?"
      call: usccb
      args:
        action: readings
        titles: ["Gospel"]

    - prompt: "Find me a prayer about peace"
      call: usccb
      args:
        action: search-prayers
        query: "peace"

    - prompt: "Search for Spanish prayers about Mary"
      call: usccb
      args:
        action: search-prayers
        query: "María"
        language: es

    - prompt: "Get the Hail Mary prayer"
      call: usccb
      args:
        action: search-prayers
        query: "Hail Mary"
        limit: 1
---

# USCCB Skill

Access Catholic churches, daily Mass readings, and prayers from the United States Conference of Catholic Bishops (USCCB) website.

## When to use this skill

- User asks to find Catholic churches or Mass times near a location
- User wants to see today's Mass readings or the daily Gospel
- User asks about readings for a specific date or feast day
- User wants to search for Catholic prayers or devotions
- User mentions Catholic liturgy, scripture, Bible readings, or prayers
- User wants to know what the Church is reading today
- User asks about specific prayers like the Rosary, Hail Mary, Our Father, etc.
- User wants prayers in Spanish (oraciones en español)

## Scripts

### ⛪ Mass Times
Find Catholic churches near a location with Mass schedules and contact information.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli mass-times <location> [--page N] [--limit N] [--json]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli mass-times "Boston, MA" --limit 5`
- **Output:** Markdown by default with church info organized by headers and bullet lists. Use `--json` for structured JSON.
- **Markdown format:** # header with coordinates, ## for each church, **Bold** labels for fields, Mass times grouped by day
- **JSON fields:** `location_searched`, `coordinates`, `page`, `total_results`, `churches` array
- **Church fields:** name, distance, address (street/city/state/postal_code), phone, url, church_worship_times (array), diocese_name
- **Note:** Churches sorted by distance. Outputs markdown for LLM parsing by default. Use `--json` for programmatic access.

### 📖 Daily Bible Readings
Get the complete daily Mass readings including First Reading, Responsorial Psalm, Second Reading (when applicable), Gospel Acclamation, and Gospel.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli readings [--date YYYY-MM-DD] [--titles "Title1" "Title2" ...] [--json]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli readings --date 2026-12-25`
- **Example (filter):** `~/.openclaw/skills/usccb_cli/usccbcli readings --titles "Gospel" "Reading 1"`
- **Output:** Markdown by default with liturgical date header and readings formatted with ## headers. Use `--json` for structured JSON.
- **Markdown format:** # header with liturgical date, ## for each reading with citation, --- separators
- **JSON fields:** `date`, `url`, `liturgical_date`, `readings` array
- **Readings fields:** title (e.g., "Reading 1", "Gospel"), citation (e.g., "Jn 3:16-21"), text (full reading text)
- **Note:** Defaults to today's date if no date specified. Use --titles to filter for specific readings. Outputs markdown for LLM parsing by default.

### 🙏 Search Prayers
Search for Catholic prayers and devotions.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli search-prayers <query> [--language {en,es}] [--limit N] [--type "Type"] [--office "Office"] [--json]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli search-prayers "Hail Mary"`
- **Example (Spanish):** `~/.openclaw/skills/usccb_cli/usccbcli search-prayers "Ave María" --language es`
- **Output:** Markdown by default with numbered prayer results. Use `--json` for structured JSON.
- **Markdown format:** # header with query and count, ## numbered entries with type and URL
- **JSON fields:** `query`, `search_url`, `total_results`, `prayers` array
- **Prayer fields:** title, url, type
- **Note:** Language defaults to 'en' (English). Use 'es' for Spanish prayers. Limit accepts 20, 50, or 100 (default: 20). Outputs markdown for LLM parsing by default.

### 📿 Get Prayer Text
Retrieve the full text of a specific prayer by URL.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli get-prayer <url> [--json]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli get-prayer "https://www.usccb.org/prayers/hail-mary"`
- **Output:** Markdown by default with # header and prayer text. Use `--json` for structured JSON.
- **Markdown format:** # title, **Source:** URL, --- separators around text
- **JSON fields:** `title`, `url`, `text` (full prayer text with line breaks preserved)
- **Note:** URL must be from USCCB.org prayers section. Outputs markdown for LLM parsing by default.

## Typical Workflows

### Finding a Church
1. User asks: "Where can I go to Mass in Boston?"
2. Call: `usccbcli mass-times "Boston, MA" --limit 5`
3. Parse the churches array to extract names, addresses, phone numbers, and Mass times
4. Present formatted list to user with distances and contact info

### Daily Scripture Reading
1. User asks: "What are today's readings?"
2. Call: `usccbcli readings`
3. Parse the readings array to find Gospel, Psalms, etc.
4. Present formatted readings with liturgical date

### Getting a Specific Prayer
1. User asks: "Can you show me the Hail Mary?"
2. Call: `usccbcli search-prayers "Hail Mary" --limit 1`
3. Get the URL from search results
4. Call: `usccbcli get-prayer <url>`
5. Present the full prayer text

### Spanish Prayers
1. User asks: "Muéstrame oraciones sobre María"
2. Call: `usccbcli search-prayers "María" --language es`
3. Parse results and present Spanish prayers

## Dependencies
- `requests`
- `beautifulsoup4`
- `lxml`

(Install via `pip install -r ~/.openclaw/skills/usccb_cli/requirements.txt`)

## Output Format
All commands output **markdown by default** to stdout for easy LLM parsing. Use `--json` flag for structured JSON output. Errors go to stderr. Exit code 1 on errors.

**Markdown (Default):**
- Optimized for LLM question-answering
- Headers (# ##) for clear structure
- Bold labels (**Field:**) for key-value pairs
- Bullet lists for schedules and times
- Easy to scan and extract specific information

**JSON (with --json flag):**
- Structured data for programmatic access
- Full API response data preserved
- Perfect for app development and automation

Perfect for shell scripts, automation, and LLM integration.

## Response Formatting Tips

When presenting results to users:
- **Mass Times (Markdown):** Parse ## headings for church names, extract Mass times from bullet lists, show distance and contact info
- **Mass Times (JSON):** Parse churches array, format worship_times by day
- **Readings (Markdown):** Show # header with liturgical date, present each ## reading section
- **Readings (JSON):** Show liturgical date first, then present each reading with its title and citation
- **Prayers (Markdown):** For searches, parse ## numbered results. For full prayers, present text preserving line breaks
- **Prayers (JSON):** For searches, show titles and types. For full prayers, preserve line breaks and formatting
- **Errors:** Check stderr for error messages and explain to user in plain language

**Pro Tip:** Use markdown output (default) when answering questions. Use `--json` when you need to extract specific fields programmatically.

## Notes
- Mass times data comes from updateparishdata.org API
- Readings are scraped from bible.usccb.org (USCCB official site)
- Prayers are from www.usccb.org/prayers
- All content is publicly available on USCCB website
- Respect USCCB terms of service when using this skill

---

✝️ **Christ is King** ✝️
