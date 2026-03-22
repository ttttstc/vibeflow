# 多语言 ST 工具配置参考

本文档描述 VibeFlow 系统测试（ST）阶段中常用的测试框架配置，包括 pytest、JUnit、Jest、Vitest 等工具的使用方法和最佳实践。

## 概述

系统测试（System Testing）关注整个系统的集成测试，验证各模块间的协作是否符合预期。ST 区别于单元测试（UT）和集成测试（IT），更接近真实用户的使用场景。

---

## 1. Python: pytest

### 1.1 安装
```bash
pip install pytest pytest-xdist pytest-html pytest-json-report
```

### 1.2 基础配置
**pytest.ini**
```ini
[pytest]
testpaths = tests/st
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    st: marks tests as system tests
    smoke: marks tests as smoke tests
```

### 1.3 Pytest fixture 示例
```python
import pytest
from app import create_app
from database import Database

@pytest.fixture(scope="session")
def app():
    """创建应用实例（session级别，所有测试共享）"""
    app = create_app(config="testing")
    yield app

@pytest.fixture(scope="function")
def client(app):
    """创建测试客户端（function级别，每个测试独立）"""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def db(app):
    """创建数据库（function级别，每个测试独立）"""
    db = Database(app.config["DATABASE_URL"])
    db.create_all()
    yield db
    db.drop_all()

@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    """自动执行的前置/后置处理"""
    # 前置
    setup_test_environment()
    yield
    # 后置
    teardown_test_environment()
```

### 1.4 参数化测试
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("login", "success"),
    ("logout", "success"),
    ("invalid", "error"),
    ("", "error"),
])
def test_user_actions(input, expected):
    result = perform_action(input)
    assert result.status == expected
```

### 1.5 数据驱动测试
```python
import pytest
import json

@pytest.fixture(params=json.load(open("test_data/users.json")))
def user_data(request):
    return request.param

def test_user_operations(user_data):
    result = create_user(user_data)
    assert result.success == user_data["expected"]
```

### 1.6 并行执行
```bash
# 使用 pytest-xdist 并行执行
pytest -n auto  # 自动检测 CPU 核心数
pytest -n 4     # 使用 4 个进程
pytest -n 2     # 使用 2 个进程
```

### 1.7 测试报告
```bash
# 生成 HTML 报告
pytest --html=reports/st_report.html --self-contained-html

# 生成 JSON 报告
pytest --json-report --json-report-file=reports/st_report.json
```

---

## 2. Java: JUnit 5

### 2.1 Maven 依赖
```xml
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.1</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.junit.platform</groupId>
        <artifactId>junit-platform-suite</artifactId>
        <version>1.10.1</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### 2.2 基础测试结构
```java
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

@Tag("st")
@DisplayName("系统测试")
class SystemTest {

    private static Application app;
    private static Database db;

    @BeforeAll
    static void setupAll() {
        app = Application.start(config);
        db = new Database();
    }

    @AfterAll
    static void teardownAll() {
        app.stop();
    }

    @BeforeEach
    void setup() {
        db.clean();
    }

    @Test
    @DisplayName("用户登录成功")
    void userLoginSuccess() {
        Result result = app.login("user", "pass");
        assertTrue(result.isSuccess());
        assertEquals("token", result.getToken());
    }

    @Test
    @DisplayName("用户登录失败")
    void userLoginFailure() {
        Result result = app.login("user", "wrong");
        assertFalse(result.isSuccess());
        assertEquals("INVALID_CREDENTIALS", result.getError());
    }
}
```

### 2.3 参数化测试
```java
@ParameterizedTest
@CsvSource({
    "admin, admin123, SUCCESS",
    "user, user123, SUCCESS",
    "guest, guest123, SUCCESS",
    "invalid, '', ERROR"
})
@DisplayName("多用户登录测试")
void multiUserLogin(String username, String password, String expected) {
    Result result = app.login(username, password);
    assertEquals(expected, result.getStatus());
}
```

### 2.4 测试套件
```java
@RunWith(JUnitPlatform.class)
@Suite({
    AuthenticationST.class,
    UserManagementST.class,
    DataProcessingST.class
})
@IncludeTags("st")
public class SystemTestSuite {
}
```

