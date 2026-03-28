#!/bin/bash
# Auto-generated migration script - REVIEW BEFORE EXECUTION
# Project: second_voice

set -e

# Create safety tag before migration
git tag -a -m 'pre-dev_notes-cleanup' pre-dev_notes-cleanup

# Move untracked files to tmp/ for review
mkdir -p tmp
mv dev_notes/specs/2026-02-09_collaborative-refinement-session.md tmp/2026-02-09_collaborative-refinement-session.md.untracked
mv dev_notes/specs/2026-01-25_02-45-00_provider_specific_config.md tmp/2026-01-25_02-45-00_provider_specific_config.md.untracked
mv dev_notes/specs/2026-02-09_cloud-code-ctrl-g-integration.md tmp/2026-02-09_cloud-code-ctrl-g-integration.md.untracked
mv dev_notes/specs/2026-01-29_09-26-14_fix-bootstrap-relative-links.md tmp/2026-01-29_09-26-14_fix-bootstrap-relative-links.md.untracked
mv dev_notes/specs/2026-01-25_18-46-25_add-tests-fix-pytest.md tmp/2026-01-25_18-46-25_add-tests-fix-pytest.md.untracked
mv dev_notes/specs/2026-01-28_10-36-41_mandatory-context-assembly.md tmp/2026-01-28_10-36-41_mandatory-context-assembly.md.untracked
mv dev_notes/specs/fix-cline.md tmp/fix-cline.md.untracked
mv dev_notes/specs/2026-02-15_14-30-00_run-and-verify-tests.md tmp/2026-02-15_14-30-00_run-and-verify-tests.md.untracked
mv dev_notes/specs/2026-02-09_two-pane-interactive-ui.md tmp/2026-02-09_two-pane-interactive-ui.md.untracked
mv dev_notes/specs/2026-01-25_21-55-00_amplify-soundbar-signal.md tmp/2026-01-25_21-55-00_amplify-soundbar-signal.md.untracked
mv dev_notes/specs/2026-01-24_23-27-34_second-voice-refactor.md tmp/2026-01-24_23-27-34_second-voice-refactor.md.untracked
mv dev_notes/specs/2026-02-09_structured-document-creation.md tmp/2026-02-09_structured-document-creation.md.untracked
mv dev_notes/specs/spec-03.md tmp/spec-03.md.untracked
mv dev_notes/specs/spec-02.md tmp/spec-02.md.untracked
mv dev_notes/specs/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md tmp/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md.untracked
mv dev_notes/specs/2026-01-25_02-00-00_cli_options.md tmp/2026-01-25_02-00-00_cli_options.md.untracked
mv dev_notes/specs/2026-01-27_07-28-35_inbox-based-spec-generation.md tmp/2026-01-27_07-28-35_inbox-based-spec-generation.md.untracked
mv dev_notes/specs/2026-02-09_redundancy-removal-consolidation.md tmp/2026-02-09_redundancy-removal-consolidation.md.untracked
mv dev_notes/specs/README.md tmp/README.md.untracked
mv dev_notes/specs/add-cline.md tmp/add-cline.md.untracked
mv dev_notes/specs/2026-02-09_dual-text-looping-editor.md tmp/2026-02-09_dual-text-looping-editor.md.untracked
mv dev_notes/specs/2026-01-29_21-00-00_hide-agent-files.md tmp/2026-01-29_21-00-00_hide-agent-files.md.untracked
mv dev_notes/specs/2026-01-25_agent-kernel-refactor.md tmp/2026-01-25_agent-kernel-refactor.md.untracked
mv dev_notes/specs/spec-01.md tmp/spec-01.md.untracked
mv dev_notes/project_plans/2026-01-26_08-54-55_make-logs-first-workflow-optional.md tmp/2026-01-26_08-54-55_make-logs-first-workflow-optional.md.untracked
mv dev_notes/project_plans/2026-01-28_10-36-41_simple-mandatory-reading-lists.md tmp/2026-01-28_10-36-41_simple-mandatory-reading-lists.md.untracked
mv dev_notes/project_plans/2026-01-25_18-46-25_add-cline-cli-support.md tmp/2026-01-25_18-46-25_add-cline-cli-support.md.untracked
mv dev_notes/project_plans/2026-01-29_09-26-14_fix-bootstrap-relative-links.md tmp/2026-01-29_09-26-14_fix-bootstrap-relative-links.md.untracked
mv dev_notes/project_plans/2026-01-25_18-46-25_add-tests-fix-pytest.md tmp/2026-01-25_18-46-25_add-tests-fix-pytest.md.untracked
mv dev_notes/project_plans/2026-01-29_21-10-00_reorganize-agent-files.md tmp/2026-01-29_21-10-00_reorganize-agent-files.md.untracked
mv dev_notes/project_plans/2026-02-15_14-30-30_run-and-verify-tests.md tmp/2026-02-15_14-30-30_run-and-verify-tests.md.untracked
mv dev_notes/project_plans/2026-01-28_10-36-41_mandatory-context-assembly.md tmp/2026-01-28_10-36-41_mandatory-context-assembly.md.untracked
mv dev_notes/project_plans/2026-01-25_23-00-00_refactor-system-prompts-independence.md tmp/2026-01-25_23-00-00_refactor-system-prompts-independence.md.untracked
mv dev_notes/project_plans/2026-01-25_00-32-27_mode-selection-architecture.md tmp/2026-01-25_00-32-27_mode-selection-architecture.md.untracked
mv dev_notes/project_plans/2026-01-25_21-55-00_amplify-soundbar-signal.md tmp/2026-01-25_21-55-00_amplify-soundbar-signal.md.untracked
mv dev_notes/project_plans/2026-01-25_02-47-00_provider_config_plan.md tmp/2026-01-25_02-47-00_provider_config_plan.md.untracked
mv dev_notes/project_plans/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md tmp/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md.untracked
mv dev_notes/project_plans/2026-01-27_07-28-35_inbox-based-spec-generation.md tmp/2026-01-27_07-28-35_inbox-based-spec-generation.md.untracked
mv dev_notes/project_plans/2026-02-15_14-00-00_pytest-and-demo-execution-with-fixes.md tmp/2026-02-15_14-00-00_pytest-and-demo-execution-with-fixes.md.untracked
mv dev_notes/project_plans/2026-01-29_21-41-49_agent-cleanup-and-fixes.md tmp/2026-01-29_21-41-49_agent-cleanup-and-fixes.md.untracked
mv dev_notes/project_plans/2025-01-25_14-00-00_improve-cleanup-prompts.md tmp/2025-01-25_14-00-00_improve-cleanup-prompts.md.untracked
mv dev_notes/project_plans/2026-01-25_02-05-00_cli_options_plan.md tmp/2026-01-25_02-05-00_cli_options_plan.md.untracked
mv dev_notes/project_plans/2026-01-25_agent-kernel-refactor.md tmp/2026-01-25_agent-kernel-refactor.md.untracked
mv dev_notes/inbox/failover.md tmp/failover.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-02-openrouter-free-models.out tmp/2026-02-04_23-00-00_prompt-02-openrouter-free-models.out.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_QUICK-REFERENCE.md tmp/2026-02-04_23-00-00_QUICK-REFERENCE.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-03.md tmp/2026-02-04_23-00-00_prompt-03.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_fix-problems.md tmp/2026-02-04_23-00-00_fix-problems.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_FINAL-CHANGES-SUMMARY.md tmp/2026-02-04_23-00-00_FINAL-CHANGES-SUMMARY.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_openrouter-models.jsonl tmp/2026-02-04_23-00-00_openrouter-models.jsonl.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-02.md tmp/2026-02-04_23-00-00_prompt-02.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_TESTING-GUIDE.md tmp/2026-02-04_23-00-00_TESTING-GUIDE.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_OPENROUTER-FIXES-SUMMARY.md tmp/2026-02-04_23-00-00_OPENROUTER-FIXES-SUMMARY.md.untracked
mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-02-fixes-summary.md tmp/2026-02-04_23-00-00_prompt-02-fixes-summary.md.untracked
mv dev_notes/analysis/2026-01-26_process-discovery-assessment.md tmp/2026-01-26_process-discovery-assessment.md.untracked
mv dev_notes/analysis/2026-01-26_tool-guides-reorganization-report.md tmp/2026-01-26_tool-guides-reorganization-report.md.untracked
mv dev_notes/analysis/2026-01-26_tool-guides-consistency-analysis.md tmp/2026-01-26_tool-guides-consistency-analysis.md.untracked
mv dev_notes/analysis/2026-01-26_tool-reference-consistency-audit.md tmp/2026-01-26_tool-reference-consistency-audit.md.untracked

