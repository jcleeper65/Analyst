# Filing blank-field audit — 2026-11-10T22:01:23.936410-05:00

Offline review of the seven candidates rejected for missing factors. Each original blank field is listed below. Filing snippets are normalized text; they are leads unless a tested parser recovered an exact value. No live SEC or LSEG calls were made.

## Validated findings

- Reviewed 73 original blank fields across the seven candidates blocked by missing factors. Related-text matches remain review leads unless an exact value was recovered.
- Enviri: recovered directors/officers group ownership of 1.4% and a count of six disclosed code-P transactions. Atrium: recovered group ownership of 3.1% and zero observed code-P transactions in the scanned interval. Mobility Global: recovered three disclosed code-P transactions. The JSON contains the ownership tables and the transaction citations. These counts retain the screen's code-P definition and coverage limits.
- First Tracks: the release dateline and “completed today” establish April 20, 2026 as completion; April 6 is the record date. Midera: the release dateline and “effective as of today” establish July 6, 2026; June 26 is the record date. Platinum: January 23 is an incorporation date, not an established distribution date. Corrected or cleared these facts in the reviewed snapshot and removed first prices and dependent factors selected from the incorrect dates.
- Octave's group ownership row has a footnote marker, not an exact percentage. The debt/assets and share-count excerpts show that related financial data exists, but the extractor did not establish the exact pro-forma inputs or the price-date share counts required by the current factor definitions. This is not proof that those facts are absent.
- Insider-buying blanks for First Tracks and Midera also involve Form 4 amendments; matching the amended transactions remains unresolved.
- The pipeline does not supply observations for analyst_count or unwanted_selling. Both currently have positive weights of 0.025, so either one still prevents a complete score. No weights were changed.

## Factor-file correction

The saved run and the current factor file both assign analyst_count and unwanted_selling weight 0.025 each. These are positive-weight requirements. No weights were changed. Factors actually set to zero do not block ranking.

## Recovered observations

- CIK 2104052: insider_ownership_pct = 1.4; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000013/exhibit991-form10x12ba3.htm; section Filing table; All directors and executive officers as a group (13 persons) |  | 409,412 |  | 1.4 | %
- CIK 2104052: insider_buying = 6; computed count of disclosed Form 4 code P transactions from 2026-06-01 through 2026-11-10; complete scanned issuer filing list https://data.sec.gov/submissions/CIK0002104052.json; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000134/wk-form4_1787141470.xml transaction date 2026-08-18 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-08-18</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>2439</value>
</transactionshares>
<transactionpricepershare>
<value>20.43</value>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>96998</value>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000134/wk-form4_1787141470.xml transaction date 2026-08-18 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-08-18</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>507</value>
</transactionshares>
<transactionpricepershare>
<value>19.50</value>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>97505</value>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000132/wk-form4_1787086511.xml transaction date 2026-08-17 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-08-17</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>4875</value>
</transactionshares>
<transactionpricepershare>
<value>20.461</value>
<footnoteid id="F1"></footnoteid>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>42955</value>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000079/wk-form4_1780951526.xml transaction date 2026-06-05 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-06-05</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>8333</value>
</transactionshares>
<transactionpricepershare>
<value>19.25</value>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>16434</value>
<footnoteid id="F1"></footnoteid>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000072/wk-form4_1780579698.xml transaction date 2026-06-03 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-06-03</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>14000</value>
</transactionshares>
<transactionpricepershare>
<value>18.10</value>
<footnoteid id="F1"></footnoteid>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>47975</value>
<footnoteid id="F2"></footnoteid>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000071/wk-form4_1780579687.xml transaction date 2026-06-03 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-06-03</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>51519</value>
</transactionshares>
<transactionpricepershare>
<value>19.43</value>
<footnoteid id="F1"></footnoteid>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>144510</value>
<footnoteid id="F2"></footnoteid>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; section Form 4 transaction coverage; See cited XML transactions in JSON.
- CIK 2093101: insider_ownership_pct = 3.1; https://www.sec.gov/Archives/edgar/data/2093101/000119312526055010/d42675dex991.htm; section Filing table; All directors and executive officers as a group (11 persons) |  |  | 478,858 |  |  |  | 3.1 | %
- CIK 2093101: insider_buying = 0; computed count of disclosed Form 4 code P transactions from 2026-02-26 through 2026-11-10; complete scanned issuer filing list https://data.sec.gov/submissions/CIK0002093101.json; ; section Form 4 transaction coverage; See cited XML transactions in JSON.
- CIK 2090312: insider_buying = 3; computed count of disclosed Form 4 code P transactions from 2026-07-01 through 2026-11-10; complete scanned issuer filing list https://data.sec.gov/submissions/CIK0002090312.json; https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/wk-form4_1786654758.xml transaction date 2026-08-11 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-08-11</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>10000</value>
</transactionshares>
<transactionpricepershare>
<value>19.50</value>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>10000</value>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/wk-form4_1786654758.xml transaction date 2026-08-12 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-08-12</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>25000</value>
</transactionshares>
<transactionpricepershare>
<value>19.4998</value>
<footnoteid id="F1"></footnoteid>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>35000</value>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/wk-form4_1786654758.xml transaction date 2026-08-13 quote <nonderivativetransaction>
<securitytitle>
<value>Common Stock</value>
</securitytitle>
<transactiondate>
<value>2026-08-13</value>
</transactiondate>
<transactioncoding>
<transactionformtype>4</transactionformtype>
<transactioncode>P</transactioncode>
<equityswapinvolved>0</equityswapinvolved>
</transactioncoding>
<transactionamounts>
<transactionshares>
<value>15000</value>
</transactionshares>
<transactionpricepershare>
<value>19.8714</value>
</transactionpricepershare>
<transactionacquireddisposedcode>
<value>A</value>
</transactionacquireddisposedcode>
</transactionamounts>
<posttransactionamounts>
<sharesownedfollowingtransaction>
<value>50000</value>
</sharesownedfollowingtransaction>
</posttransactionamounts>
<ownershipnature>
<directorindirectownership>
<value>D</value>
</directorindirectownership>
</ownershipnature>
</nonderivativetransaction>; section Form 4 transaction coverage; See cited XML transactions in JSON.

