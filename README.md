# Estimating revenue and headcount for a licensee list

Can revenue and headcount be produced, with evidence that survives the client's analyst, for 100 licensee names typed in by sales reps? For 10 of the 23 companies in my sample the answer is yes, straight from a filing; for a few more, yes as an estimate good enough to set a price tier; for the rest, a gap with a reason attached. Most of the risk sits in deciding which legal entity a name on a contract means.

## Repo layout

- `data/`: the client's list, my tagged version, the Part 1 matching file, every proxy assumption with its source in `proxy_inputs.csv`, the companies the proxies were tested on in `proxy_tests.csv`, and `manifest.csv` with the URL, size and SHA-256 of each large input.
- `output/licensee_sizes.xlsx`: the file I would send the client, built by `code/build_workbook.py`.
- `output/sample_estimates.csv`: the same data as CSV, built by `code/estimates.py`.
- `code/register.py` and `output/register_counts.txt`: the Part 5 counts.
- `code/uk_accounts.py` and `output/uk_accounts_counts.txt`: the measured reach of the UK headcount tag.
- `code/uk_licensees.py` and `output/uk_licensees.csv`: the same tag read for the eight UK licensees.
- `code/backtest.py` and `output/backtest.txt`: how often the proxy ranges hold the true figure.
- `code/ixbrl.py`: an XML parser for UK electronic accounts. `code/validate.py`: checks on currencies, registry identifiers with their check digits, dates, ranges and the layout of external files.
- `code/check.py`: checks the outputs, and every README figure against them. `tests/`: unit and integration tests.
- [NOTES.md](NOTES.md): the full proxy ledger, the proxy tests and how the Part 5 line was drawn.

## How to run

```bash
make setup
make all
```

`make test` runs the tests alone. They cover the proxy arithmetic, currency conversion, missing and zero values, inactive companies, dates, registry identifiers, filing formats and changed input layouts, and they fail if a revenue figure looks like thousands entered as millions. GitHub Actions runs the same steps on every push. `code/uk_licensees.py` reads the public Companies House site and needs no key. `code/register.py` and `code/uk_accounts.py` need the large inputs in `big_data/`, which git ignores: `code/fetch_data.py --download` fetches them and checks each against the manifest. The Romanian register files are overwritten by each new snapshot and Companies House keeps a daily file for only 60 days, so a checksum mismatch means a newer version, not a broken one. All scripts were rerun from a clean environment and reproduce the committed outputs exactly.

## Sample

I first tagged all 100 names by why each would be hard to size, giving 14 blocks such as the Siemens family, spin-offs, banks, brands, ambiguous names, dead companies and Luxembourg holdings. The sample takes 23 entities with at least one from every block, weighted to where the client's money is at risk: five micro businesses, where "three people and a mailbox" hides, and two large private groups, where a small-tier licence may cover a multinational. Fastenal is the control case. The other 77 would mostly have repeated traps already in the sample.

## Part 1: The match

Matching a name is easy; deciding which entity the contract means is the work. Seven of the 23 matched to a different legal name, and even exact matches hid traps: Yazaki has three Romanian companies, and Google Ireland's revenue is ad sales for Europe, the Middle East and Africa. Each row of [data/sample_matching.csv](data/sample_matching.csv) has the entity, registration number, status, parent, evidence link and a short note.

| Outcome | n | Rows |
|---|---|---|
| Matched, high confidence | 10 | Fastenal, Siemens Gamesa, Google Ireland, Yazaki Romania, WK Kellogg, Temasek, NHS GGC, Margot Bakery, Alin Panificatie, MSC |
| Matched, medium confidence | 6 | Siemens Energy, Blue Origin, FintechOS, Panificatie Moldova, Brooklyn Union Gas for National Grid, Drury Hotels |
| Matched through its owner | 1 | Old Spice to Procter & Gamble |
| Matched but not operating | 3 | Bakery Bakery, dissolved 2019; Wirecard, insolvent 2020; Steyn Holding, struck off 2020 |
| Ambiguous | 1 | Credit Mutuel, four separate banking groups |
| Not found | 2 | Meridian, Gunter Buchbender Tischlerei |

The two misses are different results. Meridian is one common word that nobody could match. Buchbender probably exists as an unregistered sole trader, which German registers do not list, so my search failed; a town from the contract would settle it. "Matched" also does not mean "operating": Alin Panificatie has never filed accounts and Panificatie Moldova reports no staff.

## Part 2: The estimate

I took the detective route, because the sample was chosen for traps that a model trained on Romanian SMEs cannot see.

The client gets [output/licensee_sizes.xlsx](output/licensee_sizes.xlsx): a summary tab with each licensee's size tier, how sure we are and one action, a full data tab, and a page on how to read it. Every row carries its scope, the metric used, its basis, as-of dates with the age of the older figure, a point value with a low and high, sources, a derivation, an answer to "how wrong could this be" and a client action. Where revenue misleads, the file gives a more honest measure: portfolio value for Temasek, budget for the NHS board, headcount for Google Ireland.

| Basis | Revenue | Employees |
|---|---|---|
| Reported in a filing or a segment of one | 10 | 9 |
| Declared by the company | 1 | 4 |
| Estimated from proxies | 3 | 2 |
| Left blank, with a reason | 9 | 8 |

What survived, in brief; the full ledger with every discarded proxy is in [NOTES.md](NOTES.md):

