#!/usr/bin/env python3

from __future__ import annotations

import sys
import math
from dataclasses import dataclass


# -----------------------------
# Data structures
# -----------------------------

@dataclass
class Vertex:
    x: float
    y: float  # vertical axis in X-Plane OBJ8
    z: float


@dataclass
class Cluster:
    vertices: list[Vertex]

    def center(self) -> Vertex:
        cx = sum(v.x for v in self.vertices) / len(self.vertices)
        cy = sum(v.y for v in self.vertices) / len(self.vertices)
        cz = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vertex(cx, cy, cz)

    def lowest_y(self) -> float:
        return min(v.y for v in self.vertices)


# -----------------------------
# Parsing
# -----------------------------

def parse_obj_vertices(file_path: str) -> list[Vertex]:
    vertices: list[Vertex] = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            if line.startswith("VT "):
                parts = line.split()
                if len(parts) >= 4:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    vertices.append(Vertex(x, y, z))

    return vertices


# -----------------------------
# Analysis
# -----------------------------

def get_lowest_vertices(vertices: list[Vertex], limit: int = 50) -> list[Vertex]:
    return sorted(vertices, key=lambda v: v.y)[:limit]


def cluster_vertices_by_distance(
    vertices: list[Vertex],
    distance_threshold: float = 1.0
) -> list[Cluster]:

    clusters: list[Cluster] = []

    for vertex in vertices:
        placed_in_cluster = False

        for cluster in clusters:
            center = cluster.center()

            horizontal_distance = math.dist(
                (vertex.x, vertex.z),
                (center.x, center.z)
            )

            if horizontal_distance < distance_threshold:
                cluster.vertices.append(vertex)
                placed_in_cluster = True
                break

        if not placed_in_cluster:
            clusters.append(Cluster(vertices=[vertex]))

    return clusters


# -----------------------------
# Output
# -----------------------------

def print_analysis(clusters: list[Cluster]) -> None:
    print("\n🛞 Detected Landing Gear Clusters:\n")

    for index, cluster in enumerate(clusters, start=1):
        center = cluster.center()

        print(f"Cluster {index}:")
        print(f"  Vertex count : {len(cluster.vertices)}")
        print(
            f"  Center       : ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")
        print(f"  Lowest Y     : {cluster.lowest_y():.6f}")
        print()


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python analyze_obj.py <file.obj>")
        sys.exit(1)

    obj_file_path: str = sys.argv[1]

    print(f"Loading OBJ file: {obj_file_path}")

    vertices: list[Vertex] = parse_obj_vertices(obj_file_path)
    print(f"Total vertices parsed: {len(vertices)}")

    lowest_vertices: list[Vertex] = get_lowest_vertices(vertices, limit=100)

    print("\n📉 Lowest vertices (top 10):")
    for v in lowest_vertices[:10]:
        print(f"VT {v.x:.6f} {v.y:.6f} {v.z:.6f}")

    clusters: list[Cluster] = cluster_vertices_by_distance(
        lowest_vertices,
        distance_threshold=1.0
    )

    print_analysis(clusters)


if __name__ == "__main__":
    main()