## Enviri Corp / 2104052

### parent

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R7.htm), section Filing text; excerpt:  purchasing the interests of noncontrolling shareholders, issuance of shares (interests) by the non-wholly owned subsidiary to the parent entity for other than cash, and a buyback of shares (interest) by the non-wholly owned subsidiary from the noncontrolling interests). + ReferencesReference 1: http://www.xbrl.org/2009/role/commonPracticeRef -Topic 505 -SubTopic 10 -Name Accounting Standards Codification -Section S99 -Paragraph 1 -Subparagraph (SX 
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R7.htm), section Filing text; excerpt:  purchasing the interests of noncontrolling shareholders, issuance of shares (interests) by the non-wholly owned subsidiary to the parent entity for other than cash, and a buyback of shares (interest) by the non-wholly owned subsidiary from the noncontrolling interests).

### parent_cik

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002104052

### distribution_ratio

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: ompletion of the Transactions resulted in the exchange of one share of CE Holdings common stock for one share of Legacy Enviri common stock, and subsequently one share of Enviri common stock for every three shares of CE Holdings common stock. As such, the weighted-average shares outstanding and all earnings per share data for periods prior to the Transactions have been retrospectively adjusted to reflect the impact of the Transactions on the Company's capital structureReclassificationsReclassifications have been made to prio
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: ompletion of the Transactions resulted in the exchange of one share of CE Holdings common stock for one share of Legacy Enviri common stock, and subsequently one share of Enviri common stock for every three shares of CE Holdings common stock. As such, the weighted-average shares outstanding and all earnings per share data for periods prior to the Transactions have been retrospectively adjusted to reflect the impact of the Transactions on the Company's capital structure

### record_date

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-06-01](https://www.sec.gov/Archives/edgar/data/2104052/000119312526251752/d258410dex33.htm), section Filing text; excerpt: Any such notice shall be updated and supplemented not later than the five business days after the record date for the applicable meting to disclose the information referred to in clause (b) as of the record date.
- [8-K filed 2026-06-01](https://www.sec.gov/Archives/edgar/data/2104052/000119312526251752/d258410dex33.htm), section Filing text; excerpt: fficer”) or (b) the Secretary at the written request of the stockholders of record as of the Demand Record Date (as defined below) of not less than 25% (the “Requisite Percentage”) of the outstanding shares of common stock of the Corporation entitled to vote at the meeting (the “Requesting Group”) pursuant to the procedures set forth below, and may be held at such place within or without the State of Delaware and on such date and at such

### insider_ownership_pct

Recovered by tested parser fix; exact sourced value.
Recovered value: 1.4; source: https://www.sec.gov/Archives/edgar/data/2104052/000210405226000013/exhibit991-form10x12ba3.htm; Filing table; quote All directors and executive officers as a group (13 persons) \|  \| 409,412 \|  \| 1.4 \| %
- [10-12B/A filed 2026-05-06](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000013/exhibit991-form10x12ba3.htm), section Filing text; excerpt: All directors and executive officers as a group (13 persons)409,4121.4 %
- [10-12B/A filed 2026-05-06](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000013/exhibit991-form10x12ba3.htm), section Filing text; excerpt: All directors and executive officers as a group (13 persons)

### size_relative_to_parent

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-06-02
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: viri common stock for every three shares of CE Holdings common stock. As such, the weighted-average shares outstanding and all earnings per share data for periods prior to the Transactions have been retrospectively adjusted to reflect the impact of the Transactions on the Company's capital structureReclassificationsReclassifications have been made to prior year amounts to conform with current year classifications. These reclassifications did no
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: viri common stock for every three shares of CE Holdings common stock. As such, the weighted-average shares outstanding and all earnings per share data for periods prior to the Transactions have been retrospectively adjusted to reflect the impact of the Transactions on the Company's capital structure

### insider_buying

Recovered by tested parser fix; exact sourced value.
Recovered value: 6; source: computed count of disclosed Form 4 code P transactions from 2026-06-01 through 2026-11-10; complete scanned issuer filing list https://data.sec.gov/submissions/CIK0002104052.json; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000134/wk-form4_1787141470.xml transaction date 2026-08-18 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-08-18</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>2439</value> </transactionshares> <transactionpricepershare> <value>20.43</value> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>96998</value> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000134/wk-form4_1787141470.xml transaction date 2026-08-18 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-08-18</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>507</value> </transactionshares> <transactionpricepershare> <value>19.50</value> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>97505</value> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000132/wk-form4_1787086511.xml transaction date 2026-08-17 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-08-17</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>4875</value> </transactionshares> <transactionpricepershare> <value>20.461</value> <footnoteid id="F1"></footnoteid> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>42955</value> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000079/wk-form4_1780951526.xml transaction date 2026-06-05 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-06-05</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>8333</value> </transactionshares> <transactionpricepershare> <value>19.25</value> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>16434</value> <footnoteid id="F1"></footnoteid> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000072/wk-form4_1780579698.xml transaction date 2026-06-03 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-06-03</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>14000</value> </transactionshares> <transactionpricepershare> <value>18.10</value> <footnoteid id="F1"></footnoteid> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>47975</value> <footnoteid id="F2"></footnoteid> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2104052/000210405226000071/wk-form4_1780579687.xml transaction date 2026-06-03 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-06-03</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>51519</value> </transactionshares> <transactionpricepershare> <value>19.43</value> <footnoteid id="F1"></footnoteid> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>144510</value> <footnoteid id="F2"></footnoteid> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>
Coverage: {"filings": 19, "amendments": 0, "complete_cached_xml": true}

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: certain costs related to the Transactions, interest expense related to the portion of the Company's total debt that was required to be repaid on June 1, 2026 and fees related to the Company's AR Facility that was required to be terminated at the closing of the Transactions, are also allocated to Income (loss) from discontinued operations, net of tax. CE's assets and liabilities have been reclassified as held-for-sale in the Company's Co
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R78.htm), section Filing text; excerpt: Total assets 1,731,041 1,731,041 $ 2,742,789

### absolute_market_cap

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-06-02
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: viri common stock for every three shares of CE Holdings common stock. As such, the weighted-average shares outstanding and all earnings per share data for periods prior to the Transactions have been retrospectively adjusted to reflect the impact of the Transactions on the Company's capital structureReclassificationsReclassifications have been made to prior year amounts to conform with current year classifications. These reclassifications did no
- [10-Q filed 2026-11-05](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000143/R9.htm), section Filing text; excerpt: viri common stock for every three shares of CE Holdings common stock. As such, the weighted-average shares outstanding and all earnings per share data for periods prior to the Transactions have been retrospectively adjusted to reflect the impact of the Transactions on the Company's capital structure

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.
- [8-K filed 2026-05-11](https://www.sec.gov/Archives/edgar/data/2104052/000210405226000055/exhibit991informationstate.htm), section Filing text; excerpt:  Distribution that may be adverse to New Enviri. New Enviri’s shares of common stock may come under selling pressure as certain Enviri stockholders sell their New Enviri shares because they are not interested in holding an investment in the New Enviri Business. Moreover, certain factors such as the size and expected market value of New Enviri may limit investors’ ability to appropriately value New Enviri’s shares of common stock. In addition,

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.

## First Tracks Biotherapeutics, Inc. / 2091349

**DATE ERROR:** The stored date is a record date in a today-completion announcement. Resolve the release dateline before using the price or return. Reviewed distribution date: 2026-04-20. Prices and date-dependent factors from the old date were removed.
Source: [0001193125-26-164328](https://www.sec.gov/Archives/edgar/data/2091349/000119312526164328/d78703dex991.htm), Therapies for Autoimmune Diseases; quote: The spin-off was completed today following the distribution to AnaptysBio, Inc. shareholders of one share of First Tracks Bio common stock for every one share of Anaptys common stock owned as of the close of business on April 6, 2026, the record date for the distribution.

### parent

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R49.htm), section Filing text; excerpt: [1] As part of the Spin-Off, 1,109,394 substitute awards were issued related to awards from the AnaptysBio Equity Plan.
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R48.htm), section Filing text; excerpt: [1] As part of the Spin-Off, 1,109,394 substitute awards were issued related to awards from the AnaptysBio Equity Plan. [2] As part of the Spin-Off, 1,514,446 substitute awards were issued related to awards from the AnaptysBio Equity Plan.

### parent_cik

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002091349

### record_date

Established by the exact record-date wording in the cited release.
Recovered value: 2026-04-06; source: 
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R10.htm), section Filing text; excerpt: rapeutics’ common stock for every one share of AnaptysBio’s common stock held on April 6, 2026, the record date for the distribution. On April 20, 2026, First Tracks Biotherapeutics’ shares of common stock began trading on the Nasdaq Stock Market LLC under the ticker symbol “TRAX.”On the Distribution Date, AnaptysBio distributed 29,100,902 shares of First Tracks Biotherapeutics common stock to its stockholders and the Company completed t
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R10.htm), section Filing text; excerpt: rapeutics’ common stock for every one share of AnaptysBio’s common stock held on April 6, 2026, the record date for the distribution. On April 20, 2026, First Tracks Biotherapeutics’ shares of common stock began trading on the Nasdaq Stock Market LLC under the ticker symbol “TRAX.”

