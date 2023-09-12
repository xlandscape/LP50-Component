"""
Script for documenting the code of the LP50 component.
"""
import os
import base.documentation
import LP50

root_folder = os.path.abspath(os.path.join(os.path.dirname(base.__file__), ".."))
base.documentation.document_component(
    LP50.LP50("LP50", None, None),
    os.path.join(root_folder, "..", "variant", "LP50", "README.md"),
    os.path.join(root_folder, "..", "variant", "mc.xml"),
    "IndEffect_LP50_StepsRiverNetwork_SD_Species1"
)
base.documentation.write_changelog(
    "LP50 component",
    LP50.LP50.VERSION,
    os.path.join(root_folder, "..", "variant", "LP50", "CHANGELOG.md")
)
base.documentation.write_contribution_notes(
    os.path.join(root_folder, "..", "variant", "LP50", "CONTRIBUTING.md"))
base.documentation.write_repository_info(
    os.path.join(root_folder, "..", "variant", "LP50"),
    os.path.join(root_folder, "..", "variant", "LP50", "repository.json"),
    os.path.join(root_folder, "..", "..", "..", "versions.json"),
    "component"
)
