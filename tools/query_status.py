#!/usr/bin/env python3
import os
import re
import argparse
import glob
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
DEV_NOTES_DIR = "dev_notes"
SPECS_DIR = os.path.join(DEV_NOTES_DIR, "specs")
PLANS_DIR = os.path.join(DEV_NOTES_DIR, "project_plans")
CHANGES_DIR = os.path.join(DEV_NOTES_DIR, "changes")

# Regex for header fields
HEADER_REGEX = {
    "Source": re.compile(r"\*\*Source:\*\*\s*(.+)"),
    "Status": re.compile(r"\*\*Status:\*\*\s*(.+)"),
    "Timestamp": re.compile(r"\*\*Timestamp:\*\*\s*(.+)"),
    "Priority": re.compile(r"\*\*Priority:\*\*\s*(.+)"),
}

# Status Normalization
STATUS_MAP = {
    "Completed": "✅ Complete",
    "COMPLETED": "✅ Complete",
    "✅ Complete": "✅ Complete",
    "✅ COMPLETE": "✅ Complete",
    "✓ Completed": "✅ Complete",
    "Completed ✅": "✅ Complete",
    "🔵 Ready for Implementation": "🔵 Ready for Implementation",
    "Ready for Implementation": "🔵 Ready for Implementation",
    "Under Review": "🟢 Awaiting Approval",
    "Pending Review": "🟢 Awaiting Approval",
    "Awaiting transformation": "🔵 Ready for Implementation",
    "In Progress": "🟡 In Progress",
    "🟡 In Progress": "🟡 In Progress",
    "🟢 Awaiting Approval": "🟢 Awaiting Approval",
}