# Create planning directory structure
mkdir -p planning/inbox

# Migrate specs → planning/*-prompt.md
git mv dev_notes/specs/2026-01-24_23-27-34_second-voice-refactor.md planning/2026-01-24_23-27-34_second-voice-refactor-prompt.md
git mv dev_notes/specs/2026-01-25_02-00-00_cli_options.md planning/2026-01-25_02-00-00_cli_options-prompt.md
git mv dev_notes/specs/2026-01-25_02-45-00_provider_specific_config.md planning/2026-01-25_02-45-00_provider_specific_config-prompt.md
git mv dev_notes/specs/2026-01-25_18-46-25_add-tests-fix-pytest.md planning/2026-01-25_18-46-25_add-tests-fix-pytest-prompt.md
git mv dev_notes/specs/2026-01-25_21-55-00_amplify-soundbar-signal.md planning/2026-01-25_21-55-00_amplify-soundbar-signal-prompt.md
git mv dev_notes/specs/2026-01-25_agent-kernel-refactor.md planning/2026-01-25_agent-kernel-refactor-prompt.md
git mv dev_notes/specs/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md planning/2026-01-26_23-00-24_aac-support-and-whisper-recovery-prompt.md
git mv dev_notes/specs/2026-01-27_07-28-35_inbox-based-spec-generation.md planning/2026-01-27_07-28-35_inbox-based-spec-generation-prompt.md
git mv dev_notes/specs/2026-01-28_10-36-41_mandatory-context-assembly.md planning/2026-01-28_10-36-41_mandatory-context-assembly-prompt.md
git mv dev_notes/specs/2026-01-29_09-26-14_fix-bootstrap-relative-links.md planning/2026-01-29_09-26-14_fix-bootstrap-relative-links-prompt.md
git mv dev_notes/specs/2026-01-29_21-00-00_hide-agent-files.md planning/2026-01-29_21-00-00_hide-agent-files-prompt.md
git mv dev_notes/specs/2026-02-09_cloud-code-ctrl-g-integration.md planning/2026-02-09_cloud-code-ctrl-g-integration-prompt.md
git mv dev_notes/specs/2026-02-09_collaborative-refinement-session.md planning/2026-02-09_collaborative-refinement-session-prompt.md
git mv dev_notes/specs/2026-02-09_dual-text-looping-editor.md planning/2026-02-09_dual-text-looping-editor-prompt.md
git mv dev_notes/specs/2026-02-09_redundancy-removal-consolidation.md planning/2026-02-09_redundancy-removal-consolidation-prompt.md
git mv dev_notes/specs/2026-02-09_structured-document-creation.md planning/2026-02-09_structured-document-creation-prompt.md
git mv dev_notes/specs/2026-02-09_two-pane-interactive-ui.md planning/2026-02-09_two-pane-interactive-ui-prompt.md
git mv dev_notes/specs/2026-02-15_14-30-00_run-and-verify-tests.md planning/2026-02-15_14-30-00_run-and-verify-tests-prompt.md
git mv dev_notes/specs/README.md planning/README-prompt.md
git mv dev_notes/specs/add-cline.md planning/add-cline-prompt.md
git mv dev_notes/specs/fix-cline.md planning/fix-cline-prompt.md
git mv dev_notes/specs/spec-01.md planning/spec-01-prompt.md
git mv dev_notes/specs/spec-02.md planning/spec-02-prompt.md
git mv dev_notes/specs/spec-03.md planning/spec-03-prompt.md

