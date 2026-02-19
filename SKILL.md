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

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli mass-times <location> [--page N] [--limit N]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli mass-times "Boston, MA" --limit 5`
- **Output:** JSON with `location_searched`, `coordinates`, `page`, `total_results`, and `churches` array
- **Church fields:** name, distance, address (street/city/state/postal_code), phone, email, worship_times (array of day/time), diocese_name, pastor
- **Note:** Churches are sorted by distance from the searched location. Uses OpenStreetMap Nominatim for geocoding.

### 📖 Daily Bible Readings
Get the complete daily Mass readings including First Reading, Responsorial Psalm, Second Reading (when applicable), Gospel Acclamation, and Gospel.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli readings [--date YYYY-MM-DD] [--titles "Title1" "Title2" ...]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli readings --date 2026-12-25`
- **Example (filter):** `~/.openclaw/skills/usccb_cli/usccbcli readings --titles "Gospel" "Reading 1"`
- **Output:** JSON with `date`, `url`, `liturgical_date`, and `readings` array
- **Readings fields:** title (e.g., "Reading 1", "Gospel"), citation (e.g., "Jn 3:16-21"), text (full reading text)
- **Note:** Defaults to today's date if no date specified. Use --titles to filter for specific readings only.

### 🙏 Search Prayers
Search for Catholic prayers and devotions on the USCCB website.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli search-prayers <query> [--language {en,es}] [--limit N] [--type "Type"] [--office "Office"]`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli search-prayers "Hail Mary"`
- **Example (Spanish):** `~/.openclaw/skills/usccb_cli/usccbcli search-prayers "Ave María" --language es`
- **Output:** JSON with `query`, `language`, `total_results`, and `prayers` array
- **Prayer fields:** title, url, excerpt
- **Note:** Language defaults to 'en' (English). Use 'es' for Spanish prayers. Limit accepts 20, 50, or 100 (default: 20).

### 📿 Get Prayer Text
Retrieve the full text of a specific prayer by URL.

- **Command:** `~/.openclaw/skills/usccb_cli/usccbcli get-prayer <url>`
- **Example:** `~/.openclaw/skills/usccb_cli/usccbcli get-prayer "https://www.usccb.org/prayers/hail-mary"`
- **Output:** JSON with `title`, `url`, and `text` (full prayer text with line breaks preserved)
- **Note:** URL must be from USCCB.org prayers section

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
All commands output JSON to stdout only. Errors go to stderr. Exit code 1 on errors.

Perfect for shell scripts, automation, and LLM integration.

## Response Formatting Tips

When presenting results to users:
- **Mass Times:** Format as a list with church name, distance, address, and Mass schedule
- **Readings:** Show liturgical date first, then present each reading with its title and citation
- **Prayers:** For searches, show titles and excerpts. For full prayers, preserve line breaks and formatting
- **Errors:** Check stderr for error messages and explain to user in plain language

## Notes
- Mass times data comes from updateparishdata.org API
- Readings are scraped from bible.usccb.org (USCCB official site)
- Prayers are from www.usccb.org/prayers
- All content is publicly available on USCCB website
- Respect USCCB terms of service when using this skill

---

✝️ **Christ is King** ✝️
