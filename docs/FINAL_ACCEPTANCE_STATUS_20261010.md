# ModuForge root migration — final acceptance gate (2026-10-10)

## Verified in GitHub Actions (branch: refactor/safe-root-layout)
Head commit: `aa10fadc0b53f13741ea097a60c2929a28c91606`.

Seven workflow categories completed successfully:
1. Module tests
2. Safe layout migration validation
3. Flat root layout verification
4. Flat layout completeness audit
5. Root migration dry-run
6. ModuForge staged acceptance
7. Windows GUI startup smoke

New GUI smoke executes all eight `ModulePort.create_widget()` paths on the Windows hosted runner with Qt `offscreen`, then closes each widget and calls its shutdown routine. It does **not** validate Explorer drag-and-drop, visible desktop rendering, media codecs, scan accuracy, filesystem mutations, or Recycle Bin restore.

The former `FW33/` layout and 133 migrated copies are both retained. Five altered BAT launchers are intentional. Nine older files are catalogued under `docs/MIGRATION_DOCUMENT_INVENTORY.md`.

## Release gates still not met
- [ ] Eight modules verified visually **from new repository root**, not only historical staging.
- [ ] File operation acceptance using a disposable duplicate data set; explicit consent, no-overwrite, cancel, rollback/failure.
- [ ] Media playback, compare, hash export and tree export functionality on Windows 11.
- [ ] Real Recycle Bin restore in an isolated test user/VM with original location missing/present and arbitrary restore destination.
- [ ] License scope/third-party notices reviewed. Existing FW33 MIT text is not sufficient evidence for third-party dependencies.
- [ ] Update tests/docs/workflows to remove the transitional `FW33/` dependency, then remove legacy sources in a **separate reviewed change**.
- [ ] Verify main branch protections and perform final review.

## Decision
**BLOCKED for final merge/release.** Automated structural, non-GUI and offscreen GUI startup verification have passed, but they are not end-to-end Windows acceptance. Keep PR #1 as Draft; do not delete FW33 or merge into main until the remaining checks are evidenced.

FileWorkbench Next v3.3.0-rc1 remains an unchanged integration baseline.