# Migrate project_plans → planning/*-plan.md
git mv dev_notes/project_plans/2025-01-25_14-00-00_improve-cleanup-prompts.md planning/2025-01-25_14-00-00_improve-cleanup-prompts-plan.md
git mv dev_notes/project_plans/2026-01-25_00-32-27_mode-selection-architecture.md planning/2026-01-25_00-32-27_mode-selection-architecture-plan.md
git mv dev_notes/project_plans/2026-01-25_02-05-00_cli_options_plan.md planning/2026-01-25_02-05-00_cli_options_plan-plan.md
git mv dev_notes/project_plans/2026-01-25_02-47-00_provider_config_plan.md planning/2026-01-25_02-47-00_provider_config_plan-plan.md
git mv dev_notes/project_plans/2026-01-25_18-46-25_add-cline-cli-support.md planning/2026-01-25_18-46-25_add-cline-cli-support-plan.md
git mv dev_notes/project_plans/2026-01-25_18-46-25_add-tests-fix-pytest.md planning/2026-01-25_18-46-25_add-tests-fix-pytest-plan.md
git mv dev_notes/project_plans/2026-01-25_21-55-00_amplify-soundbar-signal.md planning/2026-01-25_21-55-00_amplify-soundbar-signal-plan.md
git mv dev_notes/project_plans/2026-01-25_23-00-00_refactor-system-prompts-independence.md planning/2026-01-25_23-00-00_refactor-system-prompts-independence-plan.md
git mv dev_notes/project_plans/2026-01-25_agent-kernel-refactor.md planning/2026-01-25_agent-kernel-refactor-plan.md
git mv dev_notes/project_plans/2026-01-26_08-54-55_make-logs-first-workflow-optional.md planning/2026-01-26_08-54-55_make-logs-first-workflow-optional-plan.md
git mv dev_notes/project_plans/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md planning/2026-01-26_23-00-24_aac-support-and-whisper-recovery-plan.md
git mv dev_notes/project_plans/2026-01-27_07-28-35_inbox-based-spec-generation.md planning/2026-01-27_07-28-35_inbox-based-spec-generation-plan.md
git mv dev_notes/project_plans/2026-01-28_10-36-41_mandatory-context-assembly.md planning/2026-01-28_10-36-41_mandatory-context-assembly-plan.md
git mv dev_notes/project_plans/2026-01-28_10-36-41_simple-mandatory-reading-lists.md planning/2026-01-28_10-36-41_simple-mandatory-reading-lists-plan.md
git mv dev_notes/project_plans/2026-01-29_09-26-14_fix-bootstrap-relative-links.md planning/2026-01-29_09-26-14_fix-bootstrap-relative-links-plan.md
git mv dev_notes/project_plans/2026-01-29_21-10-00_reorganize-agent-files.md planning/2026-01-29_21-10-00_reorganize-agent-files-plan.md
git mv dev_notes/project_plans/2026-01-29_21-41-49_agent-cleanup-and-fixes.md planning/2026-01-29_21-41-49_agent-cleanup-and-fixes-plan.md
git mv dev_notes/project_plans/2026-02-15_14-00-00_pytest-and-demo-execution-with-fixes.md planning/2026-02-15_14-00-00_pytest-and-demo-execution-with-fixes-plan.md
git mv dev_notes/project_plans/2026-02-15_14-30-30_run-and-verify-tests.md planning/2026-02-15_14-30-30_run-and-verify-tests-plan.md

