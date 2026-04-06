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


def generate_c4_context_mermaid(project_name: str, tech_stack: list[dict]) -> str:
    """Generate a lightweight C4-style system context diagram.

    Static analysis cannot reliably infer real business actors or every external
    system, so this view stays conservative and only surfaces stable collaborators
    visible from repository facts.
    """
    system_id = _safe_mermaid_id(project_name)
    lines = ["```mermaid", "flowchart LR"]
    lines.append('    actor["用户 / 上游调用方"]')
    lines.append(f'    {system_id}["{project_name}<br/>System"]')
    lines.append(f"    actor --> {system_id}")

    collaborators = []
    for item in tech_stack[:3]:
        name = str(item.get("name") or "").strip()
        if name:
            collaborators.append(f"依赖: {name}")
    if not collaborators:
        collaborators = ["源码模块", "配置 / 状态文件", "测试 / 验证"]

    for index, label in enumerate(collaborators, 1):
        node_id = f"{system_id}_ctx_{index}"
        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    {system_id} --> {node_id}")

    lines.append("```")
    return "\n".join(lines)


def generate_c4_container_mermaid(project_name: str, modules: list[dict]) -> str:
    """Generate a lightweight C4-style container diagram from module paths."""
    if not modules:
        return "```mermaid\nflowchart TB\n    empty[No containers found]\n```"

    containers = _collect_containers(modules)
    lines = ["```mermaid", "flowchart TB"]
    system_id = _safe_mermaid_id(project_name)
    lines.append(f'    {system_id}["{project_name}<br/>System Boundary"]')

    for name, payload in containers.items():
        node_id = _safe_mermaid_id(f"{project_name}_{name}")
        label = f"{name}<br/>{payload['module_count']} modules"
        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    {system_id} --> {node_id}")

    for edge in _collect_container_edges(modules):
        edge_count = edge["count"]
        source_id = _safe_mermaid_id(f"{project_name}_{edge['source']}")
        target_id = _safe_mermaid_id(f"{project_name}_{edge['target']}")
        lines.append(f'    {source_id} -->|"{edge_count} deps"| {target_id}')

    lines.append("```")
    return "\n".join(lines)


def generate_c4_component_mermaid(modules: list[dict], max_nodes: int = 12) -> str:
    """Generate a compact C4-style component view from the hottest modules."""
    if not modules:
        return "```mermaid\nflowchart LR\n    empty[No components found]\n```"

    ranked = sorted(
        modules,
        key=lambda item: (
            len(item.get("deps", [])),
            -len(str(item.get("path") or "")),
            str(item.get("name") or ""),
        ),
        reverse=True,
    )[:max_nodes]
    kept_names = {str(item.get("name") or "") for item in ranked}

    lines = ["```mermaid", "flowchart LR"]
    for module in sorted(ranked, key=lambda item: str(item.get("name") or "")):
        name = str(module.get("name") or "unknown")
        node_id = _safe_mermaid_id(name)
        kind = str(module.get("kind") or "module")
        lines.append(f'    {node_id}["{name}<br/>({kind})"]')

    for module in sorted(ranked, key=lambda item: str(item.get("name") or "")):
        name = str(module.get("name") or "")
        for dep in module.get("deps", []):
            if dep in kept_names:
                lines.append(f"    {_safe_mermaid_id(name)} --> {_safe_mermaid_id(dep)}")

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


def _container_name(module: dict) -> str:
    path = str(module.get("path") or "")
    parts = path.replace("\\", "/").split("/")
    if parts and parts[0]:
        return parts[0]
    name = str(module.get("name") or "").split(".", 1)[0]
    return name or "root"


def _collect_containers(modules: list[dict]) -> dict[str, dict[str, Any]]:
    containers: dict[str, dict[str, Any]] = {}
    for module in modules:
        container = _container_name(module)
        payload = containers.setdefault(container, {"module_count": 0})
        payload["module_count"] += 1
    return containers


def _collect_container_edges(modules: list[dict]) -> list[dict[str, Any]]:
    by_name = {
        str(module.get("name") or ""): _container_name(module)
        for module in modules
        if module.get("name")
    }
    edges: dict[str, dict[str, Any]] = {}
    for module in modules:
        source_container = _container_name(module)
        for dep in module.get("deps", []):
            target_container = by_name.get(dep)
            if not target_container or target_container == source_container:
                continue
            key = f"{source_container}->{target_container}"
            payload = edges.setdefault(
                key,
                {"source": source_container, "target": target_container, "count": 0},
            )
            payload["count"] += 1
    return list(edges.values())
