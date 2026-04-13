# VibeFlow Ship 能力增强方案

> 对标 gstack `/ship` 阶段，聚焦**代码上库、PR 管理、GitHub CI/CD 流水线**三大方向的能力补齐。

## 1. 现状分析

### 1.1 当前 vibeflow-ship 已具备的能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 版本管理 | ✅ | semver，支持 VERSION/package.json/pyproject.toml |
| RELEASE_NOTES.md | ✅ | Keep a Changelog 格式 |
| Git Commit + Tag | ✅ | 发布提交 + 可选 tag |
| PR 创建 | ✅ | 支持 --draft/--reviewer/--milestone |
| PR 合并 | ✅ | 询问后 squash merge |
| Issue 同步 | ✅ | vibeflow-repo-sync，Parent/Child 层级 |
| PR Comment 同步 | ✅ | Review 结论自动同步 |

### 1.2 对标 gstack 的关键缺失（按优先级排序）

| # | 缺失能力 | gstack 对应步骤 | 影响 |
|---|---------|----------------|------|
| G1 | CI/CD 流水线自动生成 | Step 2.5 + Step 1.5 | 无法为新项目自动创建 GitHub Actions |
| G2 | Push + PR 幂等性 | Step 7 + Step 8 | 重复执行 ship 会创建重复 PR |
| G3 | Merge base branch + 冲突处理 | Step 2 | 分支落后时 ship 会失败 |
| G4 | Bisectable commits | Step 6 | 所有变更打成一个提交，不利于 bisect |
| G5 | 验证门禁（Verification Gate） | Step 5.5 | Review 后改了代码不会重新跑测试 |
| G6 | PR Body 动态更新 | Step 8 idempotency | 后续 docs 提交不会更新 PR 描述 |
| G7 | 测试覆盖率审计 | Step 3.4 | 没有代码路径 → 测试的映射检查 |
| G8 | 计划完成度审计 | Step 3.45 | 不检查 tasks.md 的完成情况 |
| G9 | Land & Deploy | 独立 skill | 只到 PR 创建，没有合并后的 CI 等待和部署验证 |

---

## 2. 增强方案

### 优先级分层

```
P0（必须先做）：G1 CI/CD 流水线 + G2 幂等性 + G3 Merge base
P1（紧接其后）：G4 Bisectable commits + G5 验证门禁 + G6 PR Body 更新
P2（按需补齐）：G7 覆盖率审计 + G8 计划完成度 + G9 Land & Deploy
```

---

### 2.1 [P0] CI/CD 流水线自动生成

**目标**：ship 时若项目缺少 CI/CD 配置，自动检测技术栈并生成 GitHub Actions workflow。

#### 2.1.1 设计

在 ship 流程的 **步骤 1（发布前检查）之后** 插入新步骤 **1.5 CI/CD 检查**。

```
步骤 1: 发布前检查
  ↓
步骤 1.5: CI/CD 流水线检查 ← 新增
  ↓
步骤 2: 版本管理
```

#### 2.1.2 流程

```
1.5a 检测项目运行时
  ├── package.json → Node.js（检查 devDependencies 区分 Vitest/Jest/Playwright）
  ├── pyproject.toml / requirements.txt → Python（检查 pytest/unittest）
  ├── Cargo.toml → Rust
  ├── go.mod → Go
  ├── Gemfile → Ruby
  └── composer.json → PHP

1.5b 检查是否已有 CI 配置
  ├── .github/workflows/*.yml 存在 → 跳过
  ├── .gitlab-ci.yml 存在 → 跳过
  └── 均不存在 → 进入生成流程

1.5c 检查是否存在测试框架
  ├── 已有（jest.config.*/vitest.config.*/pytest.ini 等）→ 直接生成 workflow
  └── 无测试框架 → 询问用户
      ├── (A) 现在 bootstrap 测试框架 + CI
      ├── (B) 只生成 CI（跳过测试步骤）
      └── (C) 跳过，不需要 CI

1.5d 生成 .github/workflows/ci.yml
  - 触发条件：push + pull_request（目标分支 main/master）
  - 步骤：checkout → 安装依赖 → lint（如有）→ test → build（如有）
  - 使用检测到的包管理器（pnpm/yarn/npm/pip/cargo 等）
  - 矩阵策略：Node 版本 / Python 版本（可选）

1.5e 提交 CI 配置
  git add .github/workflows/ci.yml
  git commit -m "chore: bootstrap CI/CD pipeline (GitHub Actions)"
```

