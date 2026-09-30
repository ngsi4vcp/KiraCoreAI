# Genome

## Current revision

**G22 / Revision 22 / Series 1000 / 2026**

The authoritative G22 source supplied for this project has SHA-256:

~~~text
d76d59ee1e4e82f57cc7dd961512e3f35898343d8196c746a10a9be59700ff65
~~~

This hash identifies the supplied G22 artifact exactly.

## Import status

The repository architecture and governance now reference G22 Rev. 22, but the verbatim 472-line G22 artifact has **not yet been copied into this repository** by the current GitHub connector workflow.

Therefore this directory deliberately does not pretend that the repository already contains the canonical genome text.

The next genome operation is a controlled verbatim import:

1. copy the exact G22 artifact;
2. verify SHA-256;
3. store it as a versioned genome artifact;
4. record the commit;
5. use that commit as genome provenance.

No implementation code should silently modify the imported text.

## Governance

Genome changes are separate from normal runtime development and require explicit authorized fixation according to G22.
