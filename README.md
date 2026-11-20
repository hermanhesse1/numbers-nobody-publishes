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

**Proxy:** the best one from Part 2, the average headcount a company reports in its annual accounts. In Romania that is the employee line on the balance sheet filed with the Ministry of Finance.

**The three numbers** (ONRC snapshot of 8 Dec 2025; [code/register.py](code/register.py), output in [output/register_counts.txt](output/register_counts.txt)):

| | |
|---|---|
| Companies inside the line | **1,296,440** |
| Share of the living register | **74.2%** (of 1,747,958) |
| Largest industries (CAEN division) | **47 Retail trade** (476,708), **46 Wholesale trade** (371,164), **49 Land transport** (250,016) |

**How I drew the lines:**
1. **Living.** The register holds 4,111,567 companies. I count a company as living if it carries status `1048 funcţiune` (operating) and no status meaning struck off, dissolved, in liquidation, insolvent, suspended, or abandoned by its owners. That leaves 1,747,958. The dead statuses are matched by keyword against the official list of status codes, and the script prints the codes it keeps, so you can disagree code by code.
2. **Inside the proxy.** The line is drawn on legal form, not activity code: what decides whether a headcount exists is whether the company must file accounts. Companies (SRL, SA, SNC, SCS, SCA), cooperatives and autonomous public companies are inside. Sole traders and family businesses (PFA, II, IF: 450,256 living) file a personal tax return with no headcount, so they are outside.
3. **Industry.** The register lists *authorised* activities with no "main activity" flag, and stores them sorted by code. My first attempt, taking each company's first-listed code, therefore just picked its lowest code number, so I dropped it. Instead, a company counts in every division where it is authorised. Shares therefore add up to more than 100%, and the ranking tells you breadth of authorisation, not where revenue is earned. 289k companies have only the new Rev.3 (2025) codes and are counted under those. 109k have no activity code at all.

**Where the line is weak:**
- **The 74% is an upper bound.** Being required to file is not the same as filing, and filing is not the same as having staff. Many SRLs report 0 employees, and the register cannot show that.
- **Some "living" companies are probably zombies.** 139,445 of the 1.30m carry "registered office expired" or "directors' mandate expired". Dropping them gives 1,156,995 (66.2%).
- **Retail is inflated.** Romanian SRLs routinely add retail to their authorised activities just in case.
- **What would turn the bound into a measured number:** joining on CUI to the Ministry of Finance file `web_uu_an2024` would show who actually filed with employees above zero.
- **Reproducibility:** the data.gov.ro server sends no file size and silently cut two downloads short. The script's inputs should be checked against the advertised sizes (675 MB for `od_firme.csv`, 400 MB for `od_caen_autorizat.csv`).

## Cut list

**Where the time went:**
- **Part 1, matching 23 entities by hand (most of it).** Deciding *which* entity a name means turned out to be the real work.
- **Part 2, sourcing the figures and building four proxy derivations.**
- **Part 5, mostly fighting a download server** that silently truncated files.

**What I deliberately did not do:**
- **Rows beyond the sample.** The other 77 would have added volume, not new lessons. The sample already covers every block A–N.
- **The quant route.** The sample is built around traps, such as group versus entity, a brand versus a legal entity, and dead companies. A model trained on Romanian SMEs cannot see those.
- **Opening every primary document.** Several figures come from press coverage of a filing (Google Ireland, FintechOS) or from a jobs portal (NHS GGC), not from the filing itself. They are labelled as such.
- **Sourcing the recalled assumptions.** These are hotel occupancy and room prices, utility customers per employee, and revenue per bakery employee. They are marked in the code. Sourcing them is the next hour of work, not a reason to hide the derivations.
- **Calibrating the ranges.** The widths are judgment, not measured error (see the third debate).
- **Parsing the Companies House bulk accounts, and joining the register to `web_uu_an2024`.** Both are the obvious next step and are named in Parts 3 and 5. Neither was needed to show that the recipe works.

## Debate topics

### Where I would not trust AI tools

- **Any number or identity claim it cannot point to.** During this work, AI-summarised search results:
  - offered Kellanova figures next to WK Kellogg's;
  - quoted a lead-gen database's $5bn for a hotel chain with about 150 hotels;
  - would have accepted Revelio's 122,763 "Temasek employees".
- **Its own logic, too.** My first industry rule took the "first-listed" activity code. It looked sensible until I noticed the file is sorted by code.
- **How I catch it:**
  - every figure needs a URL that a second fetch confirms;
  - every derived number gets a physical sanity check, such as revenue per room or per employee;
  - every "it worked" gets checked against something independent. The downloads exited with code 0 while two of three files were truncated, and only comparing byte counts with the advertised sizes caught it.

### Knowing the dataset is wrong at scale

There is no complete answer sheet, but there are partial ones.

- **Score each proxy on companies that do report.** UK and Romanian filers, listed companies, and companies acquired with disclosed financials make a labelled subset for every recipe. If a proxy is wrong there, it is wrong everywhere.
- **Look for internal contradictions:**
  - a subsidiary larger than its parent;
  - revenue per employee outside the range for its industry;
  - a company whose size jumps tenfold between refreshes with no corporate event behind it.
- **Watch how often independent sources disagree.** When the share of rows where two independent sources disagree starts rising, the pipeline has drifted, even if no single row looks wrong.

### Ranges you would bet on

- **How to set the widths:** run each recipe on companies whose real number is known (the labelled subset above) and take the empirical error quantiles per proxy and per company type. An 80% range is then the 10th–90th percentile of measured error, not a feeling.
- **How to tell a year later whether the ranges were honest:** collect the figures that surface in the meantime (new filings, IPO prospectuses, acquisition disclosures) and check what share fell inside their ranges. If 80% ranges catch 55%, they were dishonest. If they catch 98%, they were too wide to price on. Either way, the fix is to the width for that proxy, not to individual rows.
