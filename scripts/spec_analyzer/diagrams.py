# -*- coding: utf-8 -*-
"""Generate Mermaid diagrams from spec facts."""
from __future__ import annotations

from typing import Any


def generate_module_graph_mermaid(modules: list[dict]) -> str:
    """Generate Mermaid flowchart TD from module list.

    Args:
        modules: list of dicts with name, path, deps, kind

    Returns:
        Mermaid flowchart TD code
    """
    if not modules:
        return "```mermaid\nflowchart TD\n    empty[No modules found]\n```"

    # Build nodes and edges
    nodes = set()
    edges = []

    for module in modules:
        module_name = module.get("name", "")
        if module_name:
            nodes.add(module_name)

        deps = module.get("deps", [])
        for dep in deps:
            if dep in nodes or any(m.get("name") == dep for m in modules):
                edges.append((module_name, dep))

    # Generate Mermaid code
    lines = ["```mermaid", "flowchart TD"]

    # Add nodes
    for node in sorted(nodes):
        safe_name = _safe_mermaid_id(node)
        lines.append(f"    {safe_name}[{node}]")

    # Add edges
    for source, target in edges:
        safe_source = _safe_mermaid_id(source)
        safe_target = _safe_mermaid_id(target)
        lines.append(f"    {safe_source} --> {safe_target}")

    lines.append("```")
    return "\n".join(lines)


def generate_er_diagram_mermaid(entities: list[dict]) -> str:
    """Generate Mermaid erDiagram from entity list.

    Args:
        entities: list of dicts with name, bases, fields, methods

    Returns:
        Mermaid erDiagram code
    """
    if not entities:
        return "```mermaid\nerDiagram\n    empty ||--|| no_data : \"No entities found\"\n```"

    lines = ["```mermaid", "erDiagram"]

    for entity in entities:
        name = entity.get("name", "Unknown")
        fields = entity.get("fields", [])
        bases = entity.get("bases", [])

        # Class header
        if bases:
            base_str = ", ".join(bases)
            lines.append(f"    {name} {{")
            lines.append(f"        string base \"{base_str}\"")
        else:
            lines.append(f"    {name} {{")

        # Fields
        for field in fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "string")
            lines.append(f'        {field_type} {field_name}')

        lines.append("    }")

    lines.append("```")
    return "\n".join(lines)


def _safe_mermaid_id(name: str) -> str:
    """Convert a name to a safe Mermaid node ID.

    Mermaid node IDs must start with a letter or underscore,
    and contain only alphanumeric characters, underscores, and hyphens.
    """
    safe = name.replace(".", "_").replace("-", "_").replace("/", "_")
    if safe[0].isdigit():
        safe = "n" + safe
    return safe
