# Dogfood Journal — Priya

## Cycle 1 — 2026-04-05

**Explored**: README vs command source files — checked if documented behavior matches implementation

**Bug found**: README persona selection claim contradicts interview command
- README said "Every command picks a random persona" (line 89)
- Interview command requires `--persona` (commands/interview.md:26)
- Classification: documentation mismatch

**Fix**: Updated README to list which commands support random selection, noted `/interview` requires `--persona`

**Test**: `tests/test-readme-persona-claims.sh` — validates README doesn't make blanket claims contradicted by command definitions

**PR**: https://github.com/btucker/blindspots/pull/1

## Next cycle ideas
- Check if `/experiment` arguments are documented anywhere users can find them (README has no usage examples)
- Interview command Step 1 duplicates persona generation logic instead of delegating to setup — inconsistent with other commands
- Check if the `--context` flag for `/interview` is mentioned in the README (it isn't)
- Verify agent tool lists match what they actually need