#### 2.1.3 模板示例（Node.js + Vitest）

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      - name: Lint
        run: pnpm lint
      - name: Test
        run: pnpm test
      - name: Build
        run: pnpm build
```

#### 2.1.4 Distribution Pipeline（Step 1.5 扩展）

当 diff 包含新的独立产物（CLI 二进制、npm 包、PyPI 库）时：

```
检测信号：
  - 新增 bin/ 或 cmd/ 目录
  - package.json 新增 "bin" 字段
  - setup.py / pyproject.toml 新增 [project.scripts]
  - Cargo.toml 新增 [[bin]]

处理逻辑：
  ├── 已有 release workflow → 跳过
  ├── 无 release workflow → 询问
  │   ├── (A) 生成 release workflow（tag 触发 → build → publish）
  │   ├── (B) 添加到 TODOS，后续处理
  │   └── (C) 不需要（内部工具 / Web 应用）
```

#### 2.1.5 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 插入步骤 1.5
- **新增**：`templates/ci/` 目录，存放各运行时的 workflow 模板

---

### 2.2 [P0] Push + PR 幂等性

**目标**：`/vibeflow-ship` 可安全重复执行，不会创建重复 PR 或重复 push。

#### 2.2.1 Push 幂等性

在步骤 7（原"创建 PR"）之前插入 push 步骤，并加入幂等检查：

```bash
# 检查是否需要 push
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$(git branch --show-current) 2>/dev/null || echo "none")

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "分支已推送至远端，跳过 push"
else
  git push -u origin $(git branch --show-current)
fi
```

#### 2.2.2 PR 幂等性

```bash
# 检查当前分支是否已有 open PR
EXISTING_PR=$(gh pr view --json number,state 2>/dev/null)

if [ $? -eq 0 ] && [ "$(echo $EXISTING_PR | jq -r '.state')" = "OPEN" ]; then
  # PR 已存在 → 更新 body
  PR_NUM=$(echo $EXISTING_PR | jq -r '.number')
  gh pr edit $PR_NUM --body "$(cat <<'EOF'
  ... 重新生成的 PR body ...
  EOF
  )"
  echo "PR #$PR_NUM body 已更新"
else
  # PR 不存在 → 创建新 PR
  gh pr create --title "..." --body "..." --draft
fi
```

#### 2.2.3 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 步骤 7 重写为 push + PR 双幂等

---

### 2.3 [P0] Merge Base Branch + 冲突处理

**目标**：ship 前自动合并 base branch，确保分支不落后。

#### 2.3.1 流程

在步骤 1.5 之后、步骤 2 之前插入 **步骤 1.7 合并 base branch**：

```
1.7a 获取 base branch
  - 从 PR target 读取，或默认 main/master
  - git fetch origin <base>

1.7b 检查是否需要合并
  - git merge-base --is-ancestor origin/<base> HEAD
  - 若已是最新 → 跳过
  - 若有新提交 → 执行合并

1.7c 执行合并
  git merge origin/<base> --no-edit

1.7d 冲突处理
  ├── 无冲突 → 继续
  ├── 简单冲突（VERSION / CHANGELOG / RELEASE_NOTES.md）→ 自动解决
  │   - VERSION: 取当前分支版本
  │   - CHANGELOG: 保留双方内容
  └── 复杂冲突 → 停止，提示用户手动解决
      git merge --abort
      "发现无法自动解决的合并冲突，请手动处理后重新运行 ship。"
