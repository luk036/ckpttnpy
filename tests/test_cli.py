"""Tests for CLI module."""

import json
from pathlib import Path

import pytest

from ckpttnpy.cli import (
    PRESET_CHOICES,
    OBJECTIVE_CHOICES,
    read_hypergraph,
    read_hypergraph_dimacs,
    read_hypergraph_hmetis,
    read_hypergraph_json,
    write_partition,
)


class TestReadHmetis:
    """Tests for hMetis format reader."""

    def test_simple(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("4 5\n0 1 2\n1 2 3\n2 3 4\n3 4 0 1\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert graph.number_of_nodes() == 9
        assert len(weights) == 5
        assert all(w == 1 for w in weights)

    def test_with_vertex_weights(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("4 5 10\n0 1 2\n1 2 3\n2 3 4\n3 4 0 1\n1\n2\n3\n4\n5\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert len(weights) == 5
        assert weights == [1, 2, 3, 4, 5]

    def test_with_comments(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("% comment\n4 5\n% another comment\n0 1 2\n1 2 3\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert graph.number_of_nodes() == 9

    def test_small_file(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("2 3\n0 1\n1 2\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert graph.number_of_nodes() == 5


class TestReadJson:
    """Tests for JSON format reader."""

    def test_simple_nets(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text('{"nets": [[0, 1, 2], [1, 2, 3], [2, 3, 4]]}')

        graph, weights = read_hypergraph_json(str(json_file))

        assert graph.number_of_nodes() == 8

    def test_hyperedges_format(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text(
            '{"hyperedges": [[0, 1, 2], [1, 2, 3]], "num_vertices": 5}'
        )

        graph, weights = read_hypergraph_json(str(json_file))

        assert graph.number_of_nodes() == 7

    def test_edges_format(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text('{"edges": [[0, 1], [1, 2]], "num_vertices": 3}')

        graph, weights = read_hypergraph_json(str(json_file))

        assert graph.number_of_nodes() == 5

    def test_vertex_weights(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text(
            '{"hyperedges": [[0, 1], [1, 2]], "vertex_weights": [1, 2, 1]}'
        )

        graph, weights = read_hypergraph_json(str(json_file))

        assert weights == [1, 2, 1]

    def test_simple_list(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text("[[0, 1, 2], [1, 2, 3]]")

        graph, weights = read_hypergraph_json(str(json_file))

        assert graph.number_of_nodes() == 6

    def test_invalid_format(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text('{"unknown": "format"}')

        with pytest.raises(ValueError, match="Unknown JSON format"):
            read_hypergraph_json(str(json_file))


class TestReadDimacs:
    """Tests for DIMACS format reader."""

    def test_simple(self, tmp_path: Path) -> None:
        hgr = tmp_path / "hypergraph.hgr"
        hgr.write_text("p hypre 5 4\ne 0 1 2\ne 1 2 3\ne 2 3 4\ne 3 4 0 1\n")

        graph, weights = read_hypergraph_dimacs(str(hgr))

        assert graph.number_of_nodes() == 9

    def test_with_comments(self, tmp_path: Path) -> None:
        hgr = tmp_path / "hypergraph.hgr"
        hgr.write_text("c comment line\np hypre 5 4\ne 0 1 2\ne 1 2 3\n")

        graph, weights = read_hypergraph_dimacs(str(hgr))

        assert graph.number_of_nodes() == 7


class TestAutoDetect:
    """Tests for format auto-detection."""

    def test_json_extension(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text("[[0, 1], [1, 2]]")

        graph, weights = read_hypergraph(str(json_file))

        assert graph.number_of_nodes() == 5

    def test_hmetis_extension(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("2 3\n0 1\n1 2\n")

        graph, weights = read_hypergraph(str(hgr))

        assert graph.number_of_nodes() == 5

    def test_explicit_format(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.txt"
        hgr.write_text("2 3\n0 1\n1 2\n")

        graph, weights = read_hypergraph(str(hgr), input_format="hmetis")

        assert graph.number_of_nodes() == 5


class TestWritePartition:
    """Tests for partition writer."""

    def test_hmetis_format(self, tmp_path: Path) -> None:
        part = [0, 1, 0, 1, 0]
        out_file = tmp_path / "part.txt"

        write_partition(part, str(out_file))

        content = out_file.read_text()
        assert content == "0\n1\n0\n1\n0"

    def test_json_format(self, tmp_path: Path) -> None:
        part = [0, 1, 0, 1, 0]
        out_file = tmp_path / "part.json"

        write_partition(part, str(out_file), output_format="json")

        content = out_file.read_text()
        data = json.loads(content)
        assert data == [0, 1, 0, 1, 0]

    def test_stdout(self, capsys: pytest.CaptureFixture) -> None:
        part = [0, 1, 0]

        write_partition(part)

        captured = capsys.readouterr()
        assert captured.out.strip() == "0\n1\n0"


class TestConstants:
    """Tests for CLI constants."""

    def test_preset_choices(self) -> None:
        assert "default" in PRESET_CHOICES
        assert "quality" in PRESET_CHOICES
        assert "highest_quality" in PRESET_CHOICES
        assert "deterministic" in PRESET_CHOICES
        assert "large_k" in PRESET_CHOICES

    def test_objective_choices(self) -> None:
        assert "cut" in OBJECTIVE_CHOICES
        assert "km1" in OBJECTIVE_CHOICES
        assert "soed" in OBJECTIVE_CHOICES
        assert "km1a" in OBJECTIVE_CHOICES


class TestGraphStructure:
    """Tests for graph structure after reading."""

    def test_bipartite_labels(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("2 3\n0 1\n1 2\n")

        graph, _ = read_hypergraph_hmetis(str(hgr))

        vertices = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 0]
        nets = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 1]

        assert len(vertices) == 3
        assert len(nets) == 2

    def test_edges_connect_vertices_to_nets(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("2 3\n0 1\n1 2\n")

        graph, _ = read_hypergraph_hmetis(str(hgr))

        assert graph.has_edge(3, 0)
        assert graph.has_edge(3, 1)
        assert graph.has_edge(4, 1)
        assert graph.has_edge(4, 2)


class TestEdgeCases:
    """Tests for edge cases."""

    def test_single_net(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("1 3\n0 1 2\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert graph.number_of_nodes() == 4

    def test_single_vertex(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("1 1\n0\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert graph.number_of_nodes() == 2

    def test_empty_net(self, tmp_path: Path) -> None:
        hgr = tmp_path / "test.hgr"
        hgr.write_text("2 2\n0\n1\n")

        graph, weights = read_hypergraph_hmetis(str(hgr))

        assert graph.number_of_nodes() == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
