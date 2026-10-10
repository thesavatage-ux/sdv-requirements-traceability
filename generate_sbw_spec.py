# Generator script for FEAT-CHS-02 SysReq and SwReq files
import os

workspace = r"c:\Workset\AntiGravityProjects\TestOptimisationExperiement"
sys_req_file = os.path.join(workspace, "system_requirements", "FEAT-CHS-02_SbW_SysReq.md")
sw_req_file = os.path.join(workspace, "software_requirements", "FEAT-CHS-02_SbW_SwReq.md")

print("Generator script writing initiated...")
