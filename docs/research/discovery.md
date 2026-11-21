---
kind: research
title: "How worlds could be found: discovery, registries and federation compared"
status: current
date: 2026-11-21
source: "each project's specification, documentation or repository page, fetched 2026-11-21"
---

# How worlds could be found

## How to read this

The question is how separate conky worlds could be published, discovered and linked to one another, under a domain the project owns, a default one, or one a person brings. A world is a Git vault with its own signed history and key. This page records what already exists for agent discovery, registries, naming and federation, and which implementations could be reused. It decides nothing.

Every fact about an outside project comes from a page fetched on 2026-11-21. The pages are listed under [Sources](#sources). Nothing comes from memory. The fetch tool returns a condensed reading of each page, so wording is paraphrased and only short phrases are quoted. "Not confirmed" means the pages read did not settle the point. It does not mean the feature is absent. Reading depth is stated per source.

Reach and depth:

- Reached and read in full, as far as the tool showed: the A2A discovery topic, the MCP Registry overview and authentication pages, the AGNTCY directory overview, the NANDA paper abstract, the ANP repository and its discovery specification, the AI Catalog repository, the two agents.json drafts, RFC 8615, RFC 7033, the did:web specification, the did:plc repository, the AT Protocol architecture, handle, identity and sync pages, ActivityPub, NIP-01, NIP-05, NIP-65, BEP 5, the Matrix foundation page, Radicle's protocol guide and front page, ForgeFed's front page, Handshake's front page, ENS's protocol page, the DNS-AID draft and the webring page.
- Read in part. The A2A specification page was read from character 100,000 to 200,000 of 257,720 and, in a first pass, 0 to 100,000. Section 8.4 on signing was read. Section 14.3 on well-known registration was not, so the registered URI suffix rests on section 8.2 and the discovery topic. The Matrix server-server specification was read to character 100,000 of 238,850, and its event-signing section was not. DID Core was read to 100,000 of 390,147. RFC 6762 was read to 100,000 of 202,362. RFC 6763 was read to 100,000 of 140,799. The agent-uri draft was read to 100,000 of 113,016. The NANDA organisation page on GitHub was read for its repository list only.
- Not described because no primary page was reached: the AGNTCY identity page returned only a redirect notice and was not followed. The NANDA site front page returned only navigation. The MCP server-card repository does not name a well-known path, and its `docs/discovery.md` was not read. The Matrix specification licence was not stated on the page read.
- Not checked at all: WireGuard, ZeroTier, Yggdrasil, Eclipse Paho, Git's own documentation on bundles, Matrix servers (Synapse and others), Python libraries for DIDs and for ActivityPub, and the Agent Communication Protocol. Nothing is claimed about them.
- Repository facts (licence, stars, language, maintainer) were read from each repository's front page. The tool shows no release or commit dates on those pages: every Releases section came back empty and no latest-commit date was shown, so activity is stated only as the commit count and the star count shown, plus anything the page says about itself. Radicle's own site is the one exception and gives a release date. GitHub's API was not available to this session.

The earlier page [protocols.md](protocols.md) covers A2A, MCP and ANP as protocols for talking. This page covers only how they are found.

## The survey

### Family 1: agent discovery and agent cards

**Agent2Agent (A2A).** An open protocol for communication between agent systems, a Linux Foundation project, contributed by Google, whose repository states Apache 2.0 and shows 26.6k stars. The specification page reads "latest released version 1.0.0".

- Published: an Agent Card, a JSON document describing the agent.
- Found: three strategies on the discovery topic. A well-known URI, `https://{domain}/.well-known/agent-card.json` (RFC 8615 style). A curated registry, for which "the current A2A specification does not prescribe a standard API". Direct configuration.
- Identity and trust: cards "MAY" be signed with JSON Web Signature (RFC 7515), with `kid` and an optional `jku` pointing at a key set. Sensitive detail belongs in an authenticated extended card.
- Default name: none. The domain is the name.

**MCP Registry and server cards.** The Model Context Protocol's registry is "the official centralized metadata repository for publicly accessible MCP servers", backed by Anthropic, GitHub, PulseMCP and Microsoft, and in preview. Breaking changes or data resets may occur.

- Published: a `server.json` record with a unique name, where the server lives and how to run it.
- Found: a REST API, consumed mainly by downstream aggregators. The overview says the official codebase "is not designed for self-hosting", while the repository page says self-hosting is supported with a supplied PostgreSQL. The two pages disagree, and both are quoted.
- Identity and trust: names are reverse DNS. GitHub authentication yields `io.github.username/*`. Domain authentication uses either a DNS TXT record at the domain apex (`v=MCPv1; k=ed25519; p=...`) or a file at `/.well-known/mcp-registry-auth`, both holding a public key whose private half signs a login.
- Default name: yes, `io.github.<user>/` for anyone with a GitHub account.
- Licence: not stated on the pages read. Stars about 7.5k.
- Server cards: SEP-2127 "MCP Server Cards - HTTP Server Discovery" shows as merged on 2026-10-06 in a pull-request search, and the work lives in an experimental repository that says it is "for prototyping and feedback only". The card holds identity, remote endpoints and optional metadata, and the recommended location is `<streamable-http-url>/server-card`. A proposal for DNS bootstrap shows as closed without merging. The card can also be found through AI Catalog entries.

**AI Catalog.** A repository maintained under the Linux Foundation as a temporary working location. It proposes one typed, nestable JSON catalog per domain, with `/.well-known/ai-catalog.json` as the page's example path. Specification v0.9 is a release candidate for v1.0. Entries reference or inline native metadata such as agent cards, and optional Trust Manifests are independently signed. The A2A and MCP steering committees would vote on adopting it once final. Licence not stated on the page.

**AGNTCY Agent Directory.** A distributed directory for agent records, described by the Open Agentic Schema Framework (OASF). The page footer attributes AGNTCY to "a Series of LF Projects, LLC". The repository states Apache 2.0, shows 208 stars and names v1.9.1 in its install examples.

- Published: records listing skills from an OASF taxonomy.
- Found: a Kademlia distributed hash table (the IPFS libp2p implementation) maps skills to record identifiers and identifiers to the peers storing them. An Internet-Draft, `draft-mp-agntcy-ads-03`, individual and not endorsed by the IETF, expires 2027-05-06. A query must carry at least one skill. Records are stored as OCI artifacts and addressed by SHA-256 digest. A public network is reachable at ads.outshift.io, per the overview.
- Identity and trust: the draft integrates Sigstore keyless signing through OpenID Connect providers (GitHub, Google, Microsoft). The identity model itself was not read.

**NANDA (MIT).** An architecture for an index of agents. The arXiv paper (2507.14263, July 2025, 18 authors, Ramesh Raskar first) proposes a lean index that resolves to cryptographically verifiable AgentFacts records, with revocation and key rotation "within a second" claimed in the abstract. An MIT Media Lab article describes a NandaIndex Switchboard, "a shared service" mapping identifiers to pointers, and a proposed model for individuals with no domain: a provider publishes under its own domain and links the record to a verified account. The article calls the individual model "proposed" and the architecture "evolving", and says identity verification and federation need more work. The `nanda-index-v2` repository (Apache 2.0, TypeScript, 11 stars, 361 commits) is "a global switchboard for AI agent discovery" storing one AI Catalog record per organisation, with an HTTP API (`/api/v1/resolve?locator=<urn>`) and a Docker Compose self-host. The paper's abstract is the only part of the paper read.

**Agent Network Protocol (ANP).** An open protocol suite from a community, Apache 2.0, version 1.2, about 1.5k stars. Some parts (ANP-05, -06, -10) are drafts.

- Published: an Agent Description document (ANP-07).
- Found: ANP-08 defines active discovery at `https://{domain}/.well-known/agent-descriptions`, a paged JSON-LD collection, and passive registration with search services through each service's own API, which the specification does not standardise.
- Identity and trust: `did:wba` (ANP-03), a web-based DID method, and native `did:web`, with DID authentication (ANP-02) and WNS handles mapping names to DIDs (ANP-04). The discovery specification defines no signature format for description documents.
- Default name: not confirmed.

**agents.json, agents.txt and agent-uri.** No settled standard. Two individual Internet-Drafts use the same path for different things. `draft-car-agents-txt-wellknown-00` (June 2026, expires 2026-12-14, Informational, one independent author) asks IANA to register `agents.txt` and `agents.json` as capability declarations, and says they are "advisory" and "not a trust boundary". `draft-narvaneni-agent-uri-03` (Experimental, expires 2026-10-20, a later version exists) uses `/.well-known/agents.json` as a registry of agent names to descriptor URLs for `agent://` URIs, with DID authorities and optional HTTP Message Signatures (RFC 9421). Both are individual, unendorsed drafts.

**DNS-AID.** An individual Internet-Draft (`draft-mozleywilliams-dnsop-dnsaid-02`, Infoblox, Deutsche Telekom, Amazon and an unaffiliated author, expires 2026-11-28, Standards Track). It publishes agents in DNS as SVCB records, with an organisation index at `_index._agents.<domain>`. Trust rests on DNSSEC and optional DANE. It "does not require a central agent registry" and leaves cross-domain search to higher layers. Its domain-control mechanism is marked experimental.

**Agentic Commerce Protocol.** Stripe and OpenAI. The page says only that it is "working to create discovery mechanisms", so it defines none. Apache 2.0.

### Family 2: marketplaces and open indexes

The registries above are the open ones. Beyond them, a web search surfaced an index run by a single site, `agtm` and the DeepNLP marketplace (repository shows 58 stars, no licence stated, 10K+ listings claimed by its own page, registration by CLI or website, "listed after approval"). A survey paper (arXiv 2508.03095, abstract read) compares five approaches: the MCP Registry as centralised, A2A cards as decentralised manifests, the AGNTCY directory as distributed, Microsoft Entra Agent ID as enterprise, and NANDA AgentFacts. Closed stores were not surveyed. OpenAgora and a Hugging Face forum index appeared in search results only and were not fetched.

### Family 3: identity and naming

**Well-known URIs (RFC 8615).** May 2019, Standards Track, Proposed Standard, M. Nottingham. Reserves `/.well-known/<name>` at the root of an `https` origin, with an IANA registry under Specification Required. The page does not say whether a later RFC replaced it.

**WebFinger (RFC 7033).** September 2013, Proposed Standard. `GET /.well-known/webfinger?resource=acct:name@domain` returns a JSON Resource Descriptor with `subject`, `aliases` and `links`. HTTPS only. Mastodon's documentation shows its use: a `self` link to an ActivityPub actor, verified by a second lookup back.

**DIDs.** DID Core 1.0 is a W3C Recommendation of 2022-07-19. A DID document lists verification methods and service endpoints, and each DID method is specified separately. `did:web` resolves `did:web:example.com` to `https://example.com/.well-known/did.json`, and `did:web:example.com:u:bob` to `https://example.com/u/bob/did.json`. Its specification defines no access control, tells implementers to use DNS over HTTPS and DNSSEC, and notes that a path DID proves control of a file, not of the domain. The page does not state its document status. `did:plc` is a self-authenticating method with a signed operation log and reconfigurable rotation keys, run through a central directory server that "collects and validates operations". The specification is at v0.1, dual MIT and Apache 2.0, and a PLC Organization was founded in 2026 as "neutral steward". `did:key` is carried by Radicle's node identifiers, and its own specification was not read.

**DNS-SD and mDNS.** RFC 6763 (DNS-based service discovery) and RFC 6762 (Multicast DNS), both February 2013, Proposed Standard, Apple authors. A service is a PTR record listing instances, each with SRV (host and port) and TXT (key and value) records. mDNS answers on the local link under `.local` with no server, no registration and no configuration. Neither provides trust beyond the link.

**Handshake.** "An experimental peer-to-peer root naming system", names bought by auction in its own coin, licence not stated on the page, resolution through light clients and its own full node.

**ENS.** "A distributed, open, and extensible naming system based on the Ethereum blockchain". `.eth` names are tokens issued by a registrar contract, existing DNS names can be imported using DNSSEC, and the owner of a name can create subnames. Governance and cost were not on the page read.

### Family 4: federation models

**ActivityPub.** A W3C Recommendation of 2018-01-23. An actor has an `inbox` and an `outbox`. Servers POST activities to remote inboxes. Remote actors are found by dereferencing actor URIs. The Recommendation mandates no signature mechanism ("no particular mechanism for verification is authoritatively specified") and says there are "no strongly agreed upon mechanisms for authentication". In practice WebFinger finds the actor, as Mastodon's page shows. No default name beyond the host's own domain.

**ForgeFed.** An ActivityPub extension for code forges: repositories, commits, patches and issues, with users on different sites opening issues and pull requests against remote repositories. CC0 licence. The page states no formal status.

**AT Protocol.** Accounts rooted in DIDs (`did:plc` or `did:web`). Public content lives in signed, content-addressed repositories on a Personal Data Server. Handles are DNS names. A handle is trusted only when it resolves to a DID and the DID document names the handle back. Resolution is a TXT record at `_atproto.<handle>` with value `did=<DID>`, or `GET https://<handle>/.well-known/atproto-did` whose body is the DID, and DNS wins when they conflict. Relays merge PDS streams into a firehose and consumers verify each commit's signature themselves. App Views build the aggregations on top. The architecture page says the specifications are meant to go to a standards body "like the IETF" once several organisations interoperate. The identity guide shows a hosting service supplying a handle as a subdomain of its own domain (`alice.pds.com`) for people without a domain. The reference implementation is MIT and Apache 2.0, TypeScript, 9.7k stars, Bluesky Social PBC.

**Matrix.** A homeserver is found by `https://<host>/.well-known/matrix/server`, then SRV `_matrix-fed._tcp`, then port 8448. Each homeserver publishes keys at `/_matrix/key/v2/server`, notary servers can countersign, and events carry signatures that must verify or the event is dropped. Governed by the Matrix.org Foundation, a UK non-profit Community Interest Company with a Spec Core Team of ten. The licence of the specification was not stated on the page. Room directory rules were not read.

**Nostr.** Keys are secp256k1 key pairs and every event is signed (NIP-01). Relays are WebSocket servers that store and filter events. NIP-05 maps `name@domain` to a key through `https://<domain>/.well-known/nostr.json?name=<name>` with an optional `relays` hint, and says it "identifies users rather than verifying them". NIP-65 (draft) publishes a user's read and write relays as an event, and advises spreading it to well-known indexers. NIP-01 and NIP-05 are the base and a final optional specification. Licence not read.

**Radicle.** A "sovereign code forge built on Git" with no single controlling entity, MIT and Apache 2.0, release 1.10.3 dated 2026-09-08 on its front page. A node is an Ed25519 key shown as `did:key`, a repository has an ID derived from its first identity document (`rad:...`), and each node's refs are signed and stored under `refs/rad/sigrefs`, so a clone can be verified without a trusted third party. Nodes find each other by gossip (node, inventory and reference announcements) from bootstrap nodes, and seed nodes improve availability. The guide says the design has no centralised point of failure and does not say whether a global index exists. Its transport-encryption section has been withdrawn after a security vulnerability.

### Family 5: distributed indexes and the simplest case

**AT Protocol relays and App Views.** See above. The sync page describes the pattern an index follows: consume the full-network firehose, verify each commit, keep a record table, mark a repository desynchronised when the chain breaks and re-fetch it.

**Nostr relays.** Discovery is by asking relays, and a client must already know which relays to ask, which is the reason NIP-65 exists.

**Kademlia DHT (BEP 5).** Accepted Standards Track of the BitTorrent project. A 160-bit node space with XOR distance, lookups by infohash, `announce_peer` with a token. It finds peers for a known identifier and the page describes no keyword search. AGNTCY's directory builds a skill-to-record layer above a DHT for that reason.

**Webrings and directories.** A webring is "a set of websites linked in a circular structure" with `/next/` and `/previous/` pages and sometimes a public member list. It dates from 1994 and has several modern revivals (the Recurse Center webring, Fediring, the Indiewebring). It needs one host for the ring and no protocol.

## Comparison

| Project | Status, as stated | What is published, and where | How it is found | Identity and trust | Default name for someone with no domain | Licence | Maturity, as its sources state it |
|---|---|---|---|---|---|---|---|
| A2A | Linux Foundation project, spec 1.0.0 | Agent Card, `/.well-known/agent-card.json` | Well-known URI, curated registry (no standard API), configuration | Optional JWS signatures | None | Apache 2.0 | Released; 26.6k stars |
| MCP Registry | Preview, resets possible | `server.json` in a central registry | REST API, aggregators | Reverse-DNS names proved by GitHub, DNS TXT or well-known file | `io.github.<user>/` | Not stated | Preview; about 7.5k stars |
| MCP Server Cards | Experimental repository, SEP merged | Card at `<endpoint>/server-card` | Recommended URL, AI Catalog | Signing not mentioned | None | Not stated | "Prototyping and feedback only" |
| AI Catalog | v0.9 release candidate, LF temporary repo | `/.well-known/ai-catalog.json` (example path) | Well-known URL | Optional signed Trust Manifests | None | Not stated | Not final |
| AGNTCY Directory | LF Projects series; individual draft | OASF records as OCI artifacts | Kademlia DHT by skill, federation | Sigstore keyless signing | None | Apache 2.0 | v1.9.1; 208 stars |
| NANDA | Paper (preprint); reference code | AgentFacts via a switchboard | Resolver by URN, index | Verifiable records, key rotation claimed | Proposed: provider domain plus verified account | Apache 2.0 (index repo) | "Evolving"; 11 stars on the index repo |
| ANP | Community, 1.2, drafts remain | Agent Description, `/.well-known/agent-descriptions` | Well-known crawl, registration with search services | `did:wba`, `did:web` | Not confirmed | Apache 2.0 | Core released; about 1.5k stars |
| agents.json drafts | Individual Internet-Drafts | Capability file or name registry at `/.well-known/agents.json` | Well-known URL | None or optional HTTP signatures | None | Not applicable | Expiring drafts |
| DNS-AID | Individual Internet-Draft, Standards Track | SVCB records, `_index._agents.<domain>` | DNS | DNSSEC, DANE | None | Not applicable | Draft, no registry needed |
| WebFinger | RFC 7033, Proposed Standard | JRD at `/.well-known/webfinger` | Well-known URL | HTTPS only | None | Not applicable | Standard since 2013 |
| did:web | Method specification | `did.json` at the domain | Well-known URL or path | Control of the web origin | None | Not stated | Status not stated on the page |
| did:plc | v0.1, PLC Organization | Signed operation log | Central directory | Signed operations, rotation keys | Directory issues the DID | MIT and Apache 2.0 | Used by Bluesky |
| DNS-SD and mDNS | RFC 6763, 6762 | PTR, SRV, TXT records | Query on the link or in DNS | None | `.local` names | Not applicable | Standards since 2013 |
| Handshake | "Experimental" | Root zone entries | Own nodes and light clients | Chain consensus | Names bought by auction | Not stated | Experimental |
| ENS | Ethereum-based | Registry entries, resolvers | Chain lookup | Contract ownership | Subnames from a name's owner | Not stated | Not stated on the page |
| ActivityPub | W3C Recommendation, 2018 | Actor with inbox and outbox | Actor URI, WebFinger in practice | Signatures not mandated | The host's domain | Not applicable | Recommendation |
| ForgeFed | ActivityPub extension | Repository and issue actors | ActivityPub | As ActivityPub | The host's domain | CC0 | Status not stated |
| AT Protocol | Specs, intended for a standards body | Signed repo on a PDS; DID document | Handle by DNS TXT or well-known, relay, App View | DID keys, signed commits, handle checked both ways | Hosting service subdomain | MIT and Apache 2.0 (reference code) | Reference code at 9.7k stars |
| Matrix | Foundation-governed | Server keys, signed events | Well-known, SRV, notaries | Server signing keys, event signatures | The host's domain | Not stated | Governed spec |
| Nostr | NIPs; NIP-05 final, NIP-65 draft | Signed events on relays; `nostr.json` | Relays, relay list events | Key pair per user | `name@domain` from a domain operator | Not read | Not stated |
| Radicle | Released, 1.10.3 | Signed refs, repository ID | Gossip, seed nodes | Ed25519 `did:key`, signed refs | None needed | MIT and Apache 2.0 | One withdrawn section |
| Webrings | Convention | Pages on member sites | Next, previous, member list | None | Ring host's page | Not applicable | Revived, some ended |

## What could be reused

Each row below was read from the project's own repository page on 2026-11-21 unless stated. "Python" means a Python package, or a command line, local HTTP or socket interface a Python program could call, as the page shows it. Latest release and commit dates were not shown by the tool for any of them, so the commit count and stars are given instead. A reader who needs the dates should open the repository.

### Link and local discovery

| Candidate | Licence, language | Stars, commits | Maintainer | Python | What it would do for conky |
|---|---|---|---|---|---|
| [python-zeroconf](https://github.com/python-zeroconf/python-zeroconf) | LGPL-2.1-or-later, pure Python | 743, 1,860 | `python-zeroconf` organisation, says "actively maintained" | Is a Python package | Announces and browses `_conky._tcp` style services on the local link, with no server. |
| [Avahi](https://github.com/avahi/avahi) | LGPL-2.1 | 1.6k | Authors named as Lennart Poettering and Trent Lloyd | Bindings directory named; script interface not described | The Linux system daemon python-zeroconf can sit beside. |
| [Zenoh](https://github.com/eclipse-zenoh/zenoh) | EPL-2.0 and Apache-2.0, Rust | 3.4k, 4,858 | Eclipse Foundation project | Separate `zenoh-python` repository, not read | Publish and subscribe with queries across devices and links, including constrained ones. |
| [Mosquitto](https://github.com/eclipse-mosquitto/mosquitto) | Licence files suggest EPL-2.0 and EDL-1.0, not confirmed | 11.5k, 4,910 | Eclipse Foundation, Roger Light original author | The page does not mention Paho | An MQTT broker for small devices. Needs a running broker. |
| [Meshtastic Python](https://github.com/meshtastic/python) | GPL-3.0, Python | 862, 2,466 | Page says it has "gone without a consistent maintainer for a while" | Is a Python library and CLI | Sends and receives messages over radio mesh devices. GPL-3.0 and the maintainer note both weigh against it. |

### Network and reach

| Candidate | Licence, language | Stars, commits | Maintainer | Python | What it would do for conky |
|---|---|---|---|---|---|
| [iroh](https://github.com/n0-computer/iroh) | Apache-2.0 and MIT, Rust | 13.1k, 2,688 | N0, Inc. | No bindings on the page; a separate `iroh-ffi` repository is named | Dials a peer by public key with hole punching and relay fallback. Public relays exist and `iroh-relay` is the relay code. |
| [Headscale](https://github.com/juanfont/headscale) | BSD-3-Clause, Go (implied) | 45.9k, 5,282 | Owner juanfont; one active maintainer employed by Tailscale | Command line | A self-hosted Tailscale control server for one private network. |
| [Tailscale](https://github.com/tailscale/tailscale) | BSD-3-Clause, Go | 39.4k, 11,783 | Tailscale organisation | Command line | The client daemon and CLI. The page does not mention the coordination server. |
| [Nebula](https://github.com/slackhq/nebula) | MIT, Go (implied) | 18.5k, 908 | Created at Slack Technologies; slackhq organisation | Command line | Mutually authenticated overlay network, certificates signed by one CA, needs a lighthouse with a routable address. A managed version exists as a hosted product. |
| [py-libp2p](https://github.com/libp2p/py-libp2p) | MIT and Apache-2.0 files | 628, 4,839 | Five maintainers named | Is Python | DHT, mDNS, relay and hole punching marked done; WebRTC a prototype; labelled "under development". |

### Transport of signed bundles and replication

| Candidate | Licence, language | Stars, commits | Maintainer | Python | What it would do for conky |
|---|---|---|---|---|---|
| Plain Git bundles and remotes | Git's own documentation was not read | Not applicable | Not applicable | Command line | A letter as a bundle of signed commits, carried by file, mail or any remote. Nothing to run. |
| [Radicle](https://radicle.dev/) | MIT and Apache 2.0 | Not given | Not named | HTTP and JSON daemon, per its front page; CLI name not confirmed | Signed refs, gossip and seed nodes over Git, with Ed25519 identities. |
| [Syncthing](https://github.com/syncthing/syncthing) | MPL-2.0, Go | 90.6k | `syncthing` organisation | A REST API is not mentioned on the page | Continuous file sync between a person's own machines. The page does not describe discovery or relays. |
| [Hypercore](https://github.com/holepunchto/hypercore) | MIT, JavaScript | 2.9k | Holepunch | No Python bindings mentioned | A signed append-only log with Merkle trees. |

### Session, identity and federation

| Candidate | Licence, language | Stars | Maintainer | Python | What it would do for conky |
|---|---|---|---|---|---|
| [atproto SDK for Python](https://github.com/MarshalX/atproto) | MIT, Python 3.9+ | 662 | Owner MarshalX | Is Python | Resolves handles, DIDs and signing keys, and reads firehoses. Support for `did:web` was not confirmed. |
| [atproto reference](https://github.com/bluesky-social/atproto) | MIT and Apache 2.0, TypeScript | 9.7k | Bluesky Social PBC | No Python SDK named | PDS, App View and identity primitives. Go relay code lives in a separate repository. |
| [Fedify](https://github.com/fedify-dev/fedify) | MIT, TypeScript | about 1.0k | `fedify-dev` organisation | Not mentioned | ActivityPub with WebFinger and HTTP Signatures including RFC 9421. |
| [matrix-nio](https://github.com/matrix-nio/matrix-nio) | Apache-2.0, Python | 711 | `matrix-nio` organisation | Is Python | A client library only; no server. |
| [strfry](https://github.com/hoytech/strfry) | GPL-3.0, C++ | 739 | Doug Hoyte and contributors | A WebSocket client could reach it; the page does not say so | A Nostr relay with set-reconciliation sync, LMDB storage and no external database. |

### Naming and default sub-names

| Candidate | Licence, language | Stars | Maintainer | Python | Open or hosted | What it would do for conky |
|---|---|---|---|---|---|---|
| [Caddy](https://github.com/caddyserver/caddy) | Apache-2.0, Go | 79.3k | Matthew Holt; "a project of ZeroSSL, an HID Global company" | JSON API, details not on the page | Open source, self-run | Automatic HTTPS for a person's own domain. On-demand TLS is not on the page read. |
| [acme-dns](https://github.com/joohoi/acme-dns) | MIT, Go | 2.9k | Not named | HTTP API (`/register`, `/update`) | Open source, self-run | A small DNS server that issues one subdomain per registrant for certificate challenges. |
| [frp](https://github.com/fatedier/frp) | Apache-2.0, Go | about 110.7k | Owner fatedier | Command line and config | Open source, self-run | Reverse proxy through NAT with `subDomainHost` wildcard names, run by whoever has a public address. |
| [cloudflared](https://github.com/cloudflare/cloudflared) | Apache-2.0, Go | 16.7k | Cloudflare | Command line | Client is open source; named tunnels need a Cloudflare account, so a hosted product | Names for a machine behind NAT, from one company's service. |

### Discovery indexes and agent directories

| Candidate | Licence, language | Stars | Maintainer | Python | What it would do for conky |
|---|---|---|---|---|---|
| [MCP Registry](https://github.com/modelcontextprotocol/registry) | Not named on the page | about 7.5k | Model Context Protocol organisation | HTTP API | Reverse-DNS names verified by DNS or a well-known file. Self-hosting statements conflict, as noted above. |
| [AGNTCY dir](https://github.com/agntcy/dir) | Apache-2.0, Go | 208 | AGNTCY Contributors | gRPC and protocol buffers | A DHT-backed directory of agent records. Heavier than a card. |
| [nanda-index-v2](https://github.com/projnanda/nanda-index-v2) | Apache-2.0, TypeScript | 11 | `projnanda` organisation | HTTP API | A switchboard resolving URNs to catalogs or cards, self-hostable by Docker Compose. Few stars. |
| [a2a-python](https://github.com/a2aproject/a2a-python) | Apache-2.0, Python 3.10+ | 2.3k | `a2aproject` organisation | Is Python | The official A2A SDK. Whether it fetches a card by well-known URL was not confirmed. |
| [Agent Card AI Catalog](https://github.com/Agent-Card/ai-catalog) | Not stated | Not read | Linux Foundation, temporary repository | Specification only | A catalog format, no implementation read. |

## What fits conky

The fixed points: a world is a Git vault with signed commits and its own key. Worlds stay separate and exchange letters, pages pulled as signed bundles and judged by the receiver's rules. A world should be publishable under a project-owned domain, a default sub-name, or the person's own domain. Nothing should depend on one central service. The project prefers an existing standard to an invented one.

### What the findings say

- A published card is a small file at a well-known path on a domain the publisher controls. A2A, ANP, AI Catalog, MCP server cards, WebFinger, did:web, NIP-05 and AT Protocol handles all use that shape. The path names differ and none is shared across ecosystems yet, so a conky card would have to pick one or serve several. The AI Catalog's stated aim is to be the common layer, and it is a release candidate.
- The three ways to prove a name are a file on the domain, a DNS record on the domain, and an account at a provider. MCP's registry accepts all three. AT Protocol accepts the first two. Nostr accepts the first.
- No surveyed system proves that a key belongs to a domain without trusting DNS or the web origin, except the DID methods that carry their own key (`did:key`, Radicle's node identifiers). A world already has a key of its own, so `did:key` is the natural fit for identity and a domain is only an optional alias for it. This is a reading of the sources, not a finding of any of them.
- Signing of the published card is optional or undefined in A2A, ANP, agents.json and server cards. A conky card could carry the world's own signature at no cost, because the vault's commits already are signed.
- Indexes either crawl (a relay, an App View, a search service) or are asked (a registry, a DHT, a relay list). Every index in the survey holds pointers and leaves the content with the publisher, and verifies against the publisher's key. That matches letters judged by the receiver.
- A default name for someone with no domain is provisioned in three ways: a subdomain of the host's domain (AT Protocol hosting, Matrix and ActivityPub servers, frp), a namespace under the registry's account system (`io.github.*`), and a name or subname owned in a ledger (ENS, Handshake). The first needs a project-owned zone and a small issuing service. The second needs an account system. The third needs a chain.
- Several systems keep one authority at the root without making it the only path: `did:plc` has one directory, the MCP Registry is "centralized", and NANDA's switchboard is "a shared service". The ones built to avoid that (DNS-AID, Radicle, Nostr, the AGNTCY directory) give up either a human-readable name or keyword search.

### Options

**Option A: a card on any domain, with `did:web` or WebFinger, and an optional registry that is a conky world.**

- The world publishes `/.well-known/agent-card.json` (A2A shape) or an AI Catalog entry, signed with the world's key, on a domain the owner controls. `did:web` or a WebFinger `acct:` lookup maps `name@domain` to the key and the bundle location.
- Project-owned domain: the project serves cards under names it issues. Default sub-name: wildcard DNS plus a small issuing service, with acme-dns or Caddy for certificates. Person's own domain: a static file and, if wanted, a TXT record.
- A registry is a world whose pages are cards, and others pull its bundles. It is one more world, so there is no central service to depend on.
- Cost to run: a static file host per publisher, one DNS zone and one small service for default names, and nothing for the registry beyond a vault. Trade-off: the default name rests on the project's zone staying up and the owner's key staying separate from DNS.

**Option B: handles as domains, in the AT Protocol manner.**

- A name is a DNS name. A TXT record or a well-known file on that name holds the world's key identifier. The world's document names the handle back, so the claim is checked in both directions. Relays and App Views become worlds that pull many worlds' bundles and index them.
- Project-owned and default names are subdomains handed out as a hosting service hands out `alice.pds.com`. A person's own domain needs one TXT record.
- Cost to run: a DNS zone with an update API for default names, and one relay-like world if search is wanted. Trade-off: it reuses a design that already has consumers of the sync pattern, and it relies on DNS for the name, which the sources say is not proven by the key.

**Option C: keys first, names optional, on plain Git and gossip.**

- The identifier is the key (`did:key`). Bundles move over plain Git remotes, files, or a Radicle-like seed. Local worlds find one another with DNS-SD over mDNS. A domain is added later as an alias by a well-known file.
- Cost to run: nothing for the default case. Seeds or a relay are optional and anyone can run one. Trade-off: no human-readable name by default, no keyword search, and discovery beyond the local link needs a seed or an index that is not part of this option.

Option A has the shortest path to a name a stranger can type. Option B has the most precedent for names as domains with a verifiable back link. Option C needs nothing outside the person's machine. The three compose: C is the base, and A or B adds a name.

### The first reuse to try, by layer

"Own machine" means it runs entirely on a person's computer. "Service" means something must be running that the person does not hold on their own machine.

| Layer | First reuse to try | Why | Own machine or service |
|---|---|---|---|
| Link and local discovery | python-zeroconf | Pure Python, pip-installable, no daemon, and it announces and browses on the local link, which matches "a default that needs nothing". LGPL-2.1 is a licence question to settle. | Own machine |
| Network and reach | iroh, if a Python route exists | It dials by public key, and a world already has a key. Public relays are a service the project would not depend on, because `iroh-relay` is the code for running one. No Python bindings are on the page, so this is the least checked choice here. Headscale with the Tailscale client is the fallback, and it needs a running control server. | Own machine for direct dialling; service for relay fallback |
| Transport of signed bundles | Plain Git bundles and remotes | A letter is already a bundle of signed commits, so the existing tool carries it by file, mail or any remote. Radicle is the second to try for gossip and seeds. | Own machine |
| Session, identity and federation | The atproto Python identity resolver, for reading handles and DIDs, used only as a reader | It runs locally, resolves handles through DNS or a well-known file, and checks the back link. Which DID methods it supports was not confirmed. No federation server is needed because worlds exchange letters directly. | Own machine, using outside DNS and HTTPS |
| Naming and default sub-names | Caddy for a person's own domain, and acme-dns for default sub-names | Caddy serves the card with automatic certificates. acme-dns has a small HTTP API for issuing one subdomain and a challenge record at a time. A hosted tunnel such as cloudflared hands out names but needs one company's account, so it is not the first choice. | Caddy on the person's machine if it is reachable, acme-dns is a service the project runs |
| Discovery indexes and directories | A signed static card, with no software; the index is a world | The A2A card and AI Catalog formats are files, and every indexer in the survey consumes a file. Of the implementations, nanda-index-v2 is the smallest to self-host but has 11 stars. | Own machine to publish; service only for an index |

### Which choices need a running service

- Needs none: Git bundles, mDNS and DNS-SD, `did:key`, a signed card on a static host the owner already has, a Radicle-style seed that anyone may skip.
- Needs one the project would run: the default sub-name issuer (a DNS zone and, for certificates, acme-dns or similar) and, for reach beyond the local link, a relay or lighthouse.
- Needs one a third party runs: a hosted tunnel, a public iroh relay, the MCP Registry, any DNS registrar.

## Open questions

- Which card shape to serve. The A2A card is released and widely implemented. The AI Catalog would sit above it and is a release candidate. Whether serving both costs more than it returns is open.
- Whether the key or the domain is the name. The surveyed systems that prove a key against a domain trust DNS or the web origin. Which loss is easier to survive, a lost domain or a lost key, and how a world moves from one to the other, are open.
- Whether a default sub-name can be revoked, and what a receiver does with a card whose name has been reassigned. `did:plc` handles this with a signed log and a central directory. The cost of copying that was not measured.
- What a letter's header must carry for a receiver to find the sender again: a key, a name, a bundle location, or all three.
- How an index learns of a new world without a central registry. Crawling needs a seed list, and a relay list needs a first relay. The webring is the one design that needs neither and it needs a human.
- Whether letters should ride over an existing federation (ActivityPub, Matrix, Nostr) or over plain Git. The three federations were read as discovery and signing models only. Their cost as a carrier of bundles was not.
- Which of the unchecked candidates (WireGuard, ZeroTier, Yggdrasil, Eclipse Paho, a Python DID library, a Matrix server) should be read before any layer is chosen.
- Release and commit dates for every repository above, which the fetch tool did not show.
- Licence fit. python-zeroconf and Avahi are LGPL-2.1, Meshtastic's Python client and strfry are GPL-3.0, and the licence of the MCP Registry, the AI Catalog and Handshake was not stated on the pages read.

## Sources

All fetched on 2026-11-21.

- A2A: [discovery topic](https://a2a-protocol.org/latest/topics/agent-discovery/), [specification](https://a2a-protocol.org/latest/specification/), [repository](https://github.com/a2aproject/A2A), [Python SDK](https://github.com/a2aproject/a2a-python)
- MCP: [registry overview](https://modelcontextprotocol.io/registry/about), [authentication](https://modelcontextprotocol.io/registry/authentication), [registry repository](https://github.com/modelcontextprotocol/registry), [server card repository](https://github.com/modelcontextprotocol/experimental-ext-server-card), [pull-request search](https://github.com/modelcontextprotocol/modelcontextprotocol/pulls?q=well-known+server+card)
- AI Catalog: [repository](https://github.com/Agent-Card/ai-catalog)
- AGNTCY: [directory overview](https://dir.agntcy.org/latest/dir/dir-overview/), [repository](https://github.com/agntcy/dir), [Internet-Draft](https://datatracker.ietf.org/doc/draft-mp-agntcy-ads/)
- NANDA: [paper abstract](https://arxiv.org/abs/2507.14263), [MIT article](https://www.media.mit.edu/articles/nandaindex-making-ai-agents-discoverable-without-owning-a-domain/), [organisation](https://github.com/projnanda), [index repository](https://github.com/projnanda/nanda-index-v2), [front page](https://projectnanda.org)
- ANP: [repository](https://github.com/agent-network-protocol/AgentNetworkProtocol), [discovery specification](https://github.com/agent-network-protocol/AgentNetworkProtocol/blob/main/08-ANP-Agent-Discovery-Protocol-Specification.md)
- Drafts: [agents.txt and agents.json](https://datatracker.ietf.org/doc/draft-car-agents-txt-wellknown/), [agent-uri](https://datatracker.ietf.org/doc/html/draft-narvaneni-agent-uri-03), [DNS-AID](https://www.ietf.org/archive/id/draft-mozleywilliams-dnsop-dnsaid-02.html)
- Commerce: [Agentic Commerce Protocol](https://www.agenticcommerce.dev/)
- Registries and marketplaces: [agtm marketplace](https://github.com/aiagenta2z/ai-agent-marketplace), [registry survey paper](https://arxiv.org/abs/2508.03095)
- Standards: [RFC 8615](https://www.rfc-editor.org/rfc/rfc8615), [RFC 7033](https://www.rfc-editor.org/rfc/rfc7033), [RFC 6763](https://www.rfc-editor.org/rfc/rfc6763), [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762), [DID Core](https://www.w3.org/TR/did-core/), [did:web](https://w3c-ccg.github.io/did-method-web/), [did:plc](https://github.com/did-method-plc/did-method-plc)
- Naming: [Handshake](https://handshake.org/), [ENS](https://docs.ens.domains/learn/protocol)
- Federation: [ActivityPub](https://www.w3.org/TR/activitypub/), [Mastodon WebFinger](https://docs.joinmastodon.org/spec/webfinger/), [ForgeFed](https://forgefed.org/), [Matrix server-server API](https://spec.matrix.org/latest/server-server-api/), [Matrix.org Foundation](https://matrix.org/foundation/about/), [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md), [NIP-05](https://github.com/nostr-protocol/nips/blob/master/05.md), [NIP-65](https://github.com/nostr-protocol/nips/blob/master/65.md), [Radicle protocol guide](https://radicle.dev/guides/protocol), [Radicle](https://radicle.dev/)
- AT Protocol: [architecture](https://atproto.com/specs/atp), [handles](https://atproto.com/specs/handle), [identity guide](https://atproto.com/guides/identity), [sync](https://atproto.com/specs/sync)
- Indexes: [BEP 5](https://www.bittorrent.org/beps/bep_0005.html), [webrings](https://indieweb.org/webring)
- Reuse candidates: [python-zeroconf](https://github.com/python-zeroconf/python-zeroconf), [Avahi](https://github.com/avahi/avahi), [Zenoh](https://github.com/eclipse-zenoh/zenoh), [Mosquitto](https://github.com/eclipse-mosquitto/mosquitto), [Meshtastic Python](https://github.com/meshtastic/python), [Tailscale](https://github.com/tailscale/tailscale), [Headscale](https://github.com/juanfont/headscale), [Nebula](https://github.com/slackhq/nebula), [iroh](https://github.com/n0-computer/iroh), [py-libp2p](https://github.com/libp2p/py-libp2p), [Syncthing](https://github.com/syncthing/syncthing), [Hypercore](https://github.com/holepunchto/hypercore), [atproto](https://github.com/bluesky-social/atproto), [atproto Python SDK](https://github.com/MarshalX/atproto), [Fedify](https://github.com/fedify-dev/fedify), [matrix-nio](https://github.com/matrix-nio/matrix-nio), [strfry](https://github.com/hoytech/strfry), [Caddy](https://github.com/caddyserver/caddy), [acme-dns](https://github.com/joohoi/acme-dns), [frp](https://github.com/fatedier/frp), [cloudflared](https://github.com/cloudflare/cloudflared)
