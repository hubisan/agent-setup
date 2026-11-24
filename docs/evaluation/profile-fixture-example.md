# Example: Luna compatibility configuration check

Date: 2026-11-24. Issue #4. Local Python 3.13.5 execution, not a Codex client. This demonstrates the evaluation record with a small deterministic configuration case, not a skill comparison or a real provider benchmark.

**Case:** balanced Codex plan must use only model/effort combinations supported by a synthetic capability inventory. The inventory permits Luna high and xhigh, not max; Terra high and Sol medium are permitted. The only tested change is whether the plan uses the inventory. Both conditions use the same role catalogue and profile. Acceptance: no unsupported role, no changed model family, no false runtime-verification claim.

Reproduce in the repository:

```bash
tmp=$(mktemp -d)
cat > "$tmp/cap.json" <<'JSON'
{"provider":"codex","version":"fixture","models":{"gpt-6-luna":["high","xhigh"],"gpt-6.1-terra":["high"],"gpt-6.2-sol":["medium"]}}
JSON
python3 scripts/profile.py plan --provider codex
python3 scripts/profile.py plan --provider codex --capabilities "$tmp/cap.json"
rm "$tmp/cap.json"
rmdir "$tmp"
```

Compare every role's selected effort against the inventory. The local demonstration did this programmatically.

| Check | Baseline: documentation-only plan | Variant: inventory-aware plan |
| --- | --- | --- |
| Unsupported roles | 3: planner-light, implementer, reviewer-light | 0 |
| Selected effort for those roles | max | xhigh |
| Model family changes | None | None |
| Evidence state | configured | configured |
| Local elapsed wall time, one run | 0.840 s | 0.714 s |

Both commands returned successfully; only the variant meets the synthetic compatibility criterion. The wall times are single local subprocess observations (not inference latency and not a speed claim). No models were spawned, no skill package or activation was tested, and token/credit/API charges are not measured. Independent review and user acceptance are pending; real client availability, actual fallback and model/effort evidence remain untested.

**Decision:** keep the capability-aware validation path for the next review/pilot. No conclusion about real skill benefit, model quality or credit savings. Next: run the host verification with actual inventories and compare equivalent ACS cases in #5.