### insider_ownership_pct

No matching evidence in the cached documents reviewed; not proof of absence.

### size_relative_to_parent

Old distribution date was invalid; recomputation with the corrected date is required.
Selected first-close date: 2026-04-07
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R59.htm), section Filing text; excerpt: irm's shareholders and owners, and may be all or only a portion of the number of shares authorized. Shares issued include shares outstanding and shares held in the treasury. + ReferencesReference 1: http://www.xbrl.org/2003/role/disclosureRef -Topic 505 -SubTopic 10 -Name Accounting Standards Codification -Section S45 -Paragraph 3 -Publisher FASB -URI https://asc.fasb.org/1943274/2147480100/505-10-S45-3Reference 2: http://www.xbrl.org/2003/role/disclosureRef -Topic 
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R59.htm), section Filing text; excerpt: irm's shareholders and owners, and may be all or only a portion of the number of shares authorized. Shares issued include shares outstanding and shares held in the treasury.

### insider_buying

Old distribution date was invalid; recomputation with the corrected date is required.
Coverage: {"filings": 45, "amendments": 6, "complete_cached_xml": true}
- [4/A filed 2026-06-12](https://www.sec.gov/Archives/edgar/data/2091349/000118462726000006/0001184627-26-000006-index.html), section Ownership filing coverage; excerpt: Form 4 amendment requires transaction matching; the current engine leaves the count blank.
- [4/A filed 2026-06-12](https://www.sec.gov/Archives/edgar/data/2091349/000170779726000009/0001707797-26-000009-index.html), section Ownership filing coverage; excerpt: Form 4 amendment requires transaction matching; the current engine leaves the count blank.

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R2.htm), section Filing text; excerpt: Total assets 170,456 330,545
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R19.htm), section Filing text; excerpt: loss is used to monitor results. The measure of segment assets is reported on our Balance Sheets as total assets.The chief operating decision maker (“CODM”) is our Chief Executive Officer. The CODM manages the business activities on a combined basis in making decisions regarding resource allocation and performance assessment.The following table is a summary of segment loss and our significant expenses (in thousands): Three Months EndedSep

### absolute_market_cap

