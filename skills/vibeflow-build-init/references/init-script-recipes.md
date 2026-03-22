# 环境初始化模板

本文档提供多种编程语言项目的初始化脚本模板和最佳实践，帮助快速搭建符合 VibeFlow 标准的新项目环境。

## 概述

环境初始化是项目启动的第一步，需要确保：
- 开发环境一致性
- 依赖管理标准化
- 项目结构规范化
- 验证构建可成功

---

## 1. Python 项目初始化

### 1.1 目录结构
```
project_name/
├── src/
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── docs/
├── scripts/
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── setup.py
├── .gitignore
└── README.md
```

### 1.2 pyproject.toml 模板
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project_name"
version = "0.1.0"
description = "项目描述"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
st = [
    "pytest>=7.4.0",
    "pytest-xdist>=3.3.0",
    "pytest-html>=4.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
```

### 1.3 初始化脚本
```bash
#!/bin/bash
# init_python_project.sh

set -e

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

# 创建项目目录
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 创建目录结构
mkdir -p src/tests/unit tests/integration docs scripts

# 创建 Python 包
touch src/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# 创建 requirements 文件
cat > requirements.txt << 'EOF'
requests>=2.28.0
pydantic>=2.0.0
EOF

cat > requirements-dev.txt << 'EOF'
-r requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
EOF

# 创建 pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "PROJECT_NAME_PLACEHOLDER"
version = "0.1.0"
description = "项目描述"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
EOF

sed -i "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/" pyproject.toml

# 创建 .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
.env
.venv
env/
venv/
*.log
EOF

# 创建 README.md
cat > README.md << 'EOF'
# Project Name

项目描述

## 安装

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

## 开发

```bash
# 运行测试
pytest

# 代码格式化
black .

# 代码检查
ruff check .

# 类型检查
mypy .
```

## 测试

```bash
# 单元测试
pytest tests/unit/

# 集成测试
pytest tests/integration/

# 覆盖率报告
pytest --cov=src --cov-report=html
```
EOF

echo "Python 项目 $PROJECT_NAME 初始化完成"
```

---

## 2. Node.js/TypeScript 项目初始化

### 2.1 目录结构
```
project_name/
├── src/
│   ├── index.ts
│   └── ...
├── tests/
│   ├── unit/
│   └── integration/
├── dist/
├── node_modules/
├── package.json
├── tsconfig.json
├── jest.config.js
├── .gitignore
└── README.md
```

### 2.2 package.json 模板
```json
{
  "name": "project_name",
  "version": "0.1.0",
  "description": "项目描述",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:st": "vitest run tests/st",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src --ext .ts",
    "lint:fix": "eslint src --ext .ts --fix",
    "prepare": "husky install"
  },
  "dependencies": {
    "express": "^4.18.2",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "@typescript-eslint/eslint-plugin": "^6.13.0",
    "@typescript-eslint/parser": "^6.13.0",
    "@vitest/coverage-v8": "^1.0.0",
    "eslint": "^8.54.0",
    "husky": "^8.0.3",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### 2.3 tsconfig.json 模板
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 2.4 初始化脚本
```bash
#!/bin/bash
# init_nodejs_project.sh

set -e

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

# 创建项目目录
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 创建目录结构
mkdir -p src tests/unit tests/integration tests/st

# 创建 package.json
cat > package.json << 'EOF'
{
  "name": "PROJECT_NAME_PLACEHOLDER",
  "version": "0.1.0",
  "description": "项目描述",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "test": "vitest run",
    "test:st": "vitest run tests/st",
    "lint": "eslint src --ext .ts"
  },
  "dependencies": {},
  "devDependencies": {}
}
EOF

sed -i "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/" package.json

# 创建 tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "tests"]
}
EOF

# 创建 vitest.config.ts
cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html']
    }
  }
});
EOF

# 创建 .gitignore
cat > .gitignore << 'EOF'
node_modules/
dist/
.env
.env.local
*.log
coverage/
.DS_Store
*.tgz
EOF

echo "Node.js 项目 $PROJECT_NAME 初始化完成"
```

---

## 3. Java 项目初始化

### 3.1 目录结构
```
project_name/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── project/
│   │   └── resources/
│   └── test/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           └── project/
│       └── resources/
├── pom.xml
├── .gitignore
└── README.md
```

### 3.2 pom.xml 模板
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>project-name</artifactId>
    <version>0.1.0</version>
    <packaging>jar</packaging>

    <name>Project Name</name>
    <description>项目描述</description>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.10.1</junit.version>
        <jacoco.version>0.8.11</jacoco.version>
    </properties>

    <dependencies>
        <!-- JUnit 5 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>

        <!-- JaCoCo -->
        <dependency>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>${jacoco.version}</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.2</version>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>${jacoco.version}</version>
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
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### 3.3 Gradle 配置（可选）
```groovy
plugins {
    id 'java'
    id 'application'
    id 'jacoco'
}

group = 'com.example'
version = '0.1.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation "org.junit.jupiter:junit-jupiter:5.10.1"
}

test {
    useJUnitPlatform()
    finalizedBy jacocoTestReport
}

jacocoTestReport {
    reports {
        xml.required = true
        html.required = true
    }
}

application {
    mainClass = 'com.example.project.Main'
}
```

---

## 4. C/C++ 项目初始化

### 4.1 目录结构
```
project_name/
├── include/
│   └── project/
│       ├── header.h
│       └── ...
├── src/
│   ├── main.cpp
│   └── ...
├── tests/
│   ├── unit/
│   └── integration/
├── build/
├── CMakeLists.txt
├── .gitignore
└── README.md
```

### 4.2 CMakeLists.txt 模板
```cmake
cmake_minimum_required(VERSION 3.26)
project(project_name VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 源代码目录
include_directories(include)

# 可执行文件
add_executable(${PROJECT_NAME}
    src/main.cpp
    src/module1.cpp
    src/module2.cpp
)

# 测试
enable_testing()
add_subdirectory(tests)

# 安装规则
install(TARGETS ${PROJECT_NAME} DESTINATION bin)
```

### 4.3 CMake 测试配置
```cmake
# tests/CMakeLists.txt
include(GoogleTest)

add_executable(unit_tests
    unit/test_module1.cpp
    unit/test_module2.cpp
)

target_link_libraries(unit_tests
    PRIVATE
    ${PROJECT_NAME}
    gtest_main
)

gtest_discover_tests(unit_tests)
```

### 4.4 Makefile 模板（简单项目）
```makefile
CXX = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -O2 -g
LDFLAGS =

SRC = src
INC = include
BUILD = build
TESTS = tests

TARGET = $(BUILD)/app
TEST_TARGET = $(BUILD)/tests

SOURCES = $(wildcard $(SRC)/*.cpp)
OBJECTS = $(SOURCES:$(SRC)/%.cpp=$(BUILD)/%.o)

.PHONY: all clean test coverage

all: $(TARGET)

$(TARGET): $(OBJECTS) | $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

$(BUILD)/%.o: $(SRC)/%.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -I$(INC) -c -o $@ $<

$(BUILD):
	mkdir -p $@

test: $(TEST_TARGET)
	$<
	$(MAKE) clean-tests

$(TEST_TARGET): $(TESTS)/main.cpp $(OBJECTS)
	$(CXX) $(CXXFLAGS) -I$(INC) -o $@ $^ -lgtest -lgtest_main -pthread

clean:
	rm -rf $(BUILD)

coverage:
	gcov -o . $(SRC)/*.cpp
```

---

## 5. 初始化验证清单

创建完项目后，执行以下验证：

### 5.1 Python
```bash
# 安装依赖
pip install -e .

# 运行测试
pytest

# 验证构建
python -c "import project; print(project.__version__)"
```

### 5.2 Node.js
```bash
# 安装依赖
npm install

# 运行测试
npm test

# 验证构建
npm run build
```

### 5.3 Java
```bash
# 编译
mvn compile

# 运行测试
mvn test

# 打包
mvn package
```

### 5.4 C/C++
```bash
# 编译
mkdir build && cd build
cmake ..
make

# 运行测试
make test
```

---

## 6. 常见问题处理

### 6.1 Python
**问题**: `ModuleNotFoundError`
**解决**: 检查 `PYTHONPATH` 是否包含 `src` 目录，或使用 `-e` 安装

**问题**: 编码问题
**解决**: 在文件开头添加 `# -*- coding: utf-8 -*-`

### 6.2 Node.js
**问题**: `Cannot find module`
**解决**: 检查 `tsconfig.json` 的 `paths` 配置

**问题**: ESM/CommonJS 混用
**解决**: 确保 `package.json` 中 `type` 字段正确设置

### 6.3 Java
**问题**: 编码问题
**解决**: 在 `pom.xml` 中设置 `<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>`

### 6.4 C/C++
**问题**: 头文件找不到
**解决**: 检查 `include_directories()` 路径是否正确

---

## 7. 自动化工具推荐

| 语言 | 初始化工具 |
|------|------------|
| Python | `cookiecutter` |
| Node.js | `create-vite`, `yeoman` |
| Java | `Maven Archetype`, `Spring Initializr` |
| C/C++ | `cmake-init` |
