import os
import shutil
from tools.query_status import scan_documents
from datetime import datetime

def test_inbox_workflow_simulation(tmp_path):
    # Setup directories
    dev_notes = tmp_path / "dev_notes"
    inbox = dev_notes / "inbox"
    archive = dev_notes / "inbox-archive"
    specs = dev_notes / "specs"
    
    inbox.mkdir(parents=True)
    archive.mkdir(parents=True)
    specs.mkdir(parents=True)
    
    # 1. User puts file in inbox
    input_file = inbox / "feature.md"
    input_file.write_text("I want a pony.", encoding="utf-8")
    
    # 2. Agent processing (Simulation)
    # a. Read file (implicit)
    
    # b. Create spec
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    spec_file = specs / f"{timestamp}_pony_feature.md"
    header = f"""# Spec: Pony

**Source:** {input_file}
**Original File:** feature.md
**Status:** 🔵 Ready for Implementation
**Timestamp:** {timestamp}

Content...
"""
    spec_file.write_text(header, encoding="utf-8")
    
    # c. Archive input
    shutil.move(str(input_file), str(archive / "feature.md"))
    
    # 3. Verify System State
    assert not input_file.exists()
    assert (archive / "feature.md").exists()
    assert spec_file.exists()
    
    # 4. Verify Query Tool sees it
    # We need to monkeypatch config in query_status to point to tmp_path
    import tools.query_status
    tools.query_status.DEV_NOTES_DIR = str(dev_notes)
    tools.query_status.SPECS_DIR = str(specs)
    tools.query_status.PLANS_DIR = str(dev_notes / "project_plans")
    tools.query_status.CHANGES_DIR = str(dev_notes / "changes")
    
    docs = scan_documents()
    assert len(docs) == 1
    assert docs[0].type == "spec"
    assert docs[0].status == "🔵 Ready for Implementation"
