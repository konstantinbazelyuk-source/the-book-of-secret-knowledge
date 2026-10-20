# Flux operating reference and assistant application

Prepared October 20, 2026.

This reference turns the Flux study into working procedures. The study covered all **160 pages in Flux’s published documentation index**, approximately **129,975 words**, plus current official EDA/MCAD descriptions and selected public upstream source. It covers documented behavior rather than a complete audit of Flux’s proprietary application. No live Flux project was edited or simulated during this study.

## What can improve our work now

**No additional personal or project data is needed to adopt the general methods.** They can be used with the assistant’s existing research, code execution, file creation, and review tools. The useful change is a more repeatable engineering workflow; studying documentation does not retrain the underlying model or install an external engineering engine.

| Flux feature or method | Application with existing assistant tools | What additional access or data enables |
|---|---|---|
| Shared project context | Maintain requirements, assumptions, decisions, sources, and revision in one reference | A particular design supplies its actual facts |
| Engineering calculations | Execute reproducible numerical calculations, analyze data, and plot results | Circuit values, operating ranges, and acceptance limits make results design-specific |
| Specialist reviews | Divide independent reviews by domain, then reconcile findings against the same requirements | Schematics, BOM, datasheets, or mechanical constraints support substantive findings |
| Reusable components | Describe block interfaces, dependencies, ratings, and provenance explicitly | Verified parts and project files enable actual reuse |
| Change and verification loop | Make a bounded change, inspect the result, and refresh dependent outputs | A connected editor permits live changes and state read-back |
| Flux autorouting, live editing, and native checks | Prepare constraints, review inputs, and interpret supplied outputs | A working Flux connection with appropriate project permissions is required to operate those tools |

The operating loop to apply is **establish facts → define measurable outcome → calculate or model → cross-check → act → inspect actual results → record the revision and decision**. Request only missing inputs that affect the current decision. Keep assumptions visible rather than inventing component values, dimensions, or electrical limits.

## Study coverage

Each domain’s assigned pages was read in full; the assignments uniquely cover the complete index. Routing preservation received an additional cross-check.

| Domain | Pages |
|---|---:|
| Workspace, projects, collaboration, accounts, and billing | 42 |
| Schematics, components, libraries, and modules | 23 |
| Physical PCB editor, rules, geometry, and routing | 43 |
| AI, calculations, simulation, MCP, and user-facing code interfaces | 26 |
| Imports, exports, manufacturing, sourcing, and review | 20 |
| Privacy, security, IP, and service terms | 6 |
| **Total** | **160** |

