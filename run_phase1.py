"""
run_phase1.py
-------------
Usage:
    # with a PDF
    python run_phase1.py lecture.pdf

    # with sample text (no argument)
    python run_phase1.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.parser import process_text, save_to_json
from utils.pdf import extract_text_from_pdf

SAMPLE = """
In this study, we deduce a spatially and temporally linked paired metamorphism from the Western
Dharwar Craton (WDC), South India, for which we use representative rocks from the medium-grade
(MG) (e.g. pelitic schist) and high-grade (HG) (e.g. maﬁc and metasedimentary granulites) domains in
the craton. Using metamorphic reconstructions (P-T-t paths of evolution and thermobaric, T/P ratios at
the metamorphic peak), garnet-biotite diffusion chronometry, monazite chemical dating techniques of
the investigated rocks and published metamorphic and geochronological dataset, we demonstrate that the
two domains, despite having a record of uniform burial to lower crustal depths, differ in their thermal (T-
t) history. The medium-grade domain records relatively cooler, intermediate T/P type of metamorphism in
the stability ﬁeld of kyanite with TMax at ∼650-630 ◦ C, multiple metamorphic cycles, all along clockwise
P-T paths of evolution, and representing recurring burial-exhumation and heating-cooling cycles and
ﬁnally, relatively short-lived nature of residence at the medium- to lower crustal levels (t ∼ 10-20
Myrs) and faster metamorphic cooling (dT/dt ∼10-20 ◦ C/Myr) and exhumation rates (dz/dt∼0.6-1.1 to
1-2 mm/yr). The high-grade domain, in contrast records relatively warmer, high T/P metamorphism (T/P
ratios at ∼800-870 ◦ C/GPa) in the stability ﬁeld of sillimanite with TMax at ∼800–870 ◦ C, recurring burial-
exhumation stages as part of one prograde heating event along a monocyclic CW P-T path of evolution
and ﬁnally, extremely long-lived lower-mid-crustal residence (t ∼ 238 Myrs) and ultra-slow cooling
(∼2 ◦ C/Myr) and exhumation (∼0.1 mm/yr) history. Both domains show broadly coeval metamorphism
as part of the same orogenesis between c.2.53 and 2.41 Ga. We use these ﬁndings from the WDC to
suggest the development of a paired metamorphism as part of a peel-back convergence style of plate
tectonics at the Archaean-Proterozoic boundary in the planet Earth.
© 2023 Elsevier B.V. All rights reserved.
1. Introduction
There is a general consensus that a form of plate tectonics,
marking a change over from “pre-subduction”, plume-driven ver-
tical tectonics (cf. hot stagnant lid regime) to a regime of asym-
metric plate subduction mode became operational at the Archean-
Proterozoic boundary in the Planet Earth (Cawood et al., 2022
for a general review). However, there is ongoing debate on the
variability of this Early Earth process and how to recognise and
model it from the preserved Archaean rock archives (Korenaga,
* Corresponding author.
E-mail address: santanu@gg.iitkgp.ac.in (S.K. Bhowmik).
https://doi.org/10.1016/j.epsl.2023.118414
0012-821X/© 2023 Elsevier B.V. All rights reserved.
2013; Lenardic, 2018) Regional metamorphic rocks in ancient oro-
genic belts have emerged as excellent monitors of tectonic settings
during orogenesis through reconstructed P-T-t paths of evolution
and the calculated PMax and thermobaric ratios (T/P) at the meta-
morphic peak (e.g. Dasgupta et al., 2022; Basak et al., 2023). In
general, deep burials during high-pressure (HP)-amphibolite to HP-
granulite facies metamorphism, and along steeper dP/dT gradient
and CW P-T paths of evolution have been used to decipher fossil
convergent plate margins and operations of plate tectonics (Eng-
land and Thompson, 1984; Ernst, 1988; Harley, 1989; Jamieson,
1991; Brown, 1993; O’Brien and Rötzler, 2003; Ao and Bhowmik,
2014). Robust metamorphic evidence for convergent plate margin
processes at the Archaean-Proterozoic boundary is now available
from several recent studies that record the ﬁrst oceanic eclogites,A. Dasgupta, S.K. Bhowmik, A. Das et al.
Earth and Planetary Science Letters 622 (2023) 118414
indicating deep subduction of the Archean oceanic crust to a depth
of 65 to 70 km (Ning et al., 2022) and pulsating orogenesis and
recurring burial-exhumation cycles along colder thermal gradients
(Dasgupta et al., 2022). In this study, we use the term ‘pulsating
orogenesis’ after Bhowmik and Chakraborty (2017) to deﬁne an
orogenesis that consists of several short-lived heating-cooling and
burial-exhumation stages, as part of multiple metamorphic cycles,
each with a characteristic P-T path of evolution.
In an another approach, in particular for the Phanerozoic Earth,
paired metamorphism (after Miyashiro, 1961, 1973) that recog-
nises contrasting thermal gradients and metamorphism (high P/T
vs. low P/T type) (Fig. 1a) in orogen-parallel, metamorphic belts
of the same age, either occurring in situ or tectonically juxta-
posed (e.g. Brown, 1998), and from Paciﬁc-type accretionary oro-
gens, is indicative of unequivocal, one-sided, asymmetric subduc-
tion at convergent plate margins (Gerya et al., 2008). The contrast-
ing thermal regimes as marked by cooler glaucophane-jadeite-type
metamorphic facies series [prehnite-pumpellyite → blueschists →
eclogites (high-pressure to ultra-high pressure type)] and warmer
andalusite - sillimanite-type facies series (greenschist → amphi-
bolite → granulite) represent spatially adjacent fossil subduction
to collisional suture and the arc-back-arc systems in the orogenic
hinterland respectively (Oxburgh and Turcotte, 1971).
The Archaean hotter earth inhibits the formations of cold
lawsonite-blueschists/eclogites and ultra-high pressure metamor-
phic rocks, the classical petrological indicators of subduction (cf.
high P/T metamorphism of Miyashiro, 1961, 1973). In such a
scenario, the concept of paired metamorphism has been fur-
ther expanded to recognise and relate the duality of thermal
regimes - one warmer along high T/P thermal gradient [cf. high
T/P metamorphism (Fig. 1a), and producing granulites to ultra-
high-temperature granulites (G-UHT)] and the other colder along
intermediate T/P gradient [(cf. intermediate T/P metamorphism
(Fig. 1a), and producing eclogite to high-pressure granulites (E-
HPG)] with Early Earth proto-subduction zone and arc–back-arc
systems (Brown, 2006, 2009, 2010; also updated in Brown and
Johnson, 2018, 2019a, b). From statistical analysis of the global
metamorphic dataset, the ﬁrst appearance of paired metamor-
phism (cf. intermediate T/P and high T/P types), and in the process,
the advent of plate tectonics in the Planet Earth, has been argued
to have taken place since c.2.8 Ga (Brown, 2006) or at the dawn
of the Proterozoic (Holder et al., 2019). One important assump-
tion here is that the rocks representing the paired metamorphism
in the global dataset are also spatially paired in their occurrences,
which, however, is not adequately known at this stage.
Recent developments of realistic thermo-mechanical models,
akin to the hotter Early Earth and ambient mantle (e.g. Capitanio et
al., 2019) do recognise paired metamorphism in two spatially ad-
jacent tectonic domains, namely the thickened crustal zone (TCZ)
and the peel-off zone (PoZ) (nomenclature after Chowdhury et
al., 2017, 2021) that are produced by a variant of plate tecton-
ics, called the peel-back convergence mode (Fig. 1b) (Chowdhury
et al., 2017, 2020, 2021). While the modelled granulite facies rocks
from both these domains show a history of deep burials with PMax
in excess of 10 kbar and a phase of decompression from PMax , and
predating prograde heating to peak granulite facies metamorphic
conditions, they differ in Ps at TMax and attendant thermobaric
ratios (intermediate T/P for the TCZ and high T/P for the PoZ do-
mains), producing a duality of thermal regime (Fig. 1c).
Despite its promise to decode the Archaean plate tectonics, the
occurrence of spatially and temporally linked paired metamorphic
belts in the metamorphic rock record is extremely meagre (e.g. the
southern North China Craton, Huang et al., 2020). Several studies
in spatially associated high-grade terranes and granite-greenstone
cratons (e.g. high-grade Limpopo belt between Kaapvaal and Zim-
babwe cratons) recognised contrasting thermal history and P-T gra-
Fig. 1. (a) A scaled P-T diagram showing the ﬁelds of three baric (after Miyashiro,
1961) and thermobaric (after Brown and Johnson, 2019b) types of metamorphism is
contoured with model thermal gradients (values in GPa/◦ C) (compiled diagram af-
ter Dasgupta and Bhowmik, 2021). The metamorphic types in the two classiﬁcations
are referred by M and BJ respectively. While in the Phanerozoic Earth, the paired
metamorphism is indicated by temporally and spatially adjacent metamorphic belts
showing high P/T (glaucophane-jadeite-type) and low P/T (andalusite-sillimanite-
type) facies series, the same in the Early Earth is deﬁned by the recognition of
duality of thermal regimes in the metamorphic belts, one with intermediate T/P
and the other with high T/P metamorphism (see text for further details). (b) Tec-
tonic cartoon showing a thermo-mechanically modelled embryonic convergent plate
margin setting for hotter Early Earth (cf. peel-back convergence model) along with
different tectono-metamorphic domains (cf. TCZ-A, TCZ-G and PoZ-G, see text for
further details) (after Chowdhury et al., 2017, 2020, 2021). (c) Thermo-mechanical
model predictions of contrasting metamorphic types and representative P-T paths
of evolutions from two spatially adjacent tectonic domains in the peel-back conver-
gent type of plate tectonics (after Chowdhury et al., 2020).
dients (e.g. high P/T prograde-retrograde P-T paths in lower grade
greenstone belts vs. low P/T retrograde P-T paths in granulite ter-
ranes) (Perchuk and Gerya, 2011 and references cited therein).
While this feature of contrasting thermal history in spatially ad-
jacent metamorphic belts resembles paired metamorphism, this is
attributed to gravitational instability and redistribution of green-
stone successions owing to mantle-derived ﬂuid-heat ﬂow (Per-
chuk and Gerya, 2011), and not to asymmetric, one-sided plate
subduction. It is, therefore, a challenge to apply the different meta-
morphic attributes in the preserved Archaean to Earliest Palaeo-
proterozoic rock record to establish a more widespread record of
paired metamorphism, including that proposed in the peel-back
convergent setting. One way to further improve our understand-
ing of paired metamorphism, and also the emergence and style of
plate tectonics is by examining the cooling and exhumation rates
of deeply buried metamorphic rocks, in particular with a record
of contrasting thermal history. In a general way, long linear Late
Archean metamorphic belts with a record of deep burials, and in-
terpreted to be the products of subduction-accretion processes at
convergent plate boundaries (e.g. Smithies et al., 2018), seem to
2A. Dasgupta, S.K. Bhowmik, A. Das et al.
Earth and Planet
"""

# ── Get input ────────────────────────────────────────────────
if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
    print(f"📄 Reading PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    print(f"✅ Extracted {len(text):,} characters from {pdf_path}\n")
else:
    print("📝 No PDF provided — using sample lecture text\n")
    text = SAMPLE

# ── Run pipeline ─────────────────────────────────────────────
results = process_text(text)
save_to_json(results)

# ── Print results ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("NOTES")
print("=" * 50)
for i, note in enumerate(results["notes"], 1):
    print(f"{i:>2}. {note}")

print("\n" + "=" * 50)
print("FLASHCARDS")
print("=" * 50)
for i, card in enumerate(results["flashcards"], 1):
    print(f"\nCard {i}:")
    print(f"  Q: {card['q']}")
    print(f"  A: {card['a']}")

print("\n" + "=" * 50)
print("MCQs")
print("=" * 50)
icons = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
for i, q in enumerate(results["mcqs"], 1):
    print(f"\nQ{i} {icons.get(q['difficulty'], '')} [{q['difficulty']}]")
    print(f"   {q['question']}")
    for opt in q["options"]:
        marker = "✅" if opt.startswith(q["answer"]) else "  "
        print(f"   {marker} {opt}")

print("\n" + "=" * 50)
print(f"✅ {len(results['notes'])} notes  |  "
      f"{len(results['flashcards'])} flashcards  |  "
      f"{len(results['mcqs'])} MCQs")
print("=" * 50)