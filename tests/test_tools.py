import json
from agent.tools import detect_stack, compute_quality_metrics


def test_detect_stack_spring_boot(tmp_path):
    (tmp_path / "pom.xml").write_text("""
    <project>
        <artifactId>my-app</artifactId>
        <dependencies>
            <dependency><groupId>org.springframework.boot</groupId></dependency>
        </dependencies>
    </project>""")
    result = json.loads(detect_stack.invoke({"repo_path": str(tmp_path)}))
    assert "java" in result["languages"]
    assert "maven" in result["tools"]
    assert "spring-boot" in result["frameworks"]


def test_quality_metrics_no_tests(tmp_path):
    (tmp_path / "app.py").write_text("def main(): pass")
    (tmp_path / "README.md").write_text("# My Project")
    result = json.loads(compute_quality_metrics.invoke({"repo_path": str(tmp_path)}))
    assert result["test_ratio"] == 0
    assert result["has_readme"] is True
    assert result["has_ci"] is False


def test_quality_metrics_with_tests(tmp_path):
    (tmp_path / "app.py").write_text("def main(): pass")
    (tmp_path / "test_app.py").write_text("def test_main(): pass")
    result = json.loads(compute_quality_metrics.invoke({"repo_path": str(tmp_path)}))
    assert result["test_ratio"] == 50.0