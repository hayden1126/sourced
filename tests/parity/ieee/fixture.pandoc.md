# Fixture: ieee parity

<!--
This fixture exercises IEEE-specific rendering behavior:
  - sequential numeric assignment at first appearance ([1], [2], [3], [4])
  - a citation whose id sorts FIRST alphabetically (Able) but appears LATER
    in the prose, to prove bibliography ordering is by appearance, not alpha
  - a grouped citation with multiple ids at one callsite
  - a repeat citation of an already-assigned id to confirm the number is stable
  - a locator (page) on a repeat to confirm the [N, p. M] form
  - a 4-author entry to exercise et-al behavior in the bibliography
-->

The signal-processing baseline for this line of work came from @tang-2012,
whose framework underpins later treatments. A complementary hardware study
followed shortly after [@patel-2014]. Subsequent theoretical work refined the
convergence bounds [@oduya-2016]. The original framework was then revisited
with a sharper quantitative claim [@tang-2012, p. 118], confirming the
numbering stays stable on a repeat cite.

A broader survey consolidated the three lines of evidence
[@tang-2012; @patel-2014; @oduya-2016], and a four-author collaboration
extended the empirical base with field measurements
[@able-baker-chen-davies-2019]. Standards reporting added institutional
context [@ieee-std-2020].

# References
