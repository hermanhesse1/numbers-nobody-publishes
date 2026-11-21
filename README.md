# Estimating revenue and headcount for a licensee list

Can annual revenue and employee count be produced, with evidence that would survive the client's analyst, for 100 licensee names typed in by sales reps? For about ten of the 23 companies in my sample the answer is yes, straight from a filing. For a few more it is yes as a derived estimate that is good enough to set a price tier. For the rest the honest answer is a gap with a reason attached. The main finding is that most of the risk is not in the arithmetic but in deciding which legal entity a name on a contract actually means.

## Repo layout

- `data/` holds the client's original list, my tagged version and the Part 1 matching file.
- `code/estimates.py` builds the client file and holds every Part 2 input, source and derivation. `code/register.py` produces the Part 5 counts.
- `output/` holds the client file, `sample_estimates.csv`, and the register counts.
- `big_data/` is ignored by git. Part 5 expects the ONRC register files in `big_data/register/`, from data.gov.ro, and the tourism ministry's list of classified accommodation in `big_data/tourism/`, exported from se.situr.gov.ro and saved as CSV.

Run either script from the repo root with `python3 code/<name>.py`.

## Sample: what I chose and why

Before sampling, I tagged all 100 names in [data/licensee_list_tagged.csv](data/licensee_list_tagged.csv) by why each one would be hard to size. That produced 14 blocks, among them the Siemens family, recent spin-offs, banks, brands, ambiguous names, dead companies and Luxembourg holdings, each with a note on its trap and the right size measure. The sample takes 23 entities with at least one from every block, so every kind of failure is tested at least once.

Within that, the weight goes where the client's money is at risk. Five of the 23 are micro businesses, because they publish the least and are where "three people and a mailbox" hides. Two are large private companies, where a small-tier licence is most likely running across a multinational group. Fastenal is the control case: a listed company with one obvious match, to check that the method gets the easy row right. The other 77 rows would mostly have repeated traps the sample already contains.

## Part 1: The match

The matching file is [data/sample_matching.csv](data/sample_matching.csv). Each row gives the matched entity, its country, registration number, status and parent, an evidence link, an outcome bucket, a confidence level and a short note.

Matching turned out to be harder than it sounds, because the name on a contract is rarely the entity the numbers belong to. Seven of the 23 matched to a legal name different from the one typed in. FintechOS and Blue Origin are brands for FINTECH OS SRL and Blue Origin, LLC. NHS Greater Glasgow and Clyde is the operating name of a statutory body, Greater Glasgow Health Board. STEYN HOLDING S.A., SPF dropped its SPF status in 2014 and later became an S.à r.l. The Brooklyn address next to National Grid points to The Brooklyn Union Gas Company, not the UK group. Old Spice is a P&G product with no company of its own.

Even an exact name match was rarely the end of it. Yazaki has three companies in Romania, Margot Bakery's entity is registered as a property letting business, Google Ireland's revenue covers ad sales across Europe, the Middle East and Africa, and "Siemens Energy" could be the listed group or any of its local companies. Matching a name is easy; deciding which entity the contract means is the actual work.

| Outcome | n | Rows |
|---|---|---|
| Matched, high confidence | 10 | Fastenal, Siemens Gamesa, Google Ireland, Yazaki Romania, WK Kellogg, Temasek, NHS GGC, Margot Bakery, Alin Panificatie, MSC |
| Matched, medium confidence | 6 | Siemens Energy, Blue Origin, FintechOS, Panificatie Moldova, Brooklyn Union Gas for National Grid, Drury Hotels |
| Matched through its owner | 1 | Old Spice to The Procter & Gamble Company |
| Matched but not operating | 3 | Bakery Bakery Ltd, dissolved in 2019 without ever trading; Wirecard AG, insolvent since 2020; Steyn Holding, struck off in July 2020 |
| Ambiguous | 1 | Credit Mutuel, which is four separate banking groups |
| Not found | 2 | Meridian and Gunter Buchbender Tischlerei |

The two unmatched rows are different results. Meridian cannot be matched by anyone: it is a single common word with no country, legal form or address, and no amount of searching can choose between dozens of real companies. Gunter Buchbender Tischlerei probably does exist and my search failed. It is most likely an unregistered sole trader, which German registers do not list, and the only near misses were a deleted Buchbender partnership in Heilbronn and a two-partner joinery in Solingen. A town from the contract would probably settle it.