Old distribution date was invalid; recomputation with the corrected date is required.
Selected first-close date: 2026-04-07
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R59.htm), section Filing text; excerpt: irm's shareholders and owners, and may be all or only a portion of the number of shares authorized. Shares issued include shares outstanding and shares held in the treasury. + ReferencesReference 1: http://www.xbrl.org/2003/role/disclosureRef -Topic 505 -SubTopic 10 -Name Accounting Standards Codification -Section S45 -Paragraph 3 -Publisher FASB -URI https://asc.fasb.org/1943274/2147480100/505-10-S45-3Reference 2: http://www.xbrl.org/2003/role/disclosureRef -Topic 
- [10-Q filed 2026-11-03](https://www.sec.gov/Archives/edgar/data/2091349/000119312526445430/R59.htm), section Filing text; excerpt: irm's shareholders and owners, and may be all or only a portion of the number of shares authorized. Shares issued include shares outstanding and shares held in the treasury.

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.

## Octave Intelligence plc / 2083632

### parent

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R8.htm), section Filing text; excerpt: gon AB ("Hexagon") announced that its board of directors had directed management to prepare for the spin-off of the Octave business into an independent, publicly-traded company through a tax-free, from both a U.S. federal income and Swedish tax perspective, pro rata distribution of all the outstanding share capital of Octave to Hexagon shareholders via a Lex-ASEA distribution. Prior to the Distribution (as defined below), the Company was wholly owned by Hexagon.On April 24, 2026, the general meeting of shareholders of Hexagon
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R8.htm), section Filing text; excerpt: gon AB ("Hexagon") announced that its board of directors had directed management to prepare for the spin-off of the Octave business into an independent, publicly-traded company through a tax-free, from both a U.S. federal income and Swedish tax perspective, pro rata distribution of all the outstanding share capital of Octave to Hexagon shareholders via a Lex-ASEA distribution. Prior to the Distribution (as defined below), the Company was wholly owned by Hexagon.

### parent_cik

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R1.htm), section Filing text; excerpt: Central Index Key 0002083632
- [8-K filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055939/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002083632

### distribution_ratio

No matching evidence in the cached documents reviewed; not proof of absence.

### insider_ownership_pct

Related filing text found; extraction/interpretation review required.
- [10-12B/A filed 2026-04-27](https://www.sec.gov/Archives/edgar/data/2083632/000162828026027570/exhibit991-form10x12ba3.htm), section Filing text; excerpt: All directors, named executive officers and executive officers as a group 54,021 (*)(*)
- [10-12B/A filed 2026-04-27](https://www.sec.gov/Archives/edgar/data/2083632/000162828026027570/exhibit991-form10x12ba3.htm), section Filing text; excerpt: All directors, named executive officers and executive officers as a group

### size_relative_to_parent

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-05-26
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R61.htm), section Filing text; excerpt: Weighted average ordinary shares outstanding - basic (in shares) 268,438 268,438 268,438 268,438
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R61.htm), section Filing text; excerpt: Weighted average ordinary shares outstanding - diluted (in shares) 268,438 268,438 268,438 268,438

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R2.htm), section Filing text; excerpt: Total assets 6,689,750 8,696,251
- [8-K filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055939/exhibit991q2fy26.htm), section Filing text; excerpt: At June 30, 2026, total cash and cash equivalents was $304 million and total debt was $644 million.

### absolute_market_cap

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-05-26
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R61.htm), section Filing text; excerpt: Weighted average ordinary shares outstanding - basic (in shares) 268,438 268,438 268,438 268,438
- [10-Q filed 2026-08-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026055943/R61.htm), section Filing text; excerpt: Weighted average ordinary shares outstanding - diluted (in shares) 268,438 268,438 268,438 268,438

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.
- [8-K filed 2026-05-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026033950/exhibit991-informationstat.htm), section Filing text; excerpt: n turn could cause our share price or trading volume to decline. Even if we do have equity research analyst coverage, we will not have any control over the analysts or the content and opinions included in their reports. Furthermore, if one or more of the analysts who do cover us downgrade Octave Class B Ordinary Shares or our industry, or the shares of any of our competitors, or publish inaccurate or unfavorable research about our business, t

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.
- [8-K filed 2026-05-12](https://www.sec.gov/Archives/edgar/data/2083632/000162828026033950/exhibit991-informationstat.htm), section Filing text; excerpt: e effect on Hexagon as a result of the Distribution. Hexagon’s capital stock may come under initial selling pressure as certain Hexagon shareholders sell their shares because they may have differing interests in or investment mandates with respect to holding an investment in Hexagon’s remaining business. In addition, the Distribution would separate from Hexagon the business and assets of Octave, which represent significant value, and the rela

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.

## Atrium Therapeutics, Inc. / 2093101

### parent

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-11-02](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm), section Filing text; excerpt: ments with BMS and LLY, respectively, assigned to the Company in connection with the Separation and Distribution from Avidity
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex41.htm), section Filing text; excerpt:  or after the Original Issue Date, the Company shall declare or make any dividend or other pro rata distribution of its assets (or rights to acquire its assets) to holders of shares of Common Stock, by way of return of capital or otherwise (including, without limitation, any distribution of cash, stock or other securities, property, options, evidence of indebtedness or any other assets by way of a dividend, spin off, reclassification, corporate rearrangement, scheme of arrangement or other similar transaction, but, for the av

### parent_cik

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-11-02](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002093101

### record_date

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex41.htm), section Filing text; excerpt: justment made pursuant to clause (i) of this paragraph shall become effective immediately after the record date for the determination of stockholders entitled to receive such dividend or distribution, provided, however, that if such record date shall have been fixed and such dividend is not fully paid on the date fixed therefor, the Number of Warrant Shares shall be recomputed accordingly as of the close of business on such record date a
- [10-Q filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2093101/000119312526349488/R39.htm), section Filing text; excerpt: off distribution ratio, description the Separation, holders of Former Parent Equity Award as of the Record Date received a non-transferable Make Whole Award pursuant to the 2026 Plan with respect to an aggregate of 1,590,677 shares of Company common stock. The Make Whole Awards were granted at a ratio of 1 share of Company common stock per 10 shares of Former Parent Common Stock underlying Former Parent Equity Award.