class Document:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.type = self._determine_type()
        self.headers = self._parse_headers()
        self.status = self._normalize_status(self.headers.get("Status", "Unknown"))
        self.timestamp = self.headers.get("Timestamp", "")
        self.source = self.headers.get("Source", "")
        
        # Relationships
        self.related_files = [] # List of Document objects
        
    def _determine_type(self):
        if SPECS_DIR in self.filepath: return "spec"
        if PLANS_DIR in self.filepath: return "plan"
        if CHANGES_DIR in self.filepath: return "change"
        return "unknown"

    def _parse_headers(self) -> Dict[str, str]:
        headers = {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read(2048) # Read first 2KB for headers
                
            for key, pattern in HEADER_REGEX.items():
                match = pattern.search(content)
                if match:
                    headers[key] = match.group(1).strip()
        except Exception as e:
            # print(f"Error reading {self.filepath}: {e}")
            pass
        return headers

    def _normalize_status(self, raw_status):
        return STATUS_MAP.get(raw_status.strip(), raw_status.strip())

    def to_dict(self):
        return {
            "file": self.filepath,
            "type": self.type,
            "status": self.status,
            "timestamp": self.timestamp,
            "source": self.source
        }

def scan_documents() -> List[Document]:
    documents = []
    for directory in [SPECS_DIR, PLANS_DIR, CHANGES_DIR]:
        if not os.path.exists(directory):
            continue
        for filepath in glob.glob(os.path.join(directory, "*.md")):
            documents.append(Document(filepath))
    return documents

def link_documents(documents: List[Document]):
    # Create a map for easy lookup by path (normalized)
    doc_map = {os.path.normpath(d.filepath): d for d in documents}
    
    # Also map by filename for looser matching if full path fails
    filename_map = {d.filename: d for d in documents}
    
    for doc in documents:
        if doc.source:
            # Try exact path match first
            source_path = os.path.normpath(doc.source)
            # Handle relative paths if necessary (though spec implies full path)
            if not os.path.isabs(source_path) and not source_path.startswith("dev_notes"):
                 # Try to guess - if it's a plan, source is spec
                 pass # For now assume well-formed paths or relative to root
            
            # Simple path cleanup for matching
            clean_source = source_path.replace("../", "").replace("./", "")
            
            # Try to find the parent
            parent = None
            for d_path, d_obj in doc_map.items():
                if d_path.endswith(clean_source):
                    parent = d_obj
                    break
            
            if not parent:
                 # Try filename match
                 source_filename = os.path.basename(clean_source)
                 parent = filename_map.get(source_filename)
            
            if parent:
                parent.related_files.append(doc)

def get_next_unimplemented(documents: List[Document]):
    # Find plans that are "Ready for Implementation" or spec without plans?
    # Spec says: "Next unimplemented plan" -> Plan with status Ready
    plans = [d for d in documents if d.type == "plan"]
    # Sort by timestamp (oldest first? Spec doesn't strictly say, but usually FIFO)
    # Spec Task 2.2 says: "Oldest pending plan" is a separate command.
    # "Next" usually implies high priority or oldest.
    # Let's sort by timestamp.
    plans.sort(key=lambda x: x.timestamp)
    
    for plan in plans:
        if plan.status == "🔵 Ready for Implementation":
            return plan
    return None

def get_oldest_pending(documents: List[Document]):
    plans = [d for d in documents if d.type == "plan" and d.status == "🔵 Ready for Implementation"]
    if not plans:
        return None
    plans.sort(key=lambda x: x.timestamp)
    return plans[0]

def get_all_incomplete(documents: List[Document]):
    # Incomplete = Ready or In Progress
    return [d for d in documents if d.type == "plan" and d.status in ["🔵 Ready for Implementation", "🟡 In Progress"]]

def get_orphans(documents: List[Document]):
    # Plans without source specs? 
    # Spec says: "Plans without source specs"
    # But wait, logic: If plan has source field, but file doesn't exist? Or source field is empty?
    orphans = []
    doc_map = {os.path.normpath(d.filepath): d for d in documents}
    
    for doc in documents:
        if doc.type == "plan":
            if not doc.source:
                orphans.append(doc)
                continue
                
            # verify source exists
            # This is tricky because link_documents logic handles fuzzy matching.
            # Let's rely on if it was successfully linked?
            # Actually, link_documents links Parent -> Child. 
            # We want Child -> Parent check.
            pass # simplified above logic doesn't store parent ref on child clearly.
            
            # Re-verify existence
            clean_source = doc.source.replace("../", "").replace("./", "")
            found = False
            for d_path in doc_map:
                if d_path.endswith(clean_source):
                    found = True
                    break
            if not found:
                # check if file exists on disk even if not in our doc list (maybe not md?)
                if not os.path.exists(clean_source) and not os.path.exists(os.path.join(DEV_NOTES_DIR, clean_source)):
                     orphans.append(doc)
    return orphans

def print_summary(documents: List[Document]):
    specs = [d for d in documents if d.type == "spec"]
    plans = [d for d in documents if d.type == "plan"]
    changes = [d for d in documents if d.type == "change"]
    
    print(f"📊 Status Summary")
    print(f"=================")
    print(f"Specs:   {len(specs)}")
    print(f"Plans:   {len(plans)}")
    print(f"Changes: {len(changes)}")
    print(f"")
    
    # Status breakdown for plans
    status_counts = {}
    for p in plans:
        status_counts[p.status] = status_counts.get(p.status, 0) + 1
        
    print(f"Plan Status:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

def main():
    parser = argparse.ArgumentParser(description="Query status of specifications and project plans.")
    parser.add_argument("--next", action="store_true", help="Show next unimplemented plan")
    parser.add_argument("--oldest", action="store_true", help="Show oldest pending plan")
    parser.add_argument("--incomplete", action="store_true", help="List all incomplete plans")
    parser.add_argument("--orphans", action="store_true", help="List plans without source specs")
    parser.add_argument("--summary", action="store_true", help="Show overall status summary")
    
    args = parser.parse_args()
    
    documents = scan_documents()
    link_documents(documents)
    
    if args.summary:
        print_summary(documents)
        return

    if args.next:
        plan = get_next_unimplemented(documents)
        if plan:
            print(f"Next Unimplemented Plan:\n  {plan.filepath}\n  Status: {plan.status}\n  Timestamp: {plan.timestamp}")
        else:
            print("No unimplemented plans found.")
        return

    if args.oldest:
        plan = get_oldest_pending(documents)
        if plan:
            print(f"Oldest Pending Plan:\n  {plan.filepath}\n  Status: {plan.status}\n  Timestamp: {plan.timestamp}")
        else:
            print("No pending plans found.")
        return

    if args.incomplete:
        plans = get_all_incomplete(documents)
        if plans:
            print(f"Incomplete Plans ({len(plans)}):")
            for p in plans:
                print(f"  {p.filepath} [{p.status}]")
        else:
            print("No incomplete plans found.")
        return

    if args.orphans:
        orphans = get_orphans(documents)
        if orphans:
            print(f"Orphan Plans ({len(orphans)}):")
            for p in orphans:
                print(f"  {p.filepath} (Source: {p.source or 'None'})")
        else:
            print("No orphan plans found.")
        return
        
    # Default if no args
    print_summary(documents)

if __name__ == "__main__":
    main()