```

#### 2.3.2 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 插入步骤 1.7

---

### 2.4 [P1] Bisectable Commits

**目标**：将变更拆分为逻辑独立的提交，每个提交可单独编译通过。

#### 2.4.1 分组策略

```
提交顺序（从先到后）：
  1. 基础设施：migrations, config, routes, .env.example
  2. 模型 & 服务：model + 对应 test
  3. 控制器 & 视图：controller + view + 对应 test
  4. 工具 & 脚本：scripts, utilities
  5. 元数据：VERSION + CHANGELOG + RELEASE_NOTES.md + TODOS

分组规则：
  - 同一功能的 source + test → 同一提交
  - 每个提交不引入 broken import
  - 依赖项在被依赖项之前提交
```

#### 2.4.2 提交消息格式

```
<type>: <summary>

type ∈ {feat, fix, chore, refactor, docs, test, style, perf}
```

最后一个提交附加 Co-Author：

```
chore: bump version to vX.Y.Z

Co-Authored-By: Claude <noreply@anthropic.com>
```

#### 2.4.3 替换现有逻辑

当前步骤 5 的 `git add -A && git commit` 改为多步分组提交逻辑。

#### 2.4.4 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 步骤 5 重写

---

### 2.5 [P1] 验证门禁（Verification Gate）

**目标**：如果 Review 阶段之后修改了代码，必须重新运行测试，不接受过时的测试结果。

#### 2.5.1 铁律

> **NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.**

#### 2.5.2 流程

在 CHANGELOG/TODOS 更新（步骤 3）之后、提交（步骤 5）之前，插入 **步骤 4.5 验证门禁**：

```
4.5a 判断是否需要重新测试
  - 对比最后一次测试运行时的 HEAD 与当前 HEAD
  - 仅 CHANGELOG / RELEASE_NOTES / 文档变更 → 不触发
  - 任何源码 / 测试代码变更 → 触发

4.5b 重新运行测试
  - 执行与步骤 1 相同的完整测试套件
  - 失败 → 停止 ship，修复后重新运行

4.5c 重新运行构建（如有）
  - 项目有 build 步骤时执行
  - 失败 → 停止

4.5d 禁止绕过
  - "应该没问题" → 运行它
  - "我很有信心" → 信心 ≠ 证据
  - "已经测试过了" → 代码改了，重测
```

#### 2.5.3 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 插入步骤 4.5

---

### 2.6 [P1] PR Body 动态更新

**目标**：ship 后续步骤（如 docs 更新、CI 配置提交）产生新 commit 时，自动更新 PR body。

#### 2.6.1 机制

```
每次产生新 commit 并 push 后：
  1. 检查当前分支是否有 open PR
  2. 如有 → 基于最新状态重新生成 PR body
  3. gh pr edit <number> --body "<新 body>"
```

#### 2.6.2 触发点

- 步骤 1.5 CI 配置提交后
- 步骤 4 文档更新提交后
- 任何 review fix 提交后

#### 2.6.3 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 在每个可能产生新 commit 的步骤末尾加入 PR body 刷新逻辑

---

### 2.7 [P2] 测试覆盖率审计

**目标**：将 diff 中的每条代码路径映射到测试，发现并补齐覆盖盲区。

#### 2.7.1 核心逻辑

```
1. 追踪 diff 中每条代码路径
   - 读取每个变更文件的完整内容
   - 追踪：函数/方法、条件分支（if/else/switch）、错误路径、调用链

2. 生成 ASCII 覆盖图
   ├── [★★★ TESTED] — happy + edge + error 均有测试
   ├── [★★  TESTED] — 仅 happy path
   ├── [★   TESTED] — 仅 smoke test
   └── [GAP]        — 无测试覆盖

3. 为 GAP 路径生成测试
   - 优先错误处理和边界条件
   - 读取 2-3 个已有测试文件，匹配风格
   - 生成后运行 → 通过则提交 → 失败则修一次 → 仍失败则回滚
   - 上限：30 条路径，20 个测试，每个测试 2 分钟