"Matched" also does not mean "operating". Alin Panificatie has never filed accounts and Panificatie Moldova reports no staff, so two of the 16 matched licensees may be paying for software nobody uses. Steyn Holding shows how far a list can drift: it looked like an ordinary match until the Luxembourg Business Register showed it struck off in July 2020, so whoever pays under that licence today is not the company that signed it.

## Part 2: The estimate

I took the detective route. The sample was chosen for its traps, and a model trained on Romanian SMEs cannot tell me that Google Ireland's revenue is regional ad sales or that a headcount tracker has counted Temasek's portfolio companies as Temasek staff. Working one company at a time can.

The client file is [output/sample_estimates.csv](output/sample_estimates.csv), built by [code/estimates.py](code/estimates.py). Every input, source and proxy calculation lives in that script, so an analyst can change an assumption and rerun it.

### What travels with every figure

A number on its own does not survive the client's analyst, so each row carries the following:

- **Scope** says which entity or group the number describes. Most of the risk sits here, not in the arithmetic.
- **Metric** is revenue where revenue is meaningful and something more honest where it is not, such as portfolio value for Temasek or budget for the NHS board. Google Ireland's revenue is shown but flagged as the wrong measure.
- **Basis** is one of `REPORTED`, `REPORTED_SEGMENT`, `SELF_DECLARED`, `PROXY` or `NONE`.
- **Period** is the date the number belongs to, repeated as a separate as-of date for revenue and for headcount. The file also gives the age in months of the older of the two, measured from 20 November 2026, and flags any figure more than 18 months old or with no date at all.
- **A point value with a low and high** gives the range, which is zero-width only when the number comes straight from a filing.
- **Sources, a derivation, an answer to "how wrong could this be" and a client action** complete each row, written so that someone can disagree with them.

### Results on the 23-entity sample

| Basis | Revenue | Employees |
|---|---|---|
| Reported in a filing or a segment of one | 10 | 9 |
| Declared by the company, usually undated | 1 | 4 |
| Derived here from proxies | 3 | 2 |
| Deliberately left blank | 9 | 8 |

Of the nine revenue gaps, six are the unmatched or dead rows: Credit Mutuel, Buchbender, Meridian, Wirecard, Bakery Bakery and Steyn Holding. Old Spice is a brand rather than a company, and Alin has never filed. Blue Origin gets a headcount but no revenue, because no source separates its revenue from Jeff Bezos's funding.

### Proxy ledger: what I tried, what survived, how far it scales

| Proxy | Used on | Verdict | Reach at scale |
|---|---|---|---|
| **UK iXBRL tag `AverageNumberEmployeesDuringPeriod`** | Margot Bakery, which files a headcount of 13 but no turnover | **Kept, and the best find.** It turns a "no data" micro company into a reported headcount | About 1.6 million UK companies a year: Companies House expects 2.2 million sets of accounts annually, and about 75% arrive in machine-readable form in its free bulk download. This needs a parser, not research |
| Romanian balance sheets filed with the Ministry of Finance | Yazaki, FintechOS, Panificatie Moldova | Kept | Up to 1.3 million Romanian companies: the 1,296,440 living companies whose legal form must file accounts, counted by the first version of `code/register.py`, which is in the git history. How many actually file with staff above zero would take the Ministry of Finance file to count |
| Revenue per unit of capacity at listed peers, a median of about $9,050 per TEU across six carriers | MSC, about $68bn with a range of $55bn to $76bn, adding cruises priced off Carnival and Royal Caribbean | Kept, and the one proxy tested on companies that report, as described below. MSC's terminals and logistics remain the weak slice, with only its African arm sourced | About 154,000 Romanian companies, 8.8% of the living register, once the recipe is extended from ships to vehicles, seats, rooms and beds. Part 5 has the count |
| Rooms × 365 × occupancy × average room rate | Drury, about $880m with a range of $610m to $1.36bn | Kept. Occupancy and room rate come from segment and peer figures by Colliers, CoStar and Hilton, not Drury's own, and sources disagree on the hotel count, 130 against more than 150 | About 15,000 Romanian companies whose activities are mainly accommodation. The tourism ministry's list gives a room count for 6,952 of them, 45.5%, so the rooms input can be found for under half |
| Customers divided by customers per employee | Brooklyn Union Gas, before its own filing turned up | **Replaced by a reported figure.** The ratio from three listed utilities predicted about 2,000 staff; the utility's regulatory filing reports 1,464, so the proxy was 37% too high. It worked within 10% on two standalone utilities, but this one is a subsidiary whose shared work sits in a separate National Grid company | Hundreds of companies per country at most, a rough judgment rather than a count: only regulated networks report customer numbers |
| LinkedIn-based headcount trackers such as Revelio | Siemens Gamesa, 27,300 | Kept where two trackers agree within 3%. Discarded for Temasek, where Revelio shows 122,763 against Temasek's own figure of about 960 | LinkedIn lists about 69 million company pages, but the figure is safe only where the legal entity and the people are the same thing. Wrong for holdings, investment firms and brands |
| Figures a company declares about itself, such as Drury's "over 6,500 team members" | Drury, MSC, NHS GGC, Temasek | Kept as `SELF_DECLARED`, with wider ranges because they are undated | Most mid-size and large companies; no count, because each statement has to be found and dated by hand |
| Revenue from lead-generation databases | Drury | **Discarded.** LeadIQ's $5bn would mean over $500 a night with every room full, against segment rates of $128 to $159 | Universal, which is exactly what makes it dangerous |
| Old headcounts and brand-sales estimates | Brooklyn Union's 3,651 staff from decades ago, Old Spice's $564m from 2013 | Discarded because they describe a different time | None |

