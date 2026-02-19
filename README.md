<div align="center" style="background: rgba(6, 33, 55, 0.95); padding: 40px; margin-bottom: 30px;">
  <img src="images/usccb-logo.svg" alt="USCCB Logo" width="400">
</div>

# 📖 USCCB CLI

Command-line tool for accessing daily Catholic Mass readings and prayers from the United States Conference of Catholic Bishops (USCCB).

## 🙏 Overview

This skill provides scrapers that interact with the USCCB website to retrieve:
- ⛪ **Mass Times**: Find nearby Catholic churches with Mass schedules and contact information
- 📖 **Daily Bible Readings**: Complete Mass readings including First Reading, Psalm, Gospel, etc.
- 🙏 **Prayers**: Search and retrieve Catholic prayers and devotions in English or Spanish

All tools output clean JSON to stdout for easy integration with automation tools and LLMs.

## 🛠️ Installation

### Requirements
- Python 3.6+
- pip

### Setup
```bash
cd ~/.openclaw/skills/usccb_cli
pip install -r requirements.txt
chmod +x usccbcli  # Make CLI executable
```

## 📚 Usage Examples

### ⛪ Mass Times

Find Catholic churches near a location with Mass schedules and contact information.

**Find churches near a city:**
```bash
./usccbcli mass-times "Boston, MA"
```

**Find churches with pagination:**
```bash
./usccbcli mass-times "New York, NY" --page 2
```

**Limit number of results:**
```bash
./usccbcli mass-times "Chicago, IL" --limit 5
```

**Output:**
```json
{
  "location_searched": "Boston, MA",
  "coordinates": {
    "latitude": 42.3554334,
    "longitude": -71.060511
  },
  "page": 1,
  "total_results": 30,
  "churches": [
    {
      "name": "Cathedral of the Holy Cross",
      "distance": 0.5,
      "church_address_street": "1400 Washington Street",
      "church_address_city": "Boston",
      "church_address_state": "MA",
      "church_address_postal_code": "02118",
      "church_contact_phone": "(617) 542-5682",
      "church_contact_email": "info@holycrossboston.org",
      "church_worship_times": [
        {
          "day": "Sunday",
          "time": "8:00 AM, 10:00 AM, 12:00 PM, 5:30 PM"
        },
        {
          "day": "Monday-Saturday",
          "time": "9:00 AM, 12:05 PM"
        }
      ],
      "diocese_name": "Archdiocese of Boston",
      "pastor": "Rev. John Smith"
    }
  ]
}
```

**Arguments:**
- `location`: Required. City, address, or ZIP code to search near
- `--page N`: Optional. Page number for pagination (default: 1)
- `--limit N`: Optional. Maximum number of churches to return

**Note:** Churches are sorted by distance from the searched location. The API uses OpenStreetMap's Nominatim service for geocoding (no API key required).

---

### 📖 Daily Bible Readings

Get the complete daily Mass readings for any date.

**Get today's readings:**
```bash
./usccbcli readings
```

**Get readings for a specific date:**
```bash
./usccbcli readings --date 2026-12-25
```

**Filter for specific readings only:**
```bash
./usccbcli readings --titles "Gospel" "Reading 1"
```

**Output:**
```json
{
  "date": "2026-12-25",
  "url": "https://bible.usccb.org/bible/readings/122526.cfm",
  "liturgical_date": "The Nativity of the Lord (Christmas) - Mass During the Day",
  "readings": [
    {
      "title": "Reading 1",
      "citation": "Is 52:7-10",
      "text": "How beautiful upon the mountains are the feet of him who brings glad tidings..."
    },
    {
      "title": "Responsorial Psalm",
      "citation": "Ps 98:1, 2-3, 3-4, 5-6",
      "text": "R. All the ends of the earth have seen the saving power of God..."
    },
    {
      "title": "Reading 2",
      "citation": "Heb 1:1-6",
      "text": "Brothers and sisters: In times past, God spoke in partial and various ways..."
    },
    {
      "title": "Gospel",
      "citation": "Jn 1:1-18",
      "text": "In the beginning was the Word, and the Word was with God, and the Word was God..."
    }
  ]
}
```

**Arguments:**
- `--date YYYY-MM-DD`: Optional. Get readings for specific date (defaults to today)
- `--titles "Title1" "Title2" ...`: Optional. Filter to return only specific readings

---

### 🙏 Search Prayers

Search for Catholic prayers and devotions.

**Search for prayers in English (default):**
```bash
./usccbcli search-prayers "Hail Mary"
```

**Search for prayers in Spanish:**
```bash
./usccbcli search-prayers "Ave María" --language es
```

**Limit search results:**
```bash
./usccbcli search-prayers "peace" --limit 10
```

**Filter by prayer type or committee:**
```bash
./usccbcli search-prayers "Advent" --type "Seasonal Prayer"
```

**Output:**
```json
{
  "query": "Hail Mary",
  "language": "en",
  "total_results": 5,
  "prayers": [
    {
      "title": "Hail Mary",
      "url": "https://www.usccb.org/prayers/hail-mary",
      "excerpt": "The Hail Mary is a traditional Catholic prayer asking for the intercession of Mary..."
    },
    {
      "title": "The Rosary",
      "url": "https://www.usccb.org/prayers/rosary",
      "excerpt": "The Rosary is a meditation on the life of Christ through the eyes of Mary..."
    }
  ]
}
```