| Proxy | Verdict | Reach at scale |
|---|---|---|
| UK iXBRL headcount tag in micro accounts | Best find: a reported headcount where turnover is hidden | Measured on 35,144 filings from three days of the free bulk download: 89.0% carry it, 61.7% with staff above zero, while only 1.0% report turnover. About 1.5 million companies a year. Read automatically for the UK licensees: four of the five micro bakeries report a headcount |
| Capacity × revenue per unit at listed peers | MSC about $68bn, Drury about $940m | About 154,000 Romanian companies; see Part 5 |
| Customers per employee at gas utilities | Replaced by Brooklyn Union's own filing | Hundreds per country |
| LinkedIn-based headcount trackers | Kept only where two agree; wrong for holdings | About 69 million company pages |
| Lead-generation database revenue | Discarded: Drury at $5bn means over $500 a room a night | Everywhere, which is the danger |

Three proxies were tested on companies that report. The shipping rate from two carriers under-predicted three others by 8 to 10%, so MSC now uses a six-carrier median. The gas ratio came within 10% on two standalone utilities but was 37% too high on Brooklyn Union Gas, whose filing shows 1,464 staff, because its shared work sits in a separate National Grid company. A ratio learned from standalone firms overstates a subsidiary: the Part 1 scope trap again, inside a proxy. The hotel formula came within 7% on Apple Hospitality and Summit with their own occupancy and room rates, but about 30% low with Drury's segment inputs, so for Drury the inputs, not the formula, carry the risk.

## Part 3: The call

I would ship part of it, labelled. The 10 revenue and 9 headcount figures from filings can go to the client's analyst today. I would hold back the MSC and Drury estimates, which rest on peer and segment data and are good for a tier rather than a price, and the rows where I chose the scope, such as Siemens Energy and MSC, because nobody yet knows which entity signed.

My checks cannot see whether a match is the company on the contract, or errors my sources share, since three Romanian sites copy one ministry file. They can show age but not fix it: five rows hold a figure over 18 months old. On the 11 companies used to test the proxies, the ranges held the true figure 8 times, so they behave like 70% ranges, not the 90% a client would assume. Next, in order of value: ask the client for each contract's counterparty and who pays today; refresh the stale rows; test the remaining proxies, including on subsidiaries; and draw Part 5 from capacity registers instead of activity codes, starting with a data request to the road transport authority for vehicle counts.

## Part 4: The room

The licensee list goes stale, and both of the client's fears come from that. Seventeen of the 100 have changed what they are since 2020. Seven were absorbed into far larger groups, such as VMware into Broadcom and WK Kellogg into Ferrero: small-tier licences now inside multinationals. Six were carved out of parents, such as Sandoz from Novartis and Qnity from DuPont, so a licence signed by the parent may now cover a separate company that never paid. Four were renamed or disappeared, including Steyn Holding, struck off in 2020, and Leve Bakery, dissolved in 2023, both of which my own tags missed until a register check.

Each event is public and dated, and enterprise licences often carry a change-of-control clause, which makes it a moment to reprice on the client's terms rather than a renegotiation to win cold. Seventeen in six years is about 2.8% of the base a year; this list probably overstates the real rate, but even a third of it is a steady stream of triggers nobody is watching. Monitor licensees for corporate events, and reprice at the event rather than at renewal.

## Part 5: The register

The proxy is capacity times peer revenue per unit, which only works where size is a visible asset: vehicles, rooms, seats, beds, vessels or floor space. Living means operating status `1048` with no status for being struck off, dissolved, insolvent or suspended. A company is inside the line when capacity activities make up at least half of its authorised activity codes, because the register lists no main activity. This is a rough line, and the bounds show how rough.

| | |
|---|---|
| Companies inside the line | **153,881**, bounds 85,567 to 491,769 |
| Share of the living register | **8.8%** of 1,747,958 |
| Largest industries | Road transport 104,216, restaurants and bars 31,201, accommodation 15,276 |

Checked against the tourism ministry's list, only 45.5% of the line's accommodation companies have a findable room count, and the line misses over half of the listed operators, so a register beats activity codes wherever one exists. Road transport, two thirds of the line, cannot be sized from public data: the road transport authority's register lists 53,826 licensed operators with no vehicle counts, so at most half of the line's 104,216 road transport companies hold a licence at all. Code in [code/register.py](code/register.py); working in [NOTES.md](NOTES.md).

## Cut list

- Most time went into matching by hand, then sourcing the Part 2 figures; Part 5 was mostly a fight with a download server that cut files short without saying so.
- I did not take the other 77 rows, which would add volume rather than lessons, or the quant route, which cannot see the sample's traps.
- I did not open every primary document; figures from press coverage of a filing are labelled that way.
- Three proxies are tested on 11 companies; the ranges of untested proxies are judgment.
- I measured the UK headcount tag on three days of bulk accounts rather than the whole archive. I did not scrape the Romanian road transport register, because its robots.txt disallows automated access; matching it needs the authority's permission.

## Debate topics

**Where I would not trust AI tools.** On any number or identity claim it cannot point to: search summaries here mixed Kellanova into WK Kellogg and quoted a $5bn hotel chain revenue that is physically impossible. I catch it with a source a second fetch confirms, a sanity check on every derived number, and an independent check on every "it worked", which is how truncated downloads that reported success were caught.

**Knowing the dataset is wrong at scale.** Filers and listed companies are a labelled subset to score every recipe on, and internal contradictions, such as a subsidiary larger than its parent, flag the rest. A rising disagreement rate between independent sources means the pipeline has drifted even when no row looks wrong.

**Ranges you would bet on.** Set each width from the measured error of that proxy on companies that report. Mine held 8 of 11 test companies, and all three misses were companies more extreme than every peer, which a range spanning the peers cannot reach. A year later, check what share of newly published figures fell inside: an 80% range should catch about 80%, and the fix for a miss is to the proxy's width, not to single rows.