Two questions were put to every figure. The first is whether it describes the matched entity at the time claimed. That caught Kellanova figures turning up for WK Kellogg, the Temasek headcount, National Grid plc numbers next to the Brooklyn gas utility, and Google Ireland's regional revenue. The second is whether I would notice if it did not, and the honest answer is only where a second, independent number exists. Siemens Gamesa's segments add up to the group total, the MSC estimate fits the 2022 figure, and about 46 staff per hotel is plausible for Drury's format. Drury's revenue estimate also lands near RocketReach's $777m, which I kept only as a cross-check. Everywhere else the file rests on a single source, and the sources column shows which one.

One proxy was also tested the way the third debate says every proxy should be. The first version priced MSC's container slots at about $8,650 per TEU, the rate at Hapag-Lloyd and Maersk. Applied to four other carriers that publish both revenue and fleet size, it under-predicted CMA CGM by 9%, COSCO by 8% and ONE by 10%, and over-predicted Evergreen by 25%, though Evergreen's fleet figure is undated and the weakest input in the test. Three misses in the same direction meant the two-carrier rate ran low, so the estimate now uses the median of all six carriers, and the range spans them. Four test companies is far too few to call the range calibrated, but it is measured rather than assumed, and it moved the answer by about $2bn.

The gas-utility ratio got the same treatment, and the result was more useful because it failed. Tested on two standalone utilities, ONE Gas and NW Natural, it came within 10%. Tested on Brooklyn Union Gas itself, once its annual report to the New York regulator turned up a headcount of 1,464, it was 37% too high. The utility serves about 871 customers per employee, more than most of its peers, because much of its work is done by National Grid's shared service company and sits on another payroll. My earlier guess had been the opposite, that a dense city network would need more staff. The lesson is the same scope trap as Part 1, now showing up inside a proxy: a ratio learned from standalone companies overstates the staff of a subsidiary that borrows its people from the group.

## Part 3: The call

I would not ship this as one file, but I would ship part of it, clearly labelled. The 10 revenue and 9 headcount figures read from filings could go in front of the client's analyst today, including Margot Bakery's headcount even though its revenue is an estimate.

Two kinds of row I would hold back from pricing. The proxy rows for MSC and Drury show their working, and their inputs now come from listed peers and segment data. But peers are not the company itself: Drury's occupancy is its segment's, not its own, and most of MSC's terminal and logistics revenue still has no source. They are good enough to put a company in a tier, not to quote a number. The second kind is the rows where I chose the scope myself, namely Siemens Energy, Blue Origin, MSC, National Grid and Old Spice. The number is right for the entity I picked, but nobody yet knows whether that entity signed. Most of the error in this file is a scope error rather than an arithmetic one.

My checks have four blind spots. They cannot tell whether the matched entity is the one on the contract; only the contract can. They cannot see errors my sources share: termene.ro, totalfirme.ro and targetare.ro all copy the same Ministry of Finance data, so three of them agreeing is really one source. Age is the one they can now show but not fix: five of the 15 rows with figures hold one more than 18 months old, the oldest being Brooklyn Union's headcount at 35 months, and four rely on a figure with no date, while the base keeps moving, as Part 4 shows. And they cannot tell whether my ranges are honest: apart from small tests on container shipping and gas utilities, a ±20% is a judgment, not a measured error.

The next steps, in order of value per hour, would be these:

1. Ask the client, for each contract, for the counterparty's name and address and who pays today. That settles scope on about ten of the 23 rows, and tells us who now holds the four licences signed by companies that are dead or never traded.
2. Refresh the five rows still flagged as older than 18 months. Blue Origin has been refreshed from 2026 headcount trackers. For the rest, newer figures are not yet usable: Google Ireland has not filed its 2025 accounts, Yazaki's 2025 figures appear on only one site, Brooklyn Union's statements to March 2026 could not be found, and a 2025 estimate for MSC would need every peer carrier's 2025 results.
3. Parse the free Companies House bulk accounts to get a reported headcount for every UK licensee automatically.
4. Test every remaining proxy on companies that report, and include subsidiaries in the test set. The gas test showed that a ratio learned from standalone companies can miss a subsidiary by more than a third.
5. Draw the Part 5 line from capacity registers rather than activity codes wherever a register exists: the tourism ministry's list for accommodation, then the road transport authority's vehicle register for the largest group.

## Part 4: The room

The licensee list goes stale, and both of the client's fears come from that one cause. On the list exactly as it was sent, 16 of the 100 licensees have changed what they are since 2020. Seven were absorbed into far larger groups: VMware into Broadcom, ANSYS into Synopsys, Credit Suisse into UBS, WK Kellogg into Ferrero, HELLA into Forvia, Siemens Gamesa into Siemens Energy and DEGIRO into flatexDEGIRO. Six were carved out of larger parents: Siemens Energy, Sandoz, Solstice, Amentum, Qnity and Sierra Space. Three more were renamed or disappeared: Currys PC World, Wirecard, and Steyn Holding, which my tags had missed until a register check showed it struck off in 2020. The absorbed seven are the small-tier licensee now sitting inside a multinational, priced for what it was when it signed. The spin-offs are the reverse and less obvious: a licence signed by the parent may now be used by a separate company that was never priced at all, which is unlicensed use rather than underpricing.

Every one of these events is public, dated and machine-readable through SEC filings, merger notices and register changes. Enterprise licences often carry an assignment or change-of-control clause, which would make each event a contractual moment to re-paper the deal on the client's terms rather than a renegotiation to win cold. Sixteen events in about six years is roughly 2.7% of the base a year. This list was probably built to be difficult and overstates the real rate, but even a third of it across a large base is a steady stream of repricing triggers that nobody is watching. The proposal is to monitor the licensee base for corporate events, not just size, and to reprice at the event rather than at renewal.

## Part 5: The register

The proxy is capacity times revenue per unit of capacity at listed peers. It is the recipe behind both of Part 2's larger estimates: container slots for MSC and hotel rooms for Drury. The UK headcount tag was the most useful find in Part 2, but it is a reported figure rather than a proxy, so it does not belong here. Capacity only works where a company's size is a countable asset the public can see: a fleet, rooms, seats, beds or floor space. Counting delivery vans tells you nothing about a law firm, so the line is drawn on activity codes. The counts come from the ONRC snapshot of 8 December 2025, using [code/register.py](code/register.py), with the output in [output/register_counts.txt](output/register_counts.txt).

| | |
|---|---|
| Companies inside the line | **153,881**, within bounds of 85,567 and 491,769 |
| Share of the living register | **8.8%** of 1,747,958, within bounds of 4.9% and 28.1% |
| Largest industries | **Road transport** 104,216, **restaurants and bars** 31,201, **accommodation** 15,276 |

The first decision is who counts as alive. The register holds 4,111,567 companies, and I count one as living if it carries status `1048 funcţiune`, meaning operating, and no status for being struck off, dissolved, in liquidation, insolvent, suspended or abandoned by its owners. That leaves 1,747,958. The dead statuses are matched by keyword against the official list of status codes, and the code list sits in the script so it can be challenged code by code.

The line maps each capacity unit to the activity codes where it is the natural measure:

- **Rooms or beds:** hotels, holiday lets and campsites.
- **Seats or tables:** restaurants and bars.
- **Licensed vehicles:** buses, taxis and road freight.
- **Rolling stock, vessels and aircraft:** rail, water and air transport.
- **Floor area:** warehousing.
- **Beds:** hospitals.

Most of these units have a public count somewhere: the tourism ministry's list of classified accommodation, the road transport authority's register of licensed vehicles, and ship and aircraft registers.

The hard part is that the register lists the activities a company is authorised for, not its main activity, and the median living company holds four. Counting every company with a capacity code anywhere in its list gives 491,769, but that includes a great many firms that added transport or catering just in case. Counting only companies whose single code is a capacity code gives 85,567, which misses a hotel that is also authorised to run a restaurant and a gym. My line sits between the two: a company is inside when capacity activities make up at least half of its authorised codes. That gives 153,881. The industry ranking assigns each company to the capacity group holding most of its capacity codes, so unlike my first attempt the groups add up to the total.

