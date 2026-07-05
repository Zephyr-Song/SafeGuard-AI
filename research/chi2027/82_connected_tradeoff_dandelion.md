# Connected Trade-off Dandelion

## Source and adaptation boundary

An et al. (2020), *Dandelion Diagram: Aggregating Positioning and Orientation Data in the Visualization of Classroom Proxemics*, combines position, orientation, trajectory, aggregation, and color coding so multiple properties can be interpreted in one synthesized view (CHI EA 2020, DOI: 10.1145/3334480.3382795).

SafeBARS does not reuse classroom tracking data or claim that the original diagram validated ethics deliberation. It adapts the paper's synthesized-data principle to a different design problem.

## SafeBARS encodings

- Petal: one connected research-design trade-off.
- Petal orientation: which side currently receives more weight.
- Petal width and length: magnitude of the imbalance, never ethical quality.
- Dashed connections: ethics-framework dimensions affected by that trade-off.
- Node fill: framework family (foundational/VSD/ESR, Menlo ICT, or NIST AI RMF).
- Node outline: submitted evidence coverage (documented, partial, or missing).
- Text summary: exact values, leaning direction, and connected dimensions for accessibility and interpretation.

## Interaction and provenance

Researchers can adjust each parameter pair, record a rationale, and save the deliberation. The server validates positions from 0 to 100 and stores the rationale in the session event history. Saved decisions appear in the researcher-facing research-design document and the expert cross-application caseload summary.

## Interpretation boundary

The graphic supports comparison and reflection. It is not an optimization surface, ethical score, compliance result, or approval recommendation.