### insider_ownership_pct

Recovered by tested parser fix; exact sourced value.
Recovered value: 3.1; source: https://www.sec.gov/Archives/edgar/data/2093101/000119312526055010/d42675dex991.htm; Filing table; quote All directors and executive officers as a group (11 persons) \|  \|  \| 478,858 \|  \|  \|  \| 3.1 \| %
- [10-12B/A filed 2026-02-17](https://www.sec.gov/Archives/edgar/data/2093101/000119312526055010/d42675dex991.htm), section Table of Contents; excerpt: All directors and executive officers as a group (11 persons) 478,858 3.1 %
- [10-12B/A filed 2026-02-17](https://www.sec.gov/Archives/edgar/data/2093101/000119312526055010/d42675dex991.htm), section Table of Contents; excerpt: All directors and executive officers as a group (11 persons)

### size_relative_to_parent

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-02-27
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex41.htm), section Filing text; excerpt: ccordance with the terms of such stock on the Original Issue Date or as amended, that is payable in shares of Common Stock, (ii) subdivides its outstanding shares of Common Stock into a larger number of shares of Common Stock, (iii) combines its outstanding shares of Common Stock into a smaller number of shares of Common Stock or (iv) issues by reclassification of shares of capital stock any additional shares of Common Stock of the Company, then in each such case the Number of War
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex41.htm), section Filing text; excerpt:  or (3) any other notice by the Company or the Company’s transfer agent setting forth the number of shares of Common Stock outstanding (such issued and outstanding shares, the “Reported Outstanding Share Number”). For any reason at any time, upon the written or oral request of the Holder, the Company shall within one business day confirm orally and in writing or by electronic mail to the Holder the number of shares of Common Stock then outstanding. The Holder 

### insider_buying

Recovered by tested parser fix; exact sourced value.
Recovered value: 0; source: computed count of disclosed Form 4 code P transactions from 2026-02-26 through 2026-11-10; complete scanned issuer filing list https://data.sec.gov/submissions/CIK0002093101.json; 
Coverage: {"filings": 19, "amendments": 0, "complete_cached_xml": true}

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex101.htm), section Filing text; excerpt: t fair saleable value of such Person’s assets is less than the amount required to pay such Person’s total indebtedness or (ii) such Person is unable to pay its debts and liabilities, subordinated, contingent or otherwise, as such debts and liabilities become absolute and matured.
- [10-Q filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2093101/000119312526349488/R44.htm), section Filing text; excerpt: he Company’s forecast. The measure of segment assets is reported on the condensed balance sheets as total assets. Research and development expenses and general and administrative expenses are adjusted to exclude depreciation and stock-based compensation for segment presentation.

### absolute_market_cap

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-02-27
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex41.htm), section Filing text; excerpt: ccordance with the terms of such stock on the Original Issue Date or as amended, that is payable in shares of Common Stock, (ii) subdivides its outstanding shares of Common Stock into a larger number of shares of Common Stock, (iii) combines its outstanding shares of Common Stock into a smaller number of shares of Common Stock or (iv) issues by reclassification of shares of capital stock any additional shares of Common Stock of the Company, then in each such case the Number of War
- [8-K filed 2026-10-08](https://www.sec.gov/Archives/edgar/data/2093101/000119312526417402/d25901dex41.htm), section Filing text; excerpt:  or (3) any other notice by the Company or the Company’s transfer agent setting forth the number of shares of Common Stock outstanding (such issued and outstanding shares, the “Reported Outstanding Share Number”). For any reason at any time, upon the written or oral request of the Holder, the Company shall within one business day confirm orally and in writing or by electronic mail to the Holder the number of shares of Common Stock then outstanding. The Holder 

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.

## Midera Food Processing, Inc. / 2088281

**DATE ERROR:** The stored date is a record date in a today-completion announcement. Resolve the release dateline before using the price or return. Reviewed distribution date: 2026-07-06. Prices and date-dependent factors from the old date were removed.
Source: [0001193125-26-295649](https://www.sec.gov/Archives/edgar/data/2088281/000119312526295649/d25601dex991.htm), Midera Food Processing Completes Spin-Off, Begins Trading Tomorrow as Independent, Public Company; quote: To complete the spin-off, which was effective as of today at 12:01 a.m. Eastern Time, Middleby distributed all of the issued and outstanding shares of Midera common stock to Middleby stockholders on the basis of one share of Midera common stock for every one share of Middleby common stock held as of 4:00 p.m. Central Time on June 26, 2026, the record date for the distribution.

### parent

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R24.htm), section Filing text; excerpt: intent to separate its Food Processing Equipment Group into a standalone public company through the distribution of Midera common stock to Middleby stockholders (the “Spin-off”). On June 29, 2026, in connection with the completion of the Spin-off, the Company used borrowings under its revolving credit facility and cash on hand to make a distribution to Middleby of $233.0 million. On July 6, 2026, Middleby completed the Spin-off through the distribution of all of the then i
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R24.htm), section Filing text; excerpt: Basis of Presentation (b)Basis of PresentationPrior to the completion of the Spin-off, the Company historically operated as part of Middleby and not as a separate entity. These Condensed Combined Financial Statements of the Company have been derived from the historical condensed consolidated financial statements and accounting records of the Parent to present Midera’s Condensed Combined Financial Statements as if the Company had been operated on a standalone basis f

### parent_cik

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002088281

