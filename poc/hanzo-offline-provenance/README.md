# ARKHE ZERO - PoC for hanzoai/cloud#39 (HIP-1348)

This folder contains the Proof of Concept for the Offline/Edge Provenance layer proposed in issue #39.

## How to test in 10 seconds:
1. Open `arkhe-sovereign.html` in any browser (works offline).
2. Generate an Ed25519 DID.
3. Sign a mock artifact (representing the agent's output).
4. Verify it. 
5. Change 1 letter in the artifact -> The verifier rejects it.

## Bridging to Cloud (SLSA/Cosign):
When the edge agent regains connectivity, the `arkhe_signer.py` script can be used to anchor this local signature to the cloud infrastructure proposed by @breezesamuel.
