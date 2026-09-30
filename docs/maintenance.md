# Maintenance and release

Initial import groups are disclosure/architecture, executable sample, regression tests,
then CI/security documentation. Record them with current timestamps; do not imitate
historic development. No company history is imported.

After the initial validated main, use feature/, docs/ or fix/ branches and pull requests
for substantive changes. Local checks match CI commands in the root README.
After hosted CI exists, require its actual successful check names, disallow main deletion
and force pushes. Do not require a second human reviewer for a solo repository.
Check ruleset availability on the actual account before promising enforcement.

v0.1.0 is a candidate, not a release. Before tagging: owner/IP and license decision,
private reporting configured, hosted CI green, README/SVG/link review, clean tree and
no unexpected artifacts. Scan committed history, not only the checkout.
A passing heuristic scan does not certify intellectual-property clearance.

The standard-library sample has no package install step. Dependabot updates action
references; optional libraries are not covered by a tested lockfile.