### 2.5 Maven Surefire 配置
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.3</version>
    <configuration>
        <includes>
            <include>**/*ST.java</include>
        </includes>
        <groups>st</groups>
        <properties>
            <tags>st</tags>
        </properties>
    </configuration>
</plugin>
```

---

## 3. JavaScript: Jest

### 3.1 安装
```bash
npm install --save-dev jest @types/jest ts-jest
```

### 3.2 配置
**jest.config.js**
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests/st'],
  testMatch: ['**/*.test.ts', '**/*.spec.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts'
  ],
  coverageDirectory: 'coverage/st',
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/st/setup.ts'],
  testTimeout: 30000,
  verbose: true
};
```

### 3.3 基础测试结构
```typescript
import { describe, test, expect, beforeAll, afterAll, beforeEach } from '@jest/globals';

describe('System Tests', () => {
  let app: Application;
  let db: Database;

  beforeAll(async () => {
    app = await Application.create(testConfig);
    db = new Database();
    await db.connect();
  });

  afterAll(async () => {
    await app.close();
    await db.disconnect();
  });

  beforeEach(async () => {
    await db.clean();
  });

  test('user login success', async () => {
    const result = await app.login('user', 'pass');
    expect(result.success).toBe(true);
    expect(result.token).toBeDefined();
  });

  test('user login failure', async () => {
    const result = await app.login('user', 'wrong');
    expect(result.success).toBe(false);
    expect(result.error).toBe('INVALID_CREDENTIALS');
  });
});
```

### 3.4 数据驱动测试
```typescript
test.each`
  username    | password   | expected
  ${'admin'}  | ${'admin'} | ${'success'}
  ${'user'}   | ${'user'}  | ${'success'}
  ${'invalid'}| ${''}      | ${'error'}
`('login with $username should return $expected', async ({ username, password, expected }) => {
  const result = await app.login(username, password);
  expect(result.status).toBe(expected);
});
```

### 3.5 Mock 使用
```typescript
import { jest } from '@jest/globals';

test('external API call', async () => {
  const mockFn = jest.fn().mockResolvedValue({ data: 'test' });

  const result = await app.fetchData(mockFn);
  expect(mockFn).toHaveBeenCalled();
  expect(result.data).toBe('test');
});
```

### 3.6 测试报告
```bash
# JSON 报告
jest --json --outputFile=reports/st-report.json

# HTML 报告（需 jest-html-reporter）
jest --html-reporter --outputFile=reports/st-report.html
```

---

## 4. TypeScript: Vitest

### 4.1 安装
```bash
npm install --save-dev vitest @vitest/ui
```

### 4.2 配置
**vite.config.ts**
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/st/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70
      }
    },
    setupFiles: ['./tests/st/setup.ts'],
    testTimeout: 30000
  }
});
```

### 4.3 基础测试结构
```typescript
import { describe, test, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';

describe('System Tests', () => {
  beforeAll(async () => {
    await app.start();
  });

  afterAll(async () => {
    await app.stop();
  });

  test('integration test', async () => {
    const result = await app.processOrder(orderData);
    expect(result.status).toBe('success');
  });
});
```

---

## 5. 测试数据管理

### 5.1 测试数据原则
- **独立性**: 每个测试应能独立运行，不依赖其他测试
- **可重复性**: 测试数据应能多次使用，结果一致
- **真实性**: 使用接近生产环境的数据
- **最小化**: 只包含测试所需的最小数据集

### 5.2 数据文件结构
```
tests/
├── st/
│   ├── fixtures/
│   │   ├── users.json
│   │   ├── products.json
│   │   └── orders.json
│   ├── setup.ts
│   └── user.test.ts
```

### 5.3 Fixture 使用示例
```python
# pytest fixture 文件
# tests/st/fixtures/users.json
[
  {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "expected": "success"
  },
  {
    "id": 2,
    "username": "user",
    "role": "user",
    "expected": "success"
  }
]
```

---

## 6. 测试环境管理

### 6.1 环境隔离
```python
# 独立测试数据库
@pytest.fixture(scope="session")
def test_db():
    db = create_test_db()
    yield db
    db.destroy()

# 独立配置文件
@pytest.fixture(scope="session")
def test_config():
    return load_config("test_config.yaml")
```

### 6.2 Docker 集成
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  app:
    build: .
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://test:test@db:5432/testdb
      - REDIS_URL=redis://redis:6379

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=testdb

  redis:
    image: redis:7
```

---

## 7. CI/CD 集成

### 7.1 GitHub Actions
```yaml
- name: Run System Tests
  run: npm run test:st
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

- name: Upload ST Report
  uses: actions/upload-artifact@v3
  with:
    name: st-report
    path: reports/st/
```

### 7.2 测试策略建议
| 测试类型 | 执行时机 | 超时设置 |
|----------|----------|----------|
| 冒烟测试 | 每次提交 | 5 分钟 |
| 完整 ST | 每日构建 | 30 分钟 |
| 回归测试 | 每次发布 | 60 分钟 |
