<!-- 由 vibeflow-deepresearch SKILL.md 拆分，完整性由引用者保证 -->

# GitHub 搜索策略

## 竞品发现搜索策略

### 基础搜索 Query 模板

| 场景 | Query 模板 | 说明 |
|------|-----------|------|
| Topic 搜索 | `topic:<领域> stars:>500 pushed:>2024-01-01` | 查找带有特定 topic 标签的高星项目 |
| 关键词搜索 | `<领域> framework stars:>1000` | 泛搜索框架类项目 |
| README 搜索 | `<领域> in:readme stars:>500` | 在 README 中搜索关键词 |
| 组合搜索 | `topic:<领域> language:TypeScript stars:>1000` | 按语言筛选 |

### 排序策略

```bash
# 按 stars 降序（默认）
gh search repos "<query>" --sort stars --limit 10

# 按更新时间排序
gh search repos "<query>" --sort stars --limit 10 | sort -t$'\t' -k3 -r
```

### 筛选条件

| 条件 | 值 | 理由 |
|------|-----|------|
| stars | > 500 | 过滤小众项目，保证一定社区认可度 |
| 更新 | < 12 months | 排除已废弃的项目 |
| stars 上限 | 不设 | 让社区投票选出真正有价值的 |
| language | 不限 | 初次搜索不限制，发现后再按语言分类 |

---

## 竞品列表生成流程

### Step 1: 初始搜索（10-20 个）

```bash
# 执行 2-3 个不同 query 的搜索
gh search repos "AI agent framework stars:>500" --sort stars --limit 15
gh search repos "topic:ai-agents stars:>500" --sort stars --limit 15
```

### Step 2: 去重和筛选

- 去除重复项目
- 按 stars 排序
- 选择 Top 5-10 作为深度分析对象

### Step 3: 补充信息获取

```bash
# 获取每个项目的详细信息
gh repo view <owner>/<repo> --json name,description,stargazersCount,pushedAt,primaryLanguage,defaultBranchRef

# 验证项目仍在维护（最近 6 个月有更新）
gh repo view <owner>/<repo> --json pushedAt
```

---

## 常见领域 Query 示例

| 领域 | 推荐 Query |
|------|-----------|
| AI Agent | `AI agent framework stars:>500`<br>`topic:ai-agents stars:>500` |
| CLI 部署工具 | `CLI deployment automation stars:>500`<br>`devops CLI tool stars:>500` |
| 低代码平台 | `low-code platform stars:>500`<br>`topic:low-code stars:>500` |
| API Gateway | `API gateway stars:>500`<br>`topic:api-gateway stars:>500` |
| 任务队列 | `task queue stars:>500`<br>`message queue stars:>500` |

---

## 技术栈发现搜索

### 依赖文件搜索

| 语言 | 依赖文件 | API 路径 |
|------|----------|----------|
| JavaScript/TypeScript | `package.json` | `/repos/{owner}/{repo}/contents/package.json` |
| Python | `requirements.txt`<br>`pyproject.toml` | `/repos/{owner}/{repo}/contents/requirements.txt` |
| Rust | `Cargo.toml` | `/repos/{owner}/{repo}/contents/Cargo.toml` |
| Go | `go.mod` | `/repos/{owner}/{repo}/contents/go.mod` |
| Java | `pom.xml`<br>`build.gradle` | `/repos/{owner}/{repo}/contents/pom.xml` |

### 查询示例

```bash
# 获取 package.json
gh api repos/<owner>/<repo>/contents/package.json --jq '.content' | base64 -d

# 批量获取（对多个项目）
for repo in "owner/repo1" "owner/repo2" "owner/repo3"; do
  gh api repos/$repo/contents/package.json --jq '.content' 2>/dev/null | base64 -d
done
```

---

## 注意事项

1. **GitHub API 限制**：未认证请求每小时 60 次，认证后 5000 次
2. **Rate Limit 处理**：大批量调研时注意添加延迟
3. **Clone vs API**：频繁读取文件优先用 API，避免 clone 大仓库
4. **Stars 虚高**：某些项目因营销/资本因素 stars 虚高，需结合更新频率判断
