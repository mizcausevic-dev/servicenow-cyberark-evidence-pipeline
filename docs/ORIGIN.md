# Why We Built This

Privileged-access review work usually fails in the gap between systems, not inside any one system. ServiceNow incidents can look active and well-tracked. CyberArk can hold the account, safe, and approval posture. Governance teams can still end up chasing weak evidence packets later because the closure story never really got assembled in one place.

That gap becomes painful at enterprise scale. A ticket might have the right title and the wrong proof. A vault record might have the right owner and no current approval artifacts. An exception can stay open long enough that everyone assumes someone else already resolved the hard part. By the time audit asks for the real packet, the team is reconstructing the story from fragments.

We built ServiceNow CyberArk Evidence Pipeline to make that story explicit before it breaks.

The design starts with a simple premise: incident handling, evidence packaging, and privileged-review closure should be treated as one pipeline. Ticket state matters, but it is not the same as evidence quality. Vault metadata matters, but it is not the same as a closure-ready packet. The system needs to show both, attach them together, and make it obvious which records are safe to move and which ones are still carrying audit debt.

Existing tools usually miss the mark in one of three ways:

- they expose ticket workflow without proving the approval chain
- they expose vault context without packaging it for reviewers
- they archive evidence after the fact instead of helping operators fix weak packets early

This repo aims at the intersection instead. It keeps ServiceNow posture, CyberArk enrichment, ownership quality, dual approval, artifacts, and exception pressure in the same visible lane. That makes the workflow more defensible for operators and more legible for the people who eventually review the record.

What comes next is straightforward: richer evidence provenance, direct archive/export patterns, and tighter policy hooks for incident closure and certification gating. But the foundation has to be right first. If the packet is not trustworthy before the closure decision, the rest of the workflow is mostly ceremony.