4. 门禁
   - >= 80%（目标值）→ PASS
   - >= 60% && < 80% → 询问用户
   - < 60% → 关键门禁，必须补齐或用户 override
```

#### 2.7.2 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 在步骤 1 之后插入覆盖率审计
- **可选**：与 `vibeflow-quality` 的覆盖率门禁整合

---

### 2.8 [P2] 计划完成度审计

**目标**：检查 tasks.md 中的任务是否全部完成，阻止遗漏上线。

#### 2.8.1 流程

```
1. 读取 tasks.md，提取所有任务项
2. 对每个任务，对比 diff 判定状态：
   - DONE     — diff 中有明确证据
   - PARTIAL  — 部分完成
   - NOT DONE — 无对应变更
   - CHANGED  — 换了方式但目标达成

3. 门禁
   - 全部 DONE/CHANGED → PASS
   - 有 PARTIAL → 继续，在 PR body 中标注
   - 有 NOT DONE → 询问用户
     ├── (A) 补实现再 ship
     ├── (B) 推迟到下个迭代（写入 TODOS）
     └── (C) 有意放弃（从 scope 中移除）

4. 结果写入 PR body 的 "计划完成度" 章节
```

#### 2.8.2 与 vibeflow-repo-sync 的协同

如果 Issue 已同步到 GitHub，完成度审计结果也可以自动关闭对应 Issue：

```bash
# 对每个 DONE 的任务，若有对应 Issue
gh issue close <issue-number> --comment "通过 ship 完成度审计确认完成"
```

#### 2.8.3 Skill 修改范围

- **修改**：`skills/vibeflow-ship/SKILL.md` — 插入步骤
- **修改**：`skills/vibeflow-repo-sync/SKILL.md` — 添加 Issue 自动关闭能力

---

### 2.9 [P2] Land & Deploy Skill

**目标**：PR 创建后的完整落地流程 — 合并 → 等待 CI → 部署 → 验证。

#### 2.9.1 新建独立 Skill

```
skills/vibeflow-land/SKILL.md
```

#### 2.9.2 流程

```
1. 合并 PR
   - gh pr merge --squash --delete-branch（或用户选择的策略）

2. 等待 CI
   - gh pr checks --watch（或轮询 gh run list）
   - 超时设置（默认 10 分钟）
   - CI 失败 → 报告并停止

3. 部署验证（如有部署配置）
   - 读取 .vibeflow/deploy.yaml 获取部署信息
   - 等待部署完成
   - 执行 health check（curl 验证 endpoint）

4. Canary 检查
   - 检查 console errors（如有浏览器 MCP）
   - 检查关键 API 可达性
   - 检查性能指标无异常

5. 完成确认
   - 展示部署状态
   - 链接到 vibeflow-reflect
