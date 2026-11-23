# Estimating revenue and headcount for a licensee list

Can revenue and headcount be produced for these 100 names, typed in by sales reps, with evidence that survives the client's analyst? We would say yes, but not in the same way for every name. With plenty of research and some mathematical modelling, we built a framework that shows the client which numbers they can rely on and which they cannot. For 10 of the 23 companies in our sample the figure comes straight from a filing, for a few more it is an estimate good enough to set a price tier, and for the rest it is a gap with a reason attached. At the start, the gap between what we had, a list of names, and what we had to fill felt too large. Most of it turned out to be matching: working out which legal company a name on a contract actually means.

## Repo layout

- `output/licensee_sizes.xlsx`: the file we would send the client. `output/sample_estimates.csv` holds the same data.
- `data/`: the client's list, our tagged version, the Part 1 matching file, every proxy assumption with its source, the companies the proxies were tested on, and a manifest of the large inputs with sizes and checksums.
- `code/`: one script per part, plus a parser for UK electronic accounts, input validation and `check.py`, which checks every figure in this README against the outputs. `tests/` holds the unit and integration tests.
- [NOTES.md](NOTES.md): the full proxy ledger, the proxy tests, the parser findings and how the Part 5 line was drawn.

## How to run

```bash
make setup
make all
```

`make test` runs the tests alone. Part 5 and the UK accounts count need the large inputs in `big_data/`, which git ignores: `code/fetch_data.py --download` fetches them and checks each against the manifest. All scripts reproduce the committed outputs exactly from a clean environment.

## Sample

We first tagged all 100 names by why each would be hard to size, giving 14 blocks such as the Siemens family, spin-offs, banks, brands, ambiguous names, dead companies and Luxembourg holdings. The sample takes 23 entities with at least one from every block, weighted to where the client's money is at risk: five micro businesses, where "three people and a mailbox" hides, and two large private groups, where a small-tier licence may cover a multinational. Fastenal is the control case. The other 77 would mostly have repeated traps already in the sample.

## Part 1: The match

Matching a name is easy; deciding which entity the contract means is the real work. Seven of the 23 matched to a different legal name, and even exact matches hid traps: Yazaki has three Romanian companies, and Google Ireland's revenue is ad sales for Europe, the Middle East and Africa. Each row of [data/sample_matching.csv](data/sample_matching.csv) has the entity, registration number, status, parent, evidence link and a short note.

| Outcome | n | Rows |
|---|---|---|
| Matched, high confidence | 10 | Fastenal, Siemens Gamesa, Google Ireland, Yazaki Romania, WK Kellogg, Temasek, NHS GGC, Margot Bakery, Alin Panificatie, MSC |
| Matched, medium confidence | 6 | Siemens Energy, Blue Origin, FintechOS, Panificatie Moldova, Brooklyn Union Gas for National Grid, Drury Hotels |
| Matched through its owner | 1 | Old Spice to Procter & Gamble |
| Matched but not operating | 3 | Bakery Bakery, dissolved 2019; Wirecard, insolvent 2020; Steyn Holding, struck off 2020 |
| Ambiguous | 1 | Credit Mutuel, four separate banking groups |
| Not found | 2 | Meridian, Gunter Buchbender Tischlerei |

The two misses are different results. Meridian is one common word that nobody could match. Buchbender probably exists as an unregistered sole trader, which German registers do not list, so our search failed; a town from the contract would settle it. "Matched" also does not mean "operating": Alin Panificatie has never filed accounts and Panificatie Moldova reports no staff.

## Part 2: The estimate

We took the detective route, because the sample was chosen for traps that a model trained on Romanian SMEs cannot see.

The client gets [output/licensee_sizes.xlsx](output/licensee_sizes.xlsx): a summary tab with each licensee's size tier, how sure we are and one action, a full data tab, and a page on how to read it. Every figure has a basis, an as-of date, a low and a high, a source, a derivation and an action. Where revenue misleads, the file gives a more honest measure: portfolio value for Temasek, budget for the NHS board, headcount for Google Ireland.

| Basis | Revenue | Employees |
|---|---|---|
| Reported in a filing or a segment of one | 10 | 9 |
| Declared by the company | 1 | 4 |
| Estimated from proxies | 3 | 2 |
| Left blank, with a reason | 9 | 8 |

What survived, in brief; the full ledger with every discarded proxy is in [NOTES.md](NOTES.md):

| Proxy | Verdict | Reach at scale |
|---|---|---|
| UK iXBRL headcount tag in micro accounts | Best find: a reported headcount where turnover is hidden | On 35,144 filings from three days of bulk data, 89.0% carry it and 61.7% show staff above zero, while 1.0% report turnover. About 1.5 million companies a year |
| Capacity × revenue per unit at listed peers | MSC about $68bn, Drury about $940m | About 154,000 Romanian companies; see Part 5 |
| Customers per employee at gas utilities | Replaced by Brooklyn Union's own filing | Hundreds per country |
| LinkedIn-based headcount trackers | Kept only where two agree; wrong for holdings | About 69 million company pages |
| Lead-generation database revenue | Discarded: Drury at $5bn means over $500 a room a night | Everywhere, which is the danger |