### distribution_ratio

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R24.htm), section Filing text; excerpt:  then issued and outstanding shares of Midera common stock to Middleby stockholders on the basis of one share of Midera common stock for every one share of Middleby common stock held as of 4:00 p.m. Central Time on June 26, 2026, the record date for the distribution, resulting in the distribution of 45,222,349 shares of Midera common stock to Middleby stockholders. Upon completion of the Spin-off, Midera became an independent public company and Middleby has no ownersh
- [8-K filed 2026-07-06](https://www.sec.gov/Archives/edgar/data/2088281/000119312526295649/d25601dex991.htm), section Filing text; excerpt: f the issued and outstanding shares of Midera common stock to Middleby stockholders on the basis of one share of Midera common stock for every one share of Middleby common stock held as of 4:00 p.m. Central Time on June 26, 2026, the record date for the distribution.

### record_date

Established by the exact record-date wording in the cited release.
Recovered value: 2026-06-26; source: 
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R24.htm), section Filing text; excerpt: or every one share of Middleby common stock held as of 4:00 p.m. Central Time on June 26, 2026, the record date for the distribution, resulting in the distribution of 45,222,349 shares of Midera common stock to Middleby stockholders. Upon completion of the Spin-off, Midera became an independent public company and Middleby has no ownership interest in the Company. Midera common stock began “regular way” trading on The Nasdaq Stock Market 
- [8-K filed 2026-07-06](https://www.sec.gov/Archives/edgar/data/2088281/000119312526295649/d25601dex991.htm), section Filing text; excerpt: or every one share of Middleby common stock held as of 4:00 p.m. Central Time on June 26, 2026, the record date for the distribution.

### insider_ownership_pct

No matching evidence in the cached documents reviewed; not proof of absence.

### size_relative_to_parent

Old distribution date was invalid; recomputation with the corrected date is required.
Selected first-close date: 2026-06-29
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R1.htm), section Filing text; excerpt: Entity Common Stock, Shares Outstanding 45,230,455
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R1.htm), section Filing text; excerpt: - DefinitionIndicate number of shares or other units outstanding of each of registrant's classes of capital or common stock or other ownership interests, if and as stated on cover of related periodic report. Where multiple classes or units exist define each class/interest by adding class of stock items such as Common Class A [Member], Common Class B [Member] or Partnership Interest [Member] 

### insider_buying

Old distribution date was invalid; recomputation with the corrected date is required.
Coverage: {"filings": 20, "amendments": 2, "complete_cached_xml": true}
- [4/A filed 2026-08-31](https://www.sec.gov/Archives/edgar/data/2088281/000119312526377038/0001193125-26-377038-index.html), section Ownership filing coverage; excerpt: Form 4 amendment requires transaction matching; the current engine leaves the count blank.
- [4/A filed 2026-08-31](https://www.sec.gov/Archives/edgar/data/2088281/000119312526376982/0001193125-26-376982-index.html), section Ownership filing coverage; excerpt: Form 4 amendment requires transaction matching; the current engine leaves the count blank.

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R49.htm), section Filing text; excerpt: Total debt 258.6 33.5
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R28.htm), section Filing text; excerpt: 026 Revolving credit facility $ 228.0 $ — Foreign loans 22.7 25.0 Finance lease obligations 7.9 8.5 Total debt 258.6 33.5 Less: Current maturities of long-term debt 4.5 4.8 Long-term debt $ 254.1 $ 28.7

### absolute_market_cap

Old distribution date was invalid; recomputation with the corrected date is required.
Selected first-close date: 2026-06-29
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R1.htm), section Filing text; excerpt: Entity Common Stock, Shares Outstanding 45,230,455
- [10-Q filed 2026-08-18](https://www.sec.gov/Archives/edgar/data/2088281/000119312526354735/R1.htm), section Filing text; excerpt: - DefinitionIndicate number of shares or other units outstanding of each of registrant's classes of capital or common stock or other ownership interests, if and as stated on cover of related periodic report. Where multiple classes or units exist define each class/interest by adding class of stock items such as Common Class A [Member], Common Class B [Member] or Partnership Interest [Member] 

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.
- [8-K filed 2026-06-22](https://www.sec.gov/Archives/edgar/data/2088281/000119312526276742/d17861dex991.htm), section Filing text; excerpt:  Middleby common stock and SpinCo common stock could experience selling pressure after the spin-off as certain pre-spin-off stockholders may not be interested in holding an investment in one of the two post-spin-off companies.
- [8-K filed 2026-06-22](https://www.sec.gov/Archives/edgar/data/2088281/000119312526276742/d17861dex991.htm), section Filing text; excerpt: Middleby common stock and SpinCo common stock could experience selling pressure after the spin-off as certain pre-spin-off stockholders may not be interested in holding an investment in one of the two post-spin-off companies.

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.

## Mobility Global Inc. / 2090312

### parent_cik

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-10-23](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000029/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002090312

### distribution_ratio

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R20.htm), section Filing text; excerpt: P Global’s common stock outstanding as of June 15, 2026 and on the basis of a distribution ratio of one share of Mobility Global common stock for every share of S&P Global’s common stock. There were no shares outstanding as of June 30, 2025.
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R17.htm), section Filing text; excerpt: ts and liabilities of the Spin Business to Mobility Global. On July 1, 2026, S&P Global distributed one share of Mobility Global common stock for every share of S&P Global common stock held as of the close of business on June 15, 2026, the record date for the Distribution. On July 1, 2026, Mobility Global became an independent, publicly traded company under the stock symbol “MBGL” on the New York Stock Exchange. S&P Global retained no ownership interest in Mobility Global. As 

### record_date

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R17.htm), section Filing text; excerpt: k for every share of S&P Global common stock held as of the close of business on June 15, 2026, the record date for the Distribution. On July 1, 2026, Mobility Global became an independent, publicly traded company under the stock symbol “MBGL” on the New York Stock Exchange. S&P Global retained no ownership interest in Mobility Global. As of the date of Separation, the primary source of cash on hand was generated by operations and net pr
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R17.htm), section Filing text; excerpt: of the close of business on June 15, 2026, the record date for the Distribution. On July 1, 2026, Mobility Global became an