# Migrate inbox → planning/inbox/
git mv dev_notes/inbox/failover.md planning/inbox/failover.md

mkdir -p planning/inbox-archive
# Migrate inbox-archive → planning/inbox-archive/
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_FINAL-CHANGES-SUMMARY.md planning/inbox-archive/2026-02-04_23-00-00_FINAL-CHANGES-SUMMARY.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_OPENROUTER-FIXES-SUMMARY.md planning/inbox-archive/2026-02-04_23-00-00_OPENROUTER-FIXES-SUMMARY.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_QUICK-REFERENCE.md planning/inbox-archive/2026-02-04_23-00-00_QUICK-REFERENCE.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_TESTING-GUIDE.md planning/inbox-archive/2026-02-04_23-00-00_TESTING-GUIDE.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_fix-problems.md planning/inbox-archive/2026-02-04_23-00-00_fix-problems.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-02-fixes-summary.md planning/inbox-archive/2026-02-04_23-00-00_prompt-02-fixes-summary.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-02.md planning/inbox-archive/2026-02-04_23-00-00_prompt-02.md
git mv dev_notes/inbox-archive/2026-02-04_23-00-00_prompt-03.md planning/inbox-archive/2026-02-04_23-00-00_prompt-03.md

mkdir -p planning/analysis
# Migrate analysis → planning/analysis/
git mv dev_notes/analysis/2026-01-26_process-discovery-assessment.md planning/analysis/2026-01-26_process-discovery-assessment.md
git mv dev_notes/analysis/2026-01-26_tool-guides-consistency-analysis.md planning/analysis/2026-01-26_tool-guides-consistency-analysis.md
git mv dev_notes/analysis/2026-01-26_tool-guides-reorganization-report.md planning/analysis/2026-01-26_tool-guides-reorganization-report.md
git mv dev_notes/analysis/2026-01-26_tool-reference-consistency-audit.md planning/analysis/2026-01-26_tool-reference-consistency-audit.md

# Remove empty directories
rmdir dev_notes/specs 2>/dev/null || true
rmdir dev_notes/project_plans 2>/dev/null || true
rmdir dev_notes/inbox 2>/dev/null || true

echo '✓ Migration complete for second_voice'