Three proxies were tested on companies that report. The shipping rate from two carriers under-predicted three others by 8 to 10%, so MSC now uses a six-carrier median. The gas ratio came within 10% on two standalone utilities but was 37% too high on Brooklyn Union Gas, whose filing shows 1,464 staff, because its shared work sits in a separate National Grid company. A ratio learned from standalone firms overstates a subsidiary, which is the Part 1 scope trap showing up again inside a proxy. The hotel formula came within 7% on Apple Hospitality and Summit with their own occupancy and room rates, but 22% and 26% low with Drury's segment inputs, so for Drury the risk sits in the inputs.

## Part 3: The call

Yes, the client can use these numbers today, as long as they keep the labels. Working from the data we were given, this is as close as general logical judgement can get, and every figure says whether it comes from a filing, from the company itself or from an estimate. As a safety net we backtested the proxies, and the next step is simply asking around: checking the shakiest figures with the client and, where possible, with the licensee.

The one estimate we would hold back is Drury. We see the hotel business as unstable, and this is the sketchiest number in the file: its range runs from $660m to $1.52bn, and when we priced two listed hotel owners with Drury's inputs, the formula came out 22% and 26% too low.

Our checks have limits. They cannot see whether a match is the company on the contract, and they can show age but not fix it: five rows hold a figure over 18 months old. On the 11 companies used to test the proxies, the ranges held the true figure 8 times, so they behave like 70% ranges, not 90% ones.

The first thing we would ask the client for is each licensee's payment history, meaning when they pay and how regularly, which shows recurrence and habit, together with who signed each contract. Both show who is actually responsible for the licence and give us more avenues for future research.

## Part 4: The room

The licensee list goes stale, and both of the client's fears come from that. Seventeen of the 100 have changed what they are since 2020. Seven were absorbed into far larger groups, such as VMware into Broadcom and WK Kellogg into Ferrero: small-tier licences now inside multinationals. Six were carved out of parents, such as Sandoz from Novartis and Qnity from DuPont, so a licence signed by the parent may now cover a separate company that never paid. Four were renamed or disappeared, including Steyn Holding, struck off in 2020, and Leve Bakery, dissolved in 2023, both of which our own tags missed until a register check.

Each event is public and dated, and enterprise licences often carry a change-of-control clause, which makes it a moment to reprice on the client's terms rather than a renegotiation to win cold. Seventeen in six years is about 2.8% of the base a year. This list probably overstates the real rate, but even a third of it is a steady stream of triggers nobody is watching. Monitor licensees for corporate events, and reprice at the event rather than at renewal.

## Part 5: The register

The proxy is capacity times peer revenue per unit, so it only works where size is a visible asset such as vehicles, rooms or seats. A living company, with status `1048` and no dead status, is inside the line when capacity activities make up at least half of its authorised activity codes, since the register lists no main activity. The bounds show how rough that line is.

| | |
|---|---|
| Companies inside the line | **153,881**, bounds 85,567 to 491,769 |
| Share of the living register | **8.8%** of 1,747,958 |
| Largest industries | Road transport 104,216, restaurants and bars 31,201, accommodation 15,276 |

Only 45.5% of the line's accommodation companies have a room count in the tourism ministry's list, so a register beats activity codes wherever one exists. Road transport, two thirds of the line, cannot be sized from public data: the transport authority lists 53,826 licensed operators with no vehicle counts. Working in [NOTES.md](NOTES.md).

## What we tried first and what went wrong

The mistake that worried us most was a small one. When we replaced our first UK accounts reader, which used regular expressions, with a proper XML parser, the numbers changed, and one reason was that the old reader had counted "1.00" employees as 100. It left us uneasy: this was one mistake we happened to notice, so what if there were more we had not, and they rippled into everything built on top? That is why we wrote tests for every failure we could think of. They paid off quickly, catching a bug where the proxy assumptions file was not actually feeding the estimates.

Leve Bakery taught us something different. It was on the client's list as a live licensee, but Companies House shows it filed accounts with 5 staff and was then dissolved in November 2023. We honestly did not know how to justify it at first, and it was tempting to write "dissolved" and move on. What we took from it is to be more persistent and to try more than one source before deciding there is nothing more to the story.

If we started again tomorrow, we would spend less time tied up in the detail, solve the problem end to end first, and then fill in the gaps.

## Cut list

- Most time went into matching by hand, then sourcing the Part 2 figures.
- We did not take the other 77 rows, which would add volume rather than lessons, or the quant route, which cannot see the sample's traps.
- We did not open every primary document; figures from press coverage of a filing are labelled that way.
- Three proxies are tested on 11 companies; the ranges of untested proxies are judgment.
- We measured the UK headcount tag on three days of bulk accounts rather than the whole archive. We did not scrape the Romanian road transport register, because its robots.txt disallows automated access; matching it needs the authority's permission.

## Debate topics

**Where we would not trust AI tools.** On any number or identity claim it cannot point to: search summaries here mixed Kellanova into WK Kellogg and quoted a $5bn hotel chain revenue that is physically impossible. We catch it with a source a second fetch confirms, a sanity check on every derived number, and an independent check on every "it worked", which is how truncated downloads that reported success were caught.

**Knowing the dataset is wrong at scale.** Filers and listed companies are a labelled subset to score every recipe on, and internal contradictions, such as a subsidiary larger than its parent, flag the rest. A rising disagreement rate between independent sources means the pipeline has drifted even when no row looks wrong.

**Ranges you would bet on.** Set each width from the measured error of that proxy on companies that report; ours held 8 of 11, and every miss was a company more extreme than all its peers. A year later, check what share of newly published figures fell inside, since an 80% range should catch about 80%. When it does not, widen the proxy's range rather than patching single rows.
