import os
import pytest
from tools.query_status import Document, link_documents, get_next_unimplemented

class TestStatusQuery:
    def test_header_parsing(self, tmp_path):
        # Create a dummy spec file
        spec_file = tmp_path / "test_spec.md"
        spec_content = """# Spec: Test

**Source:** some/source.md
**Status:** 🔵 Ready for Implementation
**Timestamp:** 2026-01-27_10-00-00
**Priority:** High

Content...
"""
        spec_file.write_text(spec_content, encoding="utf-8")
        
        doc = Document(str(spec_file))
        assert doc.headers["Source"] == "some/source.md"
        assert doc.status == "🔵 Ready for Implementation"
        assert doc.timestamp == "2026-01-27_10-00-00"
        assert doc.headers["Priority"] == "High"

    def test_status_normalization(self, tmp_path):
        variations = {
            "Completed": "✅ Complete",
            "In Progress": "🟡 In Progress",
            "Under Review": "🟢 Awaiting Approval"
        }
        
        for raw, normalized in variations.items():
            f = tmp_path / f"test_{raw.replace(' ', '_')}.md"
            f.write_text(f"**Status:** {raw}\n", encoding="utf-8")
            doc = Document(str(f))
            assert doc.status == normalized

    def test_linking(self, tmp_path):
        # Create spec
        spec = tmp_path / "spec.md"
        spec.write_text("**Status:** 🔵 Ready for Implementation\n", encoding="utf-8")
        
        # Create plan linking to spec
        plan = tmp_path / "plan.md"
        plan_content = f"**Source:** {spec}\n**Status:** 🔵 Ready for Implementation\n"
        plan.write_text(plan_content, encoding="utf-8")
        
        # Create change linking to plan
        change = tmp_path / "change.md"
        change_content = f"**Source:** {plan}\n**Status:** 🟡 In Progress\n"
        change.write_text(change_content, encoding="utf-8")
        
        docs = [Document(str(spec)), Document(str(plan)), Document(str(change))]
        # Mock type determination since directory structure isn't standard
        docs[0].type = "spec"
        docs[1].type = "plan"
        docs[2].type = "change"
        
        link_documents(docs)
        
        assert docs[1] in docs[0].related_files
        assert docs[2] in docs[1].related_files

    def test_next_unimplemented(self, tmp_path):
        # Plan 1: Completed
        p1 = tmp_path / "p1.md"
        p1.write_text("**Status:** ✅ Complete\n**Timestamp:** 2026-01-01\n", encoding="utf-8")
        
        # Plan 2: Ready (Old)
        p2 = tmp_path / "p2.md"
        p2.write_text("**Status:** 🔵 Ready for Implementation\n**Timestamp:** 2026-01-02\n", encoding="utf-8")
        
        # Plan 3: Ready (New)
        p3 = tmp_path / "p3.md"
        p3.write_text("**Status:** 🔵 Ready for Implementation\n**Timestamp:** 2026-01-03\n", encoding="utf-8")
        
        docs = [Document(str(p)) for p in [p1, p2, p3]]
        for d in docs: d.type = "plan"
        
        next_plan = get_next_unimplemented(docs)
        assert next_plan.filepath == str(p2) # Should be p2 (oldest ready)
