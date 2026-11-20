# Estimating revenue and headcount for a licensee list

Project, checking wether annual revenue and employee count be produced, with defensible evidence, for a list of 100 licensee names?

## Repo layout

- `data/`: the original list and my tagged version
- `code/`: scripts
- `output/`: the client file

## Sample: what I chose and why

## Part 1: The match

## Part 2: The estimate

**Route: detective.** My Part 1 work was already one company at a time, and the sample was picked for its traps. A model trained on Romanian SMEs cannot tell me that Google Ireland's revenue is EMEA ad sales, or that Temasek's "122,763 employees" are its portfolio companies' staff.

Output: [output/sample_estimates.csv](output/sample_estimates.csv), produced by [code/estimates.py](code/estimates.py). Every input, source and proxy calculation lives in that script, so you can change an assumption and rerun it.

### What travels with every figure

A number on its own does not survive the client's analyst. Each row carries:

- **scope**: which entity or group the number describes. Most of the risk sits here, not in the arithmetic.
- **metric**: revenue, or something more honest. That is portfolio value for Temasek and budget for the NHS board. For Google Ireland revenue is shown but marked as the wrong measure.
- **basis**: `REPORTED`, `REPORTED_SEGMENT`, `SELF_DECLARED`, `PROXY` or `NONE`.
- **period**: the date the number belongs to.
- **point + low/high**: the range is zero-width only when the number comes straight from a filing.
- **sources**, a **derivation** you can disagree with, **how wrong could this be**, and a **client action**.

### Results on the 23-entity sample

| Basis | Revenue | Employees |
|---|---|---|
| Reported (filing, or a segment of one) | 10 | 8 |
| Self-declared (company page, undated) | 1 | 4 |
| Proxy (derived here) | 3 | 3 |
| Nothing delivered, deliberately | 9 | 8 |

The nine revenue gaps are: five unmatched or dead rows (Credit Mutuel, Buchbender, Meridian, Wirecard, Bakery Bakery), two non-entities (Old Spice, Steyn), one company that never filed (Alin) and Blue Origin. For Blue Origin I deliver headcount only, because no source separates its revenue from Bezos funding.

### Proxy ledger: what I tried, what survived, how far it scales

| Proxy | Used on | Verdict | Reach at scale |
|---|---|---|---|
| **UK micro accounts iXBRL tag `AverageNumberEmployeesDuringPeriod`** | Margot Bakery: 13 staff, filed although turnover is not | **Kept: the best find.** It turns a "no data" micro company into a reported headcount | Every UK company that files accounts. Companies House publishes them free as a bulk iXBRL download, so this is a parser, not research |
| Romanian Ministry of Finance balance sheet (turnover + employees) | Yazaki, FintechOS, Panificatie Moldova | Kept | Every Romanian filer: the dataset behind the quant route |
| Peer revenue per unit of capacity (Hapag-Lloyd and Maersk: ~$8,650 per TEU) | MSC: ~$69bn (57–82) | Kept. The two peers agree within 1%, and a 2022 figure fits once rates are rescaled | Capacity industries only: shipping (TEU), airlines (seats), hotels (rooms), hospitals (beds). Few companies, but the biggest private ones |
| Rooms × 365 × occupancy × ADR | Drury: ~$1.07bn (0.79–1.47) | Kept. Hotel count and staff are sourced; occupancy and ADR are assumptions | Any hotel group that lists its properties |
| Customers ÷ customers-per-employee | Brooklyn Union Gas: ~1,900 staff (1,260–2,890) | Kept, weakly: both inputs are assumptions | Regulated utilities, which report customer counts to regulators |
| LinkedIn-based trackers (Revelio, Statista) | Siemens Gamesa: 27,300 | Kept for an operating company (two trackers agree within 3%). **Discarded for Temasek**: 122,763 against its own ~960 | Universal, but only safe where the legal entity and the people are the same thing. Wrong for holding, investment and brand rows |
| Company-declared figures ("over 6,500 team members") | Drury, MSC, NHS GGC, Temasek | Kept as `SELF_DECLARED`; undated, so widened | Most mid-size and large companies |
| Lead-gen database revenue (LeadIQ, RocketReach, Owler) | Drury | **Discarded.** LeadIQ's $5bn implies ~$500k per room per year, which is physically impossible | Universal, which is exactly why it is dangerous |
| Old headcounts and brand-sales estimates | Brooklyn Union (3,651, decades old); Old Spice ($564m, 2013) | Discarded: they describe a different time | — |