### insider_ownership_pct

No matching evidence in the cached documents reviewed; not proof of absence.

### size_relative_to_parent

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-07-02
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R38.htm), section Filing text; excerpt: Number of shares outstanding (in shares) \| shares 294,821,320 0 294,821,320 0 294,821,320
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R38.htm), section Filing text; excerpt: - DefinitionNumber of shares of common stock outstanding. Common stock represent the ownership interest in a corporation. + ReferencesReference 1: http://www.xbrl.org/2009/role/commonPracticeRef -Topic 505 -SubTopic 10 -Name Accounting Standards Codification -Section 50 -Paragraph 2 -Publisher FASB -URI https://asc.fasb.org/1943274/2147481112/505-10-50-2Reference 2: http://www.xbrl.o

### insider_buying

Recovered by tested parser fix; exact sourced value.
Recovered value: 3; source: computed count of disclosed Form 4 code P transactions from 2026-07-01 through 2026-11-10; complete scanned issuer filing list https://data.sec.gov/submissions/CIK0002090312.json; https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/wk-form4_1786654758.xml transaction date 2026-08-11 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-08-11</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>10000</value> </transactionshares> <transactionpricepershare> <value>19.50</value> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>10000</value> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/wk-form4_1786654758.xml transaction date 2026-08-12 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-08-12</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>25000</value> </transactionshares> <transactionpricepershare> <value>19.4998</value> <footnoteid id="F1"></footnoteid> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>35000</value> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>; https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/wk-form4_1786654758.xml transaction date 2026-08-13 quote <nonderivativetransaction> <securitytitle> <value>Common Stock</value> </securitytitle> <transactiondate> <value>2026-08-13</value> </transactiondate> <transactioncoding> <transactionformtype>4</transactionformtype> <transactioncode>P</transactioncode> <equityswapinvolved>0</equityswapinvolved> </transactioncoding> <transactionamounts> <transactionshares> <value>15000</value> </transactionshares> <transactionpricepershare> <value>19.8714</value> </transactionpricepershare> <transactionacquireddisposedcode> <value>A</value> </transactionacquireddisposedcode> </transactionamounts> <posttransactionamounts> <sharesownedfollowingtransaction> <value>50000</value> </sharesownedfollowingtransaction> </posttransactionamounts> <ownershipnature> <directorindirectownership> <value>D</value> </directorindirectownership> </ownershipnature> </nonderivativetransaction>
Coverage: {"filings": 16, "amendments": 0, "complete_cached_xml": true}

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R4.htm), section Filing text; excerpt: Total assets 13,060 12,995
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R27.htm), section Filing text; excerpt: Total debt 1,981.0 0.0

### absolute_market_cap

