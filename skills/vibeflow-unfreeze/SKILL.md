---
name: vibeflow-unfreeze
description: "清除 freeze-dir.txt 边界文件，解除 Edit/Write 操作限制。解除后可恢复全局编辑权限。"
---

# /vibeflow-unfreeze — 解除编辑边界

清除 `~/.vibeflow/freeze-dir.txt`，解除 `vibeflow-freeze` 设置的编辑边界限制。

**启动宣告：** "正在使用 vibeflow-unfreeze — 解除编辑边界限制。"

## 操作

使用 Bash 清除 freeze boundary：

```bash
STATE_DIR="${VIBEFLOW_STATE_DIR:-${HOME}/.vibeflow}"
rm -f "$STATE_DIR/freeze-dir.txt"
echo "Freeze boundary cleared. Edit restrictions removed."
```

## 完成确认

验证文件已删除：

```bash
STATE_DIR="${VIBEFLOW_STATE_DIR:-${HOME}/.vibeflow}"
if [ ! -f "$STATE_DIR/freeze-dir.txt" ]; then
  echo "SUCCESS: Freeze boundary removed. All directories are now editable."
else
  echo "WARNING: Freeze file still exists. Please check permissions."
fi
```

## 集成

**调用者：** 用户在需要解除编辑边界时主动调用
**依赖：** `~/.vibeflow/freeze-dir.txt`（如不存在则表示未设置 freeze）
**效果：** 解除 `vibeflow-freeze` 和 `vibeflow-guard` 的编辑限制
**链接到：** vibeflow-freeze / vibeflow-guard（重新激活边界）
