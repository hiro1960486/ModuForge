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

## Consolidation review update (2026-10-10)
Historical head and broad pending items above describe the earlier gate. Reviewed implementation head: 0809645808b1b9188332dafaadb9fb7d46b71238.
At that head, seven check runs succeeded: dry-run, validate-root, staging-and-tests, Unit tests (non-GUI), readonly-acceptance, gui-smoke, completeness.

Later evidence supersedes earlier NOT RUN statements only for the specific cases documented:
- Rename: selected-row execution, forbidden-character rejection, case-only rename and backup-copy restore were manually checked; exact-byte verification and complete mode coverage remain outstanding.
- Tags: persistence/exact search, blank destination rejection, collision rejection, explicit move/tag persistence and refusal were checked. Some destination/body claims are user reports; full byte comparison remains outstanding.
- Organizer: COPY, collision/same-location rejection, MOVE cancellation and blank destination rejection were checked. Successful MOVE destination/body are partly user-reported; complete visual/hash evidence remains outstanding.
- Real Shell Recycle Bin restore is still not tested in an isolated user/VM. Backup-copy restore is a separate operation.

See RENAME_SAFETY_TEST_REPORT_20261010.md, TAGS_SAFETY_TEST_REPORT_20261010.md, ORGANIZER_SAFETY_TEST_REPORT_20261010.md for exact evidence limits.
Remaining whole-module functionality, media/export/API integration, licensing, legacy-reference cleanup and local staging reconciliation still block final consolidation/release.
PR #1 remains Draft. No stable release or legacy removal is authorized by a successful structural check alone.
Management policy: [REPOSITORY_CONSOLIDATION_20261010.md](REPOSITORY_CONSOLIDATION_20261010.md).

## Windows受入状況の更新（2026-10-10 22時台 JST）

記録時のブランチHEAD：52561f3。
利用者提供のPowerShell出力・画面・操作報告に基づく。
上記の過去時点の未完了記述は、以下の確認範囲について更新する。

### 今回確認した結果

- 正式作業先は E:\00_GitHub\ModuForge。旧stagingは保管名へ変更済み。
  作業先の一本化と比較判定は LOCAL_STAGING_REVIEW_20261010.md に記録済み。
  保管資料すべての内容一致を証明するものではない。
- 共通ジョブ処理：正常終了を停止扱いにする不具合を9144591で修正。
  正常終了と実際の停止ボタンを使ったQt試験がPASS。
- Preview：TXT本文表示とメディア情報を開いた際の更新を8465f72で修正。
  画像・TXT表示、試験した音声/動画の基本再生操作と終了後のロック解除を確認。
  音声再生時のAAC警告ログは原因未解決であり、全形式の再生保証とはしない。
- Tags：対象一覧へのD&Dを5e5496cで修正。
  単一ファイルの追加と再ドロップ時の重複防止を確認。
- 最新のWindows回帰試験：44件、4.331秒、全件OK。
  ログ：test_all_20261010_215708_227805.log。
  この試験結果を最新HEADのGitHub Actions合格とは扱わない。

### ファイル操作のSHA256照合

隔離したTemp試験フォルダーの256バイト生成データを使用。
既知SHA256：40AFF2E9D2D8922E47AFD4648E6967497158785FBD1DA870E7110266BF944880。

- Organizer COPY：元の内容不変、コピー先の内容一致を確認。
- Organizer MOVE：元の不在、移動先の内容一致、既存コピーの不変を確認。
- Rename：sample.bin → renamed.bin の旧名不在と内容一致を確認。
- Tags MOVE：元の不在、移動先の内容一致、画面上のタグ保持を確認。

詳細は以下の追記を参照する。
- TAGS_SAFETY_TEST_REPORT_20261010.md
- ORGANIZER_SAFETY_TEST_REPORT_20261010.md
- RENAME_SAFETY_TEST_REPORT_20261010.md

### 継続する残件と判定

確認した単一ファイルの内容保持はPASS。
全モード・複数ファイル・失敗経路・復元の受入完了を意味しない。
全8部品の受入結果整理、メディア/出力/APIの残件確認、隔離環境での実ごみ箱復元、
依存ライセンス確認、FW33参照整理、最新CI結果、main保護と最終レビューは継続する。

PR #1はDraft維持。最終マージ・正式リリースはBLOCKED。
旧FW33と保管stagingを保持し、FileWorkbench Nextへは組み込まない。
