# P100 source register - post-unblinding only

This register maps the anonymous P100 IDs to public artist and track-title metadata captured during corpus construction.

## Strict use boundary

- This file is **not** model-facing input.
- Never provide this file, its contents, or this repository root to a blind evaluator or subagent.
- A blind run must supply only `data/preview100/manifest_public.json`, the local anonymous audio directory, the frozen prompt, and the run contract.
- Reading this file before selection makes that evaluator's run unblinded and unsuitable for the blind-policy claim.

This registry contains metadata only. It does **not** grant rights to redistribute, download, publish, or re-host the audio files.

| blind_id | artist | track title |
|---|---|---|
| p001.ogg | Iron Maiden | Fear of the Dark |
| p002.ogg | Cosmic Gate | Exploration of Space |
| p003.ogg | Simon Preston | Toccata and Fugue in D Minor, BWV 565: I. Toccata |
| p004.ogg | Riva | Run Away |
| p005.ogg | Nightlapse | Love Shy |
| p006.ogg | Metallica | Enter Sandman |
| p007.ogg | Venom | Black Metal |
| p008.ogg | Iron Maiden | Fear of the Dark (Live In Buenos Aires 7/3/08) |
| p009.ogg | Iron Maiden | Fear of the Dark (Live) |
| p010.ogg | Iron Maiden | Fear of the Dark (Live) |
| p011.ogg | Iron Maiden | Fear of the Dark (Live '01) |
| p012.ogg | Cosmic Gate | Exploration of Space (Cosmic Gate's Third Contact Remix) |
| p013.ogg | Cosmic Gate | Exploration of Space (Extended Mix) |
| p014.ogg | Cosmic Gate | Exploration of Space (Radio Edit) |
| p015.ogg | Cosmic Gate | Exploration of Space (Mixed) |
| p016.ogg | Simon Preston | Toccata and Fugue in D Minor, BWV 565: II. Fugue |
| p017.ogg | Bruno Lawrence Raco | Bach Toccata and Fugue (Jete Temps Leve) |
| p018.ogg | Walter Rinaldi | Waltz No. 10 in B Minor, Op. 69, No. 2: Moderato |
| p019.ogg | Walter Rinaldi | Etude No. 3 in G -Sharp Minor, S. 140 "La Campanella": III. Allegretto |
| p020.ogg | Riva | Run Away (Mixed) [Mixed] |
| p021.ogg | NoizBasses | Run Away (ORG. RIVA) |
| p022.ogg | d4vd | Run Away |
| p023.ogg | Airborn & Bogdan Vix & KeyPlayer | Run Away (feat. Alexandra Badoi) [Live] [Mixed] |
| p024.ogg | Metallica | Enter Sandman (Live) |
| p025.ogg | Metallica | Enter Sandman (May 13th, 1991 Rough Mix) |
| p026.ogg | Metallica | Enter Sandman |
| p027.ogg | Metallica & San Francisco Symphony | Enter Sandman (Live) |
| p028.ogg | Venom | Black Metal (Radio 1 Session) |
| p029.ogg | Venom | Black Metal |
| p030.ogg | Venom | Black Metal (Live) |
| p031.ogg | Venom | Black Metal (2019 Remaster) |
| p032.ogg | London Philharmonic Orchestra & David Parry | Adagio for Strings |
| p033.ogg | Hans Zimmer | Time |
| p034.ogg | Keane Wang | Grace is Greater |
| p035.ogg | Vienna Philharmonic & Lorenzo Viotti | Manon Lescaut: Intermezzo |
| p036.ogg | Timmy Trumpet & Bassjackers | Classical Music |
| p037.ogg | Yo-Yo Ma | Cello Suite No. 1 in G Major, BWV 1007: I. Prelude |
| p038.ogg | Maxim Emelyanychev, Jakub Jozef Orlinski & Il Pomo d'Oro | Il Giustino, RV 717, Act I: Vedro con mio diletto (Anastasio) |
| p039.ogg | Rinaldo Alessandrini & Concerto Italiano | Brandenburg Concerto No. 3 in G Major, BWV 1048: I. |
| p040.ogg | Glenn Gould | Goldberg Variations, BWV 988 (1955 Recording): Aria |
| p041.ogg | Ed Sheeran | Happier |
| p042.ogg | Background Instrumental Music Collective | Romantic Symphony |
| p043.ogg | Harry Styles | Watermelon Sugar |
| p044.ogg | Lord Huron | The Night We Met |
| p045.ogg | The Goo Goo Dolls | Iris |
| p046.ogg | Richard Armstrong, London Philharmonic Orchestra & Roberto Alagna | Carmen, opera-comique in 4 acts Act II: La fleur que tu m'avais jetee |
| p047.ogg | Rory Marsden, Alexander Wilson, Alex Tschallener & Jarmila Vantuchova | Carmen, Act I: L'amour est un oiseau rebelle |
| p048.ogg | Charles K. L. Davis, New York Philharmonic & Wilfred Pelletier | Turandot: Act III - "Nessun Dorma" |
| p049.ogg | Rory Marsden, Alexander Wilson, Alex Tschallener & Giuseppe Verdi | La Traviata, Act I: Libiamo, ne'lieti calici |
| p050.ogg | Anna Netrebko, Vienna Philharmonic & Gianandrea Noseda | La Boheme, Act I: "Quando me'n vo" (Musette's Waltz, Concert Version) |
| p051.ogg | Alicia Nando | Jazz (Sexual Guitar) |
| p052.ogg | sanah & Vito Bambino | Ale jazz! |
| p053.ogg | Richard Wess & Betty Carter | Jazz (Ain't Nothin' But Soul) |
| p054.ogg | Eva | Jazz |
| p055.ogg | Sade | Smooth Operator |
| p056.ogg | Adele | Love in the Dark |
| p057.ogg | Billie Eilish | when the party's over |
| p058.ogg | Harry Styles | Sign of the Times |
| p059.ogg | Billie Eilish | BIRDS OF A FEATHER |
| p060.ogg | Everlast | Soul Music |
| p061.ogg | Powfu | i wont sell my soul |
| p062.ogg | Steve Lacy | pure colour (feat. Erykah Badu) |
| p063.ogg | Steve Lacy | show you me |
| p064.ogg | Steve Lacy | nothing |
| p065.ogg | Roy Ayers | Funk in the Hole |
| p066.ogg | Ray Charles | Hit the Road Jack |
| p067.ogg | Jamiroquai | Cloud 9 |
| p068.ogg | Jamiroquai | Automaton |
| p069.ogg | The Meters | Cissy Strut |
| p070.ogg | Fimiani & Fabo | Disco Music |
| p071.ogg | Madonna | Music |
| p072.ogg | Surf Curse | Disco |
| p073.ogg | Fancy | Flames of Love |
| p074.ogg | Lipps, Inc. | Funkytown |
| p075.ogg | Charli xcx | Rock Music |
| p076.ogg | Charli xcx | Rock Music |
| p077.ogg | Theory of a Deadman | Funeral Song |
| p078.ogg | In This Moment | Crawl |
| p079.ogg | Nightwish | Music |
| p080.ogg | In This Moment | Sleeping with the Enemy |
| p081.ogg | In This Moment & Kim Dracula | Heretic (feat. Kim Dracula) |
| p082.ogg | Tesla | Mind Your Own Business |
| p083.ogg | Skunx | Punk Rock |
| p084.ogg | Bachor | Punk Rock |
| p085.ogg | Mogwai | Punk Rock: |
| p086.ogg | The Stranglers | Golden Brown |
| p087.ogg | Fall Out Boy | Centuries |
| p088.ogg | Alice In Chains | Would? |
| p089.ogg | Alice In Chains | Nutshell |
| p090.ogg | Alice In Chains | Rooster |
| p091.ogg | Nirvana | The Man Who Sold the World (Live Acoustic) |
| p092.ogg | Mad Season | Wake Up |
| p093.ogg | Hazar Altn | Gece Bekcisi (Akustik) |
| p094.ogg | Thirty Seconds to Mars | The Kill (Bury Me) |
| p095.ogg | Guns N' Roses | Paradise City |
| p096.ogg | Meskie Granie Orkiestra, Daria Zawiaow, Bazej Krol & IGO | Swit |
| p097.ogg | Deep Purple | Child In Time |
| p098.ogg | Pink Floyd | Breathe (In the Air) |
| p099.ogg | Omega | Gyongyhaju lany |
| p100.ogg | Pink Floyd | One of My Turns |