Two checks ran on every figure.

**Does it describe the matched entity, at the claimed time?** The traps caught this way:
- Kellanova versus WK Kellogg.
- Revelio counting Temasek's portfolio companies as Temasek staff.
- National Grid plc versus the Brooklyn gas utility.
- Google Ireland revenue that is really EMEA ad sales.

**Would I notice if it didn't?** Only where a second, independent number exists. Siemens Gamesa's segments add up to the group total; MSC's TEU-based estimate fits the 2022 figure; Drury's 43 staff per hotel is plausible for the format. Rows with only one source are marked with a single source.

**New finding for Part 1:** Eulerpool lists STEYN HOLDING (B31697) as *lapsed*. The register itself needs checking before that row is called active.

## Part 3: The call (would I ship this?)

**Not as one file. I would ship part of it, labelled.** The 10 revenue and 8 headcount figures read from filings I would put in front of the client's analyst today. That includes Margot Bakery's 13 staff, which comes from a filing even though its revenue is a proxy. The rest I would not ship for pricing:
- **Proxy rows (MSC, Drury, Brooklyn Union headcount):** the arithmetic is shown, but key inputs are still my recalled assumptions, not sourced benchmarks. These are hotel occupancy and room prices, utility customers per employee, and MSC's "other businesses" slice. They are good enough to place a company in a tier, not to quote a number.
- **Rows whose scope I chose:** Siemens Energy, Blue Origin, MSC, National Grid and Old Spice. The number is right for the entity I picked, and nobody yet knows whether that entity signed. Most of the error in this file is a scope error, not an arithmetic error.

**What my checks cannot see:**
1. **Whether the matched entity is the one on the contract.** Only the contract can settle that.
2. **Errors my sources share.** Termene, Totalfirme and Targetare all mirror the same Ministry of Finance data, so three sources agreeing is really one source.
3. **Age.** Several figures are 12–20 months old, and the base is moving (see Part 4).
4. **Whether my ranges are honest.** There is no answer sheet, so a "±20%" is my judgment, not a measured error rate.

**What I would do next, in order of value per hour:**
1. **Ask the client for the counterparty name and address from each contract.** This fixes scope on ~40% of rows, more than any amount of research could.
2. **Parse the free Companies House bulk iXBRL download.** That gives reported headcount for every UK licensee automatically.
3. **Replace each recalled assumption with a sourced benchmark:** STR for hotels, utility 10-Ks for customers per employee.
4. **Calibrate each proxy on companies that do report.** Run the rooms formula on listed hotel groups and the capacity formula on Hapag-Lloyd and Maersk. The measured error then becomes the range width, instead of my judgment.

## Part 4: The room (one insight the client didn't ask for)

**The licensee list goes out of date, and both of the client's fears come from that one cause.** Using the list as it was sent, 15 of the 100 licensees have changed what they are since 2020:
- **7 were absorbed into far larger groups:** VMware into Broadcom, ANSYS into Synopsys, Credit Suisse into UBS, WK Kellogg into Ferrero, HELLA into Forvia, Siemens Gamesa into Siemens Energy, DEGIRO into flatexDEGIRO.
- **6 were carved out of larger parents:** Siemens Energy, Sandoz, Solstice, Amentum, Qnity, Sierra Space.
- **2 were renamed or collapsed:** Currys PC World, Wirecard.

The first group is the "small tier, multinational group" problem: the licensee was priced for what it was when it signed, and is now a subsidiary of a company many times its size. The second group is the reverse, and less obvious. A licence signed by the parent may now be used by a spun-off company that is a separate legal entity and was never priced at all. That is unlicensed use, not underpricing.

Every one of these events is public, dated and machine-readable: SEC 8-Ks, merger notices, register changes. Most enterprise licences also carry an assignment or change-of-control clause, so each event is a contractual moment to re-paper the deal on the client's terms, not a renegotiation they would have to win cold. 15 in about six years is roughly 2.5% of the base a year. The list was probably built to be hard and overstates the true rate, but even a third of that, across a large base, is a steady stream of repricing triggers nobody is watching. The proposal: watch the licensee base for corporate events, not just for size, and reprice at the event rather than at renewal.

## Part 5: The register

## Cut list

## Debate topics

### Where I would not trust AI tools

### Knowing the dataset is wrong at scale

### Ranges you would bet on
