# Estimating revenue and headcount for a licensee list

Can revenue and headcount be produced, with evidence that survives the client's analyst, for 100 licensee names typed in by sales reps? For about ten of the 23 companies in my sample the answer is yes, straight from a filing; for a few more, yes as an estimate good enough to set a price tier; for the rest, a gap with a reason attached. Most of the risk is not in the arithmetic but in deciding which legal entity a name on a contract means.

## Repo layout

- `data/`: the client's list, my tagged version and the Part 1 matching file.
- `output/licensee_sizes.xlsx`: the file I would send the client, built by `code/build_workbook.py`.
- `output/sample_estimates.csv`: the same data as CSV, built by `code/estimates.py`, which holds every input, source and derivation.
- `code/register.py` and `output/register_counts.txt`: the Part 5 counts.
- `code/uk_accounts.py` and `output/uk_accounts_counts.txt`: the measured reach of the UK headcount tag.
- [NOTES.md](NOTES.md): the full proxy ledger, both proxy tests and how the Part 5 line was drawn.
- `big_data/` is ignored by git; Part 5 expects the ONRC register files in `big_data/register/` the tourism ministry's accommodation list, exported from se.situr.gov.ro as CSV, in `big_data/tourism/`, and Companies House daily bulk accounts zips in `big_data/ch/`.

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
| UK iXBRL headcount tag in micro accounts | Best find: a reported headcount where turnover is hidden | Measured on 35,144 filings from three days of the free bulk download: 88.5% carry it, 61.4% with staff above zero, while only 1.0% report turnover. About 1.5 million companies a year |
| Capacity × revenue per unit at listed peers | MSC about $68bn, Drury about $880m | About 154,000 Romanian companies; see Part 5 |
| Customers per employee at gas utilities | Replaced by Brooklyn Union's own filing | Hundreds per country |
| LinkedIn-based headcount trackers | Kept only where two agree; wrong for holdings | About 69 million company pages |
| Lead-generation database revenue | Discarded: Drury at $5bn means over $500 a room a night | Everywhere, which is the danger |

Two proxies were tested on companies that report. The shipping rate from two carriers under-predicted three others by 8 to 10%, so MSC now uses a six-carrier median. The gas ratio came within 10% on two standalone utilities but was 37% too high on Brooklyn Union Gas, whose filing shows 1,464 staff, because its shared work sits in a separate National Grid company. A ratio learned from standalone firms overstates a subsidiary: the Part 1 scope trap again, inside a proxy.

## Part 3: The call

I would ship part of it, labelled. The 10 revenue and 9 headcount figures from filings can go to the client's analyst today. I would hold back the MSC and Drury estimates, which rest on peer and segment data and are good for a tier rather than a price, and the rows where I chose the scope, such as Siemens Energy and MSC, because nobody yet knows which entity signed. Most of this file's error is scope, not arithmetic.

My checks cannot see whether a match is the company on the contract, or errors my sources share, since three Romanian sites copy one ministry file. They can show age but not fix it: five rows hold a figure over 18 months old. Beyond the two tests, my range widths are judgment. Next, in order of value: ask the client for each contract's counterparty and who pays today; refresh the stale rows; match the UK licensees to the bulk accounts; test the remaining proxies, including on subsidiaries; and draw Part 5 from capacity registers instead of activity codes.

## Part 4: The room

The licensee list goes stale, and both of the client's fears come from that. Sixteen of the 100 have changed what they are since 2020. Seven were absorbed into far larger groups, such as VMware into Broadcom and WK Kellogg into Ferrero: small-tier licences now inside multinationals. Six were carved out of parents, such as Sandoz from Novartis and Qnity from DuPont, so a licence signed by the parent may now cover a separate company that never paid. Three were renamed or disappeared, including Steyn Holding, which my own tags missed until a register check.

Each event is public and dated, and enterprise licences often carry a change-of-control clause, which makes it a moment to reprice on the client's terms rather than a renegotiation to win cold. Sixteen in six years is about 2.7% of the base a year; this list probably overstates the real rate, but even a third of it is a steady stream of triggers nobody is watching. Monitor licensees for corporate events, and reprice at the event rather than at renewal.

## Part 5: The register

The proxy is capacity times peer revenue per unit, which only works where size is a visible asset: vehicles, rooms, seats, beds, vessels or floor space. Living means operating status `1048` with no status for being struck off, dissolved, insolvent or suspended. A company is inside the line when capacity activities make up at least half of its authorised activity codes, because the register lists no main activity. This is a rough line, and the bounds show how rough.

| | |
|---|---|
| Companies inside the line | **153,881**, bounds 85,567 to 491,769 |
| Share of the living register | **8.8%** of 1,747,958 |
| Largest industries | Road transport 104,216, restaurants and bars 31,201, accommodation 15,276 |

Checked against the tourism ministry's list, only 45.5% of the line's accommodation companies have a findable room count, and the line misses over half of the listed operators, so a register beats activity codes wherever one exists. Road transport, two thirds of the line, is untested. Code in [code/register.py](code/register.py); working in [NOTES.md](NOTES.md).

## Cut list

- Most time went into matching by hand, then sourcing the Part 2 figures; Part 5 was mostly a fight with a download server that cut files short without saying so.
- I did not take the other 77 rows, which would add volume rather than lessons, or the quant route, which cannot see the sample's traps.
- I did not open every primary document; figures from press coverage of a filing are labelled that way.
- Two proxies are tested; the rest of the range widths are judgment.
- I measured the UK headcount tag on three days of bulk accounts rather than the whole archive, and did not check the Romanian vehicle register; both are next steps.

## Debate topics

**Where I would not trust AI tools.** On any number or identity claim it cannot point to: search summaries here mixed Kellanova into WK Kellogg and quoted a $5bn hotel chain revenue that is physically impossible. I catch it with a source a second fetch confirms, a sanity check on every derived number, and an independent check on every "it worked", which is how truncated downloads that reported success were caught.

**Knowing the dataset is wrong at scale.** Filers and listed companies are a labelled subset to score every recipe on, and internal contradictions, such as a subsidiary larger than its parent, flag the rest. A rising disagreement rate between independent sources means the pipeline has drifted even when no row looks wrong.

**Ranges you would bet on.** Set each width from the measured error of that proxy on companies that report, as done here for shipping and gas. A year later, check what share of newly published figures fell inside: an 80% range should catch about 80%, and the fix for a miss is to the proxy's width, not to single rows.
