#!/usr/bin/env python3

from __future__ import annotations

import sys
import math
from dataclasses import dataclass
from typing import List, Optional


# -----------------------------
# Data structures
# -----------------------------

@dataclass
class Vertex:
    x: float
    y: float
    z: float


@dataclass
class Cluster:
    vertices: List[Vertex]

    def center(self) -> Vertex:
        cx = sum(v.x for v in self.vertices) / len(self.vertices)
        cy = sum(v.y for v in self.vertices) / len(self.vertices)
        cz = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vertex(cx, cy, cz)

    def lowest_y(self) -> float:
        return min(v.y for v in self.vertices)


@dataclass
class GearSet:
    nose: Optional[Cluster]
    left_main: Optional[Cluster]
    right_main: Optional[Cluster]


# -----------------------------
# Parsing
# -----------------------------

def parse_obj_vertices(file_path: str) -> List[Vertex]:
    vertices: List[Vertex] = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            if line.startswith("VT "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append(
                        Vertex(
                            x=float(parts[1]),
                            y=float(parts[2]),
                            z=float(parts[3]),
                        )
                    )

    return vertices


# -----------------------------
# Core logic
# -----------------------------

def filter_low_band(vertices: List[Vertex], height_margin: float = 0.4) -> List[Vertex]:
    min_y = min(v.y for v in vertices)
    return [v for v in vertices if v.y <= min_y + height_margin]


def cluster_vertices(vertices: List[Vertex], distance_threshold: float = 1.0) -> List[Cluster]:
    clusters: List[Cluster] = []

    for v in vertices:
        assigned = False

        for cluster in clusters:
            c = cluster.center()
            dist = math.dist((v.x, v.z), (c.x, c.z))

            if dist < distance_threshold:
                cluster.vertices.append(v)
                assigned = True
                break

        if not assigned:
            clusters.append(Cluster(vertices=[v]))

    return clusters


# -----------------------------
# Gear detection heuristics
# -----------------------------

def find_main_gear(clusters: List[Cluster], symmetry_tol: float = 1.0) -> tuple[Optional[Cluster], Optional[Cluster]]:
    best_pair = (None, None)
    best_score = float("inf")

    for i, a in enumerate(clusters):
        for b in clusters[i + 1:]:
            ca = a.center()
            cb = b.center()

            # Check symmetry in X and similarity in Z
            if abs(ca.x + cb.x) < symmetry_tol and abs(ca.z - cb.z) < symmetry_tol:
                score = abs(ca.x) + abs(cb.x)  # prefer wide stance

                if score < best_score:
                    best_score = score
                    best_pair = (a, b)

    return best_pair


def find_nose_gear(
    clusters: List[Cluster],
    exclude: List[Cluster],
    center_tol: float = 1.5
) -> Optional[Cluster]:

    candidates = []

    for cluster in clusters:
        if cluster in exclude:
            continue

        c = cluster.center()

        # near centerline
        if abs(c.x) < center_tol:
            candidates.append(cluster)

    if not candidates:
        return None

    # choose most forward/backward depending on coordinate system
    return min(candidates, key=lambda c: c.center().z)


# -----------------------------
# Output
# -----------------------------

def print_cluster(label: str, cluster: Optional[Cluster]) -> None:
    if cluster is None:
        print(f"{label}: NOT FOUND\n")
        return

    c = cluster.center()
    print(f"{label}:")
    print(f"  Center   : ({c.x:.3f}, {c.y:.3f}, {c.z:.3f})")
    print(f"  Lowest Y : {cluster.lowest_y():.6f}")
    print(f"  Points   : {len(cluster.vertices)}\n")


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python analyze_obj.py <file.obj>")
        sys.exit(1)

    file_path = sys.argv[1]

    print(f"Loading: {file_path}")
    vertices = parse_obj_vertices(file_path)
    print(f"Total vertices: {len(vertices)}")

    # Step 1: focus on near-ground vertices
    low_band = filter_low_band(vertices, height_margin=0.4)
    print(f"Vertices in low band: {len(low_band)}")

    # Step 2: cluster them
    clusters = cluster_vertices(low_band, distance_threshold=1.0)
    print(f"Clusters found: {len(clusters)}\n")

    # Step 3: detect main gear
    left_main, right_main = find_main_gear(clusters)

    # Ensure left/right ordering
    if left_main and right_main:
        if left_main.center().x > right_main.center().x:
            left_main, right_main = right_main, left_main

    # Step 4: detect nose gear
    nose = find_nose_gear(clusters, exclude=[left_main, right_main])

    # Step 5: output
    print("🛞 Landing Gear Detection\n")

    print_cluster("Left Main Gear", left_main)
    print_cluster("Right Main Gear", right_main)
    print_cluster("Nose Gear", nose)


if __name__ == "__main__":
    main()
