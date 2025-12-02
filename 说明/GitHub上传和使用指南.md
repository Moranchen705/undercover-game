# GitHub上传和使用指南

## 一、上传项目到GitHub（主持方操作）

### 准备工作

1. **确保项目完整**
   - 检查所有代码文件是否完整
   - 确认没有敏感信息（如密码、密钥等硬编码）

2. **检查.gitignore**
   - 项目根目录已有 `.gitignore` 文件
   - 确保 `__pycache__/`、`*.pyc` 等文件不会被上传

### 步骤1：在GitHub上创建仓库

1. 登录GitHub（如果没有账号，先注册：https://github.com）
2. 点击右上角 `+` → `New repository`
3. 填写仓库信息：
   - **Repository name**: 例如 `undercover-game` 或 `谁是卧底`
   - **Description**: 可选，填写项目描述
   - **Visibility**: 
     - `Public`：公开，所有人都能看到
     - `Private`：私有，只有你和协作者能看到（推荐用于课程作业）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 `Create repository`

### 步骤2：在本地初始化Git仓库

**如果项目还没有Git仓库：**

```bash
# 1. 进入项目根目录
cd "E:\学习资料\2025-2026-1\Python\谁是卧底"

# 2. 初始化Git仓库
git init

# 3. 添加所有文件到暂存区
git add .

# 4. 提交文件
git commit -m "Initial commit: 谁是卧底游戏项目"
```

**如果项目已经有Git仓库：**

```bash
# 检查当前状态
git status

# 如果有未提交的更改，先提交
git add .
git commit -m "Update: 更新项目文件"
```

### 步骤3：连接GitHub远程仓库

```bash
# 添加远程仓库（将 YOUR_USERNAME 和 REPO_NAME 替换为你的实际信息）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 例如：
# git remote add origin https://github.com/zhangsan/undercover-game.git
```

### 步骤4：推送代码到GitHub

```bash
# 推送到GitHub（首次推送）
git branch -M main
git push -u origin main
```

**如果遇到认证问题：**

GitHub已不再支持密码认证，需要使用个人访问令牌（Personal Access Token）：

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成后复制令牌
5. 推送时，用户名输入GitHub用户名，密码输入令牌

或者使用SSH方式（推荐）：

```bash
# 使用SSH地址（需要先配置SSH密钥）
git remote set-url origin git@github.com:YOUR_USERNAME/REPO_NAME.git
```

### 步骤5：验证上传成功

1. 刷新GitHub网页，应该能看到所有文件
2. 检查是否有遗漏的文件
3. 确认 `__pycache__/` 等目录没有被上传

## 二、组员下载和使用（游戏方操作）

### 方法1：使用Git克隆（推荐）

```bash
# 1. 克隆仓库到本地
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git

# 例如：
# git clone https://github.com/zhangsan/undercover-game.git

# 2. 进入项目目录
cd REPO_NAME

# 3. 查看项目结构
dir  # Windows
# 或
ls   # Mac/Linux
```

### 方法2：直接下载ZIP（简单但无法同步更新）

1. 在GitHub仓库页面，点击绿色的 `Code` 按钮
2. 选择 `Download ZIP`
3. 解压到本地目录

### 安装依赖

```bash
# 进入项目目录
cd "项目路径"

# 安装游戏方依赖
cd 玩家方
pip install -r Requirements.txt

# 如果需要运行主持方（通常不需要）
cd ../平台方
pip install -r requirements.txt
```

### 运行游戏客户端

```bash
# 进入玩家方目录
cd 玩家方

# 运行客户端
python client.py
```

## 三、后续更新和同步

### 主持方更新代码后

```bash
# 1. 修改代码后，提交更改
git add .
git commit -m "Update: 描述你的更改"

# 2. 推送到GitHub
git push origin main
```

### 组员获取最新代码

```bash
# 在项目目录下执行
git pull origin main
```

**如果使用ZIP下载的组员：**
- 需要重新下载ZIP并替换文件（不推荐，建议改用Git）

## 四、协作建议

### 1. 分支管理（可选，适合多人协作）

```bash
# 创建新分支
git checkout -b feature/新功能名称

# 提交更改
git add .
git commit -m "Add: 新功能描述"

# 推送到远程分支
git push origin feature/新功能名称

# 在GitHub上创建Pull Request合并到main分支
```

### 2. 提交信息规范

使用清晰的提交信息：
- `Add: 添加新功能`
- `Fix: 修复bug`
- `Update: 更新功能`
- `Docs: 更新文档`

### 3. 文件组织

- 代码文件放在对应目录
- 文档放在 `说明/` 目录
- 不要上传临时文件和缓存

## 五、常见问题

### Q1: 推送时提示"Permission denied"

**解决方法：**
1. 检查GitHub账号是否正确
2. 使用个人访问令牌（Personal Access Token）代替密码
3. 或配置SSH密钥

### Q2: 如何添加协作者？

1. 在GitHub仓库页面，点击 `Settings`
2. 左侧菜单选择 `Collaborators`
3. 点击 `Add people`
4. 输入组员的GitHub用户名或邮箱
5. 组员会收到邀请邮件，接受后即可访问仓库

### Q3: 如何查看谁修改了什么？

```bash
# 查看提交历史
git log

# 查看文件修改历史
git log --follow 文件名

# 查看具体修改内容
git show 提交ID
```

### Q4: 误上传了敏感信息怎么办？

1. **立即修改敏感信息**（如密码、密钥）
2. **从Git历史中删除**（需要强制推送，谨慎操作）：
   ```bash
   # 使用 git filter-branch 或 BFG Repo-Cleaner
   # 注意：这会重写历史，需要所有协作者重新克隆
   ```
3. **最佳实践**：使用环境变量或配置文件（不提交到Git）

### Q5: 组员如何贡献代码？

1. 组员克隆仓库
2. 创建新分支进行开发
3. 提交并推送到自己的分支
4. 在GitHub上创建Pull Request
5. 主持方审查后合并

## 六、快速检查清单

### 上传前检查：

- [ ] 代码完整且可以运行
- [ ] 没有硬编码的密码或密钥
- [ ] `.gitignore` 配置正确
- [ ] `__pycache__/` 等目录不会被上传
- [ ] README文件清晰易懂
- [ ] 依赖文件（requirements.txt）完整

### 下载后检查：

- [ ] 所有文件都已下载
- [ ] 依赖已正确安装
- [ ] 可以成功运行客户端
- [ ] 能够连接到主持方服务器

## 七、推荐工作流程

### 日常开发：

1. **主持方**：
   - 开发新功能
   - 测试通过后提交并推送
   - 通知组员更新

2. **组员**：
   - 定期执行 `git pull` 获取最新代码
   - 测试新功能
   - 反馈问题或建议

### 测试阶段：

1. 主持方在GitHub上发布稳定版本（使用Git Tag）
2. 组员下载指定版本进行测试
3. 发现问题及时反馈

## 八、GitHub仓库设置建议

1. **添加README.md**（如果还没有）：
   - 项目简介
   - 快速开始指南
   - 联系方式

2. **添加LICENSE**（可选）：
   - 选择适合的开源许可证

3. **设置分支保护**（可选）：
   - Settings → Branches
   - 保护main分支，防止直接推送

4. **添加项目描述和标签**：
   - 让项目更容易被找到和理解