**Arguments:**
- `query`: Required. Search term for prayers
- `--language {en,es}`: Optional. Language filter - 'en' for English, 'es' for Spanish (default: en)
- `--limit N`: Optional. Maximum number of results (valid values: 20, 50, or 100, default: 20)
- `--type "Type"`: Optional. Filter by prayer type
- `--office "Office"`: Optional. Filter by USCCB office/committee

**Note:** Due to USCCB API limitations, `--limit` only accepts values of 20, 50, or 100. Other values will be rounded to the nearest valid option.

---

### 📿 Get Prayer Text

Retrieve the full text of a specific prayer.

**Get a prayer by URL:**
```bash
./usccbcli get-prayer "https://www.usccb.org/prayers/hail-mary"
```

**Output:**
```json
{
  "title": "Hail Mary",
  "url": "https://www.usccb.org/prayers/hail-mary",
  "text": "Hail Mary, full of grace,\nthe Lord is with thee.\nBlessed art thou amongst women,\nand blessed is the fruit of thy womb, Jesus.\n\nHoly Mary, Mother of God,\npray for us sinners,\nnow and at the hour of our death.\nAmen."
}
```

**Arguments:**
- `url`: Required. Full URL to the prayer page on USCCB.org

---

## 🛒 Typical Workflows

### 📖 Daily Scripture Reading
- **Get today's readings**: `./usccbcli readings`
- **Get Gospel only**: `./usccbcli readings --titles "Gospel"`
- **Parse** the readings array to extract text
- **Present** formatted readings to user

### ⛪ Finding a Church
- **Search by location**: `./usccbcli mass-times "Boston, MA"`
- **Limit results**: `./usccbcli mass-times "Boston, MA" --limit 5`
- **Extract** church names, addresses, phone numbers
- **Display** Mass times and contact info

### 🙏 Prayer Discovery
- **Search in English**: `./usccbcli search-prayers "peace"`
- **Search in Spanish**: `./usccbcli search-prayers "paz" --language es`
- **Get full text**: `./usccbcli get-prayer "https://www.usccb.org/prayers/hail-mary"`
- **Present** prayer text for devotion

### 📅 Weekly Planning
- **Loop through dates** to get readings for the week
- **Extract** Gospel citations for quick reference
- **Plan** scripture study or homily preparation

---

## 💻 Output Format

All commands:
- Output JSON to **stdout only** (no files created)
- Send errors to **stderr**
- Exit with code **1** on errors
- No debug output - only clean JSON or error messages

This makes them perfect for:
- Shell scripts and automation
- LLM/AI agent integration
- CI/CD pipelines
- Catholic app development

---

## ⚠️ Error Handling

**Network Issues:**
```bash
$ ./usccbcli readings
Error: Failed to fetch readings: Connection timeout
```

**Invalid Date:**
```bash
$ ./usccbcli readings --date 2026-13-45
Error: Invalid date format: 2026-13-45. Use YYYY-MM-DD
```

**Location Not Found:**
```bash
$ ./usccbcli mass-times "NonexistentCity12345"
Error: Could not geocode location: NonexistentCity12345
```

**Invalid Prayer URL:**
```bash
$ ./usccbcli get-prayer "https://invalid-url.com"
Error: Failed to fetch prayer content
```

All errors are sent to stderr and commands exit with code 1.

---

## 🤖 Integration with OpenClaw

These tools are designed as an OpenClaw skill. See `SKILL.md` for LLM integration details including:
- Tool calling parameters for all commands
- Example prompts for readings, Mass times, and prayers
- Response formatting guidelines
- Multi-language support details

---

## 🧪 Testing

Run the test suite:
```bash
./run_tests.sh
```

Run with coverage:
```bash
pytest --cov=lib tests/
```

See [tests/README.md](tests/README.md) for more information.

---

## 🌿 Contributing

When modifying the tools:
- Maintain JSON output format for backward compatibility
- Send all errors to stderr
- Exit with code 1 on failures
- Update both SKILL.md and README.md with changes
- Test with real API calls to verify output
- Add unit tests for new functionality

---

## 📜 License

MIT License - See LICENSE file for details.

This project scrapes publicly available content from USCCB.org. Please respect their terms of service and use responsibly.

---

## 🔗 Resources

- [USCCB Daily Readings](https://bible.usccb.org/bible/readings)
- [USCCB Prayers](https://www.usccb.org/prayers)
- [USCCB Website](https://www.usccb.org)
- Scripture texts are from the New American Bible, revised edition © 2010, 1991, 1986, 1970 Confraternity of Christian Doctrine, Washington, D.C.

---

## 📋 Command Reference

| Command | Description | Required Args | Optional Args |
|---------|-------------|---------------|---------------|
| `readings` | Get daily Mass readings | None | `--date`, `--titles` |
| `mass-times` | Find nearby churches | `location` | `--page`, `--limit` |
| `search-prayers` | Search for prayers | `query` | `--language`, `--limit`, `--type`, `--office` |
| `get-prayer` | Get full prayer text | `url` | None |

---

## ⚖️ Disclaimer

This project is **not affiliated with or endorsed by** the United States Conference of Catholic Bishops (USCCB). It is an independent tool created by a Catholic nerd who uses [OpenClaw](https://openclaw.ai/) to access publicly available USCCB resources. All content is sourced from the official USCCB website and remains their intellectual property. Please use this tool respectfully and in accordance with USCCB's terms of service.

---

✝️ **Christ is King** ✝️