The line has four weaknesses:

- **The recipe is only tested on part of it.** Part 2 tested it on accommodation and shipping, which is about 16,000 of the 154,000 companies. Road transport, two thirds of the line, rests on an untested revenue-per-vehicle figure, and much of it is single-vehicle taxi and haulage firms.
- **Having a public count is not the same as finding one.** I tested this for accommodation against the tourism ministry's list of 32,196 classified units, which gives a fiscal code and a room count for 18,680 operators. Only 6,952 of the 15,276 accommodation companies in the line, 45.5%, appear in it with rooms. The test also ran the other way: of the 17,060 living companies the list names as running classified accommodation, only 7,924 fall inside the line, because the rest hold too many other authorised activities. For accommodation the ministry's list is a better line than activity codes, and the vehicle register for road transport was not checked.
- **Some companies are probably zombies.** 12,202 of those inside carry an expired registered office or expired directors; without them the line is 141,679.
- **The downloads need checking.** The data.gov.ro server sends no file size and silently cut two downloads short, so the inputs should be checked against the advertised sizes of 675 MB for `od_firme.csv` and 400 MB for `od_caen_autorizat.csv`.

My first attempt at this part drew the line on legal form, counting every company required to file accounts. That came to 74% of the living register, but it measured the register's mix of legal forms rather than where any proxy works, so I replaced it.

## Cut list

Most of the time went into matching the 23 entities by hand, because deciding which entity a name means turned out to be the real work. The next largest share went into sourcing the Part 2 figures and building the four proxy derivations. Part 5 was mostly a fight with a download server that truncated files without saying so.

What I deliberately left out:

- **The other 77 rows**, which would have added volume rather than new lessons, since the sample already covers every block.
- **The quant route.** The sample is built around traps such as group versus entity, brand versus company and dead firms, and a model trained on Romanian SMEs cannot see those.
- **Opening every primary document.** Several figures come from press coverage of a filing, such as Google Ireland and FintechOS, or from a jobs portal, as with NHS GGC, and are labelled that way.
- **The last unsourced inputs**: MSC's revenue from terminals and logistics beyond its African arm, and the floors on hotel size and bakery revenue per head. They are marked in the code; everything else in the derivations now has a source.
- **Calibrating the ranges** beyond two small tests, on container shipping and gas utilities. The other widths are judgment rather than measured error, as the third debate explains.
- **Parsing the Companies House bulk accounts, and opening the road transport authority's vehicle register to check that the largest group in Part 5 really has findable capacity.** Both are the obvious next steps and neither was needed to show the recipe works.

## Debate topics

### Where I would not trust AI tools

I would not trust an AI tool on any number or identity claim it cannot point to. During this work, AI-summarised search results put Kellanova figures next to WK Kellogg's, quoted a lead-generation database's $5bn for a chain of about 150 hotels, and would happily have accepted 122,763 "Temasek employees". Even the AI-assisted sanity check on that $5bn got the per-room arithmetic wrong by a factor of two and a half. Its logic needs the same scrutiny: my first industry rule took each company's first-listed activity code, which looked sensible until I noticed the file is sorted by code. The defence is simple to state and tedious to apply. Every figure needs a URL that a second fetch confirms, every derived number gets a physical sanity check such as revenue per room or per employee, and every "it worked" gets an independent check. The register downloads all reported success while two of the three files were truncated, and only comparing byte counts with the advertised sizes caught it.

### Knowing the dataset is wrong at scale

There is no complete answer sheet, but there are partial ones. UK and Romanian filers, listed companies and acquired companies with disclosed financials form a labelled subset for every recipe, and a proxy that is wrong there is wrong everywhere. Internal contradictions are a second signal: a subsidiary larger than its parent, revenue per employee far outside its industry's range, or a company whose size jumps tenfold between refreshes with no corporate event behind it. The third is the disagreement rate between independent sources. When it starts rising, the pipeline has drifted, even if no single row looks wrong.

### Ranges you would bet on

I would set the widths by running each recipe on companies whose real figures are known and taking the empirical error quantiles for each proxy and company type. An 80% range is then the 10th to 90th percentile of measured error rather than a feeling. A year later, honesty can be checked against the figures that have surfaced since, from new filings, IPO prospectuses and acquisition disclosures. If 80% ranges caught only 55% of them they were dishonest, and if they caught 98% they were too wide to price on. Either way, the fix is to the width for that proxy, not to individual rows.