No usable shares outstanding on the selected first-close date; other dated/estimated/weighted-average counts are not substitutes.
Selected first-close date: 2026-07-02
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R38.htm), section Filing text; excerpt: Number of shares outstanding (in shares) \| shares 294,821,320 0 294,821,320 0 294,821,320
- [10-Q filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/R38.htm), section Filing text; excerpt: - DefinitionNumber of shares of common stock outstanding. Common stock represent the ownership interest in a corporation. + ReferencesReference 1: http://www.xbrl.org/2009/role/commonPracticeRef -Topic 505 -SubTopic 10 -Name Accounting Standards Codification -Section 50 -Paragraph 2 -Publisher FASB -URI https://asc.fasb.org/1943274/2147481112/505-10-50-2Reference 2: http://www.xbrl.o

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.
- [10-12B/A filed 2026-05-27](https://www.sec.gov/Archives/edgar/data/2090312/000110465926066592/tm2528763d9_ex99-1.htm), section Filing text; excerpt: ct planning and financial/​investment planning. The Planning Solutions dataset is supported by deep analyst coverage and bidirectional industry feedback. Our foundational product is global vehicle, powertrain and supply chain forecasts.
- [10-12B filed 2026-05-07](https://www.sec.gov/Archives/edgar/data/2090312/000110465926057155/tm2528763d7_ex99-1.htm), section Filing text; excerpt: ct planning and financial/​investment planning. The Planning Solutions dataset is supported by deep analyst coverage and bidirectional industry feedback. Our foundational product is global vehicle, powertrain and supply chain forecasts. Leveraging this foundation allows for upselling into scenario capabilities (FAST), procurement intelligence (PIQ) and supplier workflow software (DA). We believe our market penetration is strong, with broad OE

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.

## Platinum SpinCo, Inc. / 2134183

**DATE ERROR:** The stored date is an incorporation date; this quotation describes a future distribution. Distribution date and window need correction. Reviewed distribution date: None. Prices and date-dependent factors from the old date were removed.
Source: [0001193125-26-349114](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex991.htm), Information about the Companies; quote: Platinum SpinCo Inc. was incorporated on January 23, 2026 and is currently a wholly owned direct subsidiary of Modine. In connection with the Separation and Distribution, Modine will cause specified assets and liabilities used in the Performance Technologies Business to be transferred to SpinCo, after which time all of the shares of SpinCo Common Stock will be distributed to Modine shareholders.

### parent

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-26](https://www.sec.gov/Archives/edgar/data/2134183/000110465926101088/R21.htm), section Filing text; excerpt: s to the Parent in a non-cash transaction as part of an internal reorganization associated with the Spin-Off.Cash pooling arrangementsModine utilizes a centralized approach by region for the purposes of cash management and financing its operations. The Company participates in and manages certain of these cash pooling arrangements. Cash is swept daily to the cash pool owner who funds the businesses’ operating and investing activities as needed. This mechanism optimizes cash management and is used to e
- [8-K filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex992.htm), section Filing text; excerpt: Modine’s other businesses and the subsequent merger of the Performance Technologies Business with a wholly owned subsidiary of Gentherm Incorporated (“Gentherm”) that are now available for your review. This notice provides instructions on how to access MODINE MANUFACTURING COMPANY materials for informational purposes only. The separation and merger will occur by means of a pro rata distribution by Modine of all of the outstanding common stock of Pla

### parent_cik

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-09-30](https://www.sec.gov/Archives/edgar/data/2134183/000119312526409024/R1.htm), section Filing text; excerpt: Entity Central Index Key 0002134183

### record_date

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-09-30](https://www.sec.gov/Archives/edgar/data/2134183/000119312526409024/d141507dex31.htm), section Filing text; excerpt: the “Modine Common Stock”) issued and outstanding as of the close of business, Eastern Time, on the Record Date (as defined in the Separation Agreement, dated January 29, 2026, among the Corporation, Modine and Gentherm Incorporated), excluding any shares of Modine Common Stock held as treasury stock by Modine or held by any of Modine’s subsidiaries, in each case, as of such time, minus (b) the excess, if any, of (i) 2,000, which represe
- [8-K filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex991.htm), section Filing text; excerpt: The Board of Directors of Gentherm has fixed the close of business on July 31, 2026 as the record date for the Special Meeting (the “Record Date”). Only shareholders of record of Gentherm Common Stock at the close of business on the Record Date are entitled to receive notice of, and to vote at, the Special Meeting or any adjournment or postponement thereof. For at least ten (10) days prior to the Special Meeting, a list of the s

### ticker

Related filing text found; extraction/interpretation review required.
- [8-K filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex991.htm), section Filing text; excerpt: A: Modine Common Stock is currently listed on the NYSE under the ticker symbol “MOD.” It is currently expected that there will not be an “ex-distribution” market in Modine Common Stock on the NYSE and Modine Common Stock will trade only in the “regular way” market through the Closing.
- [8-K filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex991.htm), section Filing text; excerpt: Modine Common Stock is currently listed on the NYSE under the ticker symbol “MOD.” It is currently expected that there will not be an “ex-distribution” market in Modine Common Stock on the NYSE and Modine Common Stock will trade only in the “regular way” market through the Closing.

### insider_ownership_pct

No matching evidence in the cached documents reviewed; not proof of absence.

### size_relative_to_parent

Old distribution date was invalid; recomputation with the corrected date is required.
Selected first-close date: None
- [8-K filed 2026-09-30](https://www.sec.gov/Archives/edgar/data/2134183/000119312526409024/d141507dex31.htm), section Filing text; excerpt: endment becomes effective in accordance with the DGCL (such time, the “Recapitalization Time”), all shares of Common Stock issued and outstanding immediately prior to the Recapitalization Time (including, for the avoidance of doubt, any shares of Common Stock issued by the Corporation to Modine Manufacturing Company, a Wisconsin corporation (“Modine”), at any time prior to the Recapitalization Time) shall, automatically without any further action on the part of the Corpo
- [10-Q filed 2026-08-26](https://www.sec.gov/Archives/edgar/data/2134183/000110465926101088/R1.htm), section Filing text; excerpt: Entity Common Stock, Shares Outstanding 1,000

### insider_buying

Old distribution date was invalid; recomputation with the corrected date is required.
Coverage: {"filings": 5, "amendments": 0, "complete_cached_xml": true}

### early_price_performance

Old distribution date was invalid; recomputation with the corrected date is required.
- [8-K filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex991.htm), section Filing text; excerpt: ng (a) the average volume weighted average trading price of a share of Modine Common Stock trading “regular way with due bills” on the applicable exchange (i.e., inclusive of SpinCo value) for the five (5) consecutive trading days ending two (2) trading days prior to the date on which the Determination Time occurs by (b) the average volume weighted average trading price of a share of Gentherm Common Stock trading on the applicable exchan
- [8-K filed 2026-08-13](https://www.sec.gov/Archives/edgar/data/2134183/000119312526349114/d101885dex991.htm), section Filing text; excerpt: ribution” market in Modine Common Stock on the NYSE and Modine Common Stock will trade only in the “regular way” market through the Closing.

### debt_to_assets

Related filing text found; extraction/interpretation review required.
- [10-Q filed 2026-08-26](https://www.sec.gov/Archives/edgar/data/2134183/000110465926101088/R62.htm), section Filing text; excerpt: Total assets $ 714.5 $ 815.8
- [10-Q filed 2026-08-26](https://www.sec.gov/Archives/edgar/data/2134183/000110465926101088/R62.htm), section Filing text; excerpt: Total assets 714.5 815.8

### absolute_market_cap

Old distribution date was invalid; recomputation with the corrected date is required.
Selected first-close date: None
- [8-K filed 2026-09-30](https://www.sec.gov/Archives/edgar/data/2134183/000119312526409024/d141507dex31.htm), section Filing text; excerpt: endment becomes effective in accordance with the DGCL (such time, the “Recapitalization Time”), all shares of Common Stock issued and outstanding immediately prior to the Recapitalization Time (including, for the avoidance of doubt, any shares of Common Stock issued by the Corporation to Modine Manufacturing Company, a Wisconsin corporation (“Modine”), at any time prior to the Recapitalization Time) shall, automatically without any further action on the part of the Corpo
- [10-Q filed 2026-08-26](https://www.sec.gov/Archives/edgar/data/2134183/000110465926101088/R1.htm), section Filing text; excerpt: Entity Common Stock, Shares Outstanding 1,000

### analyst_recommendations

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

### unwanted_selling_pressure

Required by current positive weight; this pipeline has no defined sourced observation for this factor.

Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
Cache limitation: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
## Limits

- Related text excerpts are review evidence, not accepted numerical observations.
- This audit covers all original blank fields for the seven candidates excluded for missing factors. Other candidates without distribution dates are outside this audit.
- Three incorrect distribution dates were corrected or cleared in the reviewed snapshot. Old first prices, early returns and other date-dependent factors were removed; replacement market data was not requested.
- Only the reviewed snapshot is changed. The original snapshot and registry are preserved.

screens, not recommendations