```

#### 2.9.3 Skill 修改范围

- **新增**：`skills/vibeflow-land/SKILL.md`
- **修改**：`skills/vibeflow-ship/SKILL.md` — 步骤 9 过渡指向 vibeflow-land（可选）

---

## 3. 修改后的 Ship 流程全景

```
┌─────────────────────────────────────────────────────┐
│                   vibeflow-ship                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1.  发布前检查                    [现有]             │
│      ├── ST/QA 报告验证                              │
│      ├── feature-list.json 检查                      │
│      └── workflow.yaml 读取                          │
│                                                      │
│  1.5 CI/CD 流水线检查              [P0 新增]         │
│      ├── 运行时检测                                  │
│      ├── 已有 CI → 跳过                              │
│      └── 无 CI → 生成 GitHub Actions workflow        │
│                                                      │
│  1.7 合并 Base Branch             [P0 新增]          │
│      ├── git fetch + merge                           │
│      ├── 简单冲突自动解决                             │
│      └── 复杂冲突 → 停止                             │
│                                                      │
│  2.  版本管理                      [现有]             │
│                                                      │
│  3.  完善 RELEASE_NOTES.md         [现有]             │
│                                                      │
│  3.5 测试覆盖率审计               [P2 新增]          │
│      ├── 代码路径 → 测试映射                          │
│      ├── GAP 检测 + 自动补测试                        │
│      └── 覆盖率门禁                                  │
│                                                      │
│  3.7 计划完成度审计               [P2 新增]          │
│      ├── tasks.md 完成情况检查                        │
│      └── NOT DONE → 询问用户                         │
│                                                      │
│  4.  更新文档                      [现有]             │
│                                                      │
│  4.5 验证门禁                     [P1 新增]          │
│      ├── 代码变更 → 重新跑测试                        │
│      └── 失败 → 停止                                 │
│                                                      │
│  5.  创建发布提交                  [P1 重写]          │
│      └── Bisectable commits（逻辑分组 + 有序提交）    │
│                                                      │
│  6.  创建 Tag                      [现有]             │
│                                                      │
│  7.  Push + 创建/更新 PR           [P0 重写]          │
│      ├── Push 幂等性                                 │
│      ├── PR 幂等性（存在则更新 body）                 │
│      └── PR Body 动态更新          [P1 新增]          │
│                                                      │
│  8.  发布摘要                      [现有]             │
│                                                      │
│  9.  过渡                          [现有 + P2 扩展]   │
│      ├── → vibeflow-reflect                          │
│      └── → vibeflow-land（可选）   [P2 新增]          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 4. 实施计划

### Phase 1：P0 能力补齐（预计 3 个任务）

| 任务 | 修改文件 | 新增文件 | 预估工作量 |
|------|---------|---------|-----------|
| CI/CD 流水线自动生成 | `vibeflow-ship/SKILL.md` | `templates/ci/*.yml` | 中 |
| Push + PR 幂等性 | `vibeflow-ship/SKILL.md` | — | 小 |
| Merge base branch | `vibeflow-ship/SKILL.md` | — | 小 |

**验收标准**：
- [ ] 对无 CI 的新项目执行 ship，自动生成 `.github/workflows/ci.yml`
- [ ] 连续两次执行 ship 不会创建重复 PR
- [ ] 分支落后 base branch 时 ship 能自动合并

### Phase 2：P1 能力补齐（预计 3 个任务）

| 任务 | 修改文件 | 新增文件 | 预估工作量 |
|------|---------|---------|-----------|
| Bisectable commits | `vibeflow-ship/SKILL.md` | — | 中 |
| 验证门禁 | `vibeflow-ship/SKILL.md` | — | 小 |
| PR Body 动态更新 | `vibeflow-ship/SKILL.md` | — | 小 |

**验收标准**：
- [ ] ship 产出 ≥ 2 个逻辑提交（非单一 `git add -A`）
- [ ] Review 后修改代码，ship 时自动重新跑测试
- [ ] CI 配置提交后 PR body 自动刷新

### Phase 3：P2 能力补齐（预计 3 个任务）

| 任务 | 修改文件 | 新增文件 | 预估工作量 |
|------|---------|---------|-----------|
| 测试覆盖率审计 | `vibeflow-ship/SKILL.md` | — | 大 |
| 计划完成度审计 | `vibeflow-ship/SKILL.md`, `vibeflow-repo-sync/SKILL.md` | — | 中 |
| Land & Deploy | — | `vibeflow-land/SKILL.md` | 大 |

**验收标准**：
- [ ] ship 时输出 ASCII 覆盖率图，自动补齐 GAP 测试
- [ ] tasks.md 有未完成项时 ship 会询问处理方式
- [ ] PR merge 后自动等待 CI 并报告结果

---

## 5. 设计约束

1. **向后兼容**：所有新增步骤默认可跳过（无 CI 需求的项目不强制生成）
2. **最小侵入**：只修改 `vibeflow-ship/SKILL.md`，不改变现有阶段流转逻辑
3. **幂等安全**：每个步骤可重复执行，不产生副作用
4. **用户确认**：破坏性操作（merge、force push）必须征得用户同意
5. **工具依赖**：仅依赖 `gh` CLI + `git` + `jq`，不引入新的外部依赖
