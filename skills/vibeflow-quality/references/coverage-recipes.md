# 多语言覆盖率工具配置参考

本文档提供各种编程语言覆盖率工具的配置示例和阈值设置指南，帮助项目建立有效的质量保障体系。

## 概述

覆盖率工具选择原则：
- Python: pytest-cov
- Java: jacoco
- JavaScript/TypeScript: c8 (NYC 的现代替代)
- C/C++: gcov (配合 GCC/G++)

---

## 1. Python: pytest-cov

### 1.1 安装
```bash
pip install pytest pytest-cov
```

### 1.2 配置方式

**方式一：命令行参数**
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing tests/
```

**方式二：pytest.ini 配置**
```ini
[pytest]
addopts = --cov=src --cov-report=html --cov-report=term-missing
```

**方式三：pyproject.toml 配置**
```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### 1.3 覆盖率阈值设置

**最低标准（建议）**
```toml
[tool.coverage.report]
fail_under = 70
```

**良好标准**
```toml
[tool.coverage.report]
fail_under = 80
```

**优秀标准**
```toml
[tool.coverage.report]
fail_under = 90
```

### 1.4 常见问题

**问题**: 如何排除特定文件？
```toml
[tool.coverage.run]
omit = ["*/tests/*", "*/migrations/*", "*/__init__.py"]
```

**问题**: 如何处理分支覆盖率？
```toml
[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

---

## 2. Java: JaCoCo

### 2.1 Maven 配置
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <phase>verify</phase>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.70</minimum>
                            </limit>
                            <limit>
                                <counter>BRANCH</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.60</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### 2.2 Gradle 配置
```groovy
plugins {
    id 'java'
    id 'jacoco'
}

jacoco {
    toolVersion = '0.8.11'
}

jacocoTestReport {
    reports {
        html.required = true
        xml.required = true
    }
}

jacocoTestCoverageVerification {
    rules {
        rule {
            element = 'BUNDLE'
            limit {
                counter = 'LINE'
                value = 'COVEREDRATIO'
                minimum = 0.70
            }
        }
    }
}
```

### 2.3 阈值建议
| 类型 | 最低标准 | 良好标准 | 优秀标准 |
|------|----------|----------|----------|
| Line Coverage | 70% | 80% | 90% |
| Branch Coverage | 60% | 70% | 80% |
| Class Coverage | 80% | 90% | 95% |
| Method Coverage | 75% | 85% | 90% |

---

## 3. JavaScript/TypeScript: c8

### 3.1 安装
```bash
npm install --save-dev c8
```

### 3.2 package.json 配置
```json
{
  "scripts": {
    "test": "node --experimental-vm-modules node_modules/jest/bin/jest.js",
    "coverage": "c8 npm test",
    "coverage:report": "c8 report --reporter=text --reporter=html"
  },
  "c8": {
    "include": [
      "src/**/*.js",
      "src/**/*.ts"
    ],
    "exclude": [
      "**/*.test.js",
      "**/*.spec.js",
      "**/node_modules/**",
      "**/dist/**",
      "**/coverage/**"
    ],
    "reporter": ["text", "html", "lcov"],
    "reportsDir": ".coverage",
    "branch": true,
    "lines": 70,
    "functions": 70,
    "statements": 70,
    "checkCoverage": true
  }
}
```

### 3.3 Jest 集成
```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.test.{js,ts}',
    '!src/**/index.{js,ts}'
  ],
  coverageThreshold: {
    "global": {
      "branches": 70,
      "functions": 70,
      "lines": 70,
      "statements": 70
    }
  }
};
```

### 3.4 Vitest 集成
```typescript
// vite.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'c8',
      reporter: ['text', 'html'],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70
      }
    }
  }
});
```

---

## 4. C/C++: gcov

### 4.1 编译配置
```bash
# 使用 GCC 编译并启用覆盖率
gcc -fprofile-arcs -ftest-coverage -O0 -g -o myprogram myprogram.c
```

### 4.2 Makefile 示例
```makefile
CC = gcc
CFLAGS = -fprofile-arcs -ftest-coverage -O0 -g
LDFLAGS = -fprofile-arcs -ftest-coverage

coverage:
	$(CC) $(CFLAGS) -o program program.c
	./program
	gcov -o . program.c
	@echo "Coverage report generated"

clean-coverage:
	rm -f *.gcno *.gcda *.gcov coverage.*
```

### 4.3 lcov 工具（可视化）
```bash
# 安装 lcov
sudo apt-get install lcov

# 生成覆盖率报告
lcov --directory . --capture --output-file coverage.info
lcov --remove coverage.info '*/usr/*' --output-file filtered.info
genhtml filtered.info --output-directory coverage_report
```

### 4.4 CMake 配置
```cmake
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --coverage")

add_executable(myprogram main.cpp)

enable_testing()
add_test(NAME myprogram_test COMMAND myprogram)
```

---

## 5. 多语言项目阈值汇总

### 5.1 阈值设置原则
- **新项目**: 设置较低的初始阈值（60-70%），逐步提高
- **成熟项目**: 维持较高的覆盖率（80%+）
- **关键模块**: 设置更严格的阈值（90%+）

### 5.2 语言对比表
| 语言 | 工具 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|------|----------|------------|------------|
| Python | pytest-cov | 70% | 60% | - |
| Java | JaCoCo | 70% | 60% | 75% |
| JavaScript | c8 | 70% | 70% | 70% |
| C/C++ | gcov/lcov | 70% | 60% | - |

---

## 6. CI/CD 集成

### 6.1 GitHub Actions
```yaml
- name: Run coverage
  run: npm run coverage

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/lcov.info
    fail_ci_if_error: true
    thresholds: '70%'
```

### 6.2 GitLab CI
```yaml
coverage:
  script:
    - npm run coverage
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura.xml
    expire_in: 1 week
```

---

## 7. 最佳实践

### 7.1 覆盖率不是万能的
- 高覆盖率不等于高质量测试
- 关注边界条件和异常情况
- 使用多种测试类型（单元、集成、端到端）

### 7.2 渐进式改进
- 从关键模块开始提高覆盖率
- 为新代码设置更高标准
- 定期审查和调整阈值

### 7.3 排除规则
以下代码通常不计入覆盖率：
- 测试代码本身
- 配置文件
- 框架/库代码
- 自动生成的代码
- 已废弃的代码