The [published documentation index](https://docs.flux.ai/llms.txt) is the source inventory. Detailed workflows and current platform claims are distinguished below because parts of the documentation disagree.

## Current workspace and project lifecycle

The August 17, 2026 workspace transition is the best navigation reference. New projects open with a large chat area; minimizing or resizing it exposes manual editing. Top tabs include Schematic, Layout, Files, Preview, Components, BOM, and Nets. Component projects add Pins and Symbol. Restore hidden tabs through **+**. The project drawer at bottom left contains library, objects, layers, rules, checks, and manufacturing; the Inspector sits on the right. Fork is in the top actions dropdown. Workspace arrangement is saved per project and user.

[Workspace transition](https://docs.flux.ai/Introduction/new-workspace-transition.md)

Start with a description and structured properties for voltage, interfaces, and other constraints. Select a suitable template or vetted example where useful. Fork preserves earlier design history; Clone starts an independent history. The forking reference says merging is not implemented and comments are not retained by either copy operation. Undo is local to the current user/tab; change history supports broader inspection and restoration. A restoration is itself recorded. Renaming can change a project URL, so update references deliberately.

[Project setup](https://docs.flux.ai/Introduction/getting-started-in-flux--project-setup.md) · [Reuse](https://docs.flux.ai/tutorials/reusing-community-projects.md) · [Fork/clone](https://docs.flux.ai/reference/reference-forking-cloning.md) · [History](https://docs.flux.ai/reference/reference-version-control.md) · [Rename](https://docs.flux.ai/reference/change-project-name.md)

## Components, symbols, footprints, and libraries

A part can contain terminals/internal schematic, external symbol, footprint, 3D representation, and simulation behavior. Completeness in one representation does not establish the others. Trace a signal from datasheet pin to schematic terminal, symbol pin, and PCB pad. Verify physical pin numbering separately from signal names. Extra footprint pads need an explicit terminal association when they carry a net.

Parametric symbols use terminal grouping, orientation, and order. Footprints use pad geometry and placement rules. Generic passives defer package, value, and MPN decisions; entering an MPN does not prove package or rating compatibility. Unitless imported SVGs can need an explicit scale, and artwork format restrictions matter.

Publish parts explicitly, and publish subsequent changes. Visibility is controlled separately through sharing. Consumers review and apply component updates, checking whether connections or pinouts need repair. Record source version and rationale when choosing an update.

[Create a part](https://docs.flux.ai/tutorials/tutorial-creating-a-part-from-scratch.md) · [Symbols](https://docs.flux.ai/tutorials/working-with-symbols.md) · [Footprints](https://docs.flux.ai/tutorials/working-with-footprints.md) · [Generic parts](https://docs.flux.ai/tutorials/tutorial-generic-part.md) · [Assets](https://docs.flux.ai/reference/reference-inspector-assets.md) · [Publish](https://docs.flux.ai/tutorials/publishing-a-part-to-the-library.md) · [Updates](https://docs.flux.ai/tutorials/tutorial-reviewing-part-updates.md)

## Connectivity and reusable modules

Portals with the same designator connect corresponding nets without a drawn wire. Ground has special fill behavior. Merely renaming a copied ground symbol does not establish a separate electrical ground domain.

Modules package several components and can preserve routed geometry. They provide hierarchical reuse with explicit interface terminals. **Internal module nets, including ground, remain isolated from the host unless exposed and connected through the interface.** Equal names do not bridge that boundary. Designator remapping prevents collisions and preserves selector relationships across insertion and updates.

For reusable blocks, record supply requirements, external interfaces, required companions, and layout dependencies. Place interface pads where the host can route to them. Converting selected components into a module without terminals creates no external connections; add terminals and publish the interface.

[Part types and portals](https://docs.flux.ai/reference/how-to-use-part-types.md) · [Ground](https://docs.flux.ai/tutorials/working-with-ground--basics--multiple-grounds--and-ground-fill-m.md) · [Modules](https://docs.flux.ai/tutorials/tutorial-parts-and-sublayouts.md) · [Module practices](https://docs.flux.ai/tutorials/tutorial-sublayouts-bestpractice.md) · [Convert to component](https://docs.flux.ai/reference/convert-to-part.md)

## PCB rules, geometry, and stackup

The object tree and rules determine layout geometry. Rules can target an individual object or match groups through CSS-like selectors. Examples include `trace`, `#R1`, and attribute selectors. Rule/property spelling and case matter. Inspect the selected object’s effective rule and inheritance rather than assuming a global setting wins.

Object-specific rules, selector specificity, inheritance, ordering, and `!important` affect precedence. Some rules are inheritable and others are not. Specify units explicitly, particularly for imported geometry. Set board outline, layer stack, manufacturing clearances, trace widths, via dimensions, mask/paste expansion, and fill behavior from the intended board requirements.

Default values are a starting point. Impedance-sensitive routing needs an actual stackup and material assumptions. Locks can extend to descendants, but should not be treated as a guarantee against every possible property edit.

[PCB rules](https://docs.flux.ai/reference/pcb-rules.md) · [Selectors](https://docs.flux.ai/reference/pcb-layout-rule-selectors.md) · [Cascade](https://docs.flux.ai/reference/pcb-layout-rules-cascade-and-inheritance.md) · [Rule types](https://docs.flux.ai/reference/layout-rules-types.md) · [Stackup](https://docs.flux.ai/reference/stackup-editor.md) · [Locks](https://docs.flux.ai/reference/locking.md)

## Placement, routing, fills, and checks

Place parts around functional groups, power paths, mechanical interfaces, and critical signal paths. Differential routing uses explicit bus grouping, impedance, skew, and related constraints. Review return paths and layer transitions alongside the signal traces.

For assisted routing, finish and commit critical traces first. The auto-layout documentation says the job snapshots and protects pre-existing traces and vias, then routes remaining connections around them. Inspect iterations and **Apply** the chosen result; unapplied iterations are lost when stopped, and applying discards alternatives. Re-read the committed design and run checks afterward.

Copper fill being enabled is distinct from being visible. Confirm net/layer assignment and connectivity. DRC covers issues such as overlaps, missing footprints, unrouted nets, invalid layers, and floating copper. Inspect muted checks too. A clean DRC result establishes only the checks performed, not circuit functionality or production performance.

[Placement](https://docs.flux.ai/tutorials/component-placement.md) · [Impedance](https://docs.flux.ai/reference/impedance-control.md) · [Auto-layout](https://docs.flux.ai/tutorials/auto-layout.md) · [Fills](https://docs.flux.ai/reference/reference-ground-fills.md) · [DRC](https://docs.flux.ai/reference/design-rule-check--drc-.md) · [PCB review](https://docs.flux.ai/tutorials/pcb-design-review.md)

## Calculations, Python, and circuit simulation

Flux documents three distinct computation surfaces:

| Surface | Purpose | Inputs and interpretation |
|---|---|---|
| Expressions | Unit-aware property and layout formulas with project/object context | Preserve dimensional consistency and inspect evaluated values |
| `@code` | Python calculations, data analysis, and plots | Preserve executable code, inputs, units, and output; Flux’s code sandbox has time/memory and external-network limits |
| SPICE simulator | Ngspice AC, DC, transient, and operating-point analysis | Use actual connectivity, device models, sources/loads, analysis settings, named outputs, and pass criteria |

For a supplied SPICE netlist, include the analysis, requested output directives, and termination. Check that simulation retries did not silently change the intended circuit or component values. The detailed simulator page covers electrical behavior, excludes thermal/mechanical/EM effects and pure digital simulation, and notes model limitations.

The assistant’s local numerical tools can support independent calculations now. A working local Ngspice/PySpice installation was not demonstrated; Flux’s own simulation engine was not run here.

[Expressions](https://docs.flux.ai/reference/expressions-overview.md) · [Python](https://docs.flux.ai/reference/code-tool.md) · [Simulator](https://docs.flux.ai/reference/simulator-tool.md)

## AI modes, knowledge, and external-agent integration

Chat and Agent differ in available actions. The mode reference describes Chat for inspection, questions, calculations, and documents; Agent adds engineering edits, placement/routing, simulation, research, manufacturing actions, and longer execution. Knowledge entries have triggers and scope; project entries can take precedence over user entries. Treat the active design, datasheets, requirements, and explicit decisions as the engineering context.

[Modes](https://docs.flux.ai/reference/chat---agent-mode.md) · [Project-aware assistant](https://docs.flux.ai/reference/copilot.md) · [Knowledge](https://docs.flux.ai/reference/knowledge-base.md)

The documented remote MCP endpoint is `https://app.flux.ai/mcp`, using Streamable HTTP with OAuth or bearer API-key authentication. The reference describes read/write/agent-run permissions conceptually, without publishing exact callable schemas or scope strings.

External clients read cloud project state and request outcomes from Flux’s agent. This is not a local project directory or a documented direct API for manually changing one net. The reliable loop is **read → request a bounded task → wait for completion → inspect outcome → read the resulting project again**. Update dependent firmware or documentation from that final hardware state. Agent runs consume account resources; a message saying work started is not completion evidence.

[Flux MCP](https://docs.flux.ai/reference/flux-mcp-server.md)

## Sourcing, reliability review, and manufacturing

Use exact manufacturer/MPN, package, ratings, quantity, and supplier packaging when comparing parts. Set build quantity before estimating cost. Recheck current availability at the time of a decision.

Passive consolidation is a candidate-finding process. A nearby value or matching package is insufficient to approve substitution: check circuit role, tolerance, stress, temperature behavior, timing, and physical fit. Maintain an original-to-proposed comparison and validate the chosen alternative.

An FMEA links failure mode, effect, likelihood, severity, detection, and corrective action. Its scores support prioritization rather than proving safety or reliability. Combine review with calculations, DRC, simulation where appropriate, and measured tests. Release the BOM, layout, fabrication, placement, and test records from one identified revision.

[Procurement](https://docs.flux.ai/tutorials/components-procurement.md) · [Availability](https://docs.flux.ai/reference/reference-inspector-pricing-and-availability.md) · [Consolidation](https://docs.flux.ai/reference/passive-component-consolidation.md) · [FMEA](https://docs.flux.ai/reference/fmea-report-generation.md) · [Testing](https://docs.flux.ai/tutorials/ai-testing-debugging.md)

## Import and export map

| Operation | Published scope or caveat |
|---|---|
| Cadence schematic | EDIF; preparation instructions specify EDIF 300 |
| Altium schematic | ASCII export; do not assume complete PCB-layout migration |
| KiCad parts | References specify v4/v5 `.lib`; another tutorial says v6, so verify the actual parser/version |
| KiCad footprint | `.kicad_mod` asset, not a complete board import |
| JEP30 | PartModel XML, Enterprise-only per reference |
| Fabrication | Gerber RS-274X and drill files in ZIP |
| Assembly | BOM CSVs and pick-and-place CSVs; inspect ZIP contents and manufacturer expectations |
| Manufacturing interchange | IPC-2581C on eligible plans |
| Connectivity | EDIF schematic netlist and IPC-D-356 layout netlist |
| 3D | STL/DAE representations; the detailed portability page describes STEP as bare board |
| Native design | `.flx` export |

Verify pin mapping, geometry, stackup, layers, units, drills, placement origin/rotation, BOM completeness, and accepted manufacturer formats after conversion.

[Schematic import](https://docs.flux.ai/reference/reference-import-designs.md) · [Component import](https://docs.flux.ai/reference/reference-import-kicad.md) · [Import tutorial](https://docs.flux.ai/tutorials/tutorial-import-part.md) · [JEP30](https://docs.flux.ai/reference/jep30-partmodel-reference.md) · [Portability](https://docs.flux.ai/reference/data-portability.md) · [Manufacturing](https://docs.flux.ai/Introduction/getting-started-in-flux--export-and-manufacturing.md)

## Broader platform, access, and account behavior

Current official EDA and MCAD pages advertise firmware work, broader board EM/thermal analysis, mechanical model import/editing, CAD-code output, enclosures, strength/heat/airflow analysis, and manufacturing services. These indicate potential integrations to evaluate with actual project inputs. They do not establish which solver, plan, model, or workflow is available in this session. Keep these broader claims separate from the detailed electrical SPICE tool.

[EDA](https://www.flux.ai/p/eda) · [MCAD](https://www.flux.ai/p/mcad)

Projects are private by default; public access settings can expose designs more widely than a private invitation. Check effective project rights before edits or distribution. Flux is cloud-hosted. Customer ownership, service-processing licenses, public-project reuse, and third-party integrations have distinct terms; a public project alone does not establish unrestricted reuse rights.

[Private/public](https://docs.flux.ai/faq/private-and-public-projects.md) · [Permissions](https://docs.flux.ai/reference/reference-sharing-and-permissions.md) · [Security](https://docs.flux.ai/faq/data-security-and-ip-protection.md) · [Terms](https://docs.flux.ai/legal/terms-of-service.md) · [Service agreement](https://docs.flux.ai/legal/main-services-agreement.md)

Agent usage and billing depend on the account and task. Newer support pages describe included usage, prepaid/promotional balances, then on-demand usage, with spending controls. Older credit documentation conflicts on reset timing, prepaid balances, and payer behavior. Check the account’s current settings rather than promising a fixed allowance or cost. No billing settings were changed in this study.

[Usage limits](https://docs.flux.ai/general-support/how-on-demand-usage-and-usage-limits-work.md) · [Charges](https://docs.flux.ai/general-support/how-acus-and-on-demand-charges-work.md)

## Source-code findings and limits

Available public material included user-facing simulator node schemas and selected Math.js/Ngspice source, not Flux’s full application or private agent implementation.

| Inspected source area | Understanding gained |
|---|---|
| Math.js `FunctionNode.js` | Expression compilation and function dispatch |
| Math.js `to.js` and `Unit.js` | Unit compatibility, scaling, normalization, and conversion |
| Ngspice `resload.c` | Conductance/current calculation and matrix stamping |
| Ngspice `capload.c` | Capacitor state, charge, and integration contribution |
| Ngspice `niiter.c` | Iterative circuit loading, solving, convergence, and failure handling |
| Flux node references | Object identity, terminal voltage/current histories, property values, and displayed outputs |

Local checks exercised the upstream Math.js 15.2.0 bundle and elementary independent circuit calculations. They validate those narrow calculations, not the deployed Flux application. The mirror source and upstream release do not prove Flux uses identical versions or modifications.

[Math.js source](https://github.com/josdejong/mathjs/tree/v15.2.0) · [Ngspice downloads/source links](https://ngspice.sourceforge.io/download.html) · [Element node](https://docs.flux.ai/reference/elementnode.md) · [Terminal node](https://docs.flux.ai/reference/elementterminalnode.md) · [Property node](https://docs.flux.ai/reference/propertynode.md) · [Output node](https://docs.flux.ai/reference/outputnode.md)

## Known documentation disagreements to resolve at execution time

- Use the 2026 workspace transition to interpret older menu screenshots.
- KiCad library versions and Eagle import availability differ across pages; test the intended format before committing a migration.
- The DRC page and fill reference disagree about automatic island removal. Inspect actual fill connectivity and warnings.
- An older rule listing marks curved traces unavailable while a dedicated reference documents them. Check the live feature.
- Older credits/review pages differ from current mode/support pages about Chat cost and account limits.
- Detailed STEP export and SPICE limits should not be generalized to every capability advertised on newer EDA/MCAD pages.
- Sharing documentation gives inconsistent precedence examples; inspect effective rights instead of inferring permission resolution.

These are bounded uncertainties, not reasons to delay the general workflow improvements.

## Inputs to retrieve when actual work begins

| Intended work | Minimum useful context |
|---|---|
| Apply the general methods | None beyond the task’s goal |
| Plan a circuit | Function, supply/load ranges, interfaces, size, environment, and major constraints |
| Review a design | Revision, schematic/netlist, BOM with exact parts, relevant datasheets, and acceptance requirements |
| Calculate or simulate | Connectivity and values, sources/loads, device models where needed, sweep/time range, outputs, and limits |
| Review PCB layout | Board geometry, placement/routing, stackup, manufacturing limits, and critical-net constraints |
| Review sourcing | MPNs, quantities, acceptable alternatives, build quantity, timing, and supplier constraints |
| Prepare firmware | Actual MCU/part, final pin mapping, voltages, clocks, protocols, and hardware revision |
| Operate Flux directly | An authorized project connection exposing the required tools |

Retrieve this context from available project files and connections first. Additional data is only necessary when it changes the engineering decision. The reusable reference preserves the working procedure; future work still needs current project facts and verification of actual outputs.